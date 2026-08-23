# LESSONS — every failure, its cause, and the fix

The most expensive file in this repo. Two months of failures compressed.
Read before replicating; each of these cost days.

---

## 1. Content

### ❌ The affiliate pivot killed a working channel (-97% views)
Same pipeline, only content changed: science 312 avg → affiliate 10.5 avg,
$0 earned across 37 videos. **Curiosity content has pull; selling content
has resistance.** YouTube buries "AI affiliate spam" patterns.
**Fix:** reverted to curiosity; deleted all 37 affiliate videos (they drag
the channel's per-channel quality signal). Monetization now sits behind a
`MONETIZATION_ENABLED=False` kill-switch — decide monetization AFTER
distribution is proven, never before.

### ❌ Topic repetition = silent death
4 of 8 videos in one week were black holes → all near-zero views. The
exact-string topic dedup missed *subject-level* repeats ("Black Hole
Survival" vs "stuck in a black hole?").
**Fix (code):** rotate across 12 curiosity DOMAINS + reject any topic
(even from the analyzer brief) sharing a keyword with the last ~6 topics.

### ❌ Vague hooks = 0 views, concrete hooks = breakouts
"The Hidden Truth About Reality" → 0 views. "Fire a gun on the Moon..."
→ 740 views. Same channel, same week.
**Fix:** heuristic hook scorer (rewards concrete nouns, specificity,
curiosity power-words), best-of-4 generation attempts, target ≥7/10,
good-vs-bad examples in the prompt.

### ❌ Archetypes are not equal
All breakouts came from `unsolved_mystery` and `how_does_it_work`.
`mind_blowing_fact`/`what_if`/`counterintuitive_truth` produced ~0.
**Fix:** weighted selection ~72% to winners, small exploration slice.

### ❌ 3×/day on a cold channel reads as spam
Phase 0 worked at ~2/day; the failed eras ran 3/day.
**Fix:** 1×/day until the channel earns trust, then test scaling.

---

## 2. Free-tier traps (each one took the pipeline down)

### ❌ Google OAuth "Testing" mode → token dies every 7 days
Caused 4+ days of silent zero uploads.
**Fix:** publish the OAuth app to **"In production"** (Google Auth
Platform → Audience → Publish). Refresh token then never expires.

### ❌ Git LFS free tier = 1GB bandwidth/MONTH
A 447MB asset fetched per run burned it in ~2 days → 11 consecutive
failed runs.
**Fix:** host big assets as **GitHub Release assets** (2GB/file, no
bandwidth quota) + `actions/cache`. On private repos use
`gh release download`, not the public URL (404s).

### ❌ GitHub Actions minutes (private repo) = 2000/month
Exhausted twice; runs fail in 2s with `runner_id: 0`, zero steps —
that signature = no runner allocated, not a code bug.
**Fix:** make the repo **public** → unlimited minutes forever. Scrub
history for secrets first (`git log --all` + pattern grep).

### ❌ Gemini free tier can be ZERO for an entire account
429 RESOURCE_EXHAUSTED on the very first call, every day, any model.
New API keys don't help — **quota is per project/account, not per key**
(Workspace accounts / some regions get no free generation quota at all).
Burned days hunting keys.
**Fix:** Groq (llama-3.3-70b) as primary — generous free tier, never
throttled us once in 6+ weeks. Gemini demoted to fail-fast fallback
(1 try, no cooldown — a daily quota never recovers in 90s; we wasted
4.5 min/run learning that). `LLM_PRIMARY` config flips it back anytime.

### ❌ A single LLM provider is a single point of failure
Groq retired `llama-3.3-70b-versatile` (~2026-08-18). Every run 404'd and,
because Gemini's free tier had already failed on that account, there was no
fallback — **four days with nothing published**, discovered only on the next
manual check. The model id was also hardcoded in three files.
**Fix:** one `GROQ_MODEL` in config, and `LLM_PROVIDERS` — an ordered chain
of OpenAI-compatible endpoints (Groq → Cerebras → OpenRouter). Entries with
no key are skipped, so adding a backup is a key plus a config line. 404 /
401 / 403 / 400 skip straight to the next provider instead of retrying
(a retired model never recovers by waiting); only 429 gets a cooldown.
Verified failover against a simulated retired model: 0.6s to recover.
**Also:** free-tier LLMs retire models with no notice. Prefer a router
(OpenRouter) for at least one link in the chain — swapping a dead model
becomes a one-line change.

### ❌ Reasoning models silently truncate JSON
`openai/gpt-oss-120b` spent 677 of 829 completion tokens on hidden reasoning
and returned JSON cut off mid-string. Raising `max_tokens` isn't the fix —
8000 returns HTTP 413 against a 12k tokens/min org limit.
**Fix:** `reasoning_effort: "low"` (reasoning → ~13 tokens). Send it only
where supported and drop it automatically on a 400 that names the parameter.

### ❌ Pollinations.ai free image gen died (HTTP 402)
Third-party free services monetize without notice; the whole visual
layer broke overnight.
**Fix:** Pexels stock photos — real API key, documented free tier,
stable company. Also: Pexels 403s Python's default urllib User-Agent;
send a browser-like UA.

### ❌ apt-get can hang for 30 minutes
One Ubuntu mirror hang ate an entire workflow budget.
**Fix:** `timeout-minutes: 5` on the system-deps step. Fail fast.

---

## 3. Engineering

### ❌ Silent failures cost days
Uploads failed quietly; nobody noticed for 4 days.
**Fix:** fail LOUD — exit code 1 on upload failure so GitHub Actions
marks the run red and emails you.

### ❌ Whisper transcription of our own TTS audio (removed 2026-06-27)
We synthesized speech from a script we wrote, then ran an ML model to
transcribe it for caption timings — 150MB model cache + ~30s CPU per
run to recover information we already had, plus occasional
misrecognitions corrupting captions.
**Fix:** Edge TTS emits exact `WordBoundary` timings during synthesis
(`boundary="WordBoundary"` required on edge-tts ≥7.x). Free, instant,
always correct.

### ❌ Old state poisons new strategy
After the reset, the analyzer kept suggesting AI-tool topics from
residual state (`used_topics`, performance history), and the few-shot
examples fed affiliate scripts into curiosity prompts.
**Fix:** taint-guards — filter recalled examples and reject brief topics
matching the old content pattern. Self-heals as new data accumulates.

### ❌ Don't A/B on noise
At 2–28 views/video, differences between variants are statistical noise.
Only read signals at meaningful volume (the 72-hour checkpoint protocol:
compare videos at equal age, median + best-of-batch gates).

### ✅ The visual layer is NOT the lever (measured, 2026-07-25)
A/B: photo slideshow + Ken Burns vs Pexels stock-video montage, 8 videos
per arm, compared at equal ≥72h age.
- photos: median 281, mean 380 · videos: median 354, mean 369
- Mann-Whitney **U=31.0 vs 32.0 expected under the null** — a coin flip
- **Variance INSIDE each arm (13→802 views) was ~4× the gap BETWEEN arms**

Don't spend effort on production polish before content selection. What
actually moved the number, same dataset (n=49, equal age):

| archetype | n | median views |
|---|---|---|
| unsolved_mystery | 14 | **690** |
| how_does_it_work | 17 | 241 |
| mind_blowing_fact | 7 | 108 |
| what_if | 6 | 84 |
| counterintuitive_truth | 5 | **1** |

**Archetype choice ≈ 3× lever; visuals ≈ 0×.** Open-question framings
("unsolved mystery") beat explanatory framings by ~3×. Weight hard toward
the winner and zero out anything with a dead median — a median of 1 view
across 5 tries is waste, not exploration.

### ❌ Subject-repeat guard window was too short
At a 6-video lookback, subjects returned just outside the window and
reliably flopped: "Ball Lightning" ran twice 9 days apart → **13 and 34
views** (the two worst in the cohort); "black holes" recurred across 7
videos → median 98.
**Fix:** widen the lookback to ~20 videos (~3 weeks of daily uploads) and
add *framing* words ("dark", "hidden", "forbidden", "revealed",
"science", "reality"…) to the stopword set — matching on framing was
letting the real subject noun hide. Verify with a false-positive check
against a list of genuinely fresh topics before shipping a wider window.

---

## 3b. The hook scorer measured nothing (2026-08-23)

`_score_hook` gated every script: below 7/10, regenerate, up to 4 times.
It ran for months and nobody ever checked it against reality.

**Validated two ways, both damning:**
- vs real 3-second retention (`audienceWatchRatio`): **r = -0.06, p = 0.86**
- vs `relativeRetentionPerformance`: r = -0.09, p = 0.78
- across all 150 logged hooks: **sd = 1.22**, 39% scored exactly 7
- two of its four rules fired on <5% of hooks, leaving little more than
  "contains a digit" + "contains the word you"

It was a 3-bit keyword check driving ~1.9 generations per video.
**Fix:** deleted the gate, moved the budget to `_critique_and_revise`.
`hook_score` is still logged so the record stays continuous.

**The lesson:** a scoring function that is never validated is not a
quality gate, it is a random number generator with a confidence interval.
Anything that *selects* must be checked against the outcome it claims to
predict, and "it looks reasonable" is not that check.

## 3c. n=11 pointed the wrong way; n=60 reversed it (2026-08-23)

The first retention read (n=11, filtered to >=100 views) showed the hook
window at 0.47 vs 0.50 overall and I reported "the openings are the weak
spot." The critique pass was built biased toward line 1 on that basis.

Backfilling all 60 eligible videos reversed it:

```
opening third  0.408
middle third   0.382   <- viewers actually leave here
final third    0.495
```

Middle is weakest in 57% of videos (opening 33%, final 10%);
opening-vs-middle p=0.0004, middle-vs-final p<0.0001. The n=11 subset was
filtered to >=100 views — which *selects for videos whose body holds up*,
inverting the very comparison it was used for. Caught and corrected before
it shipped, but only because the instrumentation landed the same day.

**The lesson:** a filter applied for convenience (">=100 views so the
numbers are stable") can encode the answer. When a subset is small AND
filtered, the filter is a confounder until proven otherwise.

## 3d. A diagnostic that lies is worse than none (2026-08-23)

`test_apis.py` reports Groq and Cerebras as `HTTP 403 / error 1010`
(Cloudflare) while production calls the same endpoints fine. The probe
omits the `User-Agent: Mozilla/5.0` header that `you.py` sets. Anyone
debugging an outage with it would conclude a working provider is dead.
Probe through the production code path, never a parallel re-implementation.

## 4. Process lessons

- **Change one thing per batch.** The clean Phase 0 vs Phase 1 comparison
  is the only reason the diagnosis was possible.
- **Let data vote, not vibes.** Decision gates (median @72h, hit-rate)
  beat gut feeling every time. Every recipe change here traced to a metric.
- **Keep dead code behind flags, not deleted.** The affiliate layer,
  Subway Surfers mode, and Gemini path are all dormant one-line revivals.
- **Verify externally-facing claims** (quota resets, free tiers) with a
  curl test before building on them.
