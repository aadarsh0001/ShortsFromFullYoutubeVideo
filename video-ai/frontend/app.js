// filepath: video-ai/frontend/app.js

const API_BASE = "http://127.0.0.1:8000/api";

let lastInputPath = null;

const uploadInput = document.getElementById("videoUpload");
const uploadBtn = document.getElementById("uploadButton");
const uploadStatus = document.getElementById("uploadStatus");

const urlInput = document.getElementById("videoUrl");
const processUrlBtn = document.getElementById("processUrlButton");
const urlStatus = document.getElementById("urlStatus");

const clipsDiv = document.getElementById("clips");
const subtitlesToggle = document.getElementById("subtitlesToggle");
const aspectRatioSelect = document.getElementById("aspectRatio");

function pathToOutputsUrl(p) {
  const marker = "\\outputs\\";
  const idx = p.toLowerCase().lastIndexOf(marker);
  if (idx === -1) return p;
  const rel = p.substring(idx + marker.length).replace(/\\/g, "/");
  return `http://127.0.0.1:8000/outputs/${rel}`;
}

function renderMetadata(meta, sourceLabel) {
  lastInputPath = meta?.input || null;
  clipsDiv.innerHTML = `
    <div class="clip-card">
      <div><strong>Source:</strong> ${sourceLabel}</div>
      <div class="meta">Duration: ${meta?.duration_sec?.toFixed?.(2) ?? meta?.duration_sec}s</div>
      <div class="meta">FPS: ${meta?.fps ?? "unknown"}</div>
      <div class="meta">Resolution: ${meta?.resolution?.width ?? "?"} x ${meta?.resolution?.height ?? "?"}</div>
      <div class="meta">Audio path: ${meta?.audio}</div>
      <button id="genShortsBtn">Generate Shorts (9:16)</button>
      <p id="genStatus" class="status"></p>
      <div id="shortsList"></div>
    </div>
  `;
  const genBtn = document.getElementById("genShortsBtn");
  const genStatus = document.getElementById("genStatus");
  const shortsList = document.getElementById("shortsList");
  genBtn.addEventListener("click", async () => {
    if (!lastInputPath) { genStatus.textContent = "No input video."; return; }
    genBtn.disabled = true;
    genStatus.textContent = "Generating clips...";
    try {
      const resp = await fetch(`${API_BASE}/generate-clips`, {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({
          input_path: lastInputPath,
          aspect: aspectRatioSelect.value,
          max_clips: 5,
          model_size: "tiny"
        })
      });
      if (!resp.ok) throw new Error(await resp.text());
      const data = await resp.json();
      genStatus.textContent = `Created ${data.count} clips.`;
      shortsList.innerHTML = data.clips.map(p => {
        const href = pathToOutputsUrl(p);
        return `<div><a href="${href}" target="_blank">${href}</a></div>`;
      }).join("");
    } catch (e) {
      genStatus.textContent = `Error: ${e.message}`;
    } finally {
      genBtn.disabled = false;
    }
  });
}

async function postProcessFile(file) {
  const form = new FormData();
  form.append("file", file);
  const resp = await fetch(`${API_BASE}/process`, { method: "POST", body: form });
  if (!resp.ok) throw new Error(await resp.text());
  return resp.json();
}

async function postProcessUrl(url) {
  const resp = await fetch(`${API_BASE}/process-url`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  });
  if (!resp.ok) throw new Error(await resp.text());
  return resp.json();
}

uploadBtn.addEventListener("click", async (e) => {
  e.preventDefault();
  const file = uploadInput.files?.[0];
  if (!file) { uploadStatus.textContent = "Please choose a video file."; return; }
  uploadBtn.disabled = true;
  uploadStatus.textContent = "Uploading and processing...";
  try {
    const result = await postProcessFile(file);
    uploadStatus.textContent = "Processed successfully.";
    renderMetadata(result.metadata, "Local file");
  } catch (e) {
    uploadStatus.textContent = `Error: ${e.message}`;
  } finally {
    uploadBtn.disabled = false;
  }
});

processUrlBtn.addEventListener("click", async (e) => {
  e.preventDefault();
  const url = urlInput.value.trim();
  if (!url) { urlStatus.textContent = "Please enter a YouTube URL."; return; }
  processUrlBtn.disabled = true;
  urlStatus.textContent = "Downloading and processing...";
  try {
    const result = await postProcessUrl(url);
    urlStatus.textContent = "Processed successfully.";
    renderMetadata(result.metadata, "URL");
  } catch (e) {
    urlStatus.textContent = `Error: ${e.message}`;
  } finally {
    processUrlBtn.disabled = false;
  }
});

// Hooks for options (subtitles / aspect ratio) – not wired yet
subtitlesToggle.addEventListener("change", () => {
  // future: send preference to backend or re-render preview
});
aspectRatioSelect.addEventListener("change", () => {
  // future: request resized preview clips
});