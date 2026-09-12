# YOU — Weekly Report · 2026-09-12 09:06 UTC

Read the **Falsifiers** table first. Everything else is context.

## Channel
- **56 subs** · 51,531 views · 140 videos (lifetime)
- last 30 d Shorts: **12,877 views** · 21 subs · **1.63 subs/1k**

## Shorts — views at 48 h (equal-age cohorts)
| cohort | n | median | mean | ≥50 | max | window |
|---|---|---|---|---|---|---|
| last 30 | 30 | **275** | 426 | 22 | 1034 | 2026-08-13 → 2026-09-09 |
| prior 30 | 30 | 416 | 494 | 29 | 1137 | 2026-07-18 → 2026-08-12 |

last/prior median ratio: **×0.66** (the falsifier bar is ×0.53; anything between 0.53 and 1.88 is noise at n=30)

last 10 uploads: 09-01 **982** HOW IT WORKS · 09-02 **817** HOW IT WORKS · 09-03 **237** UNSOLVED · 09-04 **87** UNSOLVED · 09-05 **199** UNSOLVED · 09-06 **313** UNSOLVED · 09-06 **991** HOW IT WORKS · 09-07 **237** UNSOLVED · 09-08 **14** UNSOLVED · 09-09 **96** UNSOLVED

## Geography (90 d)
- top: **US** · US+UK+CA+AU **76.5%** · India 4.9% · fetched 2026-09-12
- US 70.0% · PH 9.5% · IN 4.9% · GB 3.2% · DE 3.0%

## Retention (peer-relative, 0.50 = median comparable video)
- recorded **82 / 168** eligible (≥72 h old)
- last 30 recorded: opening 0.368 · middle **0.379** · final 0.59 · overall 0.448 (n=30)

## Long-form
- 8 uploads · 30 d: 406 views · **11.3 watch-hours** (of 4,000)
  - 2026-08-23 What the Universe Hides: Six Unsolved Mysteries Th
  - 2026-08-30 The Unsolved Mysteries That Could Rewrite Physics
  - 2026-09-06 The Unsolved Mysteries That Could Rewrite Physics

## Pipeline
- CI last 7: 09-12 ✅ (manual) · 09-12 ✅ · 09-11 ❌ failure · 09-10 ✅ · 09-09 ✅ · 09-08 ✅ · 09-07 ✅
- scheduled start delay: no scheduled runs since the cron shift yet (measures from the day after `MILESTONES.cron_shift`)
- render archive: **0 / 0** of records since the archive shipped have a URL
- LLM chain: groq → gemini → cerebras → openrouter (Cerebras 402 — billing; probe at session open)

## Falsifiers
| ID | claim | checkpoint | current | status |
|---|---|---|---|---|
| F1 | 2×/day does not halve per-video reach | 30 videos post-switch | — | not started |
| F2 | CTA overlay does not repeat May | 30 videos post-overlay | — | not started |
| F3 | The kit is sellable | 30 d post-launch | sales not tracked here | not started |
| F4 | Clone reaches like the original | clone week 8 | other repo | not started |
| F5 | Compilations get watched | after 3 monthly uploads | long-form 30d views 406 | not started |
| F6 | Meta reach worth the engineering | day 60 | not live | not started |
| F7 | Portfolio can become income | month 6 | cash not tracked here | manual |
| F8 | No termination exposure | continuous | CI failures last 7: 1 | manual — check Studio for notices |
| F9 | Affiliate accounts survive | day 150 per account | n/a | not started |

Milestone dates live in `config.MILESTONES`; a falsifier starts watching the day its milestone is set.

## Not live yet
- Meta reach (Phase 4) · Kit sales (Phase 7) · Clone (Phase 6)
