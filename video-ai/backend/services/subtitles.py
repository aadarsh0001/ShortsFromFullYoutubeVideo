from fastapi import UploadFile
from typing import Dict, List
import ffmpeg
import whisper
import os
from imageio_ffmpeg import get_ffmpeg_exe
import subprocess
import numpy as np

def _ensure_ffmpeg_on_path():
    """
    Ensure the bundled ffmpeg is discoverable by Whisper via PATH.
    """
    ffmpeg_bin = get_ffmpeg_exe()
    ff_dir = os.path.dirname(ffmpeg_bin)
    # Prepend to PATH for current process so child processes see it
    if ff_dir not in os.environ.get("PATH", ""):
        os.environ["PATH"] = ff_dir + os.pathsep + os.environ.get("PATH", "")

def _decode_audio_to_mono_16k(input_path: str) -> np.ndarray:
    """
    Use bundled ffmpeg to decode to 16kHz mono PCM and return float32 samples in [-1, 1].
    Avoids Whisper's internal ffmpeg call (fixes [WinError 2] on Windows without system ffmpeg).
    """
    ffmpeg_bin = get_ffmpeg_exe()
    cmd = [
        ffmpeg_bin,
        "-nostdin",
        "-y",
        "-i", input_path,
        "-ac", "1",
        "-ar", "16000",
        "-f", "s16le",
        "pipe:1",
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        err = proc.stderr.decode("utf-8", "ignore")
        raise RuntimeError(f"ffmpeg decode failed: {err}")
    # int16 PCM -> float32
    audio_i16 = np.frombuffer(proc.stdout, dtype=np.int16)
    if audio_i16.size == 0:
        raise RuntimeError("Decoded audio is empty.")
    audio = audio_i16.astype(np.float32) / 32768.0
    return audio

def transcribe(path: str, model_size: str = "tiny") -> Dict:
    """
    Returns { language, segments: [{start,end,text}], text } using Whisper,
    with audio decoded via bundled ffmpeg (no system install required).
    """
    if not os.path.exists(path):
        raise FileNotFoundError(path)

    audio = _decode_audio_to_mono_16k(path)

    model = whisper.load_model(model_size)
    # Pass the raw audio array directly; force CPU-friendly settings
    res = model.transcribe(audio=audio, fp16=False, word_timestamps=False)
    segments = [
        {"start": float(s["start"]), "end": float(s["end"]), "text": s["text"]}
        for s in res.get("segments", []) or []
    ]
    return {
        "language": res.get("language"),
        "segments": segments,
        "text": res.get("text"),
    }

class SubtitleService:
    def __init__(self):
        self.model = self.load_whisper_model()

    def generate_subtitles(self, audio_file: UploadFile) -> List[dict]:
        transcription = self.transcribe_audio(audio_file.file)
        subtitles = self._format_subtitles(transcription)
        return subtitles

    def _format_subtitles(self, transcription: dict) -> List[dict]:
        subtitles = []
        for segment in transcription['segments']:
            subtitles.append({
                'start': segment['start'],
                'end': segment['end'],
                'text': segment['text']
            })
        return subtitles

    def burn_subtitles_to_video(self, video_file: str, subtitles: List[dict], output_file: str):
        subtitle_file = self._create_subtitle_file(subtitles)
        (
            ffmpeg
            .input(video_file)
            .output(output_file, vf=f'subtitles={subtitle_file}')
            .run()
        )

    def _create_subtitle_file(self, subtitles: List[dict]) -> str:
        subtitle_path = 'temp_subtitles.srt'
        with open(subtitle_path, 'w') as f:
            for subtitle in subtitles:
                f.write(f"{subtitle['start']} --> {subtitle['end']}\n")
                f.write(f"{subtitle['text']}\n\n")
        return subtitle_path

    def load_whisper_model(self, model_size: str = "base"):
        return whisper.load_model(model_size)

    def transcribe_audio(self, path: str) -> Dict:
        res = self.model.transcribe(path, word_timestamps=False)
        segments = [{"start": float(s["start"]), "end": float(s["end"]), "text": s["text"]} for s in res.get("segments", [])]
        return {
            "language": res.get("language"),
            "segments": segments,
            "text": res.get("text"),
        }