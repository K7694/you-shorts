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

## State files (what the machine remembers)
| File | Role | Reset for a new channel? |
|------|------|--------------------------|
| `used_topics.json` | Topic dedup (last 200) | Yes → `[]` |
| `feedback/uploaded.json` | Upload log → performance loop | Yes → delete |
| `analyzer/top_performers.json` | Few-shot self-improvement | Yes → delete |
| `analyzer/latest_brief.json` | Daily content brief | Yes → delete (regenerates) |
