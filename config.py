"""
╔══════════════════════════════════════════════════════════════╗
║                  YOU — Configuration                         ║
║        Curiosity Science Channel · Faceless Shorts           ║
║                                                              ║
║   RESET (2026-05-31) — see RESET_BUILD_SPEC.md:              ║
║     Reverted from AI-affiliate content (failed: 10 avg      ║
║     views, $0) back to Phase 0 curiosity science (worked:   ║
║     312 avg views). Monetization is OFF via the             ║
║     MONETIZATION_ENABLED kill-switch below; affiliate code  ║
║     is dormant, not deleted.                                ║
║                                                              ║
║   PRODUCTION COST: ₹0 — Everything is free.                  ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
from pathlib import Path

# ── Auto-add ffmpeg to PATH (handles fresh WinGet installs before shell restart) ──
_FFMPEG_CANDIDATES = [
    r"C:\ffmpeg\bin",
    str(Path.home() / r"AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1-full_build\bin"),
    str(Path.home() / r"AppData\Local\Microsoft\WinGet\Links"),
]
for _d in _FFMPEG_CANDIDATES:
    if Path(_d).exists() and _d not in os.environ.get("PATH", ""):
        os.environ["PATH"] = _d + os.pathsep + os.environ.get("PATH", "")
        break

# ── Load .env for local runs ─────────────────────────────────
# CI supplies these as real environment variables (from GitHub Secrets);
# locally they live in .env. Without this, running any entrypoint directly
# gets EMPTY keys and every provider is silently skipped — which surfaces
# as the very confusing "All LLMs failed:" with an empty error list.
# Existing environment variables always win, so CI is unaffected.
_ENV_FILE = Path(__file__).parent / ".env"
if _ENV_FILE.exists():
    for _line in _ENV_FILE.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if not _line or _line.startswith("#") or "=" not in _line:
            continue
        _k, _v = _line.split("=", 1)
        os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))

# ── Directories ──────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
TEMP_DIR = BASE_DIR / "temp"
ASSETS_DIR = BASE_DIR / "assets"

for d in [OUTPUT_DIR, TEMP_DIR, ASSETS_DIR]:
    d.mkdir(exist_ok=True)

# ══════════════════════════════════════════════════════════════
#  🔴 YOU MUST CHANGE THESE 2 THINGS
# ══════════════════════════════════════════════════════════════

# 1. Your free Gemini API key
#    Get it here (30 sec): https://aistudio.google.com/apikey
#    Set via environment variable:  set GEMINI_API_KEY=your-key-here
#    (Or in GitHub Actions, add as a repository Secret)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# 1b. Your free Groq API key (backup — used when Gemini is rate-limited)
#     Get it here (30 sec): https://console.groq.com → API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# ── PRIMARY LLM (2026-06-20) ───────────────────────────────────
# This account's Gemini free tier returns 429 RESOURCE_EXHAUSTED on
# every call (zero generation quota — likely a Workspace/region limit),
# so Groq is the reliable primary. Gemini stays in the chain as a
# fail-fast fallback. The DAY a key with real Gemini quota appears,
# flip this to "gemini" (one line) and it upgrades automatically.
LLM_PRIMARY = "groq"   # "groq" | "gemini"

# 1c. YouTube Data API key (for the Analyzer — reading YouTube data)
YOUTUBE_DATA_API_KEY = os.getenv("YOUTUBE_DATA_API_KEY", "")

# 1d. Pexels API key (FREE — for stock visuals).
#     RESET (2026-06-06): Pollinations.ai's free image gen monetized
#     (returns HTTP 402), so the per-beat visuals now come from Pexels
#     stock photos. Get a free key in 30s: https://www.pexels.com/api/
#     Set via env / GitHub Secret:  PEXELS_API_KEY=your-key
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")

# Visual source for the per-beat slideshow:
#   "pexels"       → free stock photos (current, reliable, $0)
#   "pollinations" → legacy AI image gen (DEAD: now paid / 402)
IMAGE_SOURCE = "pexels"

# ── A/B TEST: photos vs video clips (started 2026-07-06) ────────
# Variant A ("photos"): 5 Pexels stock photos + Ken Burns pan-zoom
#   — the proven recipe (344 avg views, 71% hit-rate).
# Variant B ("videos"): 5 Pexels stock VIDEO clips trimmed to one
#   script beat each — real motion footage, higher production value.
# Assignment is deterministic by day-of-year parity (even=photos,
# odd=videos) so CI needs no state and variants interleave daily.
# Each upload is tagged "visual_variant" in feedback/uploaded.json.
# READOUT: after ≥6 videos per arm (~2 weeks), compare median views
# at equal 72h age by variant. Same Pexels key, still $0.
AB_VISUAL_TEST = True

# 2. What is your channel about? Be SPECIFIC.
#    RESET (2026-05-31): reverted to the curiosity niche that worked in
#    Phase 0 (312 avg views/video). This drives both the analyzer brief
#    and the curiosity script generator.
CHANNEL_NICHE = "mind-blowing science and curiosity facts — space, physics, the universe, how things work, unsolved mysteries, psychology, and counterintuitive truths that make you see reality differently"

# ══════════════════════════════════════════════════════════════
#  🟡 OPTIONAL — Customize these later
# ══════════════════════════════════════════════════════════════

# Tone of narration
CONTENT_TONE = "awe-inspiring, cinematic, and slightly ominous — like a movie-trailer narrator revealing a secret of the universe that makes you question everything"

# Language
LANGUAGE = "English"

# Video duration target (YouTube Shorts max = 60s)
TARGET_DURATION = 35  # seconds (shorter = higher completion rate)
WORDS_PER_SECOND = 2.8

# Voice — run `python you.py --voices` to see all options
# Popular picks:
#   en-US-ChristopherNeural  → deep male (facts/science)
#   en-US-GuyNeural          → casual male
#   en-US-JennyNeural        → friendly female
#   en-US-AriaNeural         → professional female
#   en-GB-RyanNeural         → British male
#   hi-IN-MadhurNeural       → Hindi male
#   hi-IN-SwaraNeural        → Hindi female
VOICE = "en-US-AndrewMultilingualNeural"
VOICE_RATE = "+5%"
# Wall-clock cap on one TTS synthesis. A stalled Edge TTS stream once hung a
# build indefinitely; in the unattended weekly job that burns the whole
# timeout. Generous enough for a ~250-word long-form segment.
TTS_TIMEOUT_SEC = 180

# Video dimensions (9:16 vertical for Shorts)
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
# 30fps is plenty for an image slideshow with pan-zoom (no fast motion)
# and roughly halves render time on free GitHub Actions runners.
VIDEO_FPS = 30

# Number of AI images per video (more = more visual variety)
IMAGES_PER_VIDEO = 5

# Caption styling
CAPTION_FONT = "Impact"
CAPTION_SIZE = 82
CAPTION_WORDS_PER_LINE = 3

# AI image style suffix.
# RESET (2026-05-31): reverted from the affiliate "tech UI / software
# screenshot" look back to Phase 0's cinematic science aesthetic — the
# style that pulled 312 avg views/video.
IMAGE_STYLE = "dark cinematic, high contrast, deep blues and purples, hyper-realistic, dramatic volumetric lighting, cosmic and microscopic scales, awe-inspiring, 4k, no text"

# Batch size (how many videos per run)
BATCH_SIZE = 1

# Background music (dark ambient, auto-generated via FFmpeg)
BGM_ENABLED = True
BGM_VOLUME = 0.12  # Volume relative to voiceover (0.0-1.0, subtle at 12%)

# ══════════════════════════════════════════════════════════════
#  🟣 GAMEPLAY/BACKGROUND VIDEO OVERLAY
# ══════════════════════════════════════════════════════════════
# RESET (2026-05-31): the static Subway Surfers brainrot loop is OFF.
# Setting this False re-enables Phase 0's per-beat AI image slideshow
# (Pollinations.ai, free) with Ken Burns pan-zoom — the visual layer
# that worked. The gameplay path is kept intact for easy A/B later.
USE_BACKGROUND_VIDEO = False
BACKGROUND_VIDEO_FILE = str(ASSETS_DIR / "subway_surfers_1hr_gameplay.mp4")
BACKGROUND_VIDEO_VOLUME = 0.0   # Mute gameplay audio — keeps voiceover clean

# ══════════════════════════════════════════════════════════════
#  🧑 AI MASCOT (channel host character)
#  When USE_MASCOT_OVERLAY=True, AI images show this same
#  character in every scene. Combined with USE_BACKGROUND_VIDEO,
#  the layout becomes 50/50 split: mascot on top, brainrot on
#  bottom — like a Twitch streamer's face-cam over gameplay.
# ══════════════════════════════════════════════════════════════
USE_MASCOT_OVERLAY = False  # Disabled — running brainrot-only for the week-long test

# The character — Pixar-style 3D animated tech entrepreneur.
# Prepended to EVERY image prompt so the same character appears
# across all 5 scenes within a video. Builds brand recognition.
CHANNEL_MASCOT = (
    "ARIA — a friendly Pixar-style 3D animated young woman in her late 20s, "
    "South Asian, shoulder-length wavy black hair, round translucent glasses, "
    "wearing a soft orange oversized hoodie, expressive warm brown eyes, "
    "subtle confident smile. Modern minimalist home office setting. "
    "Bright warm cinematic lighting, shallow depth of field. "
    "IMPORTANT: this is the SAME consistent character in every scene of the video."
)

# ══════════════════════════════════════════════════════════════
#  🟢 YOUTUBE UPLOAD (set up when ready)
# ══════════════════════════════════════════════════════════════
# Videos save locally by default. To enable auto-upload:
# 1. https://console.cloud.google.com → create project
# 2. Enable "YouTube Data API v3"
# 3. Create OAuth 2.0 credentials (Desktop App)
# 4. Download JSON → save as client_secrets.json here

YOUTUBE_SECRETS_FILE = str(BASE_DIR / "client_secrets.json")
YOUTUBE_TOKEN_FILE = str(BASE_DIR / "youtube_token.json")
YOUTUBE_PRIVACY = "public"   # Live — videos go to public channel feed for real metrics   # ⚠️ Change to "public" when ready to launch!
YOUTUBE_CATEGORY = "28"      # 28 = Science & Technology
YOUTUBE_DEFAULT_TAGS = ["shorts", "science", "space", "facts", "did you know", "mindblown", "universe", "physics", "curiosity"]
YOUTUBE_MADE_FOR_KIDS = False

# Autopilot interval (minutes between videos)
AUTOPILOT_INTERVAL = 360  # 6 hours

# ══════════════════════════════════════════════════════════════
#  💰 AFFILIATE CONFIGURATION
# ══════════════════════════════════════════════════════════════
#
# ── RESET (2026-05-31): MONETIZATION KILL-SWITCH ───────────────
# The affiliate pivot collapsed distribution (Phase 0 science:
# 312 avg views; Phase 1 affiliate: 10.5 avg, $0 earned). Per
# RESET_BUILD_SPEC.md we revert to pure curiosity content and turn
# ALL monetization OFF. The affiliate code below is NOT deleted —
# it's left dormant so it can be revived later (only after the
# channel proves it can distribute again — see spec Phase D / Week 8).
#
# When False (current): no program selection, no pinned comment,
#   no URL overlay, no FTC/disclosure text — nothing affiliate
#   touches the live render/upload path.
# When True: the legacy product-first flow returns.
MONETIZATION_ENABLED = False

# Replace YOUR_ID with your actual affiliate IDs after signing up.
# Sign up links are in the "New Pivot for Money.md" document.

AFFILIATE_LINKS = {
    # ── ACTIVE (IDs filled in) ─────────────────────────────────
    "systeme":     "https://systeme.io/?sa=026901352",                  # 60% lifetime recurring ✅
    "beehiiv":     "https://www.beehiiv.com/?via=rajan-kale",           # 50% recurring 12 mo ✅
    "elevenlabs":  "https://try.elevenlabs.io/llb0lne6yo43",            # 22% recurring 12 mo ✅
    "submagic":    "https://www.submagic.co/?via=rajan44",              # 30% lifetime recurring ✅
    "fliki":       "https://fliki.ai/?via=rajan-kale",                  # 30% lifetime recurring ✅

    # ── PENDING (no code yet / waiting list) ───────────────────
    # Leave as YOUR_ID — these are NOT featured by the pipeline
    # until filled in AND added to PRIORITY_PROGRAMS below.
    "pictory":     "https://pictory.ai/?ref=YOUR_ID",       # 20-50% lifetime recurring
    "heygen":      "https://www.heygen.com/?sid=YOUR_ID",   # 35% recurring 3 mo
    "opusclip":    "https://www.opus.pro/?via=YOUR_ID",     # 25% recurring 12 mo
    "kit":         "https://kit.com/?via=YOUR_ID",          # 50% for 12 mo
    "getresponse": "https://www.getresponse.com/?a=YOUR_ID",# 40-60% recurring 12 mo
    "amazon":      "https://amzn.to/YOUR_TAG",              # 3-10% per category
}

# Your link-in-bio page (Linktree, Beacons, etc.)
LINKTREE_URL = "https://linktr.ee/7694rk"

# Programs to prioritize (by commission value — lifetime recurring first)
# ⚠️  Only include programs with real IDs above. Adding a pending one
#     will cause the pipeline to post broken YOUR_ID affiliate links.
#
# ── PHASE 3 RECIPE LOCK (set 2026-05-19) ───────────────────────
# Analytics review of May 12–15 cohort (9 videos, 34 total views):
#   - elevenlabs: 28 views across 2 videos  ← WINNER
#   - fliki:       4 views across 2 videos
#   - systeme:     2 views across 2 videos
#   - beehiiv:     0 views across 2 videos
#   - submagic:    0 views across 1 video
# Narrowing to the two programs that earned organic impressions.
# Re-evaluate full roster on 2026-05-26 with new cohort data.
PRIORITY_PROGRAMS = ["elevenlabs", "fliki"]

# ══════════════════════════════════════════════════════════════
#  🧠 PRODUCT KNOWLEDGE BASE
#  Fixes the "ElevenLabs optimises recipes" hallucination by
#  giving the LLM a real fact sheet for each affiliate.
#  Every script must be grounded in this dict — no exceptions.
# ══════════════════════════════════════════════════════════════
AFFILIATE_PRODUCTS = {
    "systeme": {
        "name": "Systeme.io",
        "category": "All-in-one online business platform",
        "what_it_does": "Build sales funnels, send email campaigns, host courses, run an affiliate program — all in one tool. Replaces ClickFunnels + Mailchimp + Kajabi + Teachable.",
        "audience": "Solopreneurs, course creators, info-product sellers, side-hustlers tired of juggling 5 tools",
        "key_features": ["Drag-drop funnel builder", "Unlimited emails on free plan", "Course hosting", "Built-in affiliate manager", "Automation workflows"],
        "pain_solved": "Tool stack costs $300/mo across ClickFunnels + Kajabi + Mailchimp. Systeme replaces all of them.",
        "pricing": "Free forever (up to 2,000 contacts). Paid from $27/mo.",
        "topic_angles": [
            "I cancelled $300/mo of tools and replaced them with one (free)",
            "How I launched a digital course in 24 hours with zero tech skills",
            "Why ClickFunnels users are switching to this free alternative",
            "Free sales funnel builder that's actually good in 2026",
            "How a teacher made $5k/mo selling a PDF using Systeme.io",
        ],
    },
    "beehiiv": {
        "name": "Beehiiv",
        "category": "Newsletter platform with built-in monetisation",
        "what_it_does": "Send newsletters, grow them with referrals, monetise with their built-in ad network. Built by ex-Morning Brew team.",
        "audience": "Newsletter creators, indie publishers, content marketers escaping Substack's 10% cut and Mailchimp's bloat",
        "key_features": ["Free up to 2,500 subs", "Built-in ad network (you get paid)", "Referral program built in", "Boost program (paid sub recommendations)", "No transaction fees"],
        "pain_solved": "Substack takes 10% of every paid sub. Mailchimp punishes you with high prices once you grow. Beehiiv keeps the money with the creator.",
        "pricing": "Free up to 2,500 subs. Paid from $39/mo.",
        "topic_angles": [
            "How I made $4k from a 1,000-subscriber newsletter (no paid subs)",
            "Substack vs Beehiiv — the $1,200/year difference nobody talks about",
            "Newsletter monetisation in 2026 — what actually pays",
            "How Morning Brew alumni built the Substack killer",
            "Start a newsletter that pays you from day one (no audience needed)",
        ],
    },
    "elevenlabs": {
        "name": "ElevenLabs",
        "category": "AI voice generation & cloning",
        "what_it_does": "Turn text into ultra-realistic AI voiceover. Clone your own voice in 60 seconds. Generates voiceover in 30+ languages.",
        "audience": "YouTubers, podcasters, faceless-channel creators, audiobook producers, video editors, TikTokers who hate their voice",
        "key_features": ["Voice cloning from 60s of audio", "29 languages with same voice", "Free tier 10k chars/month", "Indistinguishable from human", "API for automation"],
        "pain_solved": "Recording voiceover takes hours. Hiring voice actors costs $200+/video. Robotic TTS kills retention. ElevenLabs sounds human.",
        "pricing": "Free 10k chars/mo. Paid from $5/mo (Starter) to $330/mo.",
        "topic_angles": [
            "I cloned my voice in 60 seconds — listen to this",
            "How faceless YouTube channels make $10k/mo (the secret tool)",
            "ElevenLabs vs Murf vs Speechify — which AI voice wins in 2026",
            "I made an entire YouTube video without recording a single word",
            "AI voice that's indistinguishable from human — try it free",
        ],
    },
    "submagic": {
        "name": "Submagic",
        "category": "AI auto-captions for short-form video",
        "what_it_does": "Upload a short video, get viral-style animated captions in 30 seconds. The captions style used by every top TikToker / Reels creator.",
        "audience": "TikTok / Reels / Shorts creators, social media managers, agencies running multiple accounts",
        "key_features": ["Auto-generated word-by-word captions", "Viral templates (MrBeast, Hormozi style)", "Emoji + B-roll auto-suggestions", "Background music sync", "Export in seconds"],
        "pain_solved": "Manual captioning takes 30 min/video. YouTube auto-captions look bad. Hand-styled captions are why some Shorts go viral and others don't.",
        "pricing": "From $16/mo for solo creators.",
        "topic_angles": [
            "Why every viral Short uses these captions (and yours doesn't)",
            "How MrBeast's caption style boosts retention by 80%",
            "I tested 5 caption tools — only one was worth it",
            "Submagic vs CapCut — which gets more views in 2026",
            "30-second caption hack that doubled my Reels views",
        ],
    },
    "fliki": {
        "name": "Fliki",
        "category": "Text-to-video AI for faceless creators",
        "what_it_does": "Paste a script (or blog URL), get a complete video with AI voiceover + matching stock footage + captions. The full faceless-YouTube pipeline in one tool.",
        "audience": "Faceless YouTubers, content repurposers, blog-to-video creators, anyone who doesn't want to film themselves",
        "key_features": ["Blog post → video in 1 click", "2,000+ AI voices in 75+ languages", "Built-in stock footage library", "Auto-captions", "ChatGPT integration"],
        "pain_solved": "Editing a YouTube video takes 4-8 hours. Faceless creators need 30 videos/month to compete. Fliki collapses the workflow.",
        "pricing": "Free tier (5 min/mo). Paid from $21/mo.",
        "topic_angles": [
            "I made 30 YouTube videos in one weekend (no editing software)",
            "Turn any blog post into a YouTube video in 60 seconds",
            "ChatGPT + Fliki = automated faceless YouTube channel",
            "Faceless YouTube blueprint that scales to $5k/mo (free tools)",
            "Why faceless channels are the best side hustle of 2026",
        ],
    },
}

# ══════════════════════════════════════════════════════════════
#  ⚖️ FTC COMPLIANCE (DO NOT CHANGE)
# ══════════════════════════════════════════════════════════════
# These are legally required disclosures. Removing them violates
# FTC 16 CFR Part 255 and Amazon Associates TOS.

FTC_DISCLOSURE_TEXT = "#ad"
AMAZON_DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases"

# Content archetypes — rotated for variety so the channel doesn't feel
# templated. The BRAIN agent picks one randomly per video.
#
# ── RESET (2026-05-31): CURIOSITY ARCHETYPES ───────────────────
# Replaced the affiliate archetypes (tool_comparison, money_hack, …)
# with curiosity framings. Keys MUST match the instruction map in
# you.py (_CURIOSITY_ARCHETYPE_INSTRUCTIONS). The diagnostic batch
# (spec Phase C) will show which pull; treat this as a starting set.
CONTENT_ARCHETYPES = [
    "mind_blowing_fact",        # One true, astonishing fact, built to a reveal
    "how_does_it_work",         # Demystify how something surprising works
    "unsolved_mystery",         # A real unanswered question, left open
    "counterintuitive_truth",   # The opposite of what people believe
    "what_if",                  # A vivid, scientifically honest hypothetical
]

# ── Archetype WEIGHTS — rebalanced 2026-07-25 on n=49 ───────────
# Median views per archetype across the whole curiosity era (videos
# aged >=72h, so they're compared at equal age):
#   unsolved_mystery       n=14  median 690  max 2054   <- 3x the field
#   how_does_it_work       n=17  median 241  max 1298
#   mind_blowing_fact      n=7   median 108  max  757
#   what_if                n=6   median  84  max  802
#   counterintuitive_truth n=5   median   1  max  326   <- dead
#
# Previously unsolved_mystery and how_does_it_work were weighted equally
# at 4 despite a ~3x median gap — that was the misallocation. Now:
#   unsolved_mystery ~55%, how_does_it_work ~27%, and a ~18% exploration
#   slice split between the two mid performers.
# counterintuitive_truth is set to 0: a median of 1 view across 5 videos
# isn't exploration, it's waste. Kept in CONTENT_ARCHETYPES (weight 0 is
# simply never chosen) so it can be revived by bumping this number.
CONTENT_ARCHETYPE_WEIGHTS = {
    "unsolved_mystery": 6,
    "how_does_it_work": 3,
    "mind_blowing_fact": 1,
    "what_if": 1,
    "counterintuitive_truth": 0,
}

# ── Legacy affiliate archetypes (DORMANT — MONETIZATION_ENABLED) ──
# Kept for reference / revival alongside the affiliate flow.
# MONETIZATION_ARCHETYPES = [
#     "tool_review", "tool_comparison", "workflow_tutorial",
#     "money_hack", "listicle", "myth_buster", "news_update",
# ]

# ══════════════════════════════════════════════════════════════
#  📺 CONTENT SERIES (2026-07-25) — identity + anti-template
# ══════════════════════════════════════════════════════════════
# Two problems, one fix.
#
# 1) MONETIZATION RISK. YouTube's "inauthentic content" policy
#    (Jul 2025) demonetizes work that looks "made with a template
#    with little to no variation across videos" / "easily replicable
#    at scale". Every video we shipped had the same voice, caption
#    style and 4-part structure — a textbook match. Real variation
#    is now a compliance requirement, not a nicety.
#
# 2) CONVERSION. 31 subs on 25k views (~0.12%) because there is
#    nothing to subscribe TO. Nobody subscribes to "a fact"; they
#    subscribe to a SERIES they want the next episode of.
#
# Each archetype becomes a named series with its own narrator voice,
# caption colour, script structure and title prefix — so videos differ
# from each other AND are recognisable as a returning show.
CONTENT_SERIES = {
    "unsolved_mystery": {
        "name": "UNSOLVED",
        "voice": "en-US-ChristopherNeural",      # deep, documentary
        "rate": "+0%",
        "caption_hex": "&H0000D7FF",             # amber (ASS = BGR)
        "promise": "One unsolved mystery, every day.",
        "structure": (
            "COLD OPEN with the strangest single detail of the case (no setup, "
            "start mid-story). Then the FACTS — what was observed, when, by whom. "
            "Then THE PROBLEM — why every explanation fails. End on the open "
            "question, unresolved. Never invent a solution."
        ),
    },
    "how_does_it_work": {
        "name": "HOW IT WORKS",
        "voice": "en-US-BrianMultilingualNeural",  # warm explainer
        "rate": "+6%",
        "caption_hex": "&H00FFFF00",               # cyan
        "promise": "The hidden mechanics of everyday things.",
        "structure": (
            "Open with the everyday thing people never question. Then REVEAL the "
            "counterintuitive mechanism, step by step, each step a short sentence. "
            "Build to the 'oh THAT's why' moment. Close by pointing back at the "
            "ordinary object so they never see it the same way."
        ),
    },
    "mind_blowing_fact": {
        "name": "MIND BENDER",
        "voice": "en-US-AndrewMultilingualNeural",  # current flagship voice
        "rate": "+5%",
        "caption_hex": "&H00B469FF",                # hot pink
        "promise": "A fact that breaks your brain, daily.",
        "structure": (
            "State the impossible-sounding claim flat out in one line. Spend the "
            "middle PROVING it with escalating concrete numbers and comparisons. "
            "Land a final comparison that reframes the viewer's own body or life."
        ),
    },
    "what_if": {
        "name": "WHAT IF",
        "voice": "en-GB-RyanNeural",               # British, speculative
        "rate": "+3%",
        "caption_hex": "&H0000FF7F",               # spring green
        "promise": "Impossible scenarios, real physics.",
        "structure": (
            "Pose the scenario in one vivid line. Then walk the CONSEQUENCE CHAIN "
            "— first this happens, then this, then this — each worse or stranger "
            "than the last, all scientifically honest. End at the final consequence."
        ),
    },
    "counterintuitive_truth": {
        "name": "ACTUALLY",
        "voice": "en-US-AriaNeural",
        "rate": "+4%",
        "caption_hex": "&H00FFFFFF",               # white
        "promise": "Everything you know, corrected.",
        "structure": (
            "State the belief everyone holds. Say plainly that it is wrong. "
            "Deliver the real mechanism with evidence. Close on what this means."
        ),
    },
}

# Fallback when an archetype has no series entry
DEFAULT_SERIES = {
    "name": "", "voice": VOICE, "rate": VOICE_RATE,
    "caption_hex": "&H0000FFFF", "promise": "New science every day.",
    "structure": "",
}

# Show episode numbers in titles ("UNSOLVED #12") — gives a returning
# viewer a reason to expect the next one.
SERIES_EPISODE_NUMBERS = True

# ══════════════════════════════════════════════════════════════
#  🌉 SHORTS → LONG-FORM BRIDGE (2026-08-01)
# ══════════════════════════════════════════════════════════════
# YouTube's 2026 distribution explicitly rewards Shorts viewers who click
# through to long-form, and throttles channels whose Shorts go nowhere.
# We built the weekly documentary for exactly this — but nothing pointed
# at it, so the mechanic was half-built.
#
# Deliberately NOT an on-screen overlay: the loop ending is what drives
# our completion rate (and the 700-view median), so we add the bridge
# only on surfaces that don't touch the video itself — the pinned comment
# (the clickable surface on Shorts) and the description.
#
# NOTE: this reuses the pinned-comment plumbing built for affiliates, but
# it is NOT monetization — it links our own video, so it stays on while
# MONETIZATION_ENABLED is off.
BRIDGE_ENABLED = True

# ── Curiosity DOMAINS (2026-06-14) — anti-repetition ───────────
# The batch repeated "black holes" in 4 of 8 videos because exact-
# string dedup doesn't catch subject repetition. The pipeline now
# rotates through these domains, picking one NOT used in the last few
# videos, so topics spread across the whole curiosity space instead
# of collapsing onto space/black-holes every time.
CURIOSITY_DOMAINS = [
    "deep space & astrophysics (but NOT black holes unless truly novel)",
    "the human body & the brain",
    "psychology & why people behave the way they do",
    "Earth, oceans, weather & natural phenomena",
    "animals & the strangeness of nature",
    "history's unsolved mysteries & lost civilizations",
    "physics & quantum weirdness in everyday life",
    "the human senses, perception & consciousness",
    "numbers, probability & counterintuitive math",
    "the deep past & the far future of humanity",
    "the microscopic world — cells, atoms, microbes",
    "technology & inventions that changed everything",
]
