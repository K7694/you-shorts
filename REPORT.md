# YOU — Weekly Report · 2026-10-25 04:30 UTC

Read the **Falsifiers** table first. Everything else is context.

## Channel
- **81 subs** · 74,519 views · 182 videos (lifetime)
- last 30 d Shorts: **15,249 views** · 16 subs · **1.05 subs/1k**

## Shorts — views at 48 h (equal-age cohorts)
| cohort | n | median | mean | ≥50 | max | window |
|---|---|---|---|---|---|---|
| last 30 | 30 | **579** | 560 | 25 | 1180 | 2026-09-22 → 2026-10-22 |
| prior 30 | 30 | 328 | 449 | 24 | 1023 | 2026-08-23 → 2026-09-21 |

last/prior median ratio: **×1.77** (the falsifier bar is ×0.53; anything between 0.53 and 1.88 is noise at n=30)

last 10 uploads: 10-12 **1060** MIND BENDER · 10-14 **305** MIND BENDER · 10-15 **1180** UNSOLVED · 10-16 **626** UNSOLVED · 10-17 **952** UNSOLVED · 10-18 **1092** UNSOLVED · 10-19 **304** HOW IT WORKS · 10-20 **0** HOW IT WORKS · 10-21 **32** UNSOLVED · 10-22 **961** UNSOLVED

## Geography (90 d)
- top: **US** · US+UK+CA+AU **76.5%** · India 4.9% · fetched 2026-09-12
- US 70.0% · PH 9.5% · IN 4.9% · GB 3.2% · DE 3.0%

## Retention (peer-relative, 0.50 = median comparable video)
- recorded **119 / 209** eligible (≥72 h old)
- last 30 recorded: opening 0.38 · middle **0.395** · final 0.667 · overall 0.483 (n=30)

## Long-form
- 9 uploads · 30 d: 6 views · **0.1 watch-hours** (of 4,000)
  - 2026-08-30 The Unsolved Mysteries That Could Rewrite Physics
  - 2026-09-06 The Unsolved Mysteries That Could Rewrite Physics
  - 2026-09-13 What the Universe Hides: 6 Unsolved Mysteries That

## Pipeline
- CI last 7: 10-25 ✅ · 10-24 ✅ · 10-24 ✅ · 10-23 ✅ · 10-23 ✅ · 10-22 ✅ · 10-22 ✅
- scheduled start delay vs nominal cron: min 1h48 · median **5h09** · max 8h05
- render archive: **30 / 30** of records since the archive shipped have a URL
- LLM chain: groq → gemini → cerebras → openrouter (Cerebras 402 — billing; probe at session open)

## Falsifiers
| ID | claim | checkpoint | current | status |
|---|---|---|---|---|
| F1 | 2×/day does not halve per-video reach | 30 videos post-switch | — | not started |
| F2 | CTA overlay does not repeat May | 30 videos post-overlay | — | not started |
| F3 | The kit is sellable | 30 d post-launch | sales not tracked here | not started |
| F4 | Clone reaches like the original | clone week 8 | other repo | not started |
| F5 | Compilations get watched | after 3 monthly uploads | long-form 30d views 6 | not started |
| F6 | Meta reach worth the engineering | day 60 | not live | not started |
| F7 | Portfolio can become income | month 6 | cash not tracked here | manual |
| F8 | No termination exposure | continuous | CI failures last 7: 0 | manual — check Studio for notices |
| F9 | Affiliate accounts survive | day 150 per account | n/a | not started |

Milestone dates live in `config.MILESTONES`; a falsifier starts watching the day its milestone is set.

## Not live yet
- Meta reach (Phase 4) · Kit sales (Phase 7) · Clone (Phase 6)
