# YOU — Weekly Report · 2026-11-08 05:51 UTC

Read the **Falsifiers** table first. Everything else is context.

## Channel
- **90 subs** · 81,173 views · 196 videos (lifetime)
- last 30 d Shorts: **14,161 views** · 20 subs · **1.41 subs/1k**

## Shorts — views at 48 h (equal-age cohorts)
| cohort | n | median | mean | ≥50 | max | window |
|---|---|---|---|---|---|---|
| last 30 | 30 | **365** | 517 | 24 | 1180 | 2026-10-06 → 2026-11-05 |
| prior 30 | 30 | 404 | 485 | 25 | 1158 | 2026-09-06 → 2026-10-05 |

last/prior median ratio: **×0.90** (the falsifier bar is ×0.53; anything between 0.53 and 1.88 is noise at n=30)

last 10 uploads: 10-27 **1107** HOW IT WORKS · 10-28 **1** UNSOLVED · 10-29 **995** HOW IT WORKS · 10-30 **126** UNSOLVED · 10-31 **340** UNSOLVED · 11-01 **663** WHAT IF · 11-02 **700** UNSOLVED · 11-03 **199** UNSOLVED · 11-04 **9** UNSOLVED · 11-05 **0** UNSOLVED

## Geography (90 d)
- top: **US** · US+UK+CA+AU **76.5%** · India 4.9% · fetched 2026-09-12
- US 70.0% · PH 9.5% · IN 4.9% · GB 3.2% · DE 3.0%

## Retention (peer-relative, 0.50 = median comparable video)
- recorded **131 / 223** eligible (≥72 h old)
- last 30 recorded: opening 0.406 · middle **0.429** · final 0.71 · overall 0.518 (n=30)

## Long-form
- 9 uploads · 30 d: 4 views · **0.2 watch-hours** (of 4,000)
  - 2026-08-30 The Unsolved Mysteries That Could Rewrite Physics
  - 2026-09-06 The Unsolved Mysteries That Could Rewrite Physics
  - 2026-09-13 What the Universe Hides: 6 Unsolved Mysteries That

## Pipeline
- CI last 7: 11-08 ✅ · 11-07 ✅ · 11-07 ✅ · 11-06 ✅ · 11-06 ✅ · 11-05 ✅ · 11-05 ✅
- scheduled start delay vs nominal cron: min 3h08 · median **7h04** · max 10h24
- render archive: **30 / 30** of records since the archive shipped have a URL
- LLM chain: groq → gemini → cerebras → openrouter (Cerebras 402 — billing; probe at session open)

## Falsifiers
| ID | claim | checkpoint | current | status |
|---|---|---|---|---|
| F1 | 2×/day does not halve per-video reach | 30 videos post-switch | — | not started |
| F2 | CTA overlay does not repeat May | 30 videos post-overlay | — | not started |
| F3 | The kit is sellable | 30 d post-launch | sales not tracked here | not started |
| F4 | Clone reaches like the original | clone week 8 | other repo | not started |
| F5 | Compilations get watched | after 3 monthly uploads | long-form 30d views 4 | not started |
| F6 | Meta reach worth the engineering | day 60 | not live | not started |
| F7 | Portfolio can become income | month 6 | cash not tracked here | manual |
| F8 | No termination exposure | continuous | CI failures last 7: 0 | manual — check Studio for notices |
| F9 | Affiliate accounts survive | day 150 per account | n/a | not started |

Milestone dates live in `config.MILESTONES`; a falsifier starts watching the day its milestone is set.

## Not live yet
- Meta reach (Phase 4) · Kit sales (Phase 7) · Clone (Phase 6)
