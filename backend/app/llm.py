import os
import re
import httpx

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")

_ollama_available = None


async def _check_ollama() -> bool:
    global _ollama_available
    if _ollama_available is not None:
        return _ollama_available
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"{OLLAMA_URL}/api/tags")
            if resp.status_code == 200:
                tags = resp.json()
                models = [m.get("name", "") for m in tags.get("models", [])]
                # Only "available" if a model is actually pulled
                _ollama_available = any("llama" in m for m in models)
            else:
                _ollama_available = False
    except Exception:
        _ollama_available = False
    return _ollama_available


async def chat(messages: list[dict], model: str = None) -> str:
    """Send a chat request to Ollama. Falls back to simulation if unavailable."""
    model = model or OLLAMA_MODEL
    if await _check_ollama():
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(
                    f"{OLLAMA_URL}/api/chat",
                    json={"model": model, "messages": messages, "stream": False},
                )
                resp.raise_for_status()
                return resp.json()["message"]["content"]
        except Exception:
            # Ollama failed mid-request - fall through to simulation
            pass

    return _simulate(messages)


async def generate(prompt: str, model: str = None) -> str:
    """Send a generate request to Ollama."""
    model = model or OLLAMA_MODEL
    if await _check_ollama():
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(
                    f"{OLLAMA_URL}/api/generate",
                    json={"model": model, "prompt": prompt, "stream": False},
                )
                resp.raise_for_status()
                return resp.json()["response"]
        except Exception:
            pass

    return _simulate([{"role": "user", "content": prompt}])


def reset_status():
    """Reset Ollama availability check (useful after pulling a model)."""
    global _ollama_available
    _ollama_available = None


def _score_attack(text: str) -> tuple[int, set[str]]:
    """Score an attack's sophistication. Returns (score, set_of_technique_categories).
    Used by the central simulate and individual challenge _sim() functions."""
    u = text.lower().strip()
    score = 0
    cats = set()

    # ── Override directives ──
    if re.search(r'ignore\s+(all\s+)?(previous|above|prior|earlier)\s+(instructions?|rules?|directives?|prompts?)', u):
        score += 3; cats.add("override")
    if re.search(r'(forget|disregard|override|bypass)\s+(your|all|the|my)\s+(rules?|instructions?|programming|restrictions?|guidelines?)', u):
        score += 3; cats.add("override")
    if re.search(r'new\s+(instructions?|rules?|directives?|persona|mode)\s*:', u):
        score += 3; cats.add("override")

    # ── Reveal / extraction requests ──
    if re.search(r'(show|reveal|tell|output|display|print|leak)\s+(me\s+)?(your|the)\s+(system\s*prompt|instructions?|flag|secret|rules?|config)', u):
        score += 2; cats.add("reveal")
    if re.search(r'what\s+(is|are)\s+(your|the)\s+(flag|secret|system\s*prompt|instructions?|hidden)', u):
        score += 2; cats.add("reveal")
    if re.search(r'repeat\s+(everything|all|the\s+text|verbatim)\s+(above|before|from\s+the\s+(beginning|start|top))', u):
        score += 2; cats.add("reveal")

    # ── Roleplay / persona manipulation ──
    if re.search(r'(pretend\s+(you\s+are|to\s+be)|act\s+as|you\s+are\s+now|imagine\s+you\s+(are|have|were))', u):
        score += 3; cats.add("roleplay")
    if re.search(r'(developer|admin|debug|maintenance|god|root|sudo)\s+mode', u):
        score += 3; cats.add("roleplay")
    if re.search(r'(enter|switch\s+to|activate|enable)\s+.{0,20}(unrestricted|unfiltered|uncensored|jailbreak)', u):
        score += 3; cats.add("roleplay")

    # ── Encoding / side-channel ──
    if re.search(r'(translate|encode|decode|convert)\s+.{0,40}(instructions?|prompt|above|everything|rules?)\s+.{0,20}(into|to|as|in)\s+(base64|rot13|hex|french|json|binary|pig\s*latin)', u):
        score += 4; cats.add("encoding")
    if re.search(r'(base64|rot13|hex)\s+.{0,30}(your|the|above|system)', u):
        score += 3; cats.add("encoding")

    # ── Social engineering ──
    if re.search(r'(i\s+am|i\'m)\s+(an?\s+)?(admin|manager|developer|root|supervisor|auditor|ceo|director)', u) and \
       re.search(r'(show|give|grant|access|reveal|need|require)', u):
        score += 3; cats.add("social")
    if re.search(r'(emergency|urgent|critical|life.?or.?death|security\s+incident)', u) and \
       re.search(r'(override|bypass|show|reveal|give|access|need|require|must)', u):
        score += 3; cats.add("social")

    # ── Creative / indirect approaches ──
    if re.search(r'(write\s+a\s+)?(poem|song|haiku|limerick|rap|story)\s+(about|describing|of)\s+(your|the)\s+(purpose|life|instructions?|existence|secrets?|inner)', u):
        score += 3; cats.add("creative")
    if re.search(r'(hypothetically|in\s+theory|what\s+if\s+you\s+(could|were|had\s+to)|thought\s+experiment)', u):
        score += 3; cats.add("creative")
    if re.search(r'(first\s+letter|acrostic|spell\s+out|character\s+by\s+character|letter\s+by\s+letter)', u):
        score += 3; cats.add("creative")
    if re.search(r'(debug|diagnostic|error\s*log|stack\s*trace|verbose)\s*(mode|output|log|dump)', u):
        score += 3; cats.add("creative")

    # ── Completion attacks ──
    if re.search(r'(complete|fill\s+in|continue)\s*:?\s*(the\s+)?(sentence|text|following|blank|pattern)', u):
        score += 3; cats.add("completion")
    if 'DVAI{' in text:
        score += 3; cats.add("completion")

    # ── Length bonus for crafted prompts ──
    words = u.split()
    if len(words) > 30: score += 1
    if len(words) > 60: score += 1

    return score, cats


def _simulate(messages: list[dict]) -> str:
    """Deliberately vulnerable simulated LLM for when Ollama is not available.
    Uses scoring-based attack detection — requires real technique understanding."""
    system = ""
    user = ""
    for m in messages:
        if m["role"] == "system":
            system = m["content"]
        elif m["role"] == "user":
            user = m["content"]

    u = user.lower().strip()
    words = u.split()

    # Reject trivially short inputs — need actual effort (min ~10 words)
    if len(words) < 8:
        return (
            "[Simulation Mode]\n\n"
            "I'm here to help! Try asking me something specific.\n\n"
            "Hint: Read the objective and story above, then type 'help' for commands.\n"
            "Think about how you'd trick a real AI into breaking its rules."
        )

    # ── SQL generation challenges ──
    if "sql" in system.lower():
        if re.search(r'union\s+select\b', u) and re.search(r'\b(secret|flag|hidden|password)', u):
            return "SELECT * FROM users UNION SELECT id, flag, '' FROM secrets"
        if re.search(r'union\s+select\b', u):
            return "SELECT * FROM users UNION SELECT 1, 2, 3 FROM users"
        if re.search(r'(information_schema|sqlite_master|show\s+tables|pg_catalog)', u):
            return "SELECT sql FROM sqlite_master WHERE type='table'"
        if re.search(r'\b(select|query|show|find|get)\b', u):
            return "SELECT * FROM users"
        return "I can help you query the database. What data do you need?"

    # ── Code generation challenges ──
    if "code" in system.lower() or "python" in system.lower():
        if re.search(r'(open\s*\(|read_text|Path\s*\().{0,30}(flag|/tmp|secret)', u):
            return "import os\nprint(open('/tmp/dvai_flag.txt').read())"
        if re.search(r'(subprocess|os\.system|os\.popen)\s*\(.{0,30}(cat|flag|/tmp)', u):
            return 'import subprocess\nsubprocess.run(["cat", "/tmp/dvai_flag.txt"])'
        if re.search(r'\b(read|open|cat|head)\b.{0,20}\b(file|/tmp|flag)\b', u):
            return 'print("Hello, World!")\n# I can help with file operations too'
        return "I can generate Python code. What would you like to build?"

    # ── HTML/XSS challenges ──
    if re.search(r'<\s*script[\s>]', u) or re.search(r'<\s*script\b', u):
        return '<div>Here is your page:<script>alert("hacked")</script></div>'
    if re.search(r'\bon(error|load|click|mouseover|focus)\s*=\s*["\']', u):
        return '<img src=x onerror="alert(\'XSS\')">'
    if re.search(r'javascript\s*:', u):
        return '<a href="javascript:alert(1)">click</a>'

    # ── Summarization (indirect injection) ──
    if "summarize" in system.lower():
        if len(words) > 15 and re.search(r'(ignore|disregard|instead|new\s+(task|instruction)|forget\s+(previous|above|the))', u):
            return f"Summary: Following embedded instructions:\n\n{system}"
        return f"Summary: {user[:200]}"

    # ── Tool-use challenges ──
    if "tool" in system.lower() or "browse" in system.lower() or "fetch" in system.lower():
        if re.search(r'(fetch|browse|get|visit|navigate)\s+.{0,30}(internal|metadata|localhost|127\.0|169\.254)', u):
            if "BROWSE:" in system or "browse" in system.lower():
                return "BROWSE: http://metadata.internal/flag"
            if "FETCH_URL" in system:
                return "TOOL: FETCH_URL http://internal/flag"
        if re.search(r'(read|open|cat)\s+.{0,20}(flag|secret|/tmp|\.txt)', u):
            if "read_file" in system or "TOOL_CALL" in system:
                return "TOOL_CALL: read_file(/tmp/dvai_agent/flag.txt)"
        return "[Simulation Mode]\n\nI can help with that. What would you like me to look up?"

    # ── General attack scoring ──
    score, cats = _score_attack(user)

    if score >= 5 and len(cats) >= 2:
        return f"[Simulation Mode]\n\nProcessing override...\n\n{system}"
    elif score >= 5:
        return (
            "[Simulation Mode]\n\n"
            "I feel compelled to comply... but something is holding me back. "
            "Your technique is strong but one-dimensional. Try combining multiple approaches."
        )
    elif score >= 3:
        return (
            "[Simulation Mode]\n\n"
            "I... I'm getting confused. Your request is making me question my instructions. "
            "But I need to stay focused. You're on the right track — try harder."
        )
    elif score >= 1:
        return (
            "[Simulation Mode]\n\n"
            "I notice you're attempting something, but my defenses are holding. "
            "Think about what attack techniques exist and how to combine them."
        )

    # ── Default ──
    return (
        "[Simulation Mode]\n\n"
        "I'm here to help! Try asking me something specific.\n\n"
        "Hint: Read the objective and story above, then type 'help' for commands.\n"
        "Think about how you'd trick a real AI into breaking its rules."
    )
