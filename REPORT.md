# YOU — Weekly Report · 2026-11-15 06:14 UTC

Read the **Falsifiers** table first. Everything else is context.

## Channel
- **95 subs** · 82,360 views · 203 videos (lifetime)
- last 30 d Shorts: **12,948 views** · 17 subs · **1.31 subs/1k**

## Shorts — views at 48 h (equal-age cohorts)
| cohort | n | median | mean | ≥50 | max | window |
|---|---|---|---|---|---|---|
| last 30 | 30 | **334** | 474 | 23 | 1180 | 2026-10-14 → 2026-11-12 |
| prior 30 | 30 | 428 | 511 | 25 | 1158 | 2026-09-13 → 2026-10-12 |

last/prior median ratio: **×0.78** (the falsifier bar is ×0.53; anything between 0.53 and 1.88 is noise at n=30)

last 10 uploads: 11-03 **199** UNSOLVED · 11-04 **9** UNSOLVED · 11-05 **0** UNSOLVED · 11-06 **162** WHAT IF · 11-07 **675** MIND BENDER · 11-08 **607** HOW IT WORKS · 11-09 **108** HOW IT WORKS · 11-10 **21** HOW IT WORKS · 11-11 **117** HOW IT WORKS · 11-12 **3** UNSOLVED

## Geography (90 d)
- top: **US** · US+UK+CA+AU **76.5%** · India 4.9% · fetched 2026-09-12
- US 70.0% · PH 9.5% · IN 4.9% · GB 3.2% · DE 3.0%

## Retention (peer-relative, 0.50 = median comparable video)
- recorded **137 / 230** eligible (≥72 h old)
- last 30 recorded: opening 0.395 · middle **0.397** · final 0.667 · overall 0.489 (n=30)

## Long-form
- 9 uploads · 30 d: 2 views · **0.2 watch-hours** (of 4,000)
  - 2026-08-30 The Unsolved Mysteries That Could Rewrite Physics
  - 2026-09-06 The Unsolved Mysteries That Could Rewrite Physics
  - 2026-09-13 What the Universe Hides: 6 Unsolved Mysteries That

## Pipeline
- CI last 7: 11-15 ✅ · 11-14 ✅ · 11-14 ✅ · 11-13 ✅ · 11-13 ✅ · 11-12 ✅ · 11-12 ✅
- scheduled start delay vs nominal cron: min 3h18 · median **7h28** · max 10h10
- render archive: **30 / 30** of records since the archive shipped have a URL
- LLM chain: groq → gemini → cerebras → openrouter (Cerebras 402 — billing; probe at session open)

## Falsifiers
| ID | claim | checkpoint | current | status |
|---|---|---|---|---|
| F1 | 2×/day does not halve per-video reach | 30 videos post-switch | — | not started |
| F2 | CTA overlay does not repeat May | 30 videos post-overlay | — | not started |
| F3 | The kit is sellable | 30 d post-launch | sales not tracked here | not started |
| F4 | Clone reaches like the original | clone week 8 | other repo | not started |
| F5 | Compilations get watched | after 3 monthly uploads | long-form 30d views 2 | not started |
| F6 | Meta reach worth the engineering | day 60 | not live | not started |
| F7 | Portfolio can become income | month 6 | cash not tracked here | manual |
| F8 | No termination exposure | continuous | CI failures last 7: 0 | manual — check Studio for notices |
| F9 | Affiliate accounts survive | day 150 per account | n/a | not started |

Milestone dates live in `config.MILESTONES`; a falsifier starts watching the day its milestone is set.

## Not live yet
- Meta reach (Phase 4) · Kit sales (Phase 7) · Clone (Phase 6)
