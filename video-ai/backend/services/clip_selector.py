import math
from typing import List, Dict, Tuple

def select_highlights(segments: List[Dict], max_clips: int = 5) -> List[Tuple[float, float]]:
    """
    segments: Whisper segments with start/end/text
    Returns list of (start,end) windows ~45s using simple heuristics:
      - prioritize segments with keywords
      - use speech density (short gaps)
      - avoid overlapping; clamp to source duration
    """
    keywords = {"important","best","top","secret","tips","trick","warning","note","must","why","how","key"}
    scored = []
    for s in segments:
        text = (s.get("text") or "").lower()
        score = 0
        # keyword hits
        for k in keywords:
            if k in text:
                score += 2
        # energy proxy: longer text -> higher score
        score += min(len(text) / 50.0, 3)
        # short segment bonus
        dur = float(s.get("end",0) - s.get("start",0))
        if 1.5 <= dur <= 8:
            score += 1
        scored.append((score, s))

    scored.sort(key=lambda x: x[0], reverse=True)
    windows = []
    target = 45.0
    for score, s in scored:
        st = float(s.get("start", 0))
        en = float(s.get("end", st + 4))
        # center window around this segment
        mid = (st + en) / 2.0
        win_st = max(0.0, mid - target/2.0)
        win_en = win_st + target
        # avoid overlap
        if any(not (win_en <= a or win_st >= b) for a,b in windows):
            continue
        windows.append((win_st, win_en))
        if len(windows) >= max_clips:
            break
    return windows