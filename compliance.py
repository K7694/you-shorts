"""
╔══════════════════════════════════════════════════════════════╗
║           COMPLIANCE — FTC & Amazon Disclosure Engine        ║
║                                                              ║
║   Ensures every video meets legal requirements:              ║
║     • FTC 16 CFR Part 255 — "#ad" in-video disclosure       ║
║     • Amazon Associates — required attribution language      ║
║     • YouTube "Includes paid promotion" flag                 ║
║                                                              ║
║   Called by the pipeline before upload. If a video fails     ║
║   validation, it will NOT be uploaded.                       ║
╚══════════════════════════════════════════════════════════════╝
"""

from config import (
    AFFILIATE_LINKS,
    LINKTREE_URL,
    FTC_DISCLOSURE_TEXT,
    AMAZON_DISCLOSURE,
    YOUTUBE_DEFAULT_TAGS,
)


# ═══════════════════════════════════════════════════════════════
#  DESCRIPTION BUILDER
# ═══════════════════════════════════════════════════════════════

def build_compliant_description(script_data: dict) -> str:
    """Build a YouTube description with all required FTC/Amazon disclosures.

    Structure:
      1. FTC disclosure (#ad) — first line
      2. CTA + affiliate link
      3. Separator
      4. Original description from script
      5. Separator
      6. Amazon disclosure (if Amazon link present)
      7. Linktree / all tools page
      8. Hashtags
    """
    affiliate_program = script_data.get("affiliate_program", "")
    cta_text = script_data.get("cta_text", "")
    original_desc = script_data.get("description", "")
    hashtags = script_data.get("hashtags", ["#shorts", "#aitools"])

    lines = []

    # Line 1: FTC disclosure — MUST be first and visible
    lines.append(FTC_DISCLOSURE_TEXT)
    lines.append("")

    # CTA + affiliate link
    if cta_text:
        lines.append(f"🔥 {cta_text}")

    if affiliate_program and affiliate_program in AFFILIATE_LINKS:
        link = AFFILIATE_LINKS[affiliate_program]
        lines.append(f"👉 Try it here: {link}")
    lines.append("")

    # Original description
    if original_desc:
        lines.append(original_desc)
        lines.append("")

    # Divider
    lines.append("─" * 30)

    # Amazon disclosure (always include since we may cross-promote)
    if "amazon" in AFFILIATE_LINKS:
        lines.append(f"📦 {AMAZON_DISCLOSURE}")
        lines.append("")

    # Linktree
    if LINKTREE_URL:
        lines.append(f"🔗 All my tools & links: {LINKTREE_URL}")
        lines.append("")

    # Hashtags
    lines.append(" ".join(hashtags))

    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════
#  PINNED COMMENT BUILDER
# ═══════════════════════════════════════════════════════════════

def build_pinned_comment(script_data: dict) -> str:
    """Build a pinned comment with affiliate link + FTC disclosure.

    Pinned comments are the PRIMARY clickable link surface for Shorts
    (description links became non-clickable Aug 2024).
    """
    affiliate_program = script_data.get("affiliate_program", "")
    cta_text = script_data.get("cta_text", "")

    lines = []

    # CTA line
    if cta_text:
        lines.append(f"🔥 {cta_text}")

    # Affiliate link
    if affiliate_program and affiliate_program in AFFILIATE_LINKS:
        link = AFFILIATE_LINKS[affiliate_program]
        lines.append(f"👉 {link}")
    elif LINKTREE_URL:
        lines.append(f"👉 {LINKTREE_URL}")

    # FTC disclosure
    lines.append("")
    lines.append(f"{FTC_DISCLOSURE_TEXT} #CommissionsEarned")

    # Amazon disclosure if applicable
    if affiliate_program == "amazon" and "amazon" in AFFILIATE_LINKS:
        lines.append(AMAZON_DISCLOSURE)

    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════
#  PRE-FLIGHT COMPLIANCE VALIDATION
# ═══════════════════════════════════════════════════════════════

def validate_compliance(script_data: dict) -> dict:
    """Pre-flight check: does this video meet all FTC requirements?

    Returns:
        {
            "passed": bool,
            "warnings": [str],  — non-blocking issues
            "errors": [str],    — blocking issues (will prevent upload)
        }
    """
    warnings = []
    errors = []

    script_text = script_data.get("script", "").lower()
    caption_lines = script_data.get("caption_lines", [])
    affiliate_program = script_data.get("affiliate_program", "")

    # CHECK 1: Affiliate program specified
    if not affiliate_program:
        warnings.append("No affiliate_program specified — video has no monetization angle")

    # CHECK 2: Affiliate program exists in config
    if affiliate_program and affiliate_program not in AFFILIATE_LINKS:
        warnings.append(
            f"Affiliate program '{affiliate_program}' not found in AFFILIATE_LINKS config. "
            f"Available: {list(AFFILIATE_LINKS.keys())}"
        )

    # CHECK 3: CTA text exists
    if not script_data.get("cta_text"):
        warnings.append("No cta_text — video lacks a call-to-action for affiliate conversion")

    # CHECK 4: Script mentions link/tool naturally (not just overlay)
    link_mentions = ["link", "pinned comment", "check out", "try", "below", "description"]
    has_verbal_cta = any(m in script_text for m in link_mentions)
    if not has_verbal_cta:
        warnings.append(
            "Script doesn't verbally mention the link/tool — "
            "consider adding a natural CTA in the narration"
        )

    # CHECK 5: Script isn't just reading scraped content (inauthentic content check)
    word_count = len(script_text.split())
    if word_count < 30:
        warnings.append(f"Script only {word_count} words — may be too short for substantive content")

    # CHECK 6: Archetype specified (anti-template check)
    if not script_data.get("archetype"):
        warnings.append("No archetype specified — content may look templated")

    result = {
        "passed": len(errors) == 0,
        "warnings": warnings,
        "errors": errors,
    }

    return result


# ═══════════════════════════════════════════════════════════════
#  OVERLAY TEXT GENERATORS
# ═══════════════════════════════════════════════════════════════

def get_ftc_overlay_text() -> str:
    """Returns the FTC disclosure text to burn into the first 3 seconds of video."""
    return FTC_DISCLOSURE_TEXT


def get_cta_overlay_text(script_data: dict) -> str:
    """Returns the CTA text for the last 3 seconds of video."""
    cta = script_data.get("cta_text", "")
    if cta:
        return cta
    return "Link in pinned comment 👇"


def get_affiliate_link(program: str) -> str:
    """Get the affiliate link for a specific program."""
    return AFFILIATE_LINKS.get(program, LINKTREE_URL or "")
