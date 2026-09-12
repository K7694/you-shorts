#!/usr/bin/env python3
"""
YOU — weekly REPORT.md

The one page the owner reads. Every falsifier from PLAN_2026_09_06.md gets
its current number next to it, so the weekly 20 minutes is "did anything
fire?" and nothing else.

Why this exists (2026-09-12): a green CI run only proves the job exited 0.
The retention backfill failed silently for 14 days across 14 green runs
because nothing read its OUTPUT. This report reads outputs — cohorts,
coverage, delays, archive hits — not statuses.

Usage:
    python report.py            # writes REPORT.md, prints it
    python report.py --quiet    # writes only
Runs Sundays from longform.yml before the long-form build; the state
step commits REPORT.md.
"""

import argparse
import json
import re
import statistics as st
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path

import config
from config import BASE_DIR

UPLOADS = BASE_DIR / "feedback" / "uploaded.json"
LONGFORM = BASE_DIR / "feedback" / "longform.json"
GEO = BASE_DIR / "analyzer" / "geo.json"
OUT = BASE_DIR / "REPORT.md"
WORKFLOW = BASE_DIR / ".github" / "workflows" / "create_video.yml"

UTC = timezone.utc


# ── helpers ───────────────────────────────────────────────────────

def _load(p: Path, default):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return default


def _ts(s: str) -> datetime | None:
    if not s:
        return None
    try:
        d = datetime.fromisoformat(s.replace("Z", "+00:00"))
        return d if d.tzinfo else d.replace(tzinfo=UTC)
    except Exception:
        return None


def _med(v):
    return st.median(v) if v else 0


def _gh_json(args: list) -> list | dict | None:
    try:
        r = subprocess.run(["gh", *args], capture_output=True, text=True, timeout=60)
        return json.loads(r.stdout) if r.returncode == 0 and r.stdout.strip() else None
    except Exception:
        return None


def _milestone(name: str) -> datetime | None:
    """Dates the owner-flagged changes went live; None = not started."""
    ms = getattr(config, "MILESTONES", {}) or {}
    v = ms.get(name)
    return _ts(v if isinstance(v, str) and "T" in v else (f"{v}T00:00:00+00:00" if v else ""))


# ── sections ──────────────────────────────────────────────────────

def channel_totals() -> dict:
    try:
        import analytics
        creds = analytics._creds()
        from googleapiclient.discovery import build
        yt = build("youtube", "v3", credentials=creds)
        c = yt.channels().list(part="statistics", mine=True).execute()["items"][0]["statistics"]
        return {"subs": int(c.get("subscriberCount", 0)), "views": int(c.get("viewCount", 0)),
                "videos": int(c.get("videoCount", 0))}
    except Exception as e:
        return {"error": str(e)[:80]}


def cohorts(uploads: list, lf_ids: set) -> dict:
    """48h-cohort views: last 30 uploads vs the 30 before — the only honest
    like-for-like. Lifetime totals favour old videos."""
    have = [u for u in uploads
            if u.get("stats_fetched") and (u.get("stats") or {}).get("views") is not None
            and u.get("uploaded_at") and u.get("id") not in lf_ids]
    have.sort(key=lambda u: u["uploaded_at"])
    last, prior = have[-30:], have[-60:-30]
    def stats(g):
        v = [u["stats"]["views"] for u in g]
        return {"n": len(v), "median": _med(v), "mean": (st.mean(v) if v else 0),
                "ge50": sum(1 for x in v if x >= 50), "max": max(v) if v else 0,
                "from": g[0]["uploaded_at"][:10] if g else "", "to": g[-1]["uploaded_at"][:10] if g else ""}
    return {"last": stats(last), "prior": stats(prior),
            "recent": [(u["uploaded_at"][:10], u["stats"]["views"], u.get("series") or u.get("archetype", ""))
                       for u in have[-10:]]}


def cohort_split(uploads: list, lf_ids: set, at: datetime, n: int = 30) -> dict | None:
    """The falsifier test: 48h median of the n uploads after `at` vs the n
    immediately before. Ratio < 0.53 fires (the 1.88x detectable bar)."""
    have = [u for u in uploads
            if u.get("stats_fetched") and (u.get("stats") or {}).get("views") is not None
            and _ts(u.get("uploaded_at")) and u.get("id") not in lf_ids]
    have.sort(key=lambda u: u["uploaded_at"])
    pre = [u for u in have if _ts(u["uploaded_at"]) < at][-n:]
    post = [u for u in have if _ts(u["uploaded_at"]) >= at][:n]
    if not pre or not post:
        return None
    pm, qm = _med([u["stats"]["views"] for u in pre]), _med([u["stats"]["views"] for u in post])
    return {"pre_n": len(pre), "pre_med": pm, "post_n": len(post), "post_med": qm,
            "ratio": (qm / pm) if pm else None, "complete": len(post) >= n}


def analytics_30d(lf_ids: set) -> dict:
    try:
        import analytics
        rows = analytics.fetch(30)
    except Exception as e:
        return {"error": str(e)[:80]}
    sh = [r for r in rows if r.get("video") not in lf_ids]
    lf = [r for r in rows if r.get("video") in lf_ids]
    tv = sum(int(r.get("views", 0)) for r in sh)
    ts_ = sum(int(r.get("subscribersGained", 0)) for r in sh)
    lv = sum(int(r.get("views", 0)) for r in lf)
    lh = sum(int(r.get("views", 0)) * r.get("averageViewDuration", 0) / 3600 for r in lf)
    return {"shorts_views": tv, "subs": ts_, "subs_per_1k": (ts_ / tv * 1000) if tv else 0,
            "lf_views": lv, "lf_hours": lh}


def retention(uploads: list) -> dict:
    now = datetime.now(UTC)
    elig = [u for u in uploads if u.get("id") and _ts(u.get("uploaded_at"))
            and (now - _ts(u["uploaded_at"])).total_seconds() / 3600 >= config.RETENTION_BACKFILL_AFTER_HOURS]
    rec = [u for u in elig if u.get("retention")]
    latest = sorted(rec, key=lambda u: u["uploaded_at"])[-30:]
    thirds = [u["retention"]["rrp_thirds"] for u in latest
              if len((u.get("retention") or {}).get("rrp_thirds") or []) == 3]
    return {"eligible": len(elig), "recorded": len(rec),
            "thirds": [round(st.mean(t[i] for t in thirds), 3) for i in range(3)] if thirds else None,
            "rrp_all": round(st.mean(u["retention"]["rrp_all"] for u in latest), 3) if latest else None,
            "n_curve": len(thirds)}


def pipeline(uploads: list) -> dict:
    runs = _gh_json(["run", "list", "--workflow=create_video.yml", "--limit", "14",
                     "--json", "conclusion,event,createdAt"]) or []
    # nominal first cron in the workflow → measured queue delay. Only runs
    # since the cron was last changed count; comparing older runs against
    # the new nominal time produces a meaningless 9h figure.
    delay = []
    since = _milestone("cron_shift")
    try:
        m = re.search(r"cron:\s*'(\d+)\s+(\d+)\s", WORKFLOW.read_text(encoding="utf-8"))
        nm, nh = int(m.group(1)), int(m.group(2))
        for r in runs:
            if r.get("event") != "schedule":
                continue
            t = _ts(r["createdAt"])
            if since and t <= since + timedelta(days=1):
                continue
            mins = (t.hour * 60 + t.minute) - (nh * 60 + nm)
            if mins < 0:
                mins += 24 * 60
            delay.append(mins)
    except Exception:
        pass
    recent = sorted([u for u in uploads if u.get("uploaded_at")], key=lambda u: u["uploaded_at"])[-30:]
    archived = sum(1 for u in recent if u.get("render_url"))
    since_archive = [u for u in recent if "render_url" in u]   # field exists only after 2026-09-12
    return {"runs": [(r["createdAt"][:10], r["conclusion"], r["event"]) for r in runs[:7]],
            "fail7": sum(1 for r in runs[:7] if r.get("conclusion") != "success"),
            "delay_min": (min(delay), _med(delay), max(delay)) if delay else None,
            "archived": archived, "archive_expected": len(since_archive)}


def geography() -> dict:
    g = _load(GEO, {})
    return {"summary": g.get("summary"), "top": g.get("countries", [])[:5],
            "fetched": (g.get("fetched_at") or "")[:10]}


def longform_recent(lf: list) -> list:
    return sorted(lf, key=lambda x: x.get("uploaded_at", ""))[-3:]


# ── falsifiers ────────────────────────────────────────────────────

def falsifiers(uploads, lf_ids, an, ret, pipe) -> list:
    rows = []
    def cohort_row(fid, claim, milestone, checkpoint):
        at = _milestone(milestone)
        if not at:
            return (fid, claim, checkpoint, "—", "not started")
        s = cohort_split(uploads, lf_ids, at)
        if not s:
            return (fid, claim, checkpoint, "no data yet", "watching")
        num = f"{s['post_med']:.0f} vs {s['pre_med']:.0f} (×{s['ratio']:.2f}, n={s['post_n']}/30)"
        if not s["complete"]:
            return (fid, claim, checkpoint, num, "watching")
        return (fid, claim, checkpoint, num, "**FIRED**" if s["ratio"] is not None and s["ratio"] < 0.53 else "held")
    rows.append(cohort_row("F1", "2×/day does not halve per-video reach", "cadence_2x", "30 videos post-switch"))
    rows.append(cohort_row("F2", "CTA overlay does not repeat May", "cta_on", "30 videos post-overlay"))
    rows.append(("F3", "The kit is sellable", "30 d post-launch", "sales not tracked here",
                 "not started" if not _milestone("kit_launch") else "manual (Gumroad CSV)"))
    rows.append(("F4", "Clone reaches like the original", "clone week 8", "other repo",
                 "not started" if not _milestone("clone_launch") else "see clone REPORT.md"))
    lf3 = an.get("lf_views", 0)
    rows.append(("F5", "Compilations get watched", "after 3 monthly uploads",
                 f"long-form 30d views {lf3}", "not started" if not _milestone("compilation_1") else "watching"))
    rows.append(("F6", "Meta reach worth the engineering", "day 60", "not live",
                 "not started" if not _milestone("meta_live") else "watching"))
    rows.append(("F7", "Portfolio can become income", "month 6", "cash not tracked here", "manual"))
    rows.append(("F8", "No termination exposure", "continuous",
                 f"CI failures last 7: {pipe['fail7']}", "manual — check Studio for notices"))
    rows.append(("F9", "Affiliate accounts survive", "day 150 per account", "n/a", "not started"))
    return rows


# ── render ────────────────────────────────────────────────────────

def build() -> str:
    uploads = _load(UPLOADS, [])
    lf = _load(LONGFORM, [])
    lf_ids = {x.get("id") for x in lf}
    tot = channel_totals()
    co = cohorts(uploads, lf_ids)
    an = analytics_30d(lf_ids)
    ret = retention(uploads)
    pipe = pipeline(uploads)
    geo = geography()
    now = datetime.now(UTC)

    L = []
    L.append(f"# YOU — Weekly Report · {now:%Y-%m-%d %H:%M} UTC\n")
    L.append("Read the **Falsifiers** table first. Everything else is context.\n")

    L.append("## Channel")
    if "error" in tot:
        L.append(f"- totals unavailable: `{tot['error']}`")
    else:
        L.append(f"- **{tot['subs']} subs** · {tot['views']:,} views · {tot['videos']} videos (lifetime)")
    if "error" not in an:
        L.append(f"- last 30 d Shorts: **{an['shorts_views']:,} views** · {an['subs']} subs · "
                 f"**{an['subs_per_1k']:.2f} subs/1k**")
    L.append("")

    L.append("## Shorts — views at 48 h (equal-age cohorts)")
    a, b = co["last"], co["prior"]
    L.append("| cohort | n | median | mean | ≥50 | max | window |")
    L.append("|---|---|---|---|---|---|---|")
    L.append(f"| last 30 | {a['n']} | **{a['median']:.0f}** | {a['mean']:.0f} | {a['ge50']} | {a['max']} | {a['from']} → {a['to']} |")
    L.append(f"| prior 30 | {b['n']} | {b['median']:.0f} | {b['mean']:.0f} | {b['ge50']} | {b['max']} | {b['from']} → {b['to']} |")
    if b["median"]:
        L.append(f"\nlast/prior median ratio: **×{a['median']/b['median']:.2f}** "
                 f"(the falsifier bar is ×0.53; anything between 0.53 and 1.88 is noise at n=30)")
    L.append("\nlast 10 uploads: " + " · ".join(f"{d[5:]} **{v}** {s[:12]}" for d, v, s in co["recent"]))
    L.append("")

    L.append("## Geography (90 d)")
    if geo["summary"]:
        s = geo["summary"]
        L.append(f"- top: **{s['top_country']}** · US+UK+CA+AU **{s['us_uk_ca_au_pct']}%** · India {s['india_pct']}% · fetched {geo['fetched']}")
        L.append("- " + " · ".join(f"{c['country']} {c['views_pct']}%" for c in geo["top"]))
    else:
        L.append("- not fetched — run `python analytics.py --geo`")
    L.append("")

    L.append("## Retention (peer-relative, 0.50 = median comparable video)")
    L.append(f"- recorded **{ret['recorded']} / {ret['eligible']}** eligible (≥{config.RETENTION_BACKFILL_AFTER_HOURS:.0f} h old)")
    if ret["thirds"]:
        t = ret["thirds"]
        L.append(f"- last 30 recorded: opening {t[0]} · middle **{t[1]}** · final {t[2]} · overall {ret['rrp_all']} (n={ret['n_curve']})")
    L.append("")

    L.append("## Long-form")
    L.append(f"- {len(lf)} uploads · 30 d: {an.get('lf_views', 0)} views · **{an.get('lf_hours', 0):.1f} watch-hours** (of 4,000)")
    for x in longform_recent(lf):
        L.append(f"  - {x.get('uploaded_at','')[:10]} {x.get('title','')[:50]}")
    L.append("")

    L.append("## Pipeline")
    L.append("- CI last 7: " + " · ".join(f"{d[5:]} {'✅' if c=='success' else '❌ '+str(c)}{'' if e=='schedule' else ' (manual)'}" for d, c, e in pipe["runs"]))
    if pipe["delay_min"]:
        lo, md, hi = pipe["delay_min"]
        L.append(f"- scheduled start delay vs nominal cron: min {lo//60}h{lo%60:02d} · median **{int(md)//60}h{int(md)%60:02d}** · max {hi//60}h{hi%60:02d}")
    else:
        L.append("- scheduled start delay: no scheduled runs since the cron shift yet (measures from the day after `MILESTONES.cron_shift`)")
    L.append(f"- render archive: **{pipe['archived']} / {pipe['archive_expected']}** of records since the archive shipped have a URL")
    L.append(f"- LLM chain: {' → '.join(p['name'] for p in config.LLM_PROVIDERS)} (Cerebras 402 — billing; probe at session open)")
    L.append("")

    L.append("## Falsifiers")
    L.append("| ID | claim | checkpoint | current | status |")
    L.append("|---|---|---|---|---|")
    for fid, claim, cp, num, status in falsifiers(uploads, lf_ids, an, ret, pipe):
        L.append(f"| {fid} | {claim} | {cp} | {num} | {status} |")
    L.append("")
    L.append("Milestone dates live in `config.MILESTONES`; a falsifier starts watching the day its milestone is set.")
    L.append("")
    L.append("## Not live yet")
    L.append("- Meta reach (Phase 4) · Kit sales (Phase 7) · Clone (Phase 6)")
    return "\n".join(L) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="YOU — weekly REPORT.md")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    md = build()
    OUT.write_text(md, encoding="utf-8")
    if not args.quiet:
        print(md)
    print(f"→ wrote {OUT.name} ({len(md.splitlines())} lines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
