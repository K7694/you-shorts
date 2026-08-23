# KNOBS — every tunable, what it does, and safe ranges

All in `config.py` unless noted.

## Content identity (the ones that matter most)
| Knob | What it drives | Guidance |
|------|----------------|----------|
| `CHANNEL_NICHE` | Analyzer brief + fallback topic generation | One specific sentence; curiosity, not commerce |
| `CURIOSITY_DOMAINS` | Anti-repetition rotation | 10–12 buckets; picker avoids domains used in last ~5 videos |
| `CONTENT_ARCHETYPES` | Script framing per video | Keys must match `_CURIOSITY_ARCHETYPE_INSTRUCTIONS` in you.py |
| `CONTENT_ARCHETYPE_WEIGHTS` | Winner bias | ~4:1 winners:explorers once you have data; uniform before |
| `CONTENT_TONE` | Narration voice-of-god vs friend | Movie-trailer awe worked for science |
| Few-shot examples (you.py) | Script quality ceiling | 3 proven viral scripts from the SAME niche; taint-filter keeps off-niche performers out |

## LLM
| Knob | Default | Notes |
|------|---------|-------|
| `LLM_PRIMARY` | `"groq"` | `"gemini"` only if the account has real quota (curl-test first) |
| Hook gate (you.py `_generate_with_hook_gate`) | 4 attempts, target 7 | Raise attempts before lowering target |
| `_score_hook` power-words | curiosity set | Re-tune per niche (they encode what "concrete" means there) |

## Video
| Knob | Default | Notes |
|------|---------|-------|
| `TARGET_DURATION` | 35s | 25–40 sweet spot; shorter = higher completion |
| `VIDEO_FPS` | 30 | 60 doubles encode time for zero gain on slideshows |
| `IMAGES_PER_VIDEO` | 5 | One per script beat |
| `IMAGE_SOURCE` | `"pexels"` | `"pollinations"` is dead (402) — kept for reference |
| `AB_VISUAL_TEST` | True | Daily-alternating A/B: photos+Ken Burns vs stock video montage; arm logged as `visual_variant` in feedback log; `VISUAL_VARIANT` env forces an arm for testing |
| `IMAGE_STYLE` | cinematic science | Only used in prompt/query construction |
| `CAPTION_FONT/SIZE/WORDS_PER_LINE` | Impact 82 / 3 | The proven Shorts caption look |
| `BGM_ENABLED/BGM_VOLUME` | True / 0.12 | Subtle ambient bed |
| `VOICE` / `VOICE_RATE` | Andrew Multilingual / +5% | `python you.py --voices` to browse |

## Cadence & platform
| Knob | Default | Notes |
|------|---------|-------|
| Cron (`.github/workflows/create_video.yml`) | `30 3 * * *` (9AM IST, 1×/day) | Don't scale past 1/day until channel earns trust |
| `YOUTUBE_PRIVACY` | `"public"` | Use `"unlisted"` for dry-runs |
| `YOUTUBE_CATEGORY` | 28 (Sci & Tech) | Match the niche |

## Kill-switches / dormant layers
| Flag | State | Revives |
|------|-------|---------|
| `MONETIZATION_ENABLED` | False | Affiliate program picker, pinned comment, URL overlay, FTC text |
| `USE_BACKGROUND_VIDEO` | False | Gameplay-loop visual mode (Subway Surfers era) |
| `USE_MASCOT_OVERLAY` | False | AI mascot character overlay |
| `GEMINI_API_KEY` + `LLM_PRIMARY="gemini"` | fallback | Gemini as primary LLM |

## Long-form (`longform.py`, weekly)
| Knob | Default | Notes |
|------|---------|-------|
| `SEGMENTS` / `WORDS_PER_SEGMENT` | 6 / 250 | ~7.5–9 min. Generate PER SEGMENT — one call asking for 1,200 words returns ~530 |
| `SEGMENT_PACING_SEC` | 12 | Groq free tier meters ~12k tokens/MINUTE; a 7-call burst trips 429 without this |
| `IMAGES_PER_SEGMENT` | 3 | 18 visuals total across the runtime |
| `LANDSCAPE_W/H` | 1920×1080 | Long-form must be 16:9 — watch hours come from desktop/TV. Overrides `you.py` globals, which also flips Pexels searches to landscape |
| `LONGFORM_PRESET` / `CRF` | veryfast / 23 | 15–20× the frames of a Short |
| `fast_slideshow` | True | Ken Burns at 1.3× working scale, no unsharp. Default 2× (=4K/frame) + unsharp is far too slow at 13k frames |
| Cron | Sun 05:30 UTC | `.github/workflows/longform.yml`, 90-min timeout |

Measured: 7.3-min video builds in ~18 min locally, ~100 MB, 1.8 Mbps.

## Script quality + retention instrumentation (added 2026-08-23)
| Knob | Default | Notes |
|------|---------|-------|
| `CRITIQUE_AND_REVISE` | True | Second LLM call rewrites the single weakest line. Replaced the `_score_hook >= 7` gate, which re-rolled whole scripts up to 4x on a keyword count measured at r=-0.06 vs real 3-second retention. Net call count unchanged (~1.9 -> 2.0); the second call now edits instead of re-rolling. False = one-pass generation |
| `RETENTION_BACKFILL_AFTER_HOURS` | 72 | Age before a video's retention curve is recorded. YouTube's curve is still moving in the first day or two |
| `RETENTION_HOOK_SECONDS` | 3.0 | The hook window. `elapsedVideoTimeRatio` is a fraction of duration, so this is converted per video using `word_count / 2.5 + 3s` |

Run manually: `python analytics.py --backfill` (add `--refresh` to re-fetch
already-recorded videos). Runs automatically as step 8c of the daily
workflow. Writes into each `feedback/uploaded.json` record:

```
retention: { awr_hook, rrp_hook, rrp_all, rrp_thirds[3], duration_est_s, points }
```

`rrp_*` is `relativeRetentionPerformance` — a 0-1 percentile against
comparable YouTube videos, so it already strips out topic and algorithm
luck. **This is the honest retention number.** Absolute retention flatters
short videos: this channel reads 68.5% absolute but 0.43 relative, i.e.
slightly below the median comparable video.

## State files (what the machine remembers)
| File | Role | Reset for a new channel? |
|------|------|--------------------------|
| `used_topics.json` | Topic dedup (last 200) | Yes → `[]` |
| `feedback/uploaded.json` | Upload log → performance loop | Yes → delete |
| `analyzer/top_performers.json` | Few-shot self-improvement | Yes → delete |
| `analyzer/latest_brief.json` | Daily content brief | Yes → delete (regenerates) |
