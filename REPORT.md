# YOU — Weekly Report · 2026-10-18 04:19 UTC

Read the **Falsifiers** table first. Everything else is context.

## Channel
- **77 subs** · 69,669 views · 175 videos (lifetime)
- last 30 d Shorts: **15,435 views** · 17 subs · **1.10 subs/1k**

## Shorts — views at 48 h (equal-age cohorts)
| cohort | n | median | mean | ≥50 | max | window |
|---|---|---|---|---|---|---|
| last 30 | 30 | **490** | 537 | 25 | 1180 | 2026-09-15 → 2026-10-15 |
| prior 30 | 30 | 328 | 447 | 24 | 1034 | 2026-08-17 → 2026-09-14 |

last/prior median ratio: **×1.49** (the falsifier bar is ×0.53; anything between 0.53 and 1.88 is noise at n=30)

last 10 uploads: 10-05 **777** UNSOLVED · 10-06 **1057** WHAT IF · 10-07 **263** HOW IT WORKS · 10-08 **390** MIND BENDER · 10-09 **76** MIND BENDER · 10-10 **25** UNSOLVED · 10-11 **119** MIND BENDER · 10-12 **1060** MIND BENDER · 10-14 **305** MIND BENDER · 10-15 **1180** UNSOLVED

## Geography (90 d)
- top: **US** · US+UK+CA+AU **76.5%** · India 4.9% · fetched 2026-09-12
- US 70.0% · PH 9.5% · IN 4.9% · GB 3.2% · DE 3.0%

## Retention (peer-relative, 0.50 = median comparable video)
- recorded **114 / 202** eligible (≥72 h old)
- last 30 recorded: opening 0.371 · middle **0.377** · final 0.646 · overall 0.468 (n=30)

## Long-form
- 9 uploads · 30 d: 19 views · **0.4 watch-hours** (of 4,000)
  - 2026-08-30 The Unsolved Mysteries That Could Rewrite Physics
  - 2026-09-06 The Unsolved Mysteries That Could Rewrite Physics
  - 2026-09-13 What the Universe Hides: 6 Unsolved Mysteries That

## Pipeline
- CI last 7: 10-18 ✅ · 10-17 ✅ · 10-17 ✅ · 10-16 ✅ · 10-16 ✅ · 10-15 ✅ · 10-15 ✅
- scheduled start delay vs nominal cron: min 1h36 · median **5h58** · max 9h43
- render archive: **30 / 30** of records since the archive shipped have a URL
- LLM chain: groq → gemini → cerebras → openrouter (Cerebras 402 — billing; probe at session open)

## Falsifiers
| ID | claim | checkpoint | current | status |
|---|---|---|---|---|
| F1 | 2×/day does not halve per-video reach | 30 videos post-switch | — | not started |
| F2 | CTA overlay does not repeat May | 30 videos post-overlay | — | not started |
| F3 | The kit is sellable | 30 d post-launch | sales not tracked here | not started |
| F4 | Clone reaches like the original | clone week 8 | other repo | not started |
| F5 | Compilations get watched | after 3 monthly uploads | long-form 30d views 19 | not started |
| F6 | Meta reach worth the engineering | day 60 | not live | not started |
| F7 | Portfolio can become income | month 6 | cash not tracked here | manual |
| F8 | No termination exposure | continuous | CI failures last 7: 0 | manual — check Studio for notices |
| F9 | Affiliate accounts survive | day 150 per account | n/a | not started |

Milestone dates live in `config.MILESTONES`; a falsifier starts watching the day its milestone is set.

## Not live yet
- Meta reach (Phase 4) · Kit sales (Phase 7) · Clone (Phase 6)
