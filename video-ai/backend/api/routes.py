from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from services.video_processor import process_video
from services.subtitles import transcribe
from services.clip_selector import select_highlights
from services.ffmpeg_cut import cut_and_resize_9x16
import tempfile, os, shutil, subprocess, uuid, pathlib

router = APIRouter()

VIDEOS_DIR = os.path.abspath(os.path.join(os.getcwd(), "..", "outputs", "videos"))
CLIPS_DIR = os.path.abspath(os.path.join(os.getcwd(), "..", "outputs", "clips"))
os.makedirs(VIDEOS_DIR, exist_ok=True)
os.makedirs(CLIPS_DIR, exist_ok=True)

class UrlRequest(BaseModel):
    url: str

@router.get("/health")
def health():
    return {"status": "ok"}

@router.post("/process")
async def process(file: UploadFile = File(...)):
    """
    Save uploaded file to outputs/videos, then process and return a stable input path.
    """
    # create a stable filename
    suffix = pathlib.Path(file.filename).suffix or ".mp4"
    stable_name = f"upload_{uuid.uuid4().hex}{suffix}"
    stable_path = os.path.join(VIDEOS_DIR, stable_name)

    try:
        # stream write to avoid large memory
        with open(stable_path, "wb") as out:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                out.write(chunk)

        result = process_video(stable_path)
        # override input to stable path (not temp)
        result["input"] = stable_path
        return {"message": "processed", "metadata": result}
    except Exception as e:
        # cleanup on error
        try:
            if os.path.exists(stable_path):
                os.remove(stable_path)
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process-url")
def process_url(req: UrlRequest):
    """
    Download YouTube video to outputs/videos, process, and return stable input path.
    """
    url = req.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="URL is required.")

    work_dir = tempfile.mkdtemp(prefix="videoai_")
    try:
        output_tpl = os.path.join(work_dir, "%(title)s.%(ext)s")
        # Use binary capture to avoid Windows cp1252 decode thread crashes
        proc = subprocess.run(
            ["yt-dlp", "--no-progress", "-f", "mp4", "-o", output_tpl, url],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        if proc.returncode != 0:
            err = proc.stderr.decode("utf-8", "ignore") or proc.stdout.decode("utf-8", "ignore")
            raise HTTPException(status_code=400, detail=f"yt-dlp failed: {err}")

        files = [f for f in os.listdir(work_dir) if f.lower().endswith(".mp4")]
        if not files:
            raise HTTPException(status_code=404, detail="No MP4 downloaded. Try another URL.")
        downloaded = os.path.join(work_dir, files[0])

        # Move to stable outputs/videos path
        base_name = pathlib.Path(files[0]).stem
        stable_name = f"yt_{base_name}_{uuid.uuid4().hex}.mp4"
        stable_path = os.path.join(VIDEOS_DIR, stable_name)
        shutil.move(downloaded, stable_path)

        result = process_video(stable_path)
        result["input"] = stable_path
        return {"message": "processed", "metadata": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # cleanup temp dir, but we kept the video in outputs/videos
        try:
            shutil.rmtree(work_dir)
        except Exception:
            pass

class GenerateClipsRequest(BaseModel):
    input_path: str
    aspect: str = "9:16"
    max_clips: int = 5
    model_size: str = "tiny"

@router.post("/generate-clips")
def generate_clips(req: GenerateClipsRequest):
    """
    Transcribe, select highlight windows, cut and resize to 9:16.
    """
    input_path = req.input_path
    if not os.path.exists(input_path):
        raise HTTPException(status_code=404, detail="Input video not found.")

    try:
        tr = transcribe(input_path, model_size=req.model_size)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {e}")

    segs = tr.get("segments", [])
    if not segs:
        raise HTTPException(status_code=400, detail="No speech segments found.")

    windows = select_highlights(segs, max_clips=req.max_clips)

    try:
        out_files = cut_and_resize_9x16(input_path, CLIPS_DIR, windows)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Clip cutting failed: {e}")

    # Return relative paths for browser download if you serve static files later
    return {
        "message": "clips_created",
        "count": len(out_files),
        "clips": out_files,
        "windows": windows,
        "language": tr.get("language"),
    }