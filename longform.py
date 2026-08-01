#!/usr/bin/env python3
"""
YOU — LONG-FORM builder (Phase 2)

Why this exists
---------------
Two reasons, both measured:

1. MONETIZATION MATH. The Shorts-only path to YPP needs 1,000 subs +
   10,000,000 Shorts views/90 days. We do ~700/video. The long-form door
   needs 1,000 subs + 4,000 watch HOURS — and 10M Shorts views is roughly
   55,000 hours of watching, so the long-form door is ~14x less watch time
   for the same unlock. Shorts ad revenue is also a rounding error
   ($0.01-0.07 RPM); long-form RPM is an order of magnitude higher.

2. THE BRIDGE. In 2026 YouTube tracks how many Shorts viewers click
   through to long-form. Channels with a healthy bridge get amplified;
   Shorts-only channels get throttled. Having no long-form was capping
   the Shorts.

Design
------
- Topic comes from our OWN best-performing recent Shorts, so the deep-dive
  is on a subject the audience already proved it wants (and the Short acts
  as the trailer for the long-form).
- Script is generated SEGMENT BY SEGMENT. Measured: asking one call for
  1,200 words returns ~530; six smaller calls reliably return ~1,150
  (7.7 min). Per-segment generation also lets each segment carry its own
  shape, which is what keeps the output off YouTube's "templated /
  mass-produced" line.
- Visuals: 3 Pexels stills per segment, Ken Burns pan-zoom (same free
  stack as Shorts).
- Chapters are written into the description from real segment timings.

Everything reuses you.py primitives — no new dependencies, still $0.
Run:  python longform.py [--no-upload]
"""

import argparse
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import you as Y
from config import (
    LANGUAGE, CHANNEL_NICHE, VIDEO_FPS, YOUTUBE_CATEGORY,
    YOUTUBE_DEFAULT_TAGS, TEMP_DIR, OUTPUT_DIR, BASE_DIR,
)

# ── Landscape output ──────────────────────────────────────────────
# Shorts are 9:16; a documentary must be 16:9. Long-form is watched on
# desktops and TVs, which is exactly where long sessions — and therefore
# the 4,000 WATCH HOURS this pipeline exists to earn — come from. A
# 7-minute vertical video would be shown letterboxed on every one of them.
# you.py reads these as module globals (it does `from config import *`),
# so overriding here retargets the whole render path: slideshow geometry,
# caption placement, and the orientation used for Pexels searches.
LANDSCAPE_W, LANDSCAPE_H = 1920, 1080
Y.VIDEO_WIDTH, Y.VIDEO_HEIGHT = LANDSCAPE_W, LANDSCAPE_H
# Captions sized for a 1920-wide frame (the 82px Shorts size is tuned for
# a 1080-wide frame and reads as oversized here).
Y.CAPTION_SIZE = 64

# ── Long-form settings ────────────────────────────────────────────
SEGMENTS            = 6       # ~6 x 240 words ~= 8-9 minutes
WORDS_PER_SEGMENT   = 250
IMAGES_PER_SEGMENT  = 3
LONGFORM_VOICE      = "en-US-ChristopherNeural"   # documentary narrator
LONGFORM_RATE       = "+0%"
LONGFORM_CAPTION    = "&H0000D7FF"                # amber, matches UNSOLVED
# Long videos are 15-20x the frames of a Short — a faster preset keeps the
# runner well inside its timeout at a size difference nobody can see.
LONGFORM_PRESET     = "veryfast"
LONGFORM_CRF        = "23"
# Groq free tier meters ~12k tokens/minute; space the segment calls so a
# 7-call burst can't trip a 429 mid-build.
SEGMENT_PACING_SEC  = 12

LOG = BASE_DIR / "feedback" / "longform.json"


# ── Topic selection ───────────────────────────────────────────────

def pick_topic() -> dict:
    """Pick a deep-dive topic from our own best-performing recent Shorts.

    This is the bridge: the Short already proved the subject pulls, and the
    long-form becomes the place that Short's viewers can go next.
    """
    try:
        perf = json.loads((BASE_DIR / "analyzer" / "top_performers.json").read_text(encoding="utf-8"))
        items = perf if isinstance(perf, list) else perf.get("videos", perf.get("performers", []))
    except Exception:
        items = []

    done = set()
    if LOG.exists():
        try:
            done = {e.get("theme", "").lower() for e in json.loads(LOG.read_text(encoding="utf-8"))}
        except Exception:
            pass

    for p in sorted(items, key=lambda x: -int(x.get("views", 0) or 0)):
        theme = (p.get("topic") or p.get("title") or "").strip()
        if theme and theme.lower() not in done and not Y._is_affiliate_tainted(p):
            return {"theme": theme, "seed_views": p.get("views", 0)}

    return {"theme": f"the biggest unanswered questions in {CHANNEL_NICHE.split('—')[0].strip()}",
            "seed_views": 0}


# ── Script generation (segment by segment) ────────────────────────

def build_outline(theme: str) -> dict:
    prompt = f"""You are writing a documentary-style YouTube video about: "{theme}".

Produce an outline of exactly {SEGMENTS} segments. Each segment must cover a
DISTINCT sub-question or case — no overlap, no repetition. Order them so
curiosity builds: the strangest, most gripping one goes FIRST (it decides
whether anyone stays), and the most mind-expanding one goes LAST.

Return ONLY valid JSON (no markdown, no backticks):
{{
  "title": "YouTube title, max 80 chars, specific and irresistible, no clickbait lies",
  "theme": "the through-line of the whole video in one sentence",
  "segments": [
    {{"heading": "short segment title",
      "angle": "what this segment reveals, one sentence",
      "shape": "one of: case-study | mechanism | mystery | thought-experiment | historical account"}}
  ]
}}"""
    # Outline is short structured data so JSON is fine here, but this runs
    # unattended weekly — retry once, then degrade to a usable skeleton
    # rather than failing the whole video.
    for attempt in range(2):
        try:
            data = Y._parse_json(Y._call_llm(prompt))
            if data.get("segments"):
                return data
        except Exception as e:
            print(f"      ⚠️  outline parse failed ({e}) — retry {attempt+1}")
    print("      ⚠️  falling back to a generic outline")
    shapes = ["mystery", "mechanism", "case-study", "thought-experiment",
              "historical account", "mystery"]
    return {"title": theme[:80], "theme": theme,
            "segments": [{"heading": f"Part {i+1}", "angle": theme,
                          "shape": shapes[i % len(shapes)]} for i in range(SEGMENTS)]}


def write_segment(theme: str, seg: dict, index: int, total: int, previous: str) -> dict:
    """Write one segment. Separate call per segment = reliable length + variety."""
    position = ("This is the OPENING segment — it must hook a cold viewer in the first two sentences."
                if index == 1 else
                "This is the FINAL segment — end on the biggest idea, then a closing thought. Do not add a call to action."
                if index == total else
                f"This is segment {index} of {total} — open with a short transition that does NOT repeat earlier phrasing.")

    prompt = f"""Write the NARRATION for one segment of a documentary about "{theme}".

SEGMENT: "{seg.get('heading','')}"
WHAT IT REVEALS: {seg.get('angle','')}
NARRATIVE SHAPE: {seg.get('shape','mystery')} — let this genuinely shape the
writing. A mechanism segment explains step by step; a mystery segment
withholds and deepens; a case study follows people and dates; a thought
experiment walks a consequence chain. Segments must NOT feel interchangeable.

{position}

PREVIOUS SEGMENT ENDED WITH (do not repeat this idea or phrasing):
{previous[-320:] if previous else "(this is the first segment)"}

RULES:
- EXACTLY {WORDS_PER_SEGMENT-25}-{WORDS_PER_SEGMENT+25} words of spoken narration
- Language: {LANGUAGE}. Documentary tone: vivid, precise, unhurried
- Every fact TRUE and well established. Real names, dates and numbers where
  they exist. If unsure of a detail, choose one you are certain of
- Vary sentence length deliberately. No filler, no "in this video", no
  "welcome back", no addressing subscribers
- Prose only — no headings, no bullet points, no markdown, no stage directions

OUTPUT FORMAT — use these exact tags, nothing else:
<narration>
the prose here
</narration>
<visuals>query one | query two | query three</visuals>

The visuals are {IMAGES_PER_SEGMENT} stock-footage search terms: SHORT concrete
visual subjects of 1-3 words a stock library would actually have (e.g.
deep ocean | radio telescope | human brain). No abstractions."""
    raw = Y._call_llm(prompt)

    # Deliberately NOT JSON: narration is long prose full of quotes,
    # apostrophes and dashes, which makes JSON parsing fail often enough to
    # break a weekly unattended run. Tag delimiters are robust to all of it.
    m = re.search(r"<narration>(.*?)</narration>", raw, re.S | re.I)
    narration = (m.group(1) if m else raw).strip()
    # Strip any stray tags/markdown if the model improvised
    narration = re.sub(r"</?(narration|visuals)>", "", narration, flags=re.I).strip()
    narration = re.sub(r"^```\w*|```$", "", narration).strip()

    mv = re.search(r"<visuals>(.*?)</visuals>", raw, re.S | re.I)
    visuals = []
    if mv:
        visuals = [v.strip(" \"'`") for v in mv.group(1).split("|") if v.strip()]
    visuals = [v for v in visuals if 0 < len(v) <= 40][:IMAGES_PER_SEGMENT]
    if not visuals:
        visuals = [seg.get("heading", "science")]

    return {"heading": seg.get("heading", f"Part {index}"),
            "narration": narration, "visuals": visuals}


def build_script(theme: str) -> dict:
    print(f"   🧠 Outlining: {theme}")
    outline = build_outline(theme)
    segs_in = outline.get("segments", [])[:SEGMENTS]
    print(f"   ✅ {len(segs_in)} segments planned — {outline.get('title','')}")

    segments, previous = [], ""
    for i, s in enumerate(segs_in, 1):
        # Groq's free tier is metered per MINUTE (~12k tokens/min). Seven
        # back-to-back calls can breach it, and a 429 here costs far more
        # than a short wait — nothing is waiting on a weekly job.
        if i > 1:
            time.sleep(SEGMENT_PACING_SEC)
        seg = write_segment(theme, s, i, len(segs_in), previous)
        words = len(seg["narration"].split())
        if words < 60:      # a dud segment would leave a hole in the video
            print(f"      ⚠️  segment {i} too short ({words}w) — retrying once")
            seg = write_segment(theme, s, i, len(segs_in), previous)
            words = len(seg["narration"].split())
        previous = seg["narration"]
        segments.append(seg)
        print(f"      ✍️  {i}/{len(segs_in)} {seg['heading'][:38]:40} {words:>4}w")

    total_words = sum(len(s["narration"].split()) for s in segments)
    print(f"   ✅ {total_words} words ≈ {total_words/2.5/60:.1f} min")
    return {"title": outline.get("title", theme)[:100],
            "theme": theme, "segments": segments, "total_words": total_words}


# ── Assembly ──────────────────────────────────────────────────────

def build_video(script: dict, upload: bool = True) -> dict:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    sid = f"lf_{ts}_{Y._slug(script['title'])}"
    result = {"timestamp": ts, "title": script["title"]}

    # 1. Narration per segment, so we get real chapter timings
    print("\n  ┌─ VOICE ────────────────────────────────────")
    seg_dir = TEMP_DIR / sid
    seg_dir.mkdir(parents=True, exist_ok=True)
    parts, all_words, chapters, offset = [], [], [], 0.0
    for i, seg in enumerate(script["segments"]):
        p = str(seg_dir / f"seg_{i:02d}.mp3")
        dur, words = Y.generate_voice(seg["narration"], p,
                                      voice=LONGFORM_VOICE, rate=LONGFORM_RATE)
        chapters.append({"t": offset, "heading": seg["heading"]})
        for w in words:
            all_words.append({"word": w["word"], "start": w["start"] + offset,
                              "end": w["end"] + offset})
        offset += dur
        parts.append(p)
        print(f"      🎙️  seg {i+1}: {dur:.0f}s (running {offset/60:.1f} min)")

    audio_path = str(seg_dir / "narration.mp3")
    concat_list = seg_dir / "audio.txt"
    concat_list.write_text("".join(f"file '{Path(p).as_posix()}'\n" for p in parts), encoding="utf-8")
    Y.subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i",
                      str(concat_list), "-c", "copy", audio_path],
                     capture_output=True, check=True)
    print(f"   ✅ Narration {offset/60:.1f} min · {len(all_words)} word timings")

    # 2. Visuals — spread across the whole runtime
    print("\n  ┌─ VISUALS ──────────────────────────────────")
    queries = []
    for seg in script["segments"]:
        queries.extend(seg["visuals"][:IMAGES_PER_SEGMENT])
    images = Y.generate_images(queries, sid)
    result["images"] = len(images)

    # 3. Assemble (faster preset — 15-20x the frames of a Short)
    print("\n  ┌─ ASSEMBLY ─────────────────────────────────")
    t0 = time.time()
    video_path = Y.assemble_video(
        audio_path, images, [], sid,
        word_timestamps=all_words, caption_hex=LONGFORM_CAPTION,
        preset=LONGFORM_PRESET, crf=LONGFORM_CRF, fast_slideshow=True,
    )
    print(f"   ✅ Encoded in {time.time()-t0:.0f}s")
    result["video"] = video_path

    thumb = Y.generate_thumbnail(images[0], script["title"], Y._slug(script["title"])) if images else None

    # 4. Description with real chapter timestamps (helps retention + UX)
    def stamp(sec):
        return f"{int(sec//60)}:{int(sec%60):02d}"
    # YouTube only renders chapters when the FIRST one is exactly 0:00 and
    # each is >=10s after the previous. Segment 1 already starts at 0:00, so
    # a separate "Intro" line would duplicate 0:00 and void the whole list.
    chapter_lines = "\n".join(
        f"{stamp(c['t'])} {c['heading']}"
        for i, c in enumerate(chapters)
        if i == 0 or c["t"] - chapters[i - 1]["t"] >= 10
    )
    # Reciprocal bridge: Shorts point here, this points back at the daily
    # series. Subscribing is framed around what they actually get next.
    desc = (f"{script['theme']}\n\n"
            f"CHAPTERS\n{chapter_lines}\n\n"
            f"📺 Subscribe for a new deep dive every Sunday — plus daily "
            f"science Shorts (UNSOLVED, HOW IT WORKS, MIND BENDER, WHAT IF).\n\n"
            f"#science #documentary #space")

    # 5. Publish
    print("\n  ┌─ PUBLISH ──────────────────────────────────")
    if upload:
        up = Y.upload_youtube(video_path, script["title"], desc,
                              YOUTUBE_DEFAULT_TAGS, thumbnail_path=thumb, script=None)
        result["upload"] = up
        if up.get("status") == "uploaded":
            _log(script, up, offset)
            try:
                Path(video_path).unlink()
            except OSError:
                pass
    else:
        print("   ⏭️  Skipping upload (--no-upload)")
        result["upload"] = {"status": "skipped"}
        _log(script, {"id": "local"}, offset)

    result["duration_sec"] = offset
    Y._clean_temp()
    return result


def _log(script: dict, up: dict, duration: float):
    entries = []
    if LOG.exists():
        try:
            entries = json.loads(LOG.read_text(encoding="utf-8"))
        except Exception:
            pass
    entries.append({
        "id": up.get("id", ""),
        "title": script["title"],
        "theme": script["theme"],
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
        "duration_sec": round(duration, 1),
        "words": script["total_words"],
        "segments": [s["heading"] for s in script["segments"]],
    })
    LOG.parent.mkdir(exist_ok=True)
    LOG.write_text(json.dumps(entries, indent=2), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="YOU — long-form builder")
    ap.add_argument("--no-upload", action="store_true")
    ap.add_argument("--topic", default=None, help="override the auto-picked topic")
    args = ap.parse_args()

    print("\n" + "=" * 52)
    print("  YOU — LONG-FORM BUILDER")
    print("=" * 52)

    picked = {"theme": args.topic} if args.topic else pick_topic()
    if picked.get("seed_views"):
        print(f"  Seed: best recent Short ({picked['seed_views']} views)")

    t0 = time.time()
    script = build_script(picked["theme"])
    r = build_video(script, upload=not args.no_upload)
    print("\n" + "=" * 52)
    print(f"  DONE in {(time.time()-t0)/60:.1f} min · {r['duration_sec']/60:.1f} min video")
    if r.get("upload", {}).get("url"):
        print(f"  {r['upload']['url']}")
    print("=" * 52 + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
