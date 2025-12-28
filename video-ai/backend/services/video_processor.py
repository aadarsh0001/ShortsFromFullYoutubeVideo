import subprocess
import os
from typing import Dict, Any

import cv2  # OpenCV
from imageio_ffmpeg import get_ffmpeg_exe  # bundled ffmpeg path

def _video_metadata(input_path: str) -> Dict[str, Any]:
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise RuntimeError(f"Unable to open video: {input_path}")
    fps = cap.get(cv2.CAP_PROP_FPS) or None
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0) or None
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0) or None
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0
    cap.release()
    duration = None
    if fps and frame_count and fps > 0:
        duration = float(frame_count) / float(fps)
    return {
        "duration_sec": duration,
        "fps": fps if fps and fps > 0 else None,
        "resolution": {"width": width, "height": height},
    }

def extract_audio(input_path: str, output_path: str) -> None:
    ffmpeg_bin = get_ffmpeg_exe()  # local ffmpeg binary managed by imageio-ffmpeg
    cmd = [
        ffmpeg_bin,
        "-y",
        "-i", input_path,
        "-vn",
        "-acodec", "aac",
        "-b:a", "192k",
        output_path,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg audio extract failed: {proc.stderr or proc.stdout}")

def process_video(input_path: str) -> Dict[str, Any]:
    if not os.path.exists(input_path):
        raise FileNotFoundError(input_path)

    meta = _video_metadata(input_path)

    base, _ = os.path.splitext(input_path)
    audio_path = base + ".m4a"
    extract_audio(input_path, audio_path)

    return {
        "input": input_path,
        "audio": audio_path,
        **meta,
    }