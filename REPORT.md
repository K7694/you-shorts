# YOU — Weekly Report · 2026-09-27 05:10 UTC

Read the **Falsifiers** table first. Everything else is context.

## Channel
- **65 subs** · 58,935 views · 155 videos (lifetime)
- last 30 d Shorts: **12,082 views** · 14 subs · **1.16 subs/1k**

## Shorts — views at 48 h (equal-age cohorts)
| cohort | n | median | mean | ≥50 | max | window |
|---|---|---|---|---|---|---|
| last 30 | 30 | **314** | 424 | 23 | 1023 | 2026-08-26 → 2026-09-24 |
| prior 30 | 30 | 434 | 449 | 25 | 1085 | 2026-07-30 → 2026-08-25 |

last/prior median ratio: **×0.72** (the falsifier bar is ×0.53; anything between 0.53 and 1.88 is noise at n=30)

last 10 uploads: 09-15 **421** WHAT IF · 09-16 **41** UNSOLVED · 09-17 **22** UNSOLVED · 09-18 **1023** UNSOLVED · 09-19 **905** UNSOLVED · 09-20 **167** HOW IT WORKS · 09-21 **700** HOW IT WORKS · 09-22 **613** UNSOLVED · 09-23 **982** UNSOLVED · 09-24 **7** UNSOLVED

## Geography (90 d)
- top: **US** · US+UK+CA+AU **76.5%** · India 4.9% · fetched 2026-09-12
- US 70.0% · PH 9.5% · IN 4.9% · GB 3.2% · DE 3.0%

## Retention (peer-relative, 0.50 = median comparable video)
- recorded **96 / 182** eligible (≥72 h old)
- last 30 recorded: opening 0.346 · middle **0.345** · final 0.58 · overall 0.427 (n=30)

## Long-form
- 9 uploads · 30 d: 298 views · **8.7 watch-hours** (of 4,000)
  - 2026-08-30 The Unsolved Mysteries That Could Rewrite Physics
  - 2026-09-06 The Unsolved Mysteries That Could Rewrite Physics
  - 2026-09-13 What the Universe Hides: 6 Unsolved Mysteries That

## Pipeline
- CI last 7: 09-27 ✅ · 09-26 ✅ · 09-26 ✅ · 09-25 ✅ · 09-25 ✅ · 09-24 ✅ · 09-24 ✅
- scheduled start delay vs nominal cron: min 1h50 · median **5h11** · max 8h22
- render archive: **15 / 15** of records since the archive shipped have a URL
- LLM chain: groq → gemini → cerebras → openrouter (Cerebras 402 — billing; probe at session open)

## Falsifiers
| ID | claim | checkpoint | current | status |
|---|---|---|---|---|
| F1 | 2×/day does not halve per-video reach | 30 videos post-switch | — | not started |
| F2 | CTA overlay does not repeat May | 30 videos post-overlay | — | not started |
| F3 | The kit is sellable | 30 d post-launch | sales not tracked here | not started |
| F4 | Clone reaches like the original | clone week 8 | other repo | not started |
| F5 | Compilations get watched | after 3 monthly uploads | long-form 30d views 298 | not started |
| F6 | Meta reach worth the engineering | day 60 | not live | not started |
| F7 | Portfolio can become income | month 6 | cash not tracked here | manual |
| F8 | No termination exposure | continuous | CI failures last 7: 0 | manual — check Studio for notices |
| F9 | Affiliate accounts survive | day 150 per account | n/a | not started |

Milestone dates live in `config.MILESTONES`; a falsifier starts watching the day its milestone is set.

## Not live yet
- Meta reach (Phase 4) · Kit sales (Phase 7) · Clone (Phase 6)
