import os
import subprocess
from typing import List, Tuple
from imageio_ffmpeg import get_ffmpeg_exe

def cut_and_resize_9x16(input_path: str, out_dir: str, windows: List[Tuple[float,float]]) -> List[str]:
    os.makedirs(out_dir, exist_ok=True)
    ffmpeg_bin = get_ffmpeg_exe()
    outputs = []
    for idx, (st, en) in enumerate(windows, start=1):
        dur = max(0.1, en - st)
        out_path = os.path.join(out_dir, f"clip_{idx:02d}_9x16.mp4")
        cmd = [
            ffmpeg_bin, "-y",
            "-ss", f"{st}",
            "-t", f"{dur}",
            "-i", input_path,
            "-vf", "scale=-1:1920,crop=1080:1920",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
            "-c:a", "aac", "-b:a", "128k",
            out_path
        ]
        # Binary output; no text decoding to avoid cp1252 errors
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if proc.returncode != 0:
            err = proc.stderr.decode("utf-8", "ignore")
            raise RuntimeError(f"ffmpeg failed for window {st}-{en}: {err}")
        outputs.append(out_path)
    return outputs