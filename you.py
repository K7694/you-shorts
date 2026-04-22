#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║                       YOU v2.0                                   ║
║         AI Tools Affiliate Channel · Faceless Shorts             ║
║                                                                  ║
║   python you.py                    → one video, random topic     ║
║   python you.py "pictory review"   → specific topic              ║
║   python you.py --batch 5          → make 5 videos               ║
║   python you.py --autopilot        → run forever, hands-free     ║
║   python you.py --voices           → list available voices       ║
║                                                                  ║
║   COST: ₹0 — Everything is free.                                ║
║   REVENUE: Affiliate commissions (Systeme 60%, Beehiiv 50%...)  ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
"""

import argparse
import asyncio
import json
import math
import os
import random
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
import urllib.parse
from datetime import datetime
from pathlib import Path

from config import *


# ═══════════════════════════════════════════════════════════════
#  AGENT 1: BRAIN — Script Generation (Gemini + Groq Fallback)
# ═══════════════════════════════════════════════════════════════

def _call_gemini(prompt: str) -> str:
    """Call Gemini API via REST. No SDK needed."""
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        "gemini-2.0-flash:generateContent"
        f"?key={GEMINI_API_KEY}"
    )
    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.9, "maxOutputTokens": 2048},
    }).encode()

    for attempt in range(3):
        try:
            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=45) as resp:
                data = json.loads(resp.read().decode())
                return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors="ignore")
            # 429 = quota exhausted — don't waste retries, switch immediately
            if e.code == 429 or "RESOURCE_EXHAUSTED" in body:
                raise RuntimeError(f"Gemini quota exhausted (429) — switching to Groq")
            if attempt < 2:
                print(f"      ⚠️  Gemini retry {attempt+1}: HTTP {e.code}")
                time.sleep(2 ** attempt)
            else:
                raise RuntimeError(f"Gemini failed: HTTP {e.code}")
        except Exception as e:
            if attempt < 2:
                print(f"      ⚠️  Gemini retry {attempt+1}: {e}")
                time.sleep(2 ** attempt)
            else:
                raise RuntimeError(f"Gemini failed: {e}")


def _call_groq(prompt: str) -> str:
    """Call Groq API (llama3-70b) as fallback. Free tier, very fast."""
    url = "https://api.groq.com/openai/v1/chat/completions"
    payload = json.dumps({
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.9,
        "max_tokens": 2048,
    }).encode()

    for attempt in range(3):
        try:
            req = urllib.request.Request(url, data=payload, headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "User-Agent": "Mozilla/5.0",
            })
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode())
                return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            if attempt < 2:
                print(f"      ⚠️  Groq retry {attempt+1}: {e}")
                time.sleep(2 ** attempt)
            else:
                raise RuntimeError(f"Groq failed: {e}")


def _call_ollama(prompt: str) -> str:
    """Call local Ollama API (llama3.1:8b) as final fallback. Free, unlimited, offline."""
    url = "http://localhost:11434/api/generate"
    payload = json.dumps({
        "model": "llama3.1:8b",
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.9, "num_predict": 2048},
    }).encode()

    for attempt in range(3):
        try:
            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=300) as resp:
                data = json.loads(resp.read().decode())
                return data["response"].strip()
        except Exception as e:
            if attempt < 2:
                print(f"      ⚠️  Ollama retry {attempt+1}: {e}")
                time.sleep(2 ** attempt)
            else:
                raise RuntimeError(f"Ollama failed (is it running?): {e}")


def _score_hook(hook: str) -> int:
    """Heuristic hook quality score (1-10). No API call — instant.

    Rewards: specific numbers/money, personal pronouns, tool names, urgency.
    Penalizes: cliches, vague openers, questions without punch.
    """
    score = 5
    h = hook.lower().strip()

    # Hard penalize clichés — these kill retention
    cliches = [
        "did you know", "what if i told you", "have you ever", "imagine if",
        "fun fact", "believe it or not", "you won't believe", "shocking truth",
        "here's why", "this is why", "let me tell you", "in this video",
        "today i'm going to", "hey guys",
    ]
    for c in cliches:
        if c in h:
            score -= 3
            break

    # Reward personal threat / viewer involvement
    personal = ["you ", "your ", "we ", "our ", "us ", "i "]
    if any(p in h for p in personal):
        score += 2

    # Reward concrete numbers / money (specificity = credibility)
    if re.search(r'\$[\d,]+|\d+[kKxX%]|\d+', hook):
        score += 2

    # Reward declarative ending — confident statements stop scrolls
    if hook.rstrip().endswith(".") and not hook.rstrip().endswith("..."):
        score += 1

    # Penalize if it's too short (weak hook) or a plain question with no punch
    words = hook.split()
    if len(words) < 5:
        score -= 1
    if hook.strip().endswith("?") and len(words) < 8:
        score -= 1

    # Reward money/tech/urgency language
    power_words = [
        "free", "save", "replace", "kill", "stop", "waste", "paying",
        "$", "money", "revenue", "income", "profit", "automate",
        "secret", "nobody", "most people", "don't know", "hidden",
        "just dropped", "just launched", "right now", "already",
        "tool", "app", "software", "ai",
    ]
    if any(pw in h for pw in power_words):
        score += 1

    return max(1, min(score, 10))


def _call_llm(prompt: str) -> str:
    """Call LLM with automatic fallback: Gemini → Groq → Ollama (local)."""
    errors = []

    # Try Gemini first (fastest, best quality)
    if GEMINI_API_KEY:
        try:
            return _call_gemini(prompt)
        except RuntimeError as e:
            errors.append(str(e))
            print(f"      ⚠️  {e}")

    # Try Groq second (fast, free tier)
    if GROQ_API_KEY:
        try:
            print("      🔄 Trying Groq (llama3-70b)...")
            return _call_groq(prompt)
        except RuntimeError as e:
            errors.append(str(e))
            print(f"      ⚠️  {e}")

    # Try local Ollama last (always available, no limits)
    try:
        print("      🔄 Switching to local Ollama (llama3.1:8b)...")
        return _call_ollama(prompt)
    except RuntimeError as e:
        errors.append(str(e))
        raise RuntimeError(f"All LLMs failed: {'; '.join(errors)}")


def _parse_json(text: str) -> dict:
    """Extract JSON from LLM response, handling markdown fences and control characters."""
    text = text.strip()
    if "```" in text:
        lines = text.split("\n")
        inside = False
        clean_lines = []
        for line in lines:
            if line.strip().startswith("```"):
                inside = not inside
                continue
            if inside:
                clean_lines.append(line)
        text = "\n".join(clean_lines)
    start, end = text.find("{"), text.rfind("}") + 1
    if start >= 0 and end > start:
        text = text[start:end]
    # Try strict parse first, fall back to lenient (handles control chars from local models)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return json.loads(text, strict=False)


# ── Topic deduplication ───────────────────────────────────────────
_USED_TOPICS_FILE = BASE_DIR / "used_topics.json"

def _load_used_topics() -> list:
    if _USED_TOPICS_FILE.exists():
        try:
            return json.loads(_USED_TOPICS_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return []

def _save_used_topic(topic: str):
    topics = _load_used_topics()
    topics.append({"topic": topic, "date": datetime.now().isoformat()})
    topics = topics[-200:]
    _USED_TOPICS_FILE.write_text(json.dumps(topics, indent=2), encoding="utf-8")


# ── Feedback tracking + self-improving scripts ────────────────────
FEEDBACK_DIR = BASE_DIR / "feedback"
FEEDBACK_DIR.mkdir(exist_ok=True)
_UPLOADS_LOG      = FEEDBACK_DIR / "uploaded.json"
_TOP_PERFORMERS_F = BASE_DIR / "analyzer" / "top_performers.json"


def _log_upload(video_id: str, script: dict, title: str):
    """Record a successful upload so the feedback loop can pull 48hr stats later."""
    uploads = []
    if _UPLOADS_LOG.exists():
        try:
            uploads = json.loads(_UPLOADS_LOG.read_text(encoding="utf-8"))
        except Exception:
            pass
    uploads.append({
        "id": video_id,
        "title": title,
        "uploaded_at": datetime.now().isoformat(),
        "hook":   script.get("hook", ""),
        "script": script.get("script", ""),
        "topic":  script.get("topic", ""),
        "tags":   script.get("tags", []),
        "stats_fetched": False,
    })
    _UPLOADS_LOG.write_text(json.dumps(uploads, indent=2), encoding="utf-8")


def _load_top_performers() -> list:
    """Return top-performing video hooks/scripts for use as live few-shot examples."""
    if _TOP_PERFORMERS_F.exists():
        try:
            data = json.loads(_TOP_PERFORMERS_F.read_text(encoding="utf-8"))
            return [p for p in data.get("performers", []) if p.get("hook") and p.get("script")]
        except Exception:
            pass
    return []


def _build_few_shot_examples() -> str:
    """Build the few-shot section of the script prompt.

    Uses real top-performing videos when available (self-improving),
    otherwise falls back to curated static examples.
    """
    performers = _load_top_performers()

    if performers:
        lines = ["YOUR ACTUAL TOP PERFORMING VIDEOS — study and replicate their style, tone, and structure:\n"]
        for i, p in enumerate(performers[:3], 1):
            views = p.get("views", 0)
            eng   = p.get("engagement_rate", 0)
            lines.append(f"--- YOUR TOP VIDEO #{i} ({views:,} views | {eng}% engagement) ---")
            lines.append(f'HOOK:   "{p["hook"]}"')
            lines.append(f'SCRIPT: "{p["script"][:500]}..."')
            lines.append(f"WHY IT WORKED: This is a real video from your channel that outperformed — replicate its energy.\n")
        return "\n".join(lines)

    # Static fallback — curated viral AI-tools/affiliate examples
    return """PROVEN VIRAL SCRIPTS — study and replicate their structure, then write something equally powerful:

--- EXAMPLE 1 (1.8M views, 92% completion rate) — TOOL REVIEW ---
HOOK: "This free AI tool just replaced my $500/month video editor."
SCRIPT: "This free AI tool just replaced my $500/month video editor. It's called Pictory, and it turns any blog post or script into a fully edited video in 3 minutes. Drop in your text. It picks the visuals. Adds captions. Picks music. Done. I tested it against Premiere Pro on the same script. Pictory finished in 2 minutes 40 seconds. Premiere took me 3 hours. The quality gap? Honestly smaller than I expected. For YouTube Shorts and social clips, it's not even close. I cancelled my Adobe subscription the same day. Link's in the pinned comment if you want to try it free."
WHY IT WORKS: Opens with dollar amount saved, names the tool naturally, ends with soft CTA.

--- EXAMPLE 2 (2.4M views, 94% completion rate) — MONEY HACK ---
HOOK: "I automated my entire YouTube channel for $0 per month."
SCRIPT: "I automated my entire YouTube channel for $0 per month. No editing. No scripting. No uploads. Everything is handled by 3 free AI tools working together. Tool one writes the script using Google Gemini — free. Tool two generates the voiceover with Edge TTS — free. Tool three assembles the video with FFmpeg — free. One Python command. Hit enter. A finished YouTube Short appears on my channel 4 minutes later. I've uploaded 200 videos this way. Zero manual effort after the first setup. The craziest part? The channel now makes more than my day job. Same three free tools. Link in the pinned comment."
WHY IT WORKS: $0 repeated, escalating reveal of automation stack, relatable outcome.

--- EXAMPLE 3 (1.5M views, 89% completion rate) — TOOL COMPARISON ---
HOOK: "Stop paying for Canva Pro. This free alternative does everything."
SCRIPT: "Stop paying for Canva Pro. This free alternative does everything. It's called Photopea. Same interface. Same features. No watermarks. No subscription. Here's what most people don't know — Photopea supports PSD files, layers, masks, and even Illustrator files. Canva can't do any of that. I tested both on the same thumbnail design. Photopea exported at higher quality. Canva added compression artifacts. The only advantage Canva has is templates. But Photopea has AI generation now. Free. No credit card. No trial that expires. Just the tool. You're welcome."
WHY IT WORKS: Opens by attacking a known paid tool, comparison creates drama, confident ending."""


def generate_script(topic: str = None) -> dict:
    """Generate a complete script using the 4-part viral formula."""
    target_words = int(TARGET_DURATION * WORDS_PER_SECOND)

    # Load previously used topics for deduplication
    used = _load_used_topics()
    used_list = "\n".join(f"- {t['topic']}" for t in used[-50:]) if used else "None yet."

    # Use Analyzer brief if no topic given, brief is fresh, and topic isn't already used
    if not topic:
        brief_topic_part = None
        try:
            from analyzer import get_latest_brief, BRIEF_DB
            brief = get_latest_brief()

            # Check brief age — skip if > 24 hours old
            brief_age_hrs = 999
            if BRIEF_DB.exists():
                try:
                    brief_data = json.loads(BRIEF_DB.read_text(encoding="utf-8"))
                    gen = datetime.fromisoformat(brief_data["generated"])
                    brief_age_hrs = (datetime.now() - gen).total_seconds() / 3600
                except Exception:
                    pass

            if brief.get("topic") and brief_age_hrs < 24:
                # Skip brief if topic was already used
                used_topics_lc = {t['topic'].lower() for t in used}
                if brief["topic"].lower() in used_topics_lc:
                    print(f"   ⏭️  Brief topic already used — generating fresh topic instead")
                else:
                    # Score the prescribed hook — if weak, ignore it
                    brief_hook = brief.get("hook", "")
                    brief_hook_score = _score_hook(brief_hook) if brief_hook else 0

                    if brief_hook_score >= 6:
                        print(f"   📊 Using Analyzer brief: \"{brief['topic']}\" (hook score {brief_hook_score}/10)")
                        brief_topic_part = (
                            f'The topic is: "{brief["topic"]}"\n'
                            f'Use this exact opening hook: "{brief_hook}"\n'
                            f'Script direction: {brief.get("script_direction", "")}'
                        )
                    else:
                        print(f"   ⚠️  Brief hook weak (score {brief_hook_score}/10) — using topic only, generating fresh hook")
                        brief_topic_part = (
                            f'The topic is: "{brief["topic"]}"\n'
                            f'Write your own stronger hook — do NOT use: "{brief_hook}" (too cliché).\n'
                            f'Script direction: {brief.get("script_direction", "")}'
                        )
            elif brief.get("topic"):
                print(f"   ⚠️  Analyzer brief is {brief_age_hrs:.0f}hrs old — ignoring, generating fresh")
        except Exception as e:
            print(f"   ⚠️  Could not load brief: {e}")

        topic_part = brief_topic_part or (
            f'Come up with a UNIQUE, surprising, viral-worthy topic about "{CHANNEL_NICHE}".\n'
            f'The topic MUST be different from anything in the "TOPICS ALREADY USED" list below.'
        )
    else:
        topic_part = f'The topic is: "{topic}"'

    image_prompt_instructions = ""
    image_prompt_json = ""
    if not USE_BACKGROUND_VIDEO:
        image_prompt_instructions = f'''
Also generate {IMAGES_PER_VIDEO} image prompts for AI-generated backgrounds.
- Image 1 MUST be the most visually ARRESTING (this is the first frame — it prevents the swipe)
- Style: clean tech UI, dark mode software dashboards, app interfaces, modern glassmorphism
- Think: software screenshots, AI tool interfaces, productivity dashboards, revenue charts
- Show the RESULT the tool delivers (e.g. a dashboard showing $5k revenue, an AI interface generating content)
- NO text, NO watermarks, NO realistic human faces'''
        image_prompt_json = ',\n    "image_prompts": ["prompt1", "prompt2", "prompt3", "prompt4", "prompt5"]'

    # Pick a random content archetype to avoid template-like repetition
    archetype = random.choice(CONTENT_ARCHETYPES)
    # Pick an affiliate program to feature (prioritize high-commission ones)
    featured_program = random.choice(PRIORITY_PROGRAMS)

    archetype_instructions = {
        "tool_review": f"Write a SHORT, punchy review of an AI/SaaS tool. Focus on ONE tool — what it does, how fast it works, and why it's worth trying. Name the tool naturally. The featured affiliate program is '{featured_program}' — work it in naturally, or pick a different relevant AI tool.",
        "tool_comparison": f"Compare TWO competing AI/SaaS tools head-to-head. One should be the paid incumbent, one the cheaper/free alternative. Create drama through the comparison. You may reference '{featured_program}' or pick competing tools you know.",
        "workflow_tutorial": f"Reveal a workflow or automation hack using 2-3 AI tools together. Show HOW they connect. Make the viewer feel like they discovered a cheat code. Try to work in '{featured_program}' as one of the tools.",
        "money_hack": f"Reveal how a specific AI tool saves real money or generates income. Lead with the dollar amount. Be specific with numbers. The featured program is '{featured_program}' — feature it or a relevant money-saving AI tool.",
        "listicle": "List 3-5 AI tools that solve a specific problem (e.g. '4 AI tools that replace your entire marketing team'). Name each tool. Quick-fire format.",
        "myth_buster": f"Bust a common myth about AI tools, SaaS pricing, or online income. Be contrarian. Challenge what 'everyone thinks.' You can reference '{featured_program}' as part of the truth reveal.",
        "news_update": f"React to a recent (or plausible) AI tool launch, update, or price change. Create urgency — 'they just dropped this.' The featured program is '{featured_program}' — frame it as big news.",
    }

    prompt = f"""You are the world's most viral YouTube Shorts scriptwriter specializing in AI tools and tech reviews. Your scripts generate millions of views and drive affiliate conversions.

CONTENT ARCHETYPE FOR THIS VIDEO: {archetype.upper().replace('_', ' ')}
{archetype_instructions[archetype]}

{topic_part}

Write a {TARGET_DURATION}-second script (~{target_words} words).
Language: {LANGUAGE}. Tone: {CONTENT_TONE}.

TOPICS ALREADY USED — DO NOT REPEAT THESE:
{used_list}

{_build_few_shot_examples()}

YOU MUST FOLLOW THIS EXACT 4-PART STRUCTURE:

PART 1 — THE HOOK (first 2-3 seconds, ~8 words):
- Open with a JARRING statement about money saved, time saved, or a tool discovery
- Use specific numbers: "$500/month", "3 minutes", "replaced 4 tools"
- NEVER start with "Did you know", "What if I told you", or any cliche
- Make viewers feel they're about to discover a secret advantage

PART 2 — THE PROOF (next 15-17 seconds, ~42 words):
- Show exactly what the tool does, how fast, and the result
- Use before/after comparisons or specific test results
- Short punchy sentences (max 8 words each)
- Each sentence must build credibility

PART 3 — THE REVEAL (next 10 seconds, ~28 words):
- Drop the game-changing insight — the thing most people don't know
- This is the "wait, WHAT?" moment that triggers shares
- Contrast against the expensive/slow/manual alternative

PART 4 — THE CTA LOOP (final 3-5 seconds, ~10 words):
- End with a natural call-to-action that ALSO loops back to the hook
- Mention "link in the pinned comment" naturally, not forced
- Do NOT say "subscribe" or "follow for more"
- The ending should make viewers want to rewatch AND click

CRITICAL RULES:
- ZERO filler words. Every word must earn its place.
- Name the actual tool(s) — don't say "this tool" without naming it.
- Sound like a friend sharing a discovery, NOT a salesperson.
- Include enough value that viewers learn something even WITHOUT clicking.
- The script must pass as genuine, human insight — NOT templated AI content.
{image_prompt_instructions}

Return ONLY valid JSON (no markdown, no backticks):
{{
    "topic": "topic in 5-10 words",
    "archetype": "{archetype}",
    "affiliate_program": "the primary tool/program featured (lowercase, e.g. pictory, systeme, elevenlabs)",
    "hook": "the opening hook line only",
    "script": "the COMPLETE narration from hook through CTA loop ending as one paragraph",
    "cta_text": "the call-to-action text, e.g. Try Pictory free — link in pinned comment",
    "title": "YouTube title with emoji, max 70 chars — make it feel like a money secret",
    "description": "YouTube description, max 200 chars — mention the tool name",
    "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
    "hashtags": ["#shorts", "#aitools", "#makemoneyonline"]{image_prompt_json}
}}"""

    print(f"   🧠 Writing script (archetype: {archetype}, featured: {featured_program})...")

    # Generate script with hook quality gating — max 2 attempts
    data = None
    for attempt in range(2):
        raw = _call_llm(prompt)
        data = _parse_json(raw)

        # Ensure archetype and affiliate_program are set
        if "archetype" not in data:
            data["archetype"] = archetype
        # Clamp affiliate_program to active (filled-in) programs only —
        # prevents the LLM from picking a pending one like "pictory"
        # and leaking a broken YOUR_ID link into the pinned comment.
        if data.get("affiliate_program") not in PRIORITY_PROGRAMS:
            data["affiliate_program"] = featured_program
        if "cta_text" not in data:
            data["cta_text"] = f"Link in pinned comment 👇"

        hook = data.get("hook", "")
        hook_score = _score_hook(hook)
        print(f"   📊 Hook score: {hook_score}/10  \"{hook[:60]}\"")

        if hook_score >= 6:
            break  # Good hook — proceed

        if attempt == 0:
            print(f"   🔄 Hook too weak (score {hook_score}) — regenerating...")
            # Add the weak hook to the prompt so LLM doesn't repeat it
            prompt = prompt.replace(
                "TOPICS ALREADY USED — DO NOT REPEAT THESE:",
                f'REJECTED HOOK (too weak, do NOT use): "{hook}"\n\nTOPICS ALREADY USED — DO NOT REPEAT THESE:'
            )

    # Save topic to deduplication list
    _save_used_topic(data.get("topic", "unknown"))

    # Create caption lines
    words = data["script"].split()
    data["caption_lines"] = [
        " ".join(words[i:i+CAPTION_WORDS_PER_LINE])
        for i in range(0, len(words), CAPTION_WORDS_PER_LINE)
    ]

    print(f"   ✅ \"{data['title']}\" — {len(words)} words | CTA: {data.get('cta_text', 'none')}")
    return data


# ═══════════════════════════════════════════════════════════════
#  AGENT 2: EYES — AI Image Generation (Pollinations.ai, FREE)
# ═══════════════════════════════════════════════════════════════

def _download_ai_image(prompt: str, path: str, index: int) -> bool:
    """Download one AI image from Pollinations.ai (free, no key)."""
    full_prompt = f"{prompt}, {IMAGE_STYLE}, vertical 9:16, no text, no watermark"
    encoded = urllib.parse.quote(full_prompt)
    url = (
        f"https://image.pollinations.ai/prompt/{encoded}"
        f"?width={VIDEO_WIDTH}&height={VIDEO_HEIGHT}"
        f"&seed={int(time.time()) + index}&nologo=true&model=flux"
    )
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "You-Agent/1.0"})
        with urllib.request.urlopen(req, timeout=120) as resp:
            with open(path, "wb") as f:
                f.write(resp.read())
        size_kb = Path(path).stat().st_size / 1024
        print(f"      🎨 Scene {index+1} ready ({size_kb:.0f} KB)")
        return True
    except Exception as e:
        print(f"      ⚠️  Scene {index+1} failed: {e}")
        return False


def _make_fallback_image(path: str):
    """Create a solid dark background as fallback."""
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi",
        "-i", f"color=c=0x1a1a2e:s={VIDEO_WIDTH}x{VIDEO_HEIGHT}:d=1",
        "-frames:v", "1", path,
    ], capture_output=True)


def generate_images(prompts: list, session_id: str) -> list:
    """Generate all AI images for a video."""
    if USE_BACKGROUND_VIDEO:
        return []
        
    print(f"   👁️  Generating {len(prompts)} AI images...")
    img_dir = TEMP_DIR / session_id
    img_dir.mkdir(exist_ok=True)

    paths = []
    for i, prompt in enumerate(prompts):
        path = str(img_dir / f"scene_{i:02d}.jpg")
        if not _download_ai_image(prompt, path, i):
            _make_fallback_image(path)
        paths.append(path)
        if i < len(prompts) - 1:
            time.sleep(1.5)  # Be nice to free service

    print(f"   ✅ {len(paths)} images ready")
    return paths


# ═══════════════════════════════════════════════════════════════
#  AGENT 3: VOICE — Voiceover (Microsoft Edge TTS, FREE)
# ═══════════════════════════════════════════════════════════════

def _sanitize_tts(text: str) -> str:
    """Remove emojis and special characters that break Edge TTS."""
    import unicodedata
    clean = []
    for ch in text:
        cat = unicodedata.category(ch)
        # Keep letters, numbers, punctuation, spaces — remove symbols/emojis
        if cat.startswith(("L", "N", "P", "Z")) or ch in " \n\t":
            clean.append(ch)
    return "".join(clean).strip()


def generate_voice(text: str, path: str) -> float:
    """Generate voiceover and return duration in seconds."""
    import edge_tts

    text = _sanitize_tts(text)

    async def _gen():
        comm = edge_tts.Communicate(text=text, voice=VOICE, rate=VOICE_RATE)
        await comm.save(path)

    print(f"   🎙️  Recording voiceover ({VOICE})...")
    asyncio.run(_gen())

    # Post-process: add warmth, compression, presence (makes TTS less robotic)
    raw_path = path.replace(".mp3", "_raw.mp3")
    os.rename(path, raw_path)
    subprocess.run([
        "ffmpeg", "-y", "-i", raw_path, "-af",
        "acompressor=threshold=0.08:ratio=3:attack=5:release=80,"
        "equalizer=f=180:width_type=h:width=120:g=2.5,"
        "equalizer=f=3200:width_type=h:width=800:g=2",
        "-c:a", "libmp3lame", "-b:a", "192k", path,
    ], capture_output=True)
    os.remove(raw_path)

    # Get duration
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", path],
        capture_output=True, text=True,
    )
    duration = float(result.stdout.strip())
    print(f"   ✅ Voiceover ready: {duration:.1f}s")
    return duration


def transcribe_words(audio_path: str) -> list:
    """Use faster-whisper to get word-level timestamps from audio.
    Returns list of {'word': str, 'start': float, 'end': float}."""
    try:
        from faster_whisper import WhisperModel
        print("      🔤 Transcribing word timestamps (Whisper)...")
        model = WhisperModel("base", device="cpu", compute_type="int8")
        segments, _ = model.transcribe(audio_path, word_timestamps=True)
        words = []
        for segment in segments:
            if segment.words:
                for w in segment.words:
                    words.append({"word": w.word.strip(), "start": w.start, "end": w.end})
        print(f"      ✅ {len(words)} words timestamped")
        return words
    except Exception as e:
        print(f"      ⚠️  Whisper failed ({e}), using fallback timing")
        return []


def list_voices():
    """List all free English voices available."""
    import edge_tts

    async def _list():
        voices = await edge_tts.list_voices()
        en = [v for v in voices if v["Locale"].startswith("en-")]
        hi = [v for v in voices if v["Locale"].startswith("hi-")]

        print(f"\n  {'Voice':<42} {'Gender':<8} {'Locale'}")
        print("  " + "-" * 65)
        for v in en:
            marker = " <-- current" if v["ShortName"] == VOICE else ""
            print(f"  {v['ShortName']:<42} {v['Gender']:<8} {v['Locale']}{marker}")

        if hi:
            print(f"\n  Hindi voices:")
            print("  " + "-" * 65)
            for v in hi:
                print(f"  {v['ShortName']:<42} {v['Gender']:<8} {v['Locale']}")

        print(f"\n  💡 Set your pick in config.py → VOICE = '...'")
        print(f"  📊 Total: {len(en)} English + {len(hi)} Hindi voices (all FREE)")

    asyncio.run(_list())


# ═══════════════════════════════════════════════════════════════
#  SOUND DESIGN — Dark Ambient BGM (FFmpeg Synthesis, FREE)
# ═══════════════════════════════════════════════════════════════

def generate_bgm(duration: float, path: str) -> bool:
    """Generate dark ambient background music using FFmpeg audio synthesis.

    Creates a layered soundscape: filtered pink noise + sub-bass drone +
    mid-range tremolo pad. Randomized slightly for variety across videos.
    """
    base_freq = random.choice([45, 50, 55, 60])
    mid_freq = base_freq * 2
    noise_amp = round(random.uniform(0.02, 0.04), 3)
    trem_freq = round(random.uniform(0.15, 0.5), 3)
    fade_out = max(0, duration - 2.5)

    try:
        result = subprocess.run([
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", f"anoisesrc=d={duration}:c=pink:r=44100:a={noise_amp}",
            "-f", "lavfi", "-i", f"sine=frequency={base_freq}:duration={duration}",
            "-f", "lavfi", "-i", f"sine=frequency={mid_freq}:duration={duration}",
            "-filter_complex",
            f"[0]lowpass=f=180,highpass=f=20[noise];"
            f"[1]volume=0.25,tremolo=f={trem_freq}:d=0.4[bass];"
            f"[2]volume=0.12,tremolo=f={trem_freq*2:.3f}:d=0.6[mid];"
            f"[noise][bass][mid]amix=inputs=3:duration=first,"
            f"afade=t=in:st=0:d=1.5,afade=t=out:st={fade_out}:d=2.5,"
            f"equalizer=f=60:width_type=o:width=2:g=3,"
            f"acompressor=threshold=0.05:ratio=4:attack=200:release=1000[out]",
            "-map", "[out]",
            "-c:a", "aac", "-b:a", "128k",
            path
        ], capture_output=True, text=True, timeout=60)
        return result.returncode == 0
    except Exception:
        return False


# ═══════════════════════════════════════════════════════════════
#  AGENT 4: DIRECTOR — Video Assembly (FFmpeg, FREE)
# ═══════════════════════════════════════════════════════════════

def _ass_time(sec: float) -> str:
    """Convert seconds to ASS timestamp."""
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    cs = int((sec % 1) * 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def _make_captions_whisper(word_ts: list, path: str):
    """Create ASS subtitles with TikTok-style word-by-word highlighting using Whisper timestamps."""
    ass = f"""[Script Info]
Title: You Captions
ScriptType: v4.00+
PlayResX: {VIDEO_WIDTH}
PlayResY: {VIDEO_HEIGHT}
WrapStyle: 0

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Main,{CAPTION_FONT},{CAPTION_SIZE},&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,2,0,1,8,5,5,80,80,350,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""
    cx, cy = VIDEO_WIDTH // 2, VIDEO_HEIGHT // 2 + 280
    n = CAPTION_WORDS_PER_LINE

    # Group words into chunks
    chunks = [word_ts[i:i+n] for i in range(0, len(word_ts), n)]

    for chunk in chunks:
        chunk_start = chunk[0]["start"]
        chunk_end = chunk[-1]["end"]

        # For each word in the chunk, create a dialogue line showing all words
        # but highlighting the current one in yellow
        for j, current in enumerate(chunk):
            w_start = current["start"]
            w_end = current["end"] if j < len(chunk) - 1 else chunk_end

            parts = []
            for k, w in enumerate(chunk):
                word_upper = w["word"].upper()
                if k == j:
                    # Highlighted word: yellow + slightly larger
                    parts.append(r"{\c&H00FFFF&\fscx110\fscy110}" + word_upper + r"{\c&HFFFFFF&\fscx100\fscy100}")
                else:
                    parts.append(word_upper)

            text = rf"{{\an5\pos({cx},{cy})\fad(60,40)}}" + " ".join(parts)
            ass += f"Dialogue: 0,{_ass_time(w_start)},{_ass_time(w_end)},Main,,0,0,0,,{text}\n"

    with open(path, "w") as f:
        f.write(ass)


def _make_captions_fallback(lines: list, duration: float, path: str):
    """Fallback: evenly-spaced captions when Whisper is unavailable."""
    t = duration / len(lines)
    ass = f"""[Script Info]
Title: You Captions
ScriptType: v4.00+
PlayResX: {VIDEO_WIDTH}
PlayResY: {VIDEO_HEIGHT}
WrapStyle: 0

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Main,{CAPTION_FONT},{CAPTION_SIZE},&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,2,0,1,8,5,5,80,80,350,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""
    cx, cy = VIDEO_WIDTH // 2, VIDEO_HEIGHT // 2 + 280

    for i, line in enumerate(lines):
        s, e = i * t, (i + 1) * t
        text = (
            rf"{{\fad(100,80)\an5\pos({cx},{cy})"
            rf"\fscx115\fscy115\t(0,120,\fscx100\fscy100)}}"
            + line.upper()
        )
        ass += f"Dialogue: 0,{_ass_time(s)},{_ass_time(e)},Main,,0,0,0,,{text}\n"

    with open(path, "w") as f:
        f.write(ass)


def _make_slideshow(images: list, duration: float, path: str) -> bool:
    """Create slideshow with Ken Burns effect."""
    t_each = duration / len(images)
    inputs = []
    filters = []

    for i, img in enumerate(images):
        inputs.extend(["-loop", "1", "-t", str(t_each + 0.8), "-i", img])
        frames = int((t_each + 0.8) * VIDEO_FPS)

        # Alternate zoom directions
        if i % 3 == 0:
            zoom = f"zoom='min(1+0.25*on/{frames},1.25)'"
            px = f"x='iw/2-(iw/zoom/2)'"
            py = f"y='ih/2-(ih/zoom/2)'"
        elif i % 3 == 1:
            zoom = f"zoom='max(1.25-0.25*on/{frames},1.0)'"
            px = f"x='iw/2-(iw/zoom/2)'"
            py = f"y='ih/2-(ih/zoom/2)'"
        else:
            zoom = f"zoom='1.15'"
            px = f"x='iw*0.1*on/{frames}'"
            py = f"y='ih*0.1*on/{frames}'"

        filters.append(
            f"[{i}:v]scale={VIDEO_WIDTH*2}:{VIDEO_HEIGHT*2},"
            f"eq=contrast=1.15:saturation=1.2:brightness=-0.02,unsharp=5:5:1.0:5:5:0.0,"
            f"zoompan={zoom}:{px}:{py}:d={frames}:s={VIDEO_WIDTH}x{VIDEO_HEIGHT}:fps={VIDEO_FPS},"
            f"setpts=PTS-STARTPTS[v{i}]"
        )

    # Chain crossfades
    if len(images) == 1:
        fc = f"{';'.join(filters)};[v0]copy[out]"
    else:
        fc = ";".join(filters) + ";"
        prev = "v0"
        for i in range(1, len(images)):
            label = "out" if i == len(images) - 1 else f"x{i}"
            offset = max(0, t_each * i - 0.4 * i)
            fc += f"[{prev}][v{i}]xfade=transition=fade:duration=0.8:offset={offset:.2f}[{label}];"
            prev = label
        fc = fc.rstrip(";")

    result = subprocess.run(
        ["ffmpeg", "-y", *inputs, "-filter_complex", fc,
         "-map", "[out]", "-c:v", "libx264", "-pix_fmt", "yuv420p",
         "-r", str(VIDEO_FPS), "-t", str(duration), path],
        capture_output=True, text=True,
    )
    return result.returncode == 0


def _make_simple_slideshow(images: list, duration: float, path: str):
    """Fallback: concat images without effects."""
    t_each = duration / len(images)
    concat = str(TEMP_DIR / "concat.txt")
    with open(concat, "w") as f:
        for img in images:
            f.write(f"file '{img}'\nduration {t_each}\n")
        f.write(f"file '{images[-1]}'\n")

    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat,
        "-vf", f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:force_original_aspect_ratio=increase,"
               f"crop={VIDEO_WIDTH}:{VIDEO_HEIGHT},fps={VIDEO_FPS}",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-t", str(duration), path,
    ], capture_output=True, check=True)


def assemble_video(audio: str, images: list, captions: list, filename: str, word_timestamps: list = None) -> str:
    """Assemble final video: images + audio + captions → .mp4"""
    print("   🎬 Assembling video...")

    # Get audio duration
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", audio],
        capture_output=True, text=True,
    )
    duration = float(result.stdout.strip()) + 0.3

    # Step 1: Slideshow or Background Video
    slide_path = str(TEMP_DIR / f"{filename}_slides.mp4")
    if USE_BACKGROUND_VIDEO:
        print(f"      🎞️  Using background video: {BACKGROUND_VIDEO_FILE}")
        
        # Get duration of the background video
        bg_result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", BACKGROUND_VIDEO_FILE],
            capture_output=True, text=True,
        )
        try:
            bg_duration = float(bg_result.stdout.strip())
        except ValueError:
            raise RuntimeError(f"Could not read duration of {BACKGROUND_VIDEO_FILE}")
        
        start_time = 0
        if bg_duration > duration:
            import random
            start_time = random.uniform(0, bg_duration - duration)
            
        print(f"      🔀 Slicing from {start_time:.1f}s to {start_time+duration:.1f}s")
        # Center-crop landscape to 9:16 vertical and scale to correct resolution
        # And ensure audio stream is present if volume > 0
        crop_args = []
        if BACKGROUND_VIDEO_VOLUME > 0:
            crop_args = ["-c:a", "aac"]
        else:
            crop_args = ["-an"]
            
        subprocess.run([
            "ffmpeg", "-y", "-ss", str(start_time), "-t", str(duration),
            "-i", BACKGROUND_VIDEO_FILE,
            "-vf", f"crop=ih*(9/16):ih,scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(VIDEO_FPS),
            *crop_args,
            slide_path
        ], capture_output=True, check=True)
        print("      ✅ Background segment ready")
    else:
        print("      📸 Creating slideshow with Ken Burns...")
        if not _make_slideshow(images, duration, slide_path):
            print("      ⚠️  Falling back to simple slideshow...")
            _make_simple_slideshow(images, duration, slide_path)
        print("      ✅ Slideshow done")

    # Step 2: Captions (word-synced via Whisper, or fallback)
    subs_path = str(TEMP_DIR / f"{filename}_subs.ass")
    if word_timestamps:
        _make_captions_whisper(word_timestamps, subs_path)
        print("      ✅ Captions done (word-synced)")
    else:
        _make_captions_fallback(captions, duration - 0.3, subs_path)
        print("      ✅ Captions done (fallback timing)")

    # Step 3: Background music
    bgm_path = str(TEMP_DIR / f"{filename}_bgm.m4a")
    has_bgm = False
    if BGM_ENABLED:
        print("      🎵 Generating dark ambient soundtrack...")
        has_bgm = generate_bgm(duration, bgm_path)
        if has_bgm:
            print("      ✅ Soundtrack ready")
        else:
            print("      ⚠️  BGM failed, continuing without music")

    # Step 4: Final merge (with #ad overlay + CTA overlay)
    out_path = str(OUTPUT_DIR / f"{filename}.mp4")
    subs_escaped = subs_path.replace(os.sep, '/').replace(':', '\\\\:')

    filter_complex = []
    audios = ["[1:a]volume=1.0[voice]"]
    amix_inputs = ["voice"]
    
    if USE_BACKGROUND_VIDEO and BACKGROUND_VIDEO_VOLUME > 0:
        audios.append(f"[0:a]volume={BACKGROUND_VIDEO_VOLUME}[game]")
        amix_inputs.append("game")
        
    if has_bgm:
        audios.append(f"[2:a]volume={BGM_VOLUME}[music]")
        amix_inputs.append("music")
        
    if len(audios) > 1:
        mix_str = f"[{']['.join(amix_inputs)}]amix=inputs={len(amix_inputs)}:duration=first:normalize=0[aout]"
        filter_complex_str = ";".join(audios) + ";" + mix_str
    else:
        filter_complex_str = audios[0] + ";[voice]anull[aout]"

    inputs = ["-i", slide_path, "-i", audio]
    if has_bgm:
        inputs.extend(["-i", bgm_path])

    # Build video filter: subtitles + FTC #ad overlay (first 3s) + CTA overlay (last 3s)
    # Detect font for drawtext
    _win_font = Path("C:/Windows/Fonts/impact.ttf")
    _linux_fonts = [
        Path("/usr/share/fonts/truetype/msttcorefonts/Impact.ttf"),
        Path("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    ]
    if _win_font.exists():
        _dt_font = "C\\:/Windows/Fonts/impact.ttf"
    else:
        _raw = next((str(f) for f in _linux_fonts if f.exists()), None)
        _dt_font = _raw if _raw else None

    vf_parts = [f"ass={subs_escaped}"]

    if _dt_font:
        # FTC disclosure: "#ad" in top-left corner for first 3 seconds
        vf_parts.append(
            f"drawtext=fontfile='{_dt_font}':text='%23ad':"
            f"fontsize=42:fontcolor=white:borderw=3:bordercolor=black@0.8:"
            f"x=30:y=40:enable='lt(t,3)'"
        )
        # CTA overlay: "Link in pinned comment 👇" bottom-center for last 3 seconds
        vf_parts.append(
            f"drawtext=fontfile='{_dt_font}':text='Link in pinned comment':"
            f"fontsize=38:fontcolor=yellow:borderw=3:bordercolor=black@0.9:"
            f"x=(w-text_w)/2:y=h-120:enable='gte(t,{max(0, duration - 3.5)})'"
        )
        print("      ⚖️  FTC #ad overlay + CTA overlay added")

    vf_str = ",".join(vf_parts)

    result = subprocess.run([
        "ffmpeg", "-y", *inputs,
        "-filter_complex", filter_complex_str,
        "-vf", vf_str,
        "-map", "0:v", "-map", "[aout]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest", "-pix_fmt", "yuv420p", "-r", str(VIDEO_FPS),
        "-movflags", "+faststart",
        out_path,
    ], capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg error: {result.stderr[-300:]}")

    size = Path(out_path).stat().st_size / (1024 * 1024)
    print(f"   ✅ Video ready: {filename}.mp4 ({size:.1f} MB)")
    return out_path


# ═══════════════════════════════════════════════════════════════
#  AGENT 5: PUBLISHER — YouTube Upload (YouTube API, FREE)
# ═══════════════════════════════════════════════════════════════

def generate_thumbnail(image_path: str, hook: str, slug: str) -> str | None:
    """Generate a YouTube thumbnail: first AI image + hook text overlay.

    Uses FFmpeg drawtext with Impact font for the dark-cinematic look.
    Text is written to a temp file to avoid shell-escaping issues.
    """
    if not image_path or not Path(image_path).exists():
        return None

    out_path = str(OUTPUT_DIR / f"thumb_{slug}.jpg")
    text_file = str(TEMP_DIR / f"thumb_text_{slug}.txt")

    # Wrap hook text at ~32 chars per line (looks good at 1280px wide)
    words = hook.split()
    lines, cur = [], []
    for w in words:
        if sum(len(x) for x in cur) + len(cur) + len(w) > 32 and cur:
            lines.append(" ".join(cur))
            cur = [w]
        else:
            cur.append(w)
    if cur:
        lines.append(" ".join(cur))

    try:
        with open(text_file, "w", encoding="utf-8") as f:
            f.write("\n".join(ln.upper() for ln in lines[:3]))
    except Exception:
        return None

    # Detect font path — Windows vs Linux (GitHub Actions)
    win_font = Path("C:/Windows/Fonts/impact.ttf")
    linux_fonts = [
        Path("/usr/share/fonts/truetype/msttcorefonts/Impact.ttf"),
        Path("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"),
        Path("/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    ]
    if win_font.exists():
        font = "C\\:/Windows/Fonts/impact.ttf"  # Windows — colon must be escaped
    else:
        raw = next((str(f) for f in linux_fonts if f.exists()), None)
        if not raw:
            print("      ⚠️  No font found for thumbnail — skipping")
            return None
        font = raw  # Linux — no escaping needed
    txt_escaped = text_file.replace("\\", "/").replace(":", "\\\\:")

    result = subprocess.run([
        "ffmpeg", "-y", "-i", image_path,
        "-vf",
        f"scale=1280:720:force_original_aspect_ratio=increase,"
        f"crop=1280:720,"
        # dark gradient bar at bottom
        f"drawbox=x=0:y=ih-170:w=iw:h=170:color=black@0.78:t=fill,"
        # hook text centred inside the bar
        f"drawtext=fontfile='{font}':textfile='{txt_escaped}':"
        f"fontsize=54:fontcolor=yellow:borderw=5:bordercolor=black@0.95:"
        f"line_spacing=8:"
        f"x=(w-text_w)/2:y=h-155+((155-text_h)/2)",
        "-q:v", "2", out_path,
    ], capture_output=True, text=True, timeout=30)

    if result.returncode == 0:
        size_kb = Path(out_path).stat().st_size / 1024
        print(f"      🖼️  Thumbnail ready ({size_kb:.0f} KB)")
        return out_path
    else:
        print(f"      ⚠️  Thumbnail FFmpeg error: {result.stderr[-120:]}")
        return None


def _post_pinned_comment(yt, video_id: str, comment_text: str):
    """Post a comment on the video and pin it. Contains the affiliate link.

    Pinned comments are the PRIMARY clickable link surface for Shorts
    (description links became non-clickable Aug 2024).
    """
    try:
        # Post comment
        comment_body = {
            "snippet": {
                "videoId": video_id,
                "topLevelComment": {
                    "snippet": {
                        "textOriginal": comment_text,
                    }
                }
            }
        }
        result = yt.commentThreads().insert(
            part="snippet", body=comment_body
        ).execute()
        comment_id = result["snippet"]["topLevelComment"]["id"]
        print(f"   📌 Pinned comment posted (affiliate link)")
        return comment_id
    except Exception as e:
        print(f"   ⚠️  Pinned comment failed: {e}")
        return None


def upload_youtube(video_path: str, title: str, desc: str, tags: list,
                   thumbnail_path: str = None, script: dict = None) -> dict:
    """Upload to YouTube with FTC-compliant description + pinned affiliate comment."""
    if not os.path.exists(YOUTUBE_SECRETS_FILE):
        print("   📤 YouTube not configured — video saved locally")
        print("      (Set up client_secrets.json when ready)")
        return {"status": "local_only", "path": video_path}

    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
    except ImportError:
        print("   ⚠️  YouTube libraries not installed. Run:")
        print("      pip install google-auth google-auth-oauthlib google-api-python-client")
        return {"status": "missing_deps", "path": video_path}

    SCOPES = [
        "https://www.googleapis.com/auth/youtube",
        "https://www.googleapis.com/auth/youtube.upload",
        "https://www.googleapis.com/auth/youtube.readonly",
        "https://www.googleapis.com/auth/youtube.force-ssl",
    ]
    creds = None

    if os.path.exists(YOUTUBE_TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(YOUTUBE_TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(YOUTUBE_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=8090)
        with open(YOUTUBE_TOKEN_FILE, "w") as f:
            f.write(creds.to_json())

    yt = build("youtube", "v3", credentials=creds)

    all_tags = list(set(tags + YOUTUBE_DEFAULT_TAGS))

    body = {
        "snippet": {"title": title[:100], "description": desc[:5000],
                     "tags": all_tags, "categoryId": YOUTUBE_CATEGORY},
        "status": {"privacyStatus": YOUTUBE_PRIVACY,
                    "selfDeclaredMadeForKids": YOUTUBE_MADE_FOR_KIDS},
    }

    media = MediaFileUpload(video_path, mimetype="video/mp4", resumable=True, chunksize=1024*1024)

    print("   📤 Uploading to YouTube...")
    request = yt.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"      ⏳ {int(status.progress()*100)}%")

    vid = response["id"]
    url = f"https://youtube.com/shorts/{vid}"
    print(f"   ✅ Live at: {url}")

    # Upload custom thumbnail
    if thumbnail_path and Path(thumbnail_path).exists():
        try:
            thumb_media = MediaFileUpload(thumbnail_path, mimetype="image/jpeg")
            yt.thumbnails().set(videoId=vid, media_body=thumb_media).execute()
            print(f"   🖼️  Thumbnail set")
        except Exception as e:
            print(f"   ⚠️  Thumbnail upload failed (channel may need verification): {e}")

    # Post pinned comment with affiliate link (primary monetization CTA)
    if script:
        try:
            from compliance import build_pinned_comment
            comment_text = build_pinned_comment(script)
            _post_pinned_comment(yt, vid, comment_text)
        except Exception as e:
            print(f"   ⚠️  Could not post pinned comment: {e}")

    # Log for feedback loop
    if script:
        _log_upload(vid, script, title)

    return {"status": "uploaded", "id": vid, "url": url}


# ═══════════════════════════════════════════════════════════════
#  ORCHESTRATOR — The One Command
# ═══════════════════════════════════════════════════════════════

def _slug(name: str) -> str:
    return re.sub(r'[\s]+', '_', re.sub(r'[^\w\s-]', '', name)).strip('_')[:50].lower()


def _clean_temp():
    if TEMP_DIR.exists():
        for item in TEMP_DIR.iterdir():
            if item.is_dir():
                shutil.rmtree(item, ignore_errors=True)
            else:
                item.unlink(missing_ok=True)


def create_video(topic: str = None, upload: bool = True) -> dict:
    """
    THE MAIN PIPELINE — one call creates one complete YouTube Short.

    🧠 Brain   → writes script + image prompts
    👁️ Eyes    → generates AI images
    🎙️ Voice   → records voiceover
    🎬 Director → assembles final video
    📤 Publisher → uploads to YouTube
    """
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    r = {"timestamp": ts}

    try:
        # ── STEP 1: BRAIN ───────────────────────────────────
        print("\n  ┌─ 1/5 ── 🧠 BRAIN ──────────────────────────")
        script = generate_script(topic)
        r["script"] = script
        slug = _slug(script["title"])
        sid = f"{ts}_{slug}"

        # ── STEP 2: EYES ────────────────────────────────────
        print("\n  ┌─ 2/5 ── 👁️  EYES ──────────────────────────")
        image_prompts = script.get("image_prompts")
        if not image_prompts and not USE_BACKGROUND_VIDEO:
            # LLM failed to return prompts — generate tech-themed fallbacks
            _t = script.get("topic", "AI tools")
            image_prompts = [
                f"modern dark mode software dashboard with neon accents, {_t}",
                f"AI tool interface generating content, sleek glassmorphism UI, {_t}",
                f"revenue analytics dashboard glowing charts dark background, {_t}",
                f"laptop screen showing productivity workflow automation, dark UI",
                f"futuristic AI software interface with holographic elements, dark mode",
            ]
            print("      ⚠️  No image prompts from LLM — using tech-themed fallbacks")
        images = generate_images(image_prompts or [], sid)
        r["images"] = images

        # ── STEP 3: VOICE ───────────────────────────────────
        print("\n  ┌─ 3/5 ── 🎙️  VOICE ─────────────────────────")
        audio_path = str(TEMP_DIR / f"{sid}.mp3")
        duration = generate_voice(script["script"], audio_path)
        r["audio"] = audio_path

        # ── STEP 3.5: TRANSCRIBE (word-level timestamps) ───
        word_ts = transcribe_words(audio_path)

        # ── STEP 4: DIRECTOR ────────────────────────────────
        print("\n  ┌─ 4/5 ── 🎬 DIRECTOR ───────────────────────")
        video_path = assemble_video(audio_path, images, script["caption_lines"], sid, word_timestamps=word_ts)
        r["video"] = video_path

        # Generate thumbnail from first AI image (must happen before temp cleanup)
        thumb_path = None
        if images:
            print("      🖼️  Generating thumbnail...")
            thumb_path = generate_thumbnail(images[0], script.get("hook", script["title"]), slug)
            r["thumbnail"] = thumb_path

        # ── STEP 4.5: COMPLIANCE CHECK ──────────────────────
        print("\n  ┌─ ⚖️  COMPLIANCE ─────────────────────────────")
        try:
            from compliance import build_compliant_description, validate_compliance
            compliance = validate_compliance(script)
            if compliance["warnings"]:
                for w in compliance["warnings"]:
                    print(f"      ⚠️  {w}")
            if compliance["errors"]:
                for e in compliance["errors"]:
                    print(f"      ❌ {e}")
            if compliance["passed"]:
                print("      ✅ Compliance check passed")
            compliant_desc = build_compliant_description(script)
        except Exception as e:
            print(f"      ⚠️  Compliance module error: {e} — using basic description")
            compliant_desc = script.get("description", "") + "\n\n" + " ".join(script.get("hashtags", ["#shorts"]))

        # ── STEP 5: PUBLISHER ───────────────────────────────
        print("\n  ┌─ 5/5 ── 📤 PUBLISHER ──────────────────────")
        if upload:
            r["upload"] = upload_youtube(
                video_path, script["title"],
                compliant_desc, script.get("tags", []),
                thumbnail_path=thumb_path, script=script,
            )
            # Auto-delete local video after successful upload to save storage
            if r["upload"].get("status") == "uploaded":
                try:
                    os.remove(video_path)
                    print(f"   🗑️  Local file deleted (saved to YouTube)")
                    r["video"] = r["upload"]["url"]
                except OSError:
                    pass
        else:
            print("   ⏭️  Skipping upload (--no-upload)")
            r["upload"] = {"status": "skipped"}

        r["status"] = "success"

    except Exception as e:
        r["status"] = "error"
        r["error"] = str(e)
        print(f"\n   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Always clean temp files to save storage
        _clean_temp()

    return r


def _run_analyzer_refresh():
    """Run the Analyzer in autopilot mode to refresh the content brief."""
    print("\n  ┌─ 📊 ANALYZER — Refreshing content brief...")
    try:
        import argparse as _ap
        from analyzer import run_full_analysis
        _args = _ap.Namespace(trends=False, mine=False, competitors=False, brief=False)
        run_full_analysis(_args)
        print("  └─ ✅ Fresh brief ready")
    except Exception as e:
        print(f"  └─ ⚠️  Analyzer failed: {e} — using last brief")


def run_autopilot(interval: int, upload: bool):
    """Run forever, creating videos at set intervals.
    Refreshes the Analyzer brief every 5 videos so topics stay current.
    """
    print(f"  🚀 AUTOPILOT ENGAGED — 1 video every {interval} min")
    print("  Press Ctrl+C to stop\n")

    count = 0
    while True:
        count += 1

        # Refresh Analyzer brief: on first run, then every 5 videos
        if count == 1 or count % 5 == 0:
            _run_analyzer_refresh()

        print(f"\n{'═'*50}")
        print(f"  🔄 AUTOPILOT — Video #{count} — {datetime.now():%H:%M:%S}")
        print(f"{'═'*50}")

        try:
            create_video(upload=upload)
            _clean_temp()
        except Exception as e:
            print(f"  ❌ {e} — will retry next cycle")
            _clean_temp()  # Always clean up even on error

        nxt = datetime.now().timestamp() + interval * 60
        print(f"\n  💤 Next video at {datetime.fromtimestamp(nxt):%H:%M:%S}")
        time.sleep(interval * 60)


def print_summary(results: list):
    """Print results summary."""
    print("\n  ╔══════════════════════════════════════════╗")
    print("  ║           ✅ MISSION COMPLETE             ║")
    print("  ╚══════════════════════════════════════════╝\n")

    for i, r in enumerate(results):
        title = r.get("script", {}).get("title", "?")
        status = r.get("status", "?")
        print(f"  {'✅' if status == 'success' else '❌'} {title}")
        if r.get("video"):
            print(f"     📁 {r['video']}")
        up = r.get("upload", {})
        if up.get("url"):
            print(f"     🔗 {up['url']}")
        elif up.get("status") == "local_only":
            print(f"     💾 Saved locally")
        if r.get("error"):
            print(f"     ❌ {r['error']}")
        print()

    # Save log
    log = OUTPUT_DIR / f"log_{results[0]['timestamp']}.json"
    with open(log, "w") as f:
        json.dump([{
            "timestamp": r.get("timestamp"), "status": r.get("status"),
            "title": r.get("script", {}).get("title"), "video": r.get("video"),
            "youtube": r.get("upload", {}).get("url"),
        } for r in results], f, indent=2)
    print(f"  📋 Log: {log}\n")


# ═══════════════════════════════════════════════════════════════
#  CLI
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="YOU — Your AI agent for YouTube Shorts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
  EXAMPLES:
    python you.py                       One video, random topic
    python you.py "quantum physics"     Specific topic
    python you.py --batch 5             Make 5 videos
    python you.py --no-upload           Save locally only
    python you.py --autopilot           Run forever
    python you.py --autopilot --every 120  Every 2 hours
    python you.py --voices              List available voices
        """,
    )
    parser.add_argument("topic", nargs="?", help="Specific topic (optional)")
    parser.add_argument("--batch", type=int, help="Number of videos")
    parser.add_argument("--no-upload", action="store_true", help="Don't upload")
    parser.add_argument("--autopilot", action="store_true", help="Run forever")
    parser.add_argument("--every", type=int, default=AUTOPILOT_INTERVAL, help="Minutes between runs")
    parser.add_argument("--voices", action="store_true", help="List voices")

    args = parser.parse_args()

    # ── List voices ──────────────────────────────────────────
    if args.voices:
        list_voices()
        return

    # ── Banner ───────────────────────────────────────────────
    print()
    print("  ╔══════════════════════════════════════════╗")
    print("  ║          YOU v2.0 — Online                ║")
    print("  ║   AI Tools Affiliate · Zero effort.       ║")
    print("  ╚══════════════════════════════════════════╝")

    # ── Check API key ────────────────────────────────────────
    if not GEMINI_API_KEY:
        print("\n  ❌ GEMINI_API_KEY not set!\n")
        print("  Do this once (30 seconds):")
        print("    1. Go to: https://aistudio.google.com/apikey")
        print("    2. Click 'Create API Key'")
        print("    3. Run:  export GEMINI_API_KEY='your-key'")
        print("       Or paste it in config.py")
        sys.exit(1)

    # ── Check FFmpeg ─────────────────────────────────────────
    if not shutil.which("ffmpeg"):
        print("\n  ❌ FFmpeg not found!\n")
        print("  Install it:")
        print("    Ubuntu/Debian: sudo apt install ffmpeg")
        print("    Mac:           brew install ffmpeg")
        print("    Windows:       choco install ffmpeg")
        sys.exit(1)

    # ── Check edge-tts ───────────────────────────────────────
    try:
        import edge_tts
    except ImportError:
        print("\n  ❌ edge-tts not installed!\n")
        print("  Run: pip install edge-tts")
        sys.exit(1)

    upload = not args.no_upload

    # ── Run ──────────────────────────────────────────────────
    if args.autopilot:
        run_autopilot(args.every, upload)

    elif args.batch:
        results = []
        for i in range(args.batch):
            print(f"\n{'═'*50}")
            print(f"  📹 VIDEO {i+1} OF {args.batch}")
            print(f"{'═'*50}")
            results.append(create_video(upload=upload))
            if i < args.batch - 1:
                print("\n  ⏳ Cooling down 10s...")
                time.sleep(10)
        print_summary(results)

    else:
        result = create_video(topic=args.topic, upload=upload)
        print_summary([result])


if __name__ == "__main__":
    main()
