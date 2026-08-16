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

# ── SHOT RATE (the retention fix, 2026-08-16) ─────────────────────
# Measured: 18 visuals over 7.3 min = one image every 24.5s, each with the
# same slow Ken Burns zoom. Viewers abandoned at 66-98s — in that window
# they saw FOUR images. Documentaries cut every 3-6s; we were 5x too slow.
# A denser cut is free: we use ~160 of 25,000 monthly Pexels requests, so
# even ~90 visuals per video leaves the quota barely touched.
SECONDS_PER_SHOT    = 5
IMAGES_PER_SEGMENT  = 14      # queries requested per segment (~70s / 5s)
# Motion beats stills over 7 minutes. A few real video clips per segment
# break up the pan-zoom without the bandwidth of an all-video render.
CLIPS_PER_SEGMENT   = 2
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

Produce an outline of exactly {SEGMENTS} segments.

⛔ THE #1 FAILURE TO AVOID — ENCYCLOPEDIA STRUCTURE.
Measured: viewers abandon these videos around 70-90 seconds. The cause is
outlines that read like a textbook contents page. These headings are BANNED:
"Basic Principles", "Historic Precedents", "Introduction", "Background",
"How It Works", "Modern Implementations", "Future Possibilities",
"Applications", "Overview", "The Science Of".

Instead, every segment must be a STORY BEAT that raises a question the next
segment answers. Think: a specific event, a specific person, a specific
anomaly, a specific consequence. Concrete over general, always.

GOOD headings: "The Tunnel They Sealed And Never Reopened" ·
"The Engineer Who Was Laughed Out Of The Room" · "Then The Pressure Readings
Went Wrong"
BAD headings: "Basic Principles" · "Historic Precedents" · "Applications"

Segment 1 is a COLD OPEN: it must drop the viewer straight into the single
strangest, most specific detail of the whole story — no scene-setting, no
definitions, no "for centuries humans have wondered". It decides whether
anyone is still watching at 90 seconds.
Order the rest so curiosity compounds, with the most mind-expanding last.

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
    position = ("This is the COLD OPEN. Viewers abandon at 70-90 seconds, so the first "
                "TWO SENTENCES decide everything. Open mid-story on the single strangest "
                "concrete detail — a specific object, place, number or moment. "
                "Do NOT set the scene, define terms, or open with 'For centuries...', "
                "'Imagine...', or 'Deep beneath...'. Earn the next 30 seconds."
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
deep ocean | radio telescope | human brain). No abstractions.

They are shown IN ORDER, one every ~{SECONDS_PER_SHOT}s, so they must track what
the narration is describing as it moves — not {IMAGES_PER_SEGMENT} variations of
one idea. Give genuinely different subjects across the segment, and vary the
scale between them (wide landscape → machinery → close-up detail → human scale)."""
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


# ── Visual track ──────────────────────────────────────────────────

def build_visual_track(segments: list, durations: list, sid: str, workdir) -> dict:
    """Compose the full visual track as a dense cut.

    One shot every ~SECONDS_PER_SHOT (was one every 24.5s, which is what the
    66-98s abandonment was really measuring). Each segment is rendered on its
    own and the segments are concatenated, so no single ffmpeg filtergraph
    has to swallow ~85 inputs. A couple of real Pexels video clips per
    segment break up the pan-zoom.
    """
    shot_dir = workdir / "shots"
    shot_dir.mkdir(parents=True, exist_ok=True)
    seg_files, total_shots, total_clips = [], 0, 0

    for si, (seg, dur) in enumerate(zip(segments, durations)):
        n_shots = max(2, round(dur / SECONDS_PER_SHOT))
        queries = seg.get("visuals") or [seg.get("heading", "science")]
        # Cycle the segment's queries if it gave fewer than we need
        picks = [queries[i % len(queries)] for i in range(n_shots)]

        used_img, used_vid = set(), set()
        parts = []
        for i, q in enumerate(picks):
            shot = str(shot_dir / f"s{si:02d}_{i:03d}.mp4")
            # Spread the motion clips through the segment
            want_clip = CLIPS_PER_SEGMENT and (i % max(n_shots // CLIPS_PER_SEGMENT, 1) == 1)
            made = False
            if want_clip:
                raw = str(shot_dir / f"s{si:02d}_{i:03d}_src.mp4")
                if Y._download_pexels_video(q, raw, i, used_vid):
                    made = _clip_shot(raw, shot, SECONDS_PER_SHOT)
                    if made:
                        total_clips += 1
            if not made:
                raw = str(shot_dir / f"s{si:02d}_{i:03d}.jpg")
                if not Y._download_pexels_image(q, raw, i, used_img):
                    Y._make_fallback_image(raw)
                made = _still_shot(raw, shot, SECONDS_PER_SHOT, i)
            if made:
                parts.append(shot)

        if not parts:
            continue
        seg_out = str(shot_dir / f"seg{si:02d}.mp4")
        if _concat(parts, seg_out):
            seg_files.append(seg_out)
            total_shots += len(parts)
        print(f"      🎬 segment {si+1}: {len(parts)} shots over {dur:.0f}s "
              f"(~{dur/max(len(parts),1):.1f}s each)")

    out = str(workdir / "visual_track.mp4")
    _concat(seg_files, out)
    print(f"   ✅ {total_shots} shots ({total_clips} motion clips) — "
          f"one every ~{sum(durations)/max(total_shots,1):.1f}s")
    return {"path": out, "shots": total_shots, "clips": total_clips}


def _still_shot(img: str, out: str, dur: float, idx: int) -> bool:
    """One still with a slow Ken Burns move; direction varies per shot."""
    frames = int(dur * VIDEO_FPS)
    w, h = Y.VIDEO_WIDTH, Y.VIDEO_HEIGHT
    if idx % 3 == 0:
        z, x, y = f"min(1+0.18*on/{frames},1.18)", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    elif idx % 3 == 1:
        z, x, y = f"max(1.18-0.18*on/{frames},1.0)", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    else:
        z, x, y = "1.12", f"iw*0.08*on/{frames}", "ih/2-(ih/zoom/2)"
    vf = (f"scale={int(w*1.3)}:{int(h*1.3)}:force_original_aspect_ratio=increase,"
          f"crop={int(w*1.3)}:{int(h*1.3)},"
          f"eq=contrast=1.12:saturation=1.15,"
          f"zoompan=z='{z}':x='{x}':y='{y}':d={frames}:s={w}x{h}:fps={VIDEO_FPS},"
          f"setsar=1")
    # NO `-loop 1 -t`: with a looped input, zoompan expands EVERY input frame
    # into d frames (125 x 150 = 18,750 frames — measured at 237s for one
    # 5-second shot). Feeding a single still lets d= generate exactly the
    # frames we want. Same shot now renders in ~1s.
    r = Y.subprocess.run(["ffmpeg", "-y", "-i", img,
                          "-vf", vf, "-c:v", "libx264", "-preset", "veryfast",
                          "-crf", "23", "-pix_fmt", "yuv420p", "-an",
                          "-frames:v", str(frames), out],
                         capture_output=True, text=True)
    return r.returncode == 0


def _clip_shot(src: str, out: str, dur: float) -> bool:
    """Trim/scale one stock video clip to a single shot."""
    w, h = Y.VIDEO_WIDTH, Y.VIDEO_HEIGHT
    r = Y.subprocess.run(["ffmpeg", "-y", "-stream_loop", "-1", "-t", f"{dur}", "-i", src,
                          "-vf", f"scale={w}:{h}:force_original_aspect_ratio=increase,"
                                 f"crop={w}:{h},fps={VIDEO_FPS},setsar=1",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
                          "-pix_fmt", "yuv420p", "-an", out],
                         capture_output=True, text=True)
    ok = r.returncode == 0
    try:
        Path(src).unlink()      # source clips are large; don't keep them
    except OSError:
        pass
    return ok


def _concat(parts: list, out: str) -> bool:
    if not parts:
        return False
    lst = Path(out).with_suffix(".txt")
    lst.write_text("".join(f"file '{Path(p).as_posix()}'\n" for p in parts), encoding="utf-8")
    r = Y.subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
                          "-c", "copy", out], capture_output=True, text=True)
    return r.returncode == 0


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

    # 2. Visuals — a DENSE cut, built per segment then concatenated.
    #    One shot every ~SECONDS_PER_SHOT instead of every 24s, with a couple
    #    of real motion clips per segment. Building per segment keeps each
    #    ffmpeg filtergraph small instead of one graph with ~85 inputs.
    print("\n  ┌─ VISUALS ──────────────────────────────────")
    seg_durations = []
    for i, c in enumerate(chapters):
        end = chapters[i + 1]["t"] if i + 1 < len(chapters) else offset
        seg_durations.append(max(end - c["t"], 1.0))

    track = build_visual_track(script["segments"], seg_durations, sid, seg_dir)
    result["images"] = track["shots"]

    # 3. Assemble (faster preset — 15-20x the frames of a Short)
    print("\n  ┌─ ASSEMBLY ─────────────────────────────────")
    t0 = time.time()
    video_path = Y.assemble_video(
        audio_path, [], [], sid,
        word_timestamps=all_words, caption_hex=LONGFORM_CAPTION,
        preset=LONGFORM_PRESET, crf=LONGFORM_CRF,
        prebuilt_track=track["path"],
    )
    print(f"   ✅ Encoded in {time.time()-t0:.0f}s")
    result["video"] = video_path

    # Thumbnail: pull a frame out of the finished track. There is no longer a
    # list of stills to reach into — visuals are composed into the track — and
    # a real frame is more representative of the video than the first image.
    thumb = None
    frame = str(seg_dir / "thumb_frame.jpg")
    grab = Y.subprocess.run(
        ["ffmpeg", "-y", "-ss", f"{max(offset * 0.08, 2):.1f}", "-i", track["path"],
         "-frames:v", "1", "-q:v", "2", frame],
        capture_output=True, text=True)
    if grab.returncode == 0 and Path(frame).exists():
        thumb = Y.generate_thumbnail(frame, script["title"], Y._slug(script["title"]))
    else:
        print("      ⚠️  Could not grab a thumbnail frame — continuing without one")

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
