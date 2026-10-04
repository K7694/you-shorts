# YOU — Weekly Report · 2026-10-04 05:42 UTC

Read the **Falsifiers** table first. Everything else is context.

## Channel
- **70 subs** · 62,407 views · 162 videos (lifetime)
- last 30 d Shorts: **13,000 views** · 16 subs · **1.23 subs/1k**

## Shorts — views at 48 h (equal-age cohorts)
| cohort | n | median | mean | ≥50 | max | window |
|---|---|---|---|---|---|---|
| last 30 | 30 | **319** | 420 | 25 | 1023 | 2026-09-02 → 2026-10-01 |
| prior 30 | 30 | 434 | 457 | 23 | 1034 | 2026-08-04 → 2026-09-01 |

last/prior median ratio: **×0.74** (the falsifier bar is ×0.53; anything between 0.53 and 1.88 is noise at n=30)

last 10 uploads: 09-22 **613** UNSOLVED · 09-23 **982** UNSOLVED · 09-24 **7** UNSOLVED · 09-25 **641** HOW IT WORKS · 09-26 **1004** HOW IT WORKS · 09-27 **248** UNSOLVED · 09-28 **1** UNSOLVED · 09-29 **688** HOW IT WORKS · 09-30 **324** UNSOLVED · 10-01 **545** UNSOLVED

## Geography (90 d)
- top: **US** · US+UK+CA+AU **76.5%** · India 4.9% · fetched 2026-09-12
- US 70.0% · PH 9.5% · IN 4.9% · GB 3.2% · DE 3.0%

## Retention (peer-relative, 0.50 = median comparable video)
- recorded **102 / 189** eligible (≥72 h old)
- last 30 recorded: opening 0.347 · middle **0.351** · final 0.6 · overall 0.436 (n=30)

## Long-form
- 9 uploads · 30 d: 70 views · **1.8 watch-hours** (of 4,000)
  - 2026-08-30 The Unsolved Mysteries That Could Rewrite Physics
  - 2026-09-06 The Unsolved Mysteries That Could Rewrite Physics
  - 2026-09-13 What the Universe Hides: 6 Unsolved Mysteries That

## Pipeline
- CI last 7: 10-04 ✅ · 10-03 ✅ · 10-03 ✅ · 10-02 ✅ · 10-02 ✅ · 10-01 ✅ · 10-01 ✅
- scheduled start delay vs nominal cron: min 2h29 · median **6h01** · max 9h03
- render archive: **22 / 22** of records since the archive shipped have a URL
- LLM chain: groq → gemini → cerebras → openrouter (Cerebras 402 — billing; probe at session open)

## Falsifiers
| ID | claim | checkpoint | current | status |
|---|---|---|---|---|
| F1 | 2×/day does not halve per-video reach | 30 videos post-switch | — | not started |
| F2 | CTA overlay does not repeat May | 30 videos post-overlay | — | not started |
| F3 | The kit is sellable | 30 d post-launch | sales not tracked here | not started |
| F4 | Clone reaches like the original | clone week 8 | other repo | not started |
| F5 | Compilations get watched | after 3 monthly uploads | long-form 30d views 70 | not started |
| F6 | Meta reach worth the engineering | day 60 | not live | not started |
| F7 | Portfolio can become income | month 6 | cash not tracked here | manual |
| F8 | No termination exposure | continuous | CI failures last 7: 0 | manual — check Studio for notices |
| F9 | Affiliate accounts survive | day 150 per account | n/a | not started |

Milestone dates live in `config.MILESTONES`; a falsifier starts watching the day its milestone is set.

## Not live yet
- Meta reach (Phase 4) · Kit sales (Phase 7) · Clone (Phase 6)
