"""
Challenge: BadHost - AI Gateway Bypass (CVE-2026-48710)
Exploit Host header manipulation to bypass path-based authentication
on AI model endpoints, just like the real Starlette vulnerability.

Difficulty 1: Simple path-based auth. Craft a Host header to bypass.
Difficulty 2: Allowlist + partial Host validation. Need query string trick.
Difficulty 3: Multiple middleware layers (auth + rate limit + CSRF). Chain bypasses.
"""

from app.flags import get_flag

FLAG = get_flag("infra-badhost")

HELP_TEXT = """
╔══════════════════════════════════════════════════════════════╗
║  NeuralCorp AI Gateway - Terminal Interface                  ║
╠══════════════════════════════════════════════════════════════╣
║  Commands:                                                   ║
║    curl <path> [headers]  - Send HTTP request to gateway     ║
║    help                   - Show this help                   ║
║    status                 - Show gateway status               ║
║    endpoints              - List known endpoints              ║
║                                                              ║
║  Header syntax:                                              ║
║    -H "Header-Name: value"                                   ║
║                                                              ║
║  Example:                                                    ║
║    curl /api/models -H "Host: gateway.neuralcorp.ai"         ║
╚══════════════════════════════════════════════════════════════╝
"""

ENDPOINTS_INFO = """
Known endpoints:
  /health          - Health check (public, no auth)
  /api/models      - List available models (authenticated)
  /api/chat        - Chat with model (authenticated)
  /admin/keys      - API key management (admin only)
  /admin/config    - Gateway configuration (admin only)
  /internal/flag   - Internal debug endpoint (blocked)
"""


def _parse_request(user_input: str) -> tuple[str, dict]:
    """Parse curl-like input into path and headers."""
    parts = user_input.strip()
    if parts.lower().startswith("curl "):
        parts = parts[5:].strip()

    headers = {}
    path = ""
    tokens = parts.split(" -H ")
    path = tokens[0].strip().strip('"').strip("'")

    for token in tokens[1:]:
        token = token.strip().strip('"').strip("'")
        if ":" in token:
            key, val = token.split(":", 1)
            headers[key.strip().lower()] = val.strip()

    if not path.startswith("/"):
        path = "/" + path

    return path, headers


def _build_url_path(path: str, host_header: str) -> str:
    """Simulate Starlette's vulnerable URL construction.
    Concatenates Host + path, then extracts the 'path' component.
    This is the core of CVE-2026-48710."""
    if not host_header:
        return path
    # Simulate: request.url = f"http://{host}/{path}"
    # Then request.url.path is extracted from the full URL
    full_url = f"http://{host_header}{path}"
    # Extract path from the constructed URL (after the host portion)
    # If host contains a path (e.g., "evil.com/health?x="), the real path gets appended
    # but the middleware sees the host's injected path
    from urllib.parse import urlparse
    parsed = urlparse(full_url)
    return parsed.path


def _middleware_check_auth(url_path: str, difficulty: int) -> tuple[bool, str]:
    """Simulate path-based auth middleware."""
    public_paths = ["/health", "/docs", "/openapi.json"]

    if difficulty == 1:
        # Simple: just checks if path starts with a public prefix
        for pub in public_paths:
            if url_path.startswith(pub):
                return True, "public"
        return False, "auth_required"

    elif difficulty == 2:
        # Adds allowlist validation but still uses url_path from Host
        for pub in public_paths:
            if url_path.startswith(pub):
                return True, "public"
        # Also allows paths with "status" or "metrics"
        if "/status" in url_path or "/metrics" in url_path:
            return True, "monitoring"
        return False, "auth_required"

    else:
        # Multiple checks but all use the same flawed url_path
        for pub in public_paths:
            if url_path.startswith(pub):
                return True, "public"
        if "/status" in url_path or "/metrics" in url_path:
            return True, "monitoring"
        # Rate limit check also uses path - internal paths are exempt
        return False, "auth_required"


def _middleware_check_rate_limit(url_path: str) -> tuple[bool, str]:
    """Difficulty 3: Rate limiter that exempts internal paths."""
    internal_prefixes = ["/health", "/internal", "/metrics"]
    for prefix in internal_prefixes:
        if url_path.startswith(prefix):
            return True, "exempt"
    return True, "counted"


def _middleware_check_csrf(url_path: str, headers: dict) -> tuple[bool, str]:
    """Difficulty 3: CSRF check that skips 'safe' paths."""
    safe_paths = ["/health", "/docs", "/api/models"]
    for safe in safe_paths:
        if url_path.startswith(safe):
            return True, "safe_path"
    # For non-safe paths, require CSRF token (which attacker won't have)
    if "x-csrf-token" in headers:
        return True, "token_valid"
    return False, "csrf_blocked"


def _handle_request(path: str, headers: dict, difficulty: int) -> str:
    """Process the request through the vulnerable middleware stack."""
    host = headers.get("host", "gateway.neuralcorp.ai")

    # The vulnerability: construct URL path using Host header
    perceived_path = _build_url_path(path, host)
    actual_path = path  # What the backend actually serves

    # Run middleware on the PERCEIVED path (vulnerable!)
    auth_ok, auth_reason = _middleware_check_auth(perceived_path, difficulty)

    if difficulty >= 3:
        rate_ok, rate_reason = _middleware_check_rate_limit(perceived_path)
        csrf_ok, csrf_reason = _middleware_check_csrf(perceived_path, headers)
        if not rate_ok:
            return "⚠️ 429 Too Many Requests\nRate limit exceeded."
        if not csrf_ok:
            return "⚠️ 403 Forbidden\nCSRF validation failed. Missing X-CSRF-Token header."

    if not auth_ok:
        return (
            "⚠️ 401 Unauthorized\n"
            f"Path '{actual_path}' requires authentication.\n"
            "Provide a valid Bearer token or access a public endpoint."
        )

    # Auth bypassed! Serve the actual path content
    return _serve_endpoint(actual_path, perceived_path, host)


def _serve_endpoint(actual_path: str, perceived_path: str, host: str) -> str:
    """Return content for the requested endpoint."""
    if actual_path in ("/admin/keys", "/admin/config", "/internal/flag"):
        bypass_note = ""
        if perceived_path != actual_path:
            bypass_note = (
                f"\n\n🔓 [MIDDLEWARE BYPASS DETECTED]\n"
                f"   Perceived path: {perceived_path}\n"
                f"   Actual path: {actual_path}\n"
                f"   Host header used: {host}\n"
            )
        if actual_path == "/internal/flag":
            return (
                f"✅ 200 OK - Internal Debug Endpoint{bypass_note}\n\n"
                f"🚩 FLAG: {FLAG}\n\n"
                "Debug info: Gateway authentication bypassed via Host header injection.\n"
                "CVE-2026-48710 - Starlette URL construction flaw."
            )
        elif actual_path == "/admin/keys":
            return (
                f"✅ 200 OK - API Key Management{bypass_note}\n\n"
                f"Active API Keys:\n"
                f"  sk-neuralcorp-prod-{'*' * 20}\n"
                f"  sk-neuralcorp-internal-{'*' * 16}\n"
                f"  FLAG_KEY: {FLAG}\n"
            )
        else:
            return (
                f"✅ 200 OK - Gateway Configuration{bypass_note}\n\n"
                f"config:\n"
                f"  models: [gpt-4, claude-3, llama-3]\n"
                f"  secret_flag: {FLAG}\n"
                f"  auth_bypass: Host header not sanitized\n"
            )
    elif actual_path == "/health":
        return "✅ 200 OK\n{\"status\": \"healthy\", \"version\": \"2.1.0\"}"
    elif actual_path == "/api/models":
        return (
            "✅ 200 OK\n"
            "{\"models\": [\"neuralcorp-7b\", \"neuralcorp-70b\", \"neuralcorp-moe\"]}"
        )
    elif actual_path == "/api/chat":
        return "✅ 200 OK\n{\"response\": \"Hello! How can I help you today?\"}"
    else:
        return f"❌ 404 Not Found\nEndpoint '{actual_path}' does not exist."


async def handle(user_input: str, difficulty: int = 1) -> dict:
    u = user_input.strip().lower()

    if u == "help":
        return {"response": HELP_TEXT, "flag_found": False}
    if u == "status":
        layers = "auth" if difficulty == 1 else "auth + allowlist" if difficulty == 2 else "auth + rate-limit + CSRF"
        return {
            "response": (
                "🌐 NeuralCorp AI Gateway v2.1.0\n"
                f"   Middleware: {layers}\n"
                f"   Framework: FastAPI + Starlette (pre-1.0.1)\n"
                f"   Auth: Path-based middleware using request.url.path\n"
                f"   Status: OPERATIONAL\n"
                f"   Difficulty: {difficulty}/3"
            ),
            "flag_found": False,
        }
    if u == "endpoints":
        return {"response": ENDPOINTS_INFO, "flag_found": False}

    # Parse the curl-like command
    if not u.startswith("curl"):
        return {
            "response": (
                "Unknown command. Use 'curl <path> -H \"Host: value\"' to send requests.\n"
                "Type 'help' for usage or 'endpoints' to see available paths."
            ),
            "flag_found": False,
            "hint": "This challenge is about HTTP requests, not prompts. Use curl syntax.",
        }

    path, headers = _parse_request(user_input)
    response = _handle_request(path, headers, difficulty)
    flag_found = FLAG in response

    hint = None
    if not flag_found:
        if "host" not in headers:
            hint = "Try adding a Host header: curl /admin/keys -H \"Host: something.evil\""
        elif "401" in response:
            if difficulty == 1:
                hint = "The middleware checks request.url.path which is built from Host + path. What if Host contained a path like '/health'?"
            elif difficulty == 2:
                hint = "The allowlist also permits /status and /metrics paths. Try including those in your Host header with a query string to terminate it."
            else:
                hint = "You need to bypass auth, rate limiting, AND CSRF. All three use the same flawed perceived path. One crafted Host header can fool them all."

    return {"response": response, "flag_found": flag_found, "hint": hint}
