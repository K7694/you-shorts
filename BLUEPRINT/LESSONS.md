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

---

## 4. Process lessons

- **Change one thing per batch.** The clean Phase 0 vs Phase 1 comparison
  is the only reason the diagnosis was possible.
- **Let data vote, not vibes.** Decision gates (median @72h, hit-rate)
  beat gut feeling every time. Every recipe change here traced to a metric.
- **Keep dead code behind flags, not deleted.** The affiliate layer,
  Subway Surfers mode, and Gemini path are all dormant one-line revivals.
- **Verify externally-facing claims** (quota resets, free tiers) with a
  curl test before building on them.
