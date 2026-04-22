"""
╔══════════════════════════════════════════════════════════════╗
║                  YOU — Configuration                         ║
║        AI Tools Affiliate Channel · Faceless Shorts          ║
║                                                              ║
║   MONETIZATION STACK (active):                               ║
║     Systeme.io    → 60% lifetime recurring  ✅               ║
║     Beehiiv       → 50% recurring 12 mo     ✅               ║
║     ElevenLabs    → 22% recurring 12 mo     ✅               ║
║     Submagic      → 30% lifetime recurring  ✅               ║
║     Fliki         → 30% lifetime recurring  ✅               ║
║     (Pictory / HeyGen / Opus / Kit / GetResp / Amazon        ║
║      pending — on waiting list or no code yet)               ║
║     Shorts Ad Rev → rounding error ($0.08-$0.20 RPM)         ║
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

# 1c. YouTube Data API key (for the Analyzer — reading YouTube data)
YOUTUBE_DATA_API_KEY = os.getenv("YOUTUBE_DATA_API_KEY", "")

# 2. What is your channel about? Be SPECIFIC.
#    Bad:  "tech stuff"
#    Good: "honest AI tool reviews that help creators save time and make money"
CHANNEL_NICHE = "AI tools and software reviews that help creators and entrepreneurs save time and make money — honest, no-BS breakdowns of what actually works and what's a waste of money"

# ══════════════════════════════════════════════════════════════
#  🟡 OPTIONAL — Customize these later
# ══════════════════════════════════════════════════════════════

# Tone of narration
CONTENT_TONE = "confident, direct, slightly edgy — like a tech-savvy friend who has already tested everything and just tells you what's worth your money"

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

# Video dimensions (9:16 vertical for Shorts)
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
VIDEO_FPS = 60

# Number of AI images per video (more = more visual variety)
IMAGES_PER_VIDEO = 5

# Caption styling
CAPTION_FONT = "Impact"
CAPTION_SIZE = 82
CAPTION_WORDS_PER_LINE = 3

# AI image style suffix (tech/software review aesthetic)
IMAGE_STYLE = "clean modern tech UI, dark mode interface, glassmorphism panels, neon accent lighting, professional software screenshot aesthetic, 4k, minimal and sleek"

# Batch size (how many videos per run)
BATCH_SIZE = 1

# Background music (dark ambient, auto-generated via FFmpeg)
BGM_ENABLED = True
BGM_VOLUME = 0.12  # Volume relative to voiceover (0.0-1.0, subtle at 12%)

# ══════════════════════════════════════════════════════════════
#  🟣 GAMEPLAY/BACKGROUND VIDEO OVERLAY
# ══════════════════════════════════════════════════════════════
USE_BACKGROUND_VIDEO = False
BACKGROUND_VIDEO_FILE = str(ASSETS_DIR / "Brainrot.mov")
BACKGROUND_VIDEO_VOLUME = 0.05  # Volume of gameplay audio (0.0 to mute)

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
YOUTUBE_PRIVACY = "unlisted"   # ⚠️ Change to "public" when ready to launch!
YOUTUBE_CATEGORY = "28"      # 28 = Science & Tech (correct for AI tools)
YOUTUBE_DEFAULT_TAGS = ["shorts", "ai tools", "make money online", "saas", "tech review", "ai software", "creator tools", "side hustle"]
YOUTUBE_MADE_FOR_KIDS = False

# Autopilot interval (minutes between videos)
AUTOPILOT_INTERVAL = 360  # 6 hours

# ══════════════════════════════════════════════════════════════
#  💰 AFFILIATE CONFIGURATION
# ══════════════════════════════════════════════════════════════
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
PRIORITY_PROGRAMS = ["systeme", "beehiiv", "elevenlabs", "submagic", "fliki"]

# ══════════════════════════════════════════════════════════════
#  ⚖️ FTC COMPLIANCE (DO NOT CHANGE)
# ══════════════════════════════════════════════════════════════
# These are legally required disclosures. Removing them violates
# FTC 16 CFR Part 255 and Amazon Associates TOS.

FTC_DISCLOSURE_TEXT = "#ad"
AMAZON_DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases"

# Content archetypes — rotated to avoid YouTube "inauthentic content" flags
# The BRAIN agent picks one randomly per video to ensure variety
CONTENT_ARCHETYPES = [
    "tool_review",        # Single tool deep-dive
    "tool_comparison",    # Head-to-head: Tool A vs Tool B
    "workflow_tutorial",  # "How I automate X using these 3 tools"
    "money_hack",         # "This free AI tool saved me $X/month"
    "listicle",           # "5 AI tools that replace your editor"
    "myth_buster",        # "AI video tools are NOT what you think"
    "news_update",        # "[Tool] just dropped something insane"
]
