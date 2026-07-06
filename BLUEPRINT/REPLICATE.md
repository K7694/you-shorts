# REPLICATE — launch a clone for a new channel/niche in ~1 hour

Follow in order. Every step is $0.

## Phase 1 — Accounts & keys (~25 min)

| # | What | Where | Notes |
|---|------|-------|-------|
| 1 | New YouTube channel | youtube.com (Google account → Create channel) | Name it for the niche |
| 2 | Google Cloud project | console.cloud.google.com | Enable **YouTube Data API v3** |
| 3 | OAuth client (Desktop app) | APIs & Services → Credentials | Download as `client_secrets.json` |
| 4 | **Publish OAuth app to Production** | Google Auth Platform → Audience → "Publish app" | ⚠️ Skip this = token dies every 7 days |
| 5 | YouTube Data API key | Credentials → API key | For the analyzer (read-only calls) |
| 6 | Groq API key | console.groq.com → API Keys | Primary LLM, free |
| 7 | Pexels API key | pexels.com/api | Visuals, free |
| 8 | (Optional) Gemini key | aistudio.google.com/apikey | Only if account has real quota — test with one curl call first (LESSONS.md §Gemini) |

## Phase 2 — Repo (~15 min)

1. Copy the pipeline files into a fresh **public** repo (public = unlimited
   Actions minutes):
   ```
   you.py  config.py  analyzer.py  refresh_brief.py  compliance.py
   requirements.txt  .gitignore  .github/workflows/create_video.yml
   BLUEPRINT/
   ```
2. `.gitignore` MUST keep out: `client_secrets.json`, `youtube_token.json`,
   `.env`, `output/`, `temp/`.
3. Local `.env` for testing:
   ```
   GROQ_API_KEY=...
   YOUTUBE_DATA_API_KEY=...
   PEXELS_API_KEY=...
   GEMINI_API_KEY=...   (optional)
   ```

## Phase 3 — Auth (~5 min)

```bash
cd <repo>
python auth_youtube.py        # browser opens → sign in with the CHANNEL's account
type youtube_token.json       # verify refresh_token present
```

## Phase 4 — GitHub Secrets (~5 min)

```bash
gh secret set GROQ_API_KEY            # paste value
gh secret set YOUTUBE_DATA_API_KEY
gh secret set PEXELS_API_KEY
gh secret set GEMINI_API_KEY          # optional
gh secret set CLIENT_SECRETS_JSON < client_secrets.json
gh secret set YOUTUBE_TOKEN_JSON < youtube_token.json
```

## Phase 5 — Configure the niche (~10 min)

Edit `config.py` — the knobs that define the channel (full list in KNOBS.md):

- `CHANNEL_NICHE` — one specific sentence. Must be *intrinsic-curiosity*
  content people seek out, not content that sells.
- `CURIOSITY_DOMAINS` — 10–12 subject buckets inside the niche
  (drives anti-repetition rotation).
- `CONTENT_ARCHETYPES` + `CONTENT_ARCHETYPE_WEIGHTS` — start with this
  repo's proven set; re-weight after ~15 videos of YOUR data.
- `CONTENT_TONE`, `VOICE`, `IMAGE_STYLE` — the aesthetic.
- `YOUTUBE_DEFAULT_TAGS`, `YOUTUBE_CATEGORY`.
- In `analyzer.py`: `DEFAULT_COMPETITORS` (5 top channels in the niche)
  and the search query list (~line 82).
- Update the few-shot examples in `you.py` (`_CURIOSITY_STATIC_EXAMPLES`)
  with 3 proven viral scripts *from the new niche*.
- Reset state for a clean start: `used_topics.json` → `[]`,
  delete `feedback/uploaded.json`, `analyzer/*.json`.

## Phase 6 — Test → launch (~10 min)

```bash
python you.py --no-upload     # or run create_video(upload=False) — check output/*.mp4
git push
gh workflow run create_video.yml   # full CI test incl. upload
gh run watch                       # expect green + video live
```
Cron (1×/day) is already in the workflow file. Done — it runs itself.

## Phase 7 — Operate (the part people skip)

- **Hold the recipe constant for 6–8 videos**, then read the batch:
  views at equal 72h age, median + best.
- Gates: median ≥50 & one ≥200 → healthy, keep going.
  Median single-digits after 8 → something's wrong; check LESSONS.md.
- Re-weight archetypes to YOUR winners after ~15 videos.
- Never add monetization before distribution is proven (Week 8 gate).
