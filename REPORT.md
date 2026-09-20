# YOU — Weekly Report · 2026-09-20 04:46 UTC

Read the **Falsifiers** table first. Everything else is context.

## Channel
- **60 subs** · 54,032 views · 148 videos (lifetime)
- last 30 d Shorts: **14,389 views** · 21 subs · **1.46 subs/1k**

## Shorts — views at 48 h (equal-age cohorts)
| cohort | n | median | mean | ≥50 | max | window |
|---|---|---|---|---|---|---|
| last 30 | 30 | **328** | 435 | 23 | 1034 | 2026-08-21 → 2026-09-17 |
| prior 30 | 30 | 440 | 461 | 26 | 1137 | 2026-07-25 → 2026-08-21 |

last/prior median ratio: **×0.75** (the falsifier bar is ×0.53; anything between 0.53 and 1.88 is noise at n=30)

last 10 uploads: 09-07 **237** UNSOLVED · 09-08 **14** UNSOLVED · 09-09 **96** UNSOLVED · 09-10 **342** HOW IT WORKS · 09-12 **218** UNSOLVED · 09-13 **314** UNSOLVED · 09-14 **388** HOW IT WORKS · 09-15 **421** WHAT IF · 09-16 **41** UNSOLVED · 09-17 **22** UNSOLVED

## Geography (90 d)
- top: **US** · US+UK+CA+AU **76.5%** · India 4.9% · fetched 2026-09-12
- US 70.0% · PH 9.5% · IN 4.9% · GB 3.2% · DE 3.0%

## Retention (peer-relative, 0.50 = median comparable video)
- recorded **89 / 175** eligible (≥72 h old)
- last 30 recorded: opening 0.355 · middle **0.36** · final 0.591 · overall 0.438 (n=30)

## Long-form
- 9 uploads · 30 d: 365 views · **11.0 watch-hours** (of 4,000)
  - 2026-08-30 The Unsolved Mysteries That Could Rewrite Physics
  - 2026-09-06 The Unsolved Mysteries That Could Rewrite Physics
  - 2026-09-13 What the Universe Hides: 6 Unsolved Mysteries That

## Pipeline
- CI last 7: 09-20 ✅ · 09-19 ✅ · 09-19 ✅ · 09-18 ✅ · 09-18 ✅ · 09-17 ✅ · 09-17 ✅
- scheduled start delay vs nominal cron: min 1h42 · median **5h03** · max 8h18
- render archive: **8 / 8** of records since the archive shipped have a URL
- LLM chain: groq → gemini → cerebras → openrouter (Cerebras 402 — billing; probe at session open)

## Falsifiers
| ID | claim | checkpoint | current | status |
|---|---|---|---|---|
| F1 | 2×/day does not halve per-video reach | 30 videos post-switch | — | not started |
| F2 | CTA overlay does not repeat May | 30 videos post-overlay | — | not started |
| F3 | The kit is sellable | 30 d post-launch | sales not tracked here | not started |
| F4 | Clone reaches like the original | clone week 8 | other repo | not started |
| F5 | Compilations get watched | after 3 monthly uploads | long-form 30d views 365 | not started |
| F6 | Meta reach worth the engineering | day 60 | not live | not started |
| F7 | Portfolio can become income | month 6 | cash not tracked here | manual |
| F8 | No termination exposure | continuous | CI failures last 7: 0 | manual — check Studio for notices |
| F9 | Affiliate accounts survive | day 150 per account | n/a | not started |

Milestone dates live in `config.MILESTONES`; a falsifier starts watching the day its milestone is set.

## Not live yet
- Meta reach (Phase 4) · Kit sales (Phase 7) · Clone (Phase 6)
