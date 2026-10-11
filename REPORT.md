# YOU — Weekly Report · 2026-10-11 05:36 UTC

Read the **Falsifiers** table first. Everything else is context.

## Channel
- **71 subs** · 66,380 views · 169 videos (lifetime)
- last 30 d Shorts: **14,887 views** · 16 subs · **1.07 subs/1k**

## Shorts — views at 48 h (equal-age cohorts)
| cohort | n | median | mean | ≥50 | max | window |
|---|---|---|---|---|---|---|
| last 30 | 30 | **406** | 491 | 25 | 1158 | 2026-09-08 → 2026-10-08 |
| prior 30 | 30 | 380 | 456 | 23 | 1034 | 2026-08-11 → 2026-09-07 |

last/prior median ratio: **×1.07** (the falsifier bar is ×0.53; anything between 0.53 and 1.88 is noise at n=30)

last 10 uploads: 09-29 **688** HOW IT WORKS · 09-30 **324** UNSOLVED · 10-01 **545** UNSOLVED · 10-02 **1158** HOW IT WORKS · 10-03 **434** HOW IT WORKS · 10-04 **939** MIND BENDER · 10-05 **777** UNSOLVED · 10-06 **1057** WHAT IF · 10-07 **263** HOW IT WORKS · 10-08 **390** MIND BENDER

## Geography (90 d)
- top: **US** · US+UK+CA+AU **76.5%** · India 4.9% · fetched 2026-09-12
- US 70.0% · PH 9.5% · IN 4.9% · GB 3.2% · DE 3.0%

## Retention (peer-relative, 0.50 = median comparable video)
- recorded **108 / 196** eligible (≥72 h old)
- last 30 recorded: opening 0.361 · middle **0.377** · final 0.65 · overall 0.466 (n=30)

## Long-form
- 9 uploads · 30 d: 32 views · **0.6 watch-hours** (of 4,000)
  - 2026-08-30 The Unsolved Mysteries That Could Rewrite Physics
  - 2026-09-06 The Unsolved Mysteries That Could Rewrite Physics
  - 2026-09-13 What the Universe Hides: 6 Unsolved Mysteries That

## Pipeline
- CI last 7: 10-11 ✅ · 10-10 ✅ · 10-10 ✅ · 10-09 ✅ · 10-09 ✅ · 10-08 ✅ · 10-08 ✅
- scheduled start delay vs nominal cron: min 2h35 · median **6h18** · max 9h26
- render archive: **29 / 29** of records since the archive shipped have a URL
- LLM chain: groq → gemini → cerebras → openrouter (Cerebras 402 — billing; probe at session open)

## Falsifiers
| ID | claim | checkpoint | current | status |
|---|---|---|---|---|
| F1 | 2×/day does not halve per-video reach | 30 videos post-switch | — | not started |
| F2 | CTA overlay does not repeat May | 30 videos post-overlay | — | not started |
| F3 | The kit is sellable | 30 d post-launch | sales not tracked here | not started |
| F4 | Clone reaches like the original | clone week 8 | other repo | not started |
| F5 | Compilations get watched | after 3 monthly uploads | long-form 30d views 32 | not started |
| F6 | Meta reach worth the engineering | day 60 | not live | not started |
| F7 | Portfolio can become income | month 6 | cash not tracked here | manual |
| F8 | No termination exposure | continuous | CI failures last 7: 0 | manual — check Studio for notices |
| F9 | Affiliate accounts survive | day 150 per account | n/a | not started |

Milestone dates live in `config.MILESTONES`; a falsifier starts watching the day its milestone is set.

## Not live yet
- Meta reach (Phase 4) · Kit sales (Phase 7) · Clone (Phase 6)
