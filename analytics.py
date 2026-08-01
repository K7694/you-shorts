#!/usr/bin/env python3
"""
YOU — retention analytics (the metric the algorithm actually ranks on)

The Data API only exposes views/likes. YouTube ranks Shorts primarily on
swipe-away in the first seconds and completion rate, and we could never see
either — so we've been optimising a proxy and could never explain WHY a
video flopped. Those numbers live in the ANALYTICS API.

It also reports subscribersGained PER VIDEO, which finally answers the
question the whole channel hinges on: which videos actually convert.

REQUIRES the yt-analytics.readonly scope (read-only). One-time setup:
    del youtube_token.json
    python auth_youtube.py            # grants the new scope too
    gh secret set YOUTUBE_TOKEN_JSON < youtube_token.json

you.py deliberately still requests only its two upload scopes, so the daily
pipeline keeps working both before and after that re-auth (a token may hold
more scopes than the code asks for — never fewer).

Usage:
    python analytics.py            # last 30 days, per video
    python analytics.py --days 60
"""

import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path

from config import YOUTUBE_TOKEN_FILE, BASE_DIR

ANALYTICS_SCOPE = "https://www.googleapis.com/auth/yt-analytics.readonly"
UPLOADS_LOG = BASE_DIR / "feedback" / "uploaded.json"


def _creds():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request

    if not Path(YOUTUBE_TOKEN_FILE).exists():
        print("❌ youtube_token.json not found — run: python auth_youtube.py")
        return None

    info = json.loads(Path(YOUTUBE_TOKEN_FILE).read_text(encoding="utf-8"))
    granted = info.get("scopes", [])
    if ANALYTICS_SCOPE not in granted:
        print("❌ Token lacks the analytics scope, so retention data is unavailable.")
        print("   Granted scopes:")
        for s in granted:
            print(f"     - {s}")
        print("\n   One-time fix (safe — the daily pipeline keeps running):")
        print("     del youtube_token.json")
        print("     python auth_youtube.py")
        print("     gh secret set YOUTUBE_TOKEN_JSON < youtube_token.json")
        return None

    creds = Credentials.from_authorized_user_info(info, granted)
    if not creds.valid and creds.refresh_token:
        creds.refresh(Request())
    return creds


def fetch(days: int = 30) -> list:
    creds = _creds()
    if not creds:
        return []
    from googleapiclient.discovery import build

    yta = build("youtubeAnalytics", "v2", credentials=creds)
    end = date.today()
    start = end - timedelta(days=days)

    resp = yta.reports().query(
        ids="channel==MINE",
        startDate=start.isoformat(),
        endDate=end.isoformat(),
        # averageViewPercentage IS the retention signal; subscribersGained
        # attributes conversion to the individual video.
        metrics=("views,averageViewDuration,averageViewPercentage,"
                 "subscribersGained,likes,shares"),
        dimensions="video",
        sort="-views",
        maxResults=200,
    ).execute()

    cols = [h["name"] for h in resp.get("columnHeaders", [])]
    return [dict(zip(cols, row)) for row in resp.get("rows", [])]


def main() -> int:
    ap = argparse.ArgumentParser(description="YOU — retention analytics")
    ap.add_argument("--days", type=int, default=30)
    args = ap.parse_args()

    rows = fetch(args.days)
    if not rows:
        return 1

    # Enrich with our own metadata (series/archetype) where we have it
    meta = {}
    try:
        for u in json.loads(UPLOADS_LOG.read_text(encoding="utf-8")):
            meta[u.get("id", "")] = u
    except Exception:
        pass

    print(f"\n=== LAST {args.days} DAYS — per video ===")
    print(f"{'video':13}{'views':>7}{'AVD':>6}{'ret%':>7}{'subs':>6}  series / title")
    print("-" * 78)
    for r in rows[:30]:
        vid = r.get("video", "")
        m = meta.get(vid, {})
        label = m.get("series") or m.get("archetype") or ""
        print(f"{vid:13}{int(r.get('views',0)):>7}"
              f"{int(r.get('averageViewDuration',0)):>5}s"
              f"{r.get('averageViewPercentage',0):>6.1f}%"
              f"{int(r.get('subscribersGained',0)):>6}  {label}")

    tv = sum(int(r.get("views", 0)) for r in rows)
    ts = sum(int(r.get("subscribersGained", 0)) for r in rows)
    avg_ret = (sum(r.get("averageViewPercentage", 0) * int(r.get("views", 0)) for r in rows)
               / tv) if tv else 0
    print("-" * 78)
    print(f"totals: {tv:,} views · {ts} subs gained · view-weighted retention {avg_ret:.1f}%")
    print(f"        {ts/tv*1000:.2f} subs per 1k views" if tv else "")

    # Retention is the actual ranking input — call out the extremes so the
    # next content change is aimed at a cause, not a guess.
    ranked = [r for r in rows if int(r.get("views", 0)) >= 50]
    if len(ranked) >= 4:
        ranked.sort(key=lambda r: r.get("averageViewPercentage", 0), reverse=True)
        print("\nBEST retention:")
        for r in ranked[:3]:
            print(f"  {r.get('averageViewPercentage',0):>5.1f}%  {r.get('video')}  "
                  f"{meta.get(r.get('video',''),{}).get('series','')}")
        print("WORST retention:")
        for r in ranked[-3:]:
            print(f"  {r.get('averageViewPercentage',0):>5.1f}%  {r.get('video')}  "
                  f"{meta.get(r.get('video',''),{}).get('series','')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
