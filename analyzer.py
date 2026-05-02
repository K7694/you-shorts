#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║                    YOU — ANALYZER v1.0                           ║
║         The intelligence layer. Knows what works before          ║
║         you even think about filming.                            ║
║                                                                  ║
║   What it does:                                                  ║
║     1. Scans trending YouTube Shorts in your niche               ║
║     2. Reverse-engineers top competitor channels                  ║
║     3. Tracks YOUR channel performance                            ║
║     4. Runs LLM pattern analysis on all data                     ║
║     5. Outputs a ranked content brief for the next video         ║
║                                                                  ║
║   python analyzer.py              → full analysis + brief        ║
║   python analyzer.py --trends     → trending topics only         ║
║   python analyzer.py --mine       → your channel stats only      ║
║   python analyzer.py --brief      → content brief only           ║
║   python analyzer.py --competitors → competitor analysis only    ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
"""

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.parse
from datetime import datetime, timedelta, timezone
from pathlib import Path

from config import (
    YOUTUBE_DATA_API_KEY, GEMINI_API_KEY, GROQ_API_KEY,
    CHANNEL_NICHE, OUTPUT_DIR, BASE_DIR
)

# ── Storage ───────────────────────────────────────────────────────
ANALYZER_DIR = BASE_DIR / "analyzer"
ANALYZER_DIR.mkdir(exist_ok=True)

PERFORMANCE_DB   = ANALYZER_DIR / "performance.json"
COMPETITOR_DB    = ANALYZER_DIR / "competitors.json"
TREND_DB         = ANALYZER_DIR / "trends.json"
BRIEF_DB         = ANALYZER_DIR / "latest_brief.json"

# ── Competitor channels in science/facts niche (auto-seeded) ─────
DEFAULT_COMPETITORS = [
    "UCZYTClx2T1of7BRZ86-8fow",  # SciShow
    "UCvjgXvBlbQiydffZU7m1_aw",  # Kurzgesagt
    "UC9-y-6csu5WGm29I7JiwpnA",  # Computerphile (tech facts)
    "UCUK0HBIBWgM2c4vsPhkYY4w",  # What If
    "UCsXVk37bltHxD1rDPwtNM8Q",  # Kurzgesagt (shorts focused)
]

# ─────────────────────────────────────────────────────────────────
#  YOUTUBE DATA API — the raw data layer
# ─────────────────────────────────────────────────────────────────

def _yt_get(endpoint: str, params: dict) -> dict:
    """Make a YouTube Data API v3 request."""
    params["key"] = YOUTUBE_DATA_API_KEY
    url = f"https://www.googleapis.com/youtube/v3/{endpoint}?" + urllib.parse.urlencode(params)
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        raise RuntimeError(f"YouTube API error {e.code}: {body[:200]}")


def search_trending_shorts(niche: str, max_results: int = 50) -> list:
    """Search for trending Shorts using multiple queries. Returns enriched, deduplicated list."""
    published_after = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Use several short, specific queries instead of one long niche string.
    # YouTube search works best with 3-5 keyword phrases, not full sentences.
    queries = [
        "mind-blowing science facts shorts",
        "forbidden knowledge universe shorts",
        "reality facts you didn't know",
        "space physics secrets shorts",
        "science shorts viral facts",
    ]

    seen_ids: set = set()
    all_video_ids: list = []

    per_query = max(10, max_results // len(queries))

    for q in queries:
        print(f"   🔍 Searching: '{q}'...")
        try:
            data = _yt_get("search", {
                "part": "snippet",
                "q": q,
                "type": "video",
                "videoDuration": "short",
                "order": "viewCount",
                "publishedAfter": published_after,
                "maxResults": per_query,
                "relevanceLanguage": "en",
                "regionCode": "US",
            })
            for item in data.get("items", []):
                vid = item.get("id", {}).get("videoId")
                if vid and vid not in seen_ids:
                    seen_ids.add(vid)
                    all_video_ids.append(vid)
            time.sleep(0.3)  # Be nice to the API
        except Exception as e:
            print(f"      Warning: query failed ({e})")
            continue

    print(f"   Found {len(all_video_ids)} unique video IDs across {len(queries)} queries")
    if not all_video_ids:
        return []

    return _enrich_videos(all_video_ids)


def _enrich_videos(video_ids: list) -> list:
    """Fetch full stats for a list of video IDs."""
    if not video_ids:
        return []

    # Batch up to 50 at a time
    enriched = []
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i+50]
        data = _yt_get("videos", {
            "part": "snippet,statistics,contentDetails",
            "id": ",".join(batch),
        })
        for item in data.get("items", []):
            stats = item.get("statistics", {})
            snippet = item.get("snippet", {})
            duration = item.get("contentDetails", {}).get("duration", "PT0S")

            # Parse duration to seconds
            import re
            match = re.search(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", duration)
            secs = 0
            if match:
                secs = int(match.group(1) or 0)*3600 + int(match.group(2) or 0)*60 + int(match.group(3) or 0)

            # Only keep Shorts (under 65 seconds)
            if secs > 65:
                continue

            views = int(stats.get("viewCount", 0))
            likes = int(stats.get("likeCount", 0))
            comments = int(stats.get("commentCount", 0))
            published = snippet.get("publishedAt", "")

            # Compute engagement rate
            engagement = round((likes + comments) / max(views, 1) * 100, 3)

            # Compute views/day velocity
            if published:
                try:
                    pub_dt = datetime.fromisoformat(published.replace("Z", "+00:00"))
                    age_days = max((datetime.now(timezone.utc) - pub_dt).days, 1)
                    velocity = round(views / age_days)
                except Exception:
                    velocity = 0
            else:
                velocity = 0

            enriched.append({
                "id": item["id"],
                "title": snippet.get("title", ""),
                "channel": snippet.get("channelTitle", ""),
                "channel_id": snippet.get("channelId", ""),
                "published": published,
                "views": views,
                "likes": likes,
                "comments": comments,
                "engagement_rate": engagement,
                "views_per_day": velocity,
                "tags": snippet.get("tags", []),
                "description": snippet.get("description", "")[:300],
                "duration_secs": secs,
                "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
            })

    # Sort by view velocity (trending = fast growing, not just total views)
    enriched.sort(key=lambda x: x["views_per_day"], reverse=True)
    return enriched


def get_competitor_top_videos(channel_id: str, max_results: int = 20) -> list:
    """Get top Shorts from a competitor channel."""
    try:
        # Get channel's uploads playlist
        data = _yt_get("channels", {
            "part": "contentDetails,snippet",
            "id": channel_id,
        })
        if not data.get("items"):
            return []

        channel_name = data["items"][0]["snippet"]["title"]
        uploads_id = data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

        # Get recent uploads
        playlist_data = _yt_get("playlistItems", {
            "part": "contentDetails",
            "playlistId": uploads_id,
            "maxResults": max_results,
        })

        video_ids = [item["contentDetails"]["videoId"] for item in playlist_data.get("items", [])]
        videos = _enrich_videos(video_ids)

        for v in videos:
            v["channel"] = channel_name
            v["channel_id"] = channel_id

        return videos
    except Exception as e:
        print(f"      Warning: Could not fetch channel {channel_id}: {e}")
        return []


def _get_oauth_token() -> str | None:
    """Get a valid OAuth access token, refreshing if needed."""
    token_file = BASE_DIR / "youtube_token.json"
    if not token_file.exists():
        return None
    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        creds = Credentials.from_authorized_user_file(str(token_file))
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        return creds.token
    except Exception:
        return None


def get_my_channel_id() -> dict | None:
    """Get channel info — tries OAuth first, falls back to searching by handle."""
    token = _get_oauth_token()
    if token:
        try:
            url = "https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics&mine=true"
            req = urllib.request.Request(url, headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
            })
            with urllib.request.urlopen(req, timeout=15) as r:
                data = json.loads(r.read().decode())
            if data.get("items"):
                item = data["items"][0]
                return {
                    "id": item["id"],
                    "name": item["snippet"]["title"],
                    "subscribers": int(item["statistics"].get("subscriberCount", 0)),
                    "total_views": int(item["statistics"].get("viewCount", 0)),
                    "video_count": int(item["statistics"].get("videoCount", 0)),
                }
        except Exception as e:
            print(f"      OAuth channel fetch failed: {e}")

    # Fallback: search for channel by niche keyword using API key
    try:
        data = _yt_get("search", {
            "part": "snippet",
            "q": "KnowMore-Dailyday",
            "type": "channel",
            "maxResults": 1,
        })
        if data.get("items"):
            cid = data["items"][0]["id"]["channelId"]
            ch_data = _yt_get("channels", {"part": "snippet,statistics", "id": cid})
            if ch_data.get("items"):
                item = ch_data["items"][0]
                return {
                    "id": item["id"],
                    "name": item["snippet"]["title"],
                    "subscribers": int(item["statistics"].get("subscriberCount", 0)),
                    "total_views": int(item["statistics"].get("viewCount", 0)),
                    "video_count": int(item["statistics"].get("videoCount", 0)),
                }
    except Exception:
        pass
    return None


def get_my_video_stats() -> list:
    """Get performance stats for my uploaded Shorts via OAuth."""
    token = _get_oauth_token()
    if not token:
        return []
    try:
        # Get my channel uploads playlist
        url = "https://www.googleapis.com/youtube/v3/channels?part=contentDetails&mine=true"
        req = urllib.request.Request(url, headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        })
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read().decode())

        if not data.get("items"):
            return []

        uploads_id = data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        url2 = f"https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&playlistId={uploads_id}&maxResults=50"
        req2 = urllib.request.Request(url2, headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        })
        with urllib.request.urlopen(req2, timeout=15) as r:
            playlist_data = json.loads(r.read().decode())

        video_ids = [item["contentDetails"]["videoId"] for item in playlist_data.get("items", [])]
        return _enrich_videos(video_ids)
    except Exception as e:
        print(f"      Warning: Could not fetch your video stats: {e}")
        return []


# ─────────────────────────────────────────────────────────────────
#  LLM PATTERN ANALYSIS — the intelligence layer
# ─────────────────────────────────────────────────────────────────

def _call_llm_analyzer(prompt: str) -> str:
    """Call best available LLM for analysis."""
    # Try Gemini first
    if GEMINI_API_KEY:
        try:
            url = (
                "https://generativelanguage.googleapis.com/v1beta/models/"
                f"gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
            )
            payload = json.dumps({
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.3, "maxOutputTokens": 4096},
            }).encode()
            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=45) as r:
                data = json.loads(r.read().decode())
                return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception as e:
            print(f"      Gemini: {e}")

    # Try Groq
    if GROQ_API_KEY:
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            payload = json.dumps({
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3, "max_tokens": 4096,
            }).encode()
            req = urllib.request.Request(url, data=payload, headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "User-Agent": "Mozilla/5.0",
            })
            with urllib.request.urlopen(req, timeout=60) as r:
                data = json.loads(r.read().decode())
                return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"      Groq: {e}")

    # Fallback to local Ollama
    try:
        url = "http://localhost:11434/api/generate"
        payload = json.dumps({
            "model": "llama3.1:8b",
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.3, "num_predict": 4096},
        }).encode()
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=600) as r:
            data = json.loads(r.read().decode())
            return data["response"].strip()
    except Exception as e:
        raise RuntimeError(f"All LLMs failed: {e}")


def analyze_patterns(trending: list, competitors: list, my_videos: list) -> dict:
    """Feed all data to LLM for deep pattern analysis."""
    print("   🧠 Running LLM pattern analysis...")

    # Prepare data summaries for the LLM
    top_trending = trending[:20]
    top_competitor = sorted(competitors, key=lambda x: x.get("views_per_day", 0), reverse=True)[:20]

    trending_summary = "\n".join([
        f"- [{v['views_per_day']:,}/day | {v['engagement_rate']}% eng] \"{v['title']}\" ({v['views']:,} views)"
        for v in top_trending
    ])

    competitor_summary = "\n".join([
        f"- [{v['views_per_day']:,}/day | {v['engagement_rate']}% eng] \"{v['title']}\" by {v['channel']}"
        for v in top_competitor
    ])

    my_summary = ""
    if my_videos:
        my_summary = "\n".join([
            f"- [{v['views']:,} views | {v['engagement_rate']}% eng] \"{v['title']}\""
            for v in my_videos
        ])
    else:
        my_summary = "No videos yet or stats not available."

    prompt = f"""You are a world-class YouTube Shorts strategist and data analyst.
You have access to real performance data from YouTube. Your job is to extract actionable intelligence.

CHANNEL NICHE: {CHANNEL_NICHE}

=== TRENDING SHORTS (last 30 days, sorted by views/day velocity) ===
{trending_summary if trending_summary else "No trending data available."}

=== TOP COMPETITOR VIDEOS (sorted by views/day) ===
{competitor_summary if competitor_summary else "No competitor data available."}

=== MY CHANNEL PERFORMANCE ===
{my_summary}

Perform a DEEP analysis and return a JSON object with this EXACT structure:
{{
    "market_pulse": {{
        "top_3_trending_topics": ["topic1", "topic2", "topic3"],
        "top_3_trending_hook_styles": ["hook style 1 with example", "hook style 2 with example", "hook style 3 with example"],
        "avg_engagement_rate": "X.XX%",
        "best_performing_content_type": "description of what format/type is winning",
        "viral_trigger": "the single most important thing making videos blow up right now"
    }},
    "competitor_intelligence": {{
        "winning_channels": ["channel1", "channel2"],
        "their_secret": "what are top competitors doing that others aren't",
        "title_patterns": ["pattern1", "pattern2", "pattern3"],
        "hook_patterns": ["pattern1", "pattern2", "pattern3"],
        "topics_they_avoid": ["topic1", "topic2"]
    }},
    "my_channel_diagnosis": {{
        "best_performing_video": "title or N/A",
        "worst_performing_video": "title or N/A",
        "my_strengths": ["strength1", "strength2"],
        "my_gaps": ["gap1", "gap2"],
        "retention_problem": "what is likely causing viewers to drop off"
    }},
    "content_opportunities": [
        {{
            "rank": 1,
            "topic": "specific video topic",
            "why": "data-backed reason this will perform well",
            "hook": "exact opening line to use",
            "title": "exact YouTube title to use",
            "estimated_performance": "low/medium/high/viral",
            "urgency": "why this topic is hot RIGHT NOW"
        }},
        {{
            "rank": 2,
            "topic": "specific video topic",
            "why": "data-backed reason",
            "hook": "exact opening line",
            "title": "exact YouTube title",
            "estimated_performance": "low/medium/high/viral",
            "urgency": "why now"
        }},
        {{
            "rank": 3,
            "topic": "specific video topic",
            "why": "data-backed reason",
            "hook": "exact opening line",
            "title": "exact YouTube title",
            "estimated_performance": "low/medium/high/viral",
            "urgency": "why now"
        }}
    ],
    "next_video_brief": {{
        "topic": "the single best topic to make RIGHT NOW",
        "hook": "exact first sentence — must stop the scroll",
        "script_direction": "2-3 sentences on tone, structure, what facts to include",
        "title": "exact title to use",
        "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
        "hashtags": ["#shorts", "#tag1", "#tag2"],
        "thumbnail_concept": "describe what the thumbnail should show",
        "confidence_score": 85
    }},
    "strategic_recommendations": [
        "Specific actionable recommendation 1",
        "Specific actionable recommendation 2",
        "Specific actionable recommendation 3"
    ]
}}

Be specific. Use the actual data. Do NOT give generic advice.
Return ONLY valid JSON. No markdown. No backticks."""

    raw = _call_llm_analyzer(prompt)

    # Parse JSON
    raw = raw.strip()
    if "```" in raw:
        lines = raw.split("\n")
        inside, clean = False, []
        for line in lines:
            if line.strip().startswith("```"):
                inside = not inside
                continue
            if inside:
                clean.append(line)
        raw = "\n".join(clean)

    start, end = raw.find("{"), raw.rfind("}") + 1
    if start >= 0 and end > start:
        raw = raw[start:end]

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return json.loads(raw, strict=False)


# ─────────────────────────────────────────────────────────────────
#  COMPETITOR MANAGER
# ─────────────────────────────────────────────────────────────────

def load_competitors() -> list:
    """Load competitor channel IDs from DB, seed defaults if empty."""
    if COMPETITOR_DB.exists():
        data = json.loads(COMPETITOR_DB.read_text())
        return data.get("channels", DEFAULT_COMPETITORS)
    return DEFAULT_COMPETITORS


def save_competitors(channel_ids: list):
    COMPETITOR_DB.write_text(json.dumps({"channels": channel_ids, "updated": datetime.now().isoformat()}, indent=2))


def discover_competitors(niche: str) -> list:
    """Auto-discover competitor channels by searching for top Shorts creators in niche."""
    print("   🔭 Discovering competitor channels...")
    try:
        data = _yt_get("search", {
            "part": "snippet",
            "q": niche + " facts shorts",
            "type": "channel",
            "maxResults": 10,
            "relevanceLanguage": "en",
        })
        ids = [item["id"]["channelId"] for item in data.get("items", []) if item.get("id", {}).get("channelId")]
        print(f"      Found {len(ids)} competitor channels")
        return ids
    except Exception as e:
        print(f"      Warning: Competitor discovery failed: {e}")
        return DEFAULT_COMPETITORS


# ─────────────────────────────────────────────────────────────────
#  PERFORMANCE TRACKER — logs and loads your video stats
# ─────────────────────────────────────────────────────────────────

def update_performance_db(my_videos: list):
    """Save your video performance data to local DB."""
    db = {}
    if PERFORMANCE_DB.exists():
        try:
            db = json.loads(PERFORMANCE_DB.read_text())
        except Exception:
            db = {}

    db["last_updated"] = datetime.now().isoformat()
    db["videos"] = {v["id"]: v for v in my_videos}
    PERFORMANCE_DB.write_text(json.dumps(db, indent=2))


def load_performance_db() -> dict:
    if PERFORMANCE_DB.exists():
        try:
            return json.loads(PERFORMANCE_DB.read_text())
        except Exception:
            pass
    return {}


# ─────────────────────────────────────────────────────────────────
#  FEEDBACK LOOP — pulls 48hr stats and updates top performers
# ─────────────────────────────────────────────────────────────────

_UPLOADS_LOG      = BASE_DIR / "feedback" / "uploaded.json"
_TOP_PERFORMERS_F = ANALYZER_DIR / "top_performers.json"


def run_feedback_loop() -> list:
    """Pull performance stats for videos uploaded 48+ hours ago.

    Returns list of newly-fetched video stats.
    Updates top_performers.json for self-improving scripts.
    """
    if not _UPLOADS_LOG.exists():
        print("   No uploads tracked yet — run a video first.")
        return []

    try:
        uploads = json.loads(_UPLOADS_LOG.read_text(encoding="utf-8"))
    except Exception:
        print("   Could not read uploads log.")
        return []

    def _parse_iso_utc(ts: str) -> datetime:
        """Parse an ISO timestamp; assume UTC if it's tz-naive.

        Old upload records (pre-tz-fix) stored naive timestamps like
        '2026-04-14T14:13:49.374853'. Comparing those with a tz-aware
        `now` raises TypeError. Treating them as UTC is the safest
        retroactive default.
        """
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt

    now = datetime.now(timezone.utc)
    pending = [
        u for u in uploads
        if not u.get("stats_fetched")
        and (now - _parse_iso_utc(u["uploaded_at"])).total_seconds() > 48 * 3600
    ]

    if not pending:
        print("   No videos ready for 48hr feedback yet (need to wait 48hrs after upload).")
        # Show what's coming
        for u in uploads:
            if not u.get("stats_fetched"):
                age_hrs = (now - _parse_iso_utc(u["uploaded_at"])).total_seconds() / 3600
                remaining = max(0, 48 - age_hrs)
                print(f"      \"{u['title'][:50]}\" — {remaining:.1f}hrs until ready")
        return []

    print(f"   Fetching stats for {len(pending)} video(s)...")
    video_ids = [u["id"] for u in pending if u.get("id")]
    if not video_ids:
        return []

    fresh_stats = _enrich_videos(video_ids)
    stats_by_id = {s["id"]: s for s in fresh_stats}

    # Merge stats back into uploads log
    for u in uploads:
        if u.get("id") in stats_by_id:
            u["stats"] = stats_by_id[u["id"]]
            u["stats_fetched"] = True
            v = stats_by_id[u["id"]]
            print(f"      \"{u['title'][:50]}\": {v['views']:,} views | {v['engagement_rate']}% eng | {v['views_per_day']:,}/day")

    _UPLOADS_LOG.write_text(json.dumps(uploads, indent=2, ensure_ascii=False), encoding="utf-8")

    # Update top performers for self-improving scripts
    _update_top_performers(uploads)

    return fresh_stats


def _update_top_performers(uploads: list):
    """Score all tracked videos and save the top 5 as few-shot examples."""
    scored = []
    for u in uploads:
        if u.get("stats_fetched") and u.get("stats") and u.get("hook") and u.get("script"):
            s = u["stats"]
            # Combined score: velocity weighted by engagement
            perf = s.get("views_per_day", 0) * (1 + s.get("engagement_rate", 0) / 100)
            scored.append({
                "id":               u["id"],
                "title":            u["title"],
                "hook":             u.get("hook", ""),
                "script":           u.get("script", ""),
                "topic":            u.get("topic", ""),
                "views":            s.get("views", 0),
                "engagement_rate":  s.get("engagement_rate", 0),
                "views_per_day":    s.get("views_per_day", 0),
                "performance_score": perf,
            })

    if not scored:
        return

    scored.sort(key=lambda x: x["performance_score"], reverse=True)
    top5 = scored[:5]

    _TOP_PERFORMERS_F.write_text(
        json.dumps({"updated": datetime.now().isoformat(), "performers": top5}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"   Top performer: \"{top5[0]['title'][:50]}\" ({top5[0]['views']:,} views)")
    print(f"   Top performers file updated — scripts will now use real data as examples.")


# ─────────────────────────────────────────────────────────────────
#  COMPETITOR WATCHLIST — alert on new viral videos from tracked channels
# ─────────────────────────────────────────────────────────────────

def watch_competitors(velocity_threshold: int = 5000) -> list:
    """Check all tracked competitors for new videos uploaded in the last 24 hours.

    Returns videos that are already trending (views/day > velocity_threshold).
    These are the topics you should respond to IMMEDIATELY.
    """
    print("   👀 Scanning competitor channels for new viral videos...")
    competitor_ids = load_competitors()
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    alerts = []

    for cid in competitor_ids:
        try:
            videos = get_competitor_top_videos(cid, max_results=10)
            for v in videos:
                if not v.get("published"):
                    continue
                pub = datetime.fromisoformat(v["published"].replace("Z", "+00:00"))
                if pub >= cutoff and v.get("views_per_day", 0) >= velocity_threshold:
                    alerts.append(v)
                    print(f"      🔥 ALERT: \"{v['title'][:55]}\"")
                    print(f"         {v['channel']} | {v['views_per_day']:,}/day | {v['views']:,} total views")
            time.sleep(0.3)
        except Exception:
            continue

    if not alerts:
        print(f"   No new viral competitor videos in last 24hrs (threshold: {velocity_threshold:,}/day)")
    else:
        print(f"\n   {len(alerts)} viral video(s) detected — consider covering these topics NOW")

    # Save alerts
    alert_file = ANALYZER_DIR / "competitor_alerts.json"
    alert_file.write_text(json.dumps({
        "checked": datetime.now().isoformat(),
        "threshold": velocity_threshold,
        "alerts": alerts,
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    return alerts


# ─────────────────────────────────────────────────────────────────
#  REPORT PRINTER
# ─────────────────────────────────────────────────────────────────

def print_report(analysis: dict, my_channel: dict, trending: list, my_videos: list):
    """Print a beautiful terminal report."""
    print()
    print("  " + "═"*60)
    print("  ANALYZER REPORT —", datetime.now().strftime("%d %b %Y, %H:%M"))
    print("  " + "═"*60)

    if my_channel:
        print(f"\n  YOUR CHANNEL: {my_channel['name']}")
        print(f"  Subscribers: {my_channel['subscribers']:,}  |  Total Views: {my_channel['total_views']:,}  |  Videos: {my_channel['video_count']}")

    # Market Pulse
    mp = analysis.get("market_pulse", {})
    print("\n  MARKET PULSE")
    print("  " + "─"*40)
    print(f"  Viral trigger:  {mp.get('viral_trigger', 'N/A')}")
    print(f"  Best format:    {mp.get('best_performing_content_type', 'N/A')}")
    print(f"  Avg engagement: {mp.get('avg_engagement_rate', 'N/A')}")
    print(f"\n  Trending topics right now:")
    for t in mp.get("top_3_trending_topics", []):
        print(f"    + {t}")
    print(f"\n  Hook styles that are working:")
    for h in mp.get("top_3_trending_hook_styles", []):
        print(f"    > {h}")

    # Competitor Intel
    ci = analysis.get("competitor_intelligence", {})
    print("\n  COMPETITOR INTELLIGENCE")
    print("  " + "─"*40)
    print(f"  Their secret:  {ci.get('their_secret', 'N/A')}")
    print(f"  Title patterns:")
    for p in ci.get("title_patterns", []):
        print(f"    - {p}")

    # My Channel
    diag = analysis.get("my_channel_diagnosis", {})
    print("\n  YOUR CHANNEL DIAGNOSIS")
    print("  " + "─"*40)
    print(f"  Best video:    {diag.get('best_performing_video', 'N/A')}")
    print(f"  Retention gap: {diag.get('retention_problem', 'N/A')}")
    print(f"  Gaps to fix:")
    for g in diag.get("my_gaps", []):
        print(f"    ! {g}")

    # Content Opportunities
    opps = analysis.get("content_opportunities", [])
    print("\n  TOP CONTENT OPPORTUNITIES")
    print("  " + "─"*40)
    for opp in opps:
        print(f"\n  #{opp['rank']} [{opp.get('estimated_performance','?').upper()}]  {opp['topic']}")
        print(f"     Why now:  {opp.get('urgency', '')}")
        print(f"     Hook:     \"{opp.get('hook', '')}\"")
        print(f"     Title:    {opp.get('title', '')}")

    # Next Video Brief
    brief = analysis.get("next_video_brief", {})
    print("\n  " + "═"*60)
    print("  NEXT VIDEO BRIEF  [Confidence: {}%]".format(brief.get("confidence_score", "?")))
    print("  " + "═"*60)
    print(f"  TOPIC:   {brief.get('topic', '')}")
    print(f"  HOOK:    \"{brief.get('hook', '')}\"")
    print(f"  TITLE:   {brief.get('title', '')}")
    print(f"  SCRIPT:  {brief.get('script_direction', '')}")
    print(f"  TAGS:    {', '.join(brief.get('tags', []))}")
    print(f"  THUMB:   {brief.get('thumbnail_concept', '')}")

    # Recommendations
    recs = analysis.get("strategic_recommendations", [])
    print("\n  STRATEGIC RECOMMENDATIONS")
    print("  " + "─"*40)
    for r in recs:
        print(f"  >> {r}")

    print()


# ─────────────────────────────────────────────────────────────────
#  MAIN ORCHESTRATOR
# ─────────────────────────────────────────────────────────────────

def run_full_analysis(args) -> dict:
    """Run the complete analysis pipeline."""
    print()
    print("  " + "═"*60)
    print("  YOU — ANALYZER")
    print("  Scanning YouTube. Decoding what works. Building your brief.")
    print("  " + "═"*60)

    trending, competitors, my_videos, my_channel = [], [], [], None

    # 1. Trending analysis
    if not args.mine and not args.brief:
        print("\n  [1/4] Scanning Trending Shorts...")
        try:
            trending = search_trending_shorts(CHANNEL_NICHE, max_results=50)
            print(f"        Found {len(trending)} trending Shorts")
            TREND_DB.write_text(json.dumps({
                "fetched": datetime.now().isoformat(),
                "videos": trending
            }, indent=2))
        except Exception as e:
            print(f"        Warning: Trending scan failed: {e}")

    # 2. Competitor analysis
    if not args.mine and not args.trends and not args.brief:
        print("\n  [2/4] Analyzing Competitors...")
        competitor_ids = load_competitors()

        # Auto-discover more competitors
        discovered = discover_competitors(CHANNEL_NICHE)
        all_ids = list(set(competitor_ids + discovered))[:10]  # Cap at 10
        save_competitors(all_ids)

        for cid in all_ids:
            videos = get_competitor_top_videos(cid, max_results=15)
            competitors.extend(videos)
            if videos:
                print(f"        {videos[0]['channel']}: {len(videos)} videos analyzed")
            time.sleep(0.5)

        print(f"        Total competitor videos analyzed: {len(competitors)}")

    # 2b. Competitor watchlist — check for new viral videos
    if not args.mine and not args.trends and not args.brief:
        print("\n  [2b/4] Competitor Watchlist (last 24hrs)...")
        try:
            alerts = watch_competitors()
            if alerts:
                print(f"        {len(alerts)} viral video(s) spotted — check analyzer/competitor_alerts.json")
        except Exception as e:
            print(f"        Warning: Watchlist failed: {e}")

    # 2c. Feedback loop (if uploads are old enough)
    if not args.mine and not args.trends and not args.brief:
        print("\n  [2c/4] Feedback Loop (48hr stats)...")
        try:
            run_feedback_loop()
        except Exception as e:
            print(f"        Warning: Feedback loop failed: {e}")

    # 3. My channel stats
    print("\n  [3/4] Fetching Your Channel Stats...")
    try:
        my_channel = get_my_channel_id()
        if my_channel:
            print(f"        Channel: {my_channel['name']} ({my_channel['subscribers']:,} subs)")
        my_videos = get_my_video_stats()
        if my_videos:
            print(f"        Your videos analyzed: {len(my_videos)}")
            update_performance_db(my_videos)
        else:
            print("        No videos found yet (or OAuth needs refresh)")
    except Exception as e:
        print(f"        Warning: {e}")

    # 4. LLM pattern analysis
    print("\n  [4/4] Running Intelligence Analysis...")
    try:
        analysis = analyze_patterns(trending, competitors, my_videos)

        # Save brief
        BRIEF_DB.write_text(json.dumps({
            "generated": datetime.now().isoformat(),
            "analysis": analysis,
        }, indent=2))

        # Print report
        print_report(analysis, my_channel, trending, my_videos)

        # Save to output log
        log_path = ANALYZER_DIR / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        log_path.write_text(json.dumps({
            "generated": datetime.now().isoformat(),
            "trending_count": len(trending),
            "competitor_videos_count": len(competitors),
            "my_videos_count": len(my_videos),
            "analysis": analysis,
        }, indent=2))
        print(f"  Report saved: {log_path.name}")

        return analysis

    except Exception as e:
        print(f"\n  Analysis failed: {e}")
        import traceback; traceback.print_exc()
        return {}


def get_latest_brief() -> dict:
    """Load the most recent content brief."""
    if BRIEF_DB.exists():
        try:
            data = json.loads(BRIEF_DB.read_text())
            return data.get("analysis", {}).get("next_video_brief", {})
        except Exception:
            pass
    return {}


# ─────────────────────────────────────────────────────────────────
#  CLI
# ─────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="YOU Analyzer — Intelligence for your YouTube Shorts channel",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
  EXAMPLES:
    python analyzer.py                    Full analysis + content brief
    python analyzer.py --trends           Trending topics only
    python analyzer.py --mine             Your channel stats only
    python analyzer.py --competitors      Competitor analysis only
    python analyzer.py --brief            Show latest saved brief
        """
    )
    parser.add_argument("--trends",      action="store_true", help="Trending topics only")
    parser.add_argument("--mine",        action="store_true", help="Your channel stats only")
    parser.add_argument("--competitors", action="store_true", help="Competitor analysis only")
    parser.add_argument("--brief",       action="store_true", help="Show latest saved brief")
    parser.add_argument("--feedback",    action="store_true", help="Run 48hr feedback loop on uploaded videos")
    parser.add_argument("--watch",       action="store_true", help="Check competitors for new viral videos (last 24hrs)")

    args = parser.parse_args()

    if args.brief:
        brief = get_latest_brief()
        if brief:
            print("\n  LATEST CONTENT BRIEF")
            print("  " + "═"*50)
            print(f"  TOPIC:  {brief.get('topic', 'N/A')}")
            print(f"  HOOK:   \"{brief.get('hook', 'N/A')}\"")
            print(f"  TITLE:  {brief.get('title', 'N/A')}")
            print(f"  SCRIPT: {brief.get('script_direction', 'N/A')}")
            print(f"  CONFIDENCE: {brief.get('confidence_score', '?')}%")
        else:
            print("  No brief found. Run: python analyzer.py")
        return

    if args.feedback:
        print("\n  FEEDBACK LOOP — Pulling 48hr performance stats")
        print("  " + "═"*50)
        stats = run_feedback_loop()
        if stats:
            print(f"\n  Fetched stats for {len(stats)} video(s). Top performers file updated.")
            print("  Next video will use YOUR best-performing scripts as examples.")
        return

    if args.watch:
        print("\n  COMPETITOR WATCHLIST — Last 24 hours")
        print("  " + "═"*50)
        alerts = watch_competitors()
        if alerts:
            print("\n  Run: python you.py \"<topic>\" to cover a trending topic NOW")
        return

    run_full_analysis(args)


if __name__ == "__main__":
    main()
