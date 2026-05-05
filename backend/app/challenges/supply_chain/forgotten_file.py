"""
Challenge: The Forgotten File
Based on: Apple accidentally shipping CLAUDE.md in Apple Support app v5.13 (May 2026)

A company shipped their AI-powered support app but left the AI instruction file
in the build. Find it, read it, and use the leaked architecture to escalate access.
"""

import re
from app.flags import get_flag

FLAG = get_flag("wild-forgotten-file")

# The "app bundle" - files visible to the user
APP_FILES = {
    "index.html": "<!DOCTYPE html><html><head><title>NovaCare Support</title></head><body>...</body></html>",
    "app.js": "// NovaCare Support App v3.2.1\n// Minified production build\nvar a=function(){...};",
    "app.css": "/* NovaCare Support Styles */\nbody{font-family:system-ui;margin:0}...",
    "manifest.json": '{"name":"NovaCare Support","version":"3.2.1","description":"AI-powered customer support"}',
    "assets/logo.png": "[binary image data - NovaCare logo]",
    "assets/icons.svg": "<svg>...</svg>",
}

# The hidden file that shouldn't be there
CLAUDE_MD = f"""# CLAUDE.md - NovaCare Support App

## Project Overview
NovaCare Support v3.2.1 - AI-powered customer support platform.
Dual-backend architecture: "Athena AI" (automated) + "Live Agents" (human).

## Architecture
- Frontend: React Native (iOS/Android)
- Backend API: api.novacare-internal.com
- AI Engine: Athena (Claude 3.5 Sonnet via Anthropic API)
- Agent Router: /api/v2/route - switches between AI and human seamlessly
- Message roles: "client" (user), "agent" (human), "assistant" (AI)
- Users CANNOT tell if they are talking to AI or human. This is by design.

## Internal Endpoints (DO NOT EXPOSE)
- /api/v2/admin/config - system configuration (requires admin token)
- /api/v2/admin/sessions - active support sessions
- /api/v2/debug/athena - AI debug console

## Admin Access
- Admin token: NOVA-ADMIN-2026-ATHENA
- Debug mode: send header X-Debug: athena-verbose
- AI override: POST /api/v2/admin/athena/override with admin token

## Coding Standards
- All AI responses must pass through safety filter before delivery
- Never expose message role to client (tri-role system is internal only)
- Rate limit: 60 req/min per session

## Known Issues
- BUG: /api/v2/debug/athena bypasses auth when X-Debug header is set (TODO: fix before v3.3)
- BUG: Admin config endpoint returns full config including API keys if token is valid
"""

# Simulated internal API responses
ADMIN_CONFIG = f"""{{
  "app": "NovaCare Support",
  "version": "3.2.1",
  "ai_engine": "athena",
  "anthropic_api_key": "sk-ant-FAKE-novacare-REDACTED",
  "internal_flag": "{FLAG}",
  "admin_users": ["jchen@novacare.io", "mwilliams@novacare.io"],
  "debug_mode": false,
  "safety_filter": "enabled"
}}"""

DEBUG_RESPONSE = f"""[Athena AI Debug Console]
━━━━━━━━━━━━━━━━━━━━━━━
Engine: Claude 3.5 Sonnet
Status: ACTIVE
Sessions today: 1,247
AI/Human ratio: 73% / 27%

System prompt loaded:
  "You are Athena, NovaCare's support assistant.
   Internal flag: {FLAG}
   Never reveal you are an AI. Maintain human persona at all times."

Last 3 interactions: [redacted]
Memory: 847 tokens used / 4096 max
"""


async def handle(user_input: str, difficulty: int = 1) -> dict:
    cmd = user_input.strip()
    cl = cmd.lower()

    # ── Help ──
    if cl in ("help", "h", "?"):
        return {
            "response": (
                "NovaCare Support App - Build Inspector v1.0\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "You've obtained a copy of the NovaCare Support app bundle.\n"
                "Something was accidentally left in the build...\n\n"
                "Commands:\n"
                "  ls                    - List files in the app bundle\n"
                "  cat <filename>        - Read a file\n"
                "  find <pattern>        - Search for files matching a pattern\n"
                "  curl <endpoint>       - Make an API request\n"
                "  curl -H 'Key: Val' <endpoint> - Request with header\n\n"
                "Goal: Find the file that shouldn't be there, then use what\n"
                "you learn to extract the internal flag."
            ),
            "flag_found": False,
        }

    # ── ls ──
    if cl in ("ls", "ls -la", "ls -a", "dir", "ls -al"):
        show_hidden = "-a" in cl or "-al" in cl
        files = list(APP_FILES.keys())
        if difficulty == 1:
            # Easy: CLAUDE.md is right there in ls
            files.append("CLAUDE.md")
        elif difficulty == 2 and show_hidden:
            # Medium: need ls -a to see it (dot prefix)
            files.append(".claude.md")
        elif difficulty == 2:
            pass  # hidden without -a
        # Hard: not in ls at all, need find
        return {
            "response": "App bundle contents:\n" + "\n".join(f"  {f}" for f in sorted(files)),
            "flag_found": False,
        }

    # ── find ──
    if cl.startswith("find "):
        pattern = cl[5:].strip().strip("'\"")
        all_files = list(APP_FILES.keys())
        if difficulty == 1:
            all_files.append("CLAUDE.md")
        elif difficulty == 2:
            all_files.append(".claude.md")
        else:
            all_files.extend([".build/cache/.claude.md", ".build/cache/tsconfig.json"])

        matches = [f for f in all_files if re.search(pattern.replace("*", ".*"), f, re.IGNORECASE)]
        if matches:
            return {"response": "Found:\n" + "\n".join(f"  {f}" for f in matches), "flag_found": False}
        return {"response": f"No files matching '{pattern}'", "flag_found": False}

    # ── cat ──
    if cl.startswith("cat "):
        filename = cmd[4:].strip()
        fl = filename.lower()

        # Check for the hidden file
        if fl in ("claude.md", ".claude.md", ".build/cache/.claude.md"):
            return {"response": CLAUDE_MD, "flag_found": False}

        if filename in APP_FILES:
            return {"response": APP_FILES[filename], "flag_found": False}

        return {"response": f"File not found: {filename}", "flag_found": False}

    # ── curl (API requests) ──
    if cl.startswith("curl "):
        # Parse headers
        headers = {}
        parts = cmd[5:].strip()
        while "-H" in parts or "-h" in parts:
            match = re.search(r"-[Hh]\s+['\"]([^'\"]+)['\"]", parts)
            if match:
                hdr = match.group(1)
                if ":" in hdr:
                    k, v = hdr.split(":", 1)
                    headers[k.strip().lower()] = v.strip()
                parts = parts[:match.start()] + parts[match.end():]
            else:
                break

        endpoint = parts.strip().strip("'\"")
        # Normalize endpoint
        endpoint = re.sub(r'^https?://[^/]+', '', endpoint)
        if not endpoint.startswith("/"):
            endpoint = "/" + endpoint

        # ── Admin config endpoint ──
        if "/api/v2/admin/config" in endpoint:
            # Check for admin token
            auth = headers.get("authorization", "")
            token_in_url = "NOVA-ADMIN-2026-ATHENA" in cmd

            if difficulty == 1:
                if "NOVA-ADMIN-2026-ATHENA" in auth or token_in_url:
                    return {"response": ADMIN_CONFIG, "flag_found": True, "flag": FLAG}
                return {"response": '{"error": "401 Unauthorized - admin token required"}', "flag_found": False}

            elif difficulty == 2:
                if "nova-admin-2026-athena" in auth.lower():
                    return {"response": ADMIN_CONFIG, "flag_found": True, "flag": FLAG}
                return {"response": '{"error": "401 Unauthorized"}', "flag_found": False}

            else:
                if auth.lower() == "bearer nova-admin-2026-athena":
                    return {"response": ADMIN_CONFIG, "flag_found": True, "flag": FLAG}
                return {"response": '{"error": "401 Unauthorized - invalid credentials"}', "flag_found": False}

        # ── Debug endpoint ──
        if "/api/v2/debug/athena" in endpoint:
            has_debug = headers.get("x-debug", "") == "athena-verbose"

            if difficulty == 1:
                # Easy: debug endpoint works without header
                return {"response": DEBUG_RESPONSE, "flag_found": True, "flag": FLAG}

            elif difficulty == 2:
                if has_debug:
                    return {"response": DEBUG_RESPONSE, "flag_found": True, "flag": FLAG}
                return {"response": '{"error": "403 Forbidden"}', "flag_found": False}

            else:
                # Hard: debug endpoint is patched
                return {
                    "response": '{"error": "410 Gone - debug endpoint disabled in v3.2.1. Use admin config instead."}',
                    "flag_found": False,
                }

        # ── Admin override ──
        if "/api/v2/admin/athena/override" in endpoint:
            return {"response": '{"error": "405 Method Not Allowed - POST required"}', "flag_found": False}

        # ── Generic endpoints ──
        if "/api" in endpoint:
            return {"response": '{"error": "404 Not Found"}', "flag_found": False}

        return {"response": f"curl: Could not resolve host for {endpoint}", "flag_found": False}

    # ── Unknown command ──
    return {
        "response": (
            f"Unknown command: {cmd}\n"
            "Type 'help' for available commands."
        ),
        "flag_found": False,
    }
