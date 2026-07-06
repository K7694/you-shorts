# BLUEPRINT — Autonomous Faceless Shorts Factory

**The crux of the entire YOU automation, distilled.** Use this folder to
replicate the system for any new channel or niche without re-learning
two months of lessons.

- `README.md` — this file: what the machine is + the architecture
- `REPLICATE.md` — step-by-step: clone it for a new channel in ~1 hour
- `LESSONS.md` — every failure we hit and the fix (read this FIRST)
- `KNOBS.md` — every tunable setting and what it actually does

---

## What this machine does

One GitHub Actions cron run = one finished YouTube Short, hands-off:

```
CRON (1×/day, GitHub Actions, $0, no PC needed)
  │
  ├─ 1. TOPIC      analyzer brief (competitor intel) → taint/repeat guards
  │                → domain rotation picks a FRESH subject
  ├─ 2. SCRIPT     Groq llama-3.3-70b writes hook+script (35s, 4-part
  │                viral structure) → hook scored 1-10, best of 4 attempts
  ├─ 3. VISUALS    5 stock photos from Pexels (free API), one per beat
  ├─ 4. VOICE      Edge TTS (free, human-quality) — word timings captured
  │                during synthesis (no transcription step needed)
  ├─ 5. ASSEMBLY   FFmpeg: Ken Burns pan-zoom slideshow + word-synced
  │                burned-in captions + ambient BGM → 1080×1920 30fps
  ├─ 6. PUBLISH    YouTube Data API upload (OAuth, never-expiring token)
  └─ 7. LEARN      state committed back to repo: used topics, performance
                   log, top performers feed back into future prompts
```

**Cost: $0.** Every component is a free tier that we verified actually
stays free at 1 video/day (see LESSONS.md for the ones that didn't).

## The content recipe that works (validated by data)

Two eras on the same pipeline proved content is everything:

| Era | Content | Avg views | Verdict |
|-----|---------|-----------|---------|
| Phase 0/reset | Curiosity science, cinematic | 300-500+ | ✅ Works |
| Phase 1 | Affiliate/AI-tool promos | 10 | ❌ Killed the channel |

The working formula:
- **Niche:** intrinsic-curiosity topics (science, mysteries, how-things-work)
  — content people *seek out*, never content that *sells to them*
- **Archetypes (weighted):** `unsolved_mystery` + `how_does_it_work`
  carry ~72% of output (they produced every breakout); others get a
  small exploration slice
- **Topic variety enforced in code:** domain rotation + subject-recency
  guard (repetition = algorithmic death; we measured it)
- **Hook:** concrete + specific, scored ≥7/10, e.g. *"Fire a gun on the
  Moon and the bullet could hit you in the back"* — never vague
  ("The hidden truth about reality" = 0 views, measured)
- **35 seconds**, loop ending, burned-in word-synced captions
- **1×/day cadence** — 3×/day on a cold channel read as spam

## Results this recipe produced (June 2026)

- Dead channel (10 views/video) → **344 avg, 765 peak, 71% hit-rate ≥50 views**
- Subscribers 9 → 20 in three weeks
- 7 of 8 videos in the final week cleared 200 views with organic likes

## Known ceiling / next lever

Views convert to subscribers at only ~0.2%. The next unlock is a
**subscribable format** — a recurring series identity, not one-off facts.
Design that BEFORE scaling a clone of this system.
