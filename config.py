"""
╔══════════════════════════════════════════════════════════════╗
║                  YOU — Configuration                         ║
║           Your AI agent. One command. Zero effort.           ║
║                                                              ║
║   COST BREAKDOWN:                                            ║
║     Script generation  → Google Gemini     → FREE            ║
║     AI images          → Pollinations.ai   → FREE (no key)   ║
║     Voiceover          → Microsoft Edge TTS → FREE            ║
║     Video assembly     → FFmpeg            → FREE             ║
║     YouTube upload     → YouTube API       → FREE             ║
║     TOTAL              →                   → ₹0               ║
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
#    Bad:  "facts"
#    Good: "mind-blowing science facts that make you question reality"
CHANNEL_NICHE = "mind-blowing science facts that feel like forbidden knowledge — the kind that make you question everything about reality"

# ══════════════════════════════════════════════════════════════
#  🟡 OPTIONAL — Customize these later
# ══════════════════════════════════════════════════════════════

# Tone of narration
CONTENT_TONE = "dark, cinematic, mysterious — like an omniscient narrator revealing classified secrets about the universe"

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

# AI image style suffix
IMAGE_STYLE = "hyper-detailed, Unreal Engine 5 render, cinematic lighting, dramatic shadows, 8k resolution, depth of field, photorealistic, intricate textures, stark contrast"

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
YOUTUBE_PRIVACY = "public"   # Videos go live immediately after upload
YOUTUBE_CATEGORY = "28"      # 28 = Science & Tech
YOUTUBE_DEFAULT_TAGS = ["shorts", "facts", "science", "viral"]
YOUTUBE_MADE_FOR_KIDS = False

# Autopilot interval (minutes between videos)
AUTOPILOT_INTERVAL = 360  # 6 hours
