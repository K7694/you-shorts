# YOU — Weekly Report · 2026-11-01 05:50 UTC

Read the **Falsifiers** table first. Everything else is context.

## Channel
- **86 subs** · 78,700 views · 189 videos (lifetime)
- last 30 d Shorts: **16,139 views** · 18 subs · **1.12 subs/1k**

## Shorts — views at 48 h (equal-age cohorts)
| cohort | n | median | mean | ≥50 | max | window |
|---|---|---|---|---|---|---|
| last 30 | 30 | **586** | 611 | 26 | 1180 | 2026-09-29 → 2026-10-29 |
| prior 30 | 30 | 314 | 421 | 24 | 1023 | 2026-08-30 → 2026-09-28 |

last/prior median ratio: **×1.87** (the falsifier bar is ×0.53; anything between 0.53 and 1.88 is noise at n=30)

last 10 uploads: 10-20 **0** HOW IT WORKS · 10-21 **32** UNSOLVED · 10-22 **961** UNSOLVED · 10-23 **328** UNSOLVED · 10-24 **1008** HOW IT WORKS · 10-25 **480** UNSOLVED · 10-26 **1104** UNSOLVED · 10-27 **1107** HOW IT WORKS · 10-28 **1** UNSOLVED · 10-29 **995** HOW IT WORKS

## Geography (90 d)
- top: **US** · US+UK+CA+AU **76.5%** · India 4.9% · fetched 2026-09-12
- US 70.0% · PH 9.5% · IN 4.9% · GB 3.2% · DE 3.0%

## Retention (peer-relative, 0.50 = median comparable video)
- recorded **125 / 216** eligible (≥72 h old)
- last 30 recorded: opening 0.399 · middle **0.424** · final 0.712 · overall 0.515 (n=30)

## Long-form
- 9 uploads · 30 d: 3 views · **0.0 watch-hours** (of 4,000)
  - 2026-08-30 The Unsolved Mysteries That Could Rewrite Physics
  - 2026-09-06 The Unsolved Mysteries That Could Rewrite Physics
  - 2026-09-13 What the Universe Hides: 6 Unsolved Mysteries That

## Pipeline
- CI last 7: 11-01 ✅ · 10-31 ✅ · 10-31 ✅ · 10-30 ✅ · 10-30 ✅ · 10-29 ✅ · 10-29 ✅
- scheduled start delay vs nominal cron: min 2h02 · median **5h46** · max 9h04
- render archive: **30 / 30** of records since the archive shipped have a URL
- LLM chain: groq → gemini → cerebras → openrouter (Cerebras 402 — billing; probe at session open)

## Falsifiers
| ID | claim | checkpoint | current | status |
|---|---|---|---|---|
| F1 | 2×/day does not halve per-video reach | 30 videos post-switch | — | not started |
| F2 | CTA overlay does not repeat May | 30 videos post-overlay | — | not started |
| F3 | The kit is sellable | 30 d post-launch | sales not tracked here | not started |
| F4 | Clone reaches like the original | clone week 8 | other repo | not started |
| F5 | Compilations get watched | after 3 monthly uploads | long-form 30d views 3 | not started |
| F6 | Meta reach worth the engineering | day 60 | not live | not started |
| F7 | Portfolio can become income | month 6 | cash not tracked here | manual |
| F8 | No termination exposure | continuous | CI failures last 7: 0 | manual — check Studio for notices |
| F9 | Affiliate accounts survive | day 150 per account | n/a | not started |

Milestone dates live in `config.MILESTONES`; a falsifier starts watching the day its milestone is set.

## Not live yet
- Meta reach (Phase 4) · Kit sales (Phase 7) · Clone (Phase 6)
