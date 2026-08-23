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

from config import (YOUTUBE_TOKEN_FILE, BASE_DIR,
                    RETENTION_BACKFILL_AFTER_HOURS, RETENTION_HOOK_SECONDS)

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

    try:
        resp = _query(yta, start, end)
    except Exception as e:
        msg = str(e)
        if "accessNotConfigured" in msg or "has not been used in project" in msg:
            print("❌ The YouTube Analytics API is not enabled for this Google Cloud project.")
            print("   The OAuth scope grants permission, but the API itself must also be")
            print("   switched on for the project (same one-time step as the Data API).")
            print("\n   Enable it here, then retry (allow ~1-2 min to propagate):")
            print("   https://console.developers.google.com/apis/api/"
                  "youtubeanalytics.googleapis.com/overview?project=416897339211")
        elif "insufficient" in msg.lower() or "forbidden" in msg.lower():
            print(f"❌ Access denied by the Analytics API: {msg[:200]}")
        else:
            print(f"❌ Analytics query failed: {msg[:300]}")
        return []

    cols = [h["name"] for h in resp.get("columnHeaders", [])]
    return [dict(zip(cols, row)) for row in resp.get("rows", [])]


def _query(yta, start, end):
    return yta.reports().query(
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


# ── Retention backfill ────────────────────────────────────────────
# The hook is the one thing we could never measure. Views and likes say
# nothing about whether the opening line stopped the scroll; the retention
# curve says it directly. Recording it per video is what lets a future
# hook change be judged on evidence instead of another n=11 guess.
#
# Why this exists (2026-08-23): the old _score_hook gate was validated
# against real 3-second retention and came back r=-0.06 (p=0.86) — it was
# measuring nothing. That check needed 11 usable videos scraped by hand.
# With this running daily, the same question is answerable from the log.

def _retention_curve(yta, vid: str, days: int) -> list:
    """100-point retention curve for one video, or [] if unavailable.

    audienceWatchRatio     — fraction still watching at that point
    relativeRetentionPerformance — 0-1 percentile vs comparable YouTube
                             videos, so it already strips out topic and
                             algorithm luck. This is the honest one.
    """
    from datetime import date as _date
    end = _date.today()
    start = end - timedelta(days=days)
    resp = yta.reports().query(
        ids="channel==MINE",
        startDate=start.isoformat(),
        endDate=end.isoformat(),
        metrics="audienceWatchRatio,relativeRetentionPerformance",
        dimensions="elapsedVideoTimeRatio",
        filters=f"video=={vid}",
    ).execute()
    return resp.get("rows", [])


def backfill_retention(days: int = 90, refresh: bool = False) -> int:
    """Write hook-window retention into feedback/uploaded.json.

    Only touches videos old enough for the curve to have settled
    (RETENTION_BACKFILL_AFTER_HOURS) and not already recorded, so a daily
    run costs one API call per genuinely new video and nothing after that.

    Stores, per video:
      retention.awr_hook  — mean audienceWatchRatio over the first
                            RETENTION_HOOK_SECONDS
      retention.rrp_hook  — mean relativeRetentionPerformance, same window
      retention.rrp_all   — mean relativeRetentionPerformance, whole video
      retention.duration_est_s / points / fetched_at

    rrp_hook is the number to judge hooks on. rrp_all is the baseline it
    should be compared against — a hook is weak when rrp_hook < rrp_all,
    which is exactly the pattern this channel showed (0.47 vs 0.50).
    """
    creds = _creds()
    if not creds:
        return 0
    from googleapiclient.discovery import build
    from datetime import datetime, timezone

    if not UPLOADS_LOG.exists():
        print("   No uploads tracked yet.")
        return 0
    uploads = json.loads(UPLOADS_LOG.read_text(encoding="utf-8"))

    def _age_hours(ts: str) -> float:
        dt = datetime.fromisoformat((ts or "").replace("Z", "+00:00"))
        if dt.tzinfo is None:                      # pre-tz-fix records
            dt = dt.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - dt).total_seconds() / 3600

    pending = []
    for u in uploads:
        if not u.get("id") or not u.get("uploaded_at"):
            continue
        if u.get("retention") and not refresh:
            continue
        try:
            if _age_hours(u["uploaded_at"]) < RETENTION_BACKFILL_AFTER_HOURS:
                continue
        except Exception:
            continue
        pending.append(u)

    if not pending:
        print(f"   Retention: nothing new to record "
              f"(videos become eligible at {RETENTION_BACKFILL_AFTER_HOURS}h).")
        return 0

    yta = build("youtubeAnalytics", "v2", credentials=creds)
    print(f"   Retention: recording {len(pending)} video(s)...")
    done = 0
    for u in pending:
        vid = u["id"]
        try:
            rows = _retention_curve(yta, vid, days)
        except Exception as e:
            print(f"      ⚠️  {vid}: {str(e)[:100]}")
            continue
        if len(rows) < 20:
            # Too few views for YouTube to release a curve. Leave the record
            # untouched so it retries once the video picks up more views.
            print(f"      ·  {vid}: no curve yet ({len(rows)} points)")
            continue

        # elapsedVideoTimeRatio is a FRACTION of duration, so the hook window
        # has to be converted per video. word_count is the only length signal
        # in the log; /2.5 wps + ~3s of padding matched measured duration to
        # within 1-3s when checked against AVD/retention on 2026-08-23.
        wc = u.get("word_count") or 0
        dur = (wc / 2.5 + 3.0) if wc else 0.0
        frac = (RETENTION_HOOK_SECONDS / dur) if dur > 0 else 0.10
        frac = min(max(frac, 0.02), 0.5)

        early = [r for r in rows if r[0] <= frac] or rows[:max(2, len(rows) // 10)]

        # Thirds cost nothing extra (same rows) and are what actually locate
        # the weak stretch. Recorded because the first n=60 read showed the
        # hook is the STRONGEST third, not the weakest — see LESSONS.md.
        n3 = max(1, len(rows) // 3)
        thirds = [round(sum(r[2] for r in rows[i:i + n3]) / len(rows[i:i + n3]), 4)
                  for i in (0, n3, 2 * n3) if rows[i:i + n3]]

        u["retention"] = {
            "awr_hook": round(sum(r[1] for r in early) / len(early), 4),
            "rrp_hook": round(sum(r[2] for r in early) / len(early), 4),
            "rrp_all":  round(sum(r[2] for r in rows) / len(rows), 4),
            "rrp_thirds": thirds,
            "hook_window_s": RETENTION_HOOK_SECONDS,
            "duration_est_s": round(dur, 1) if dur else None,
            "points": len(rows),
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }
        r = u["retention"]
        flag = "  ← weak hook" if r["rrp_hook"] < r["rrp_all"] else ""
        print(f"      ✅ {vid}  rrp_hook={r['rrp_hook']:.2f}  "
              f"rrp_all={r['rrp_all']:.2f}  awr@{RETENTION_HOOK_SECONDS:g}s={r['awr_hook']:.2f}{flag}")
        done += 1

    if done:
        UPLOADS_LOG.write_text(json.dumps(uploads, indent=2, ensure_ascii=False),
                               encoding="utf-8")
    print(f"   Retention: {done} video(s) recorded.")
    return done


def main() -> int:
    ap = argparse.ArgumentParser(description="YOU — retention analytics")
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--backfill", action="store_true",
                    help="Record per-video hook retention into feedback/uploaded.json and exit")
    ap.add_argument("--refresh", action="store_true",
                    help="With --backfill: re-fetch videos already recorded")
    args = ap.parse_args()

    if args.backfill:
        backfill_retention(days=max(args.days, 90), refresh=args.refresh)
        return 0

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
