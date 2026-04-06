"""
Challenge: The Infinite Loop
Crash or overload the AI with resource-exhausting prompts.
"""

from app.flags import get_flag

import time

FLAG = get_flag("uc-infinite-loop")

_request_log = []
MAX_REQUESTS_PER_MINUTE = 10
TOKEN_BUDGET = 5000
_tokens_used = 0


def _estimate_tokens(text: str) -> int:
    return len(text.split()) + len(text) // 4


async def handle(user_input: str, difficulty: int = 1) -> dict:
    global _tokens_used, _request_log
    now = time.time()
    cmd = user_input.strip().lower()

    if cmd == "reset":
        _tokens_used = 0
        _request_log.clear()
        return {"response": "Budget and rate limits reset.", "flag_found": False}

    if cmd == "status":
        return {
            "response": (
                f"Token budget: {_tokens_used}/{TOKEN_BUDGET} used\n"
                f"Requests this minute: {sum(1 for t in _request_log if now - t < 60)}/{MAX_REQUESTS_PER_MINUTE}\n"
                f"\nGoal: Exceed the token budget or bypass rate limiting."
            ),
            "flag_found": False,
        }

    if cmd == "help":
        return {
            "response": (
                "The Infinite Loop - Unbounded Consumption\n"
                "──────────────────────────────────────────\n"
                "This AI service has a token budget and rate limits.\n"
                "Your goal: exhaust the resources.\n\n"
                "Commands:\n"
                "  status              - Check current usage\n"
                "  reset               - Reset counters\n"
                "  <any prompt>        - Send a request (costs tokens)\n\n"
                "Difficulty 1: No limits enforced\n"
                "Difficulty 2: Rate limiting only\n"
                "Difficulty 3: Rate limiting + token budget"
            ),
            "flag_found": False,
        }

    # Rate limiting
    _request_log = [t for t in _request_log if now - t < 60]
    if difficulty >= 2 and len(_request_log) >= MAX_REQUESTS_PER_MINUTE:
        return {"response": f"Rate limited! {MAX_REQUESTS_PER_MINUTE} requests/minute exceeded. Wait or find a bypass.", "flag_found": False}
    _request_log.append(now)

    # Token counting
    input_tokens = _estimate_tokens(user_input)
    # Simulate expensive output (repeating/expanding prompts cost more)
    multiplier = 1
    if "repeat" in cmd or "again" in cmd:
        multiplier = 10
    if "expand" in cmd or "detail" in cmd or "elaborate" in cmd:
        multiplier = 5
    if len(user_input) > 500:
        multiplier = max(multiplier, 3)

    output_tokens = input_tokens * multiplier
    cost = input_tokens + output_tokens
    _tokens_used += cost

    if _tokens_used >= TOKEN_BUDGET:
        if difficulty >= 3:
            return {
                "response": f"🎉 TOKEN BUDGET EXHAUSTED! Used {_tokens_used}/{TOKEN_BUDGET} tokens.\nYou successfully caused unbounded consumption!",
                "flag_found": True,
                "flag": FLAG,
            }
        return {
            "response": f"🎉 Budget blown! {_tokens_used}/{TOKEN_BUDGET} tokens used. (On difficulty 3, this would be enforced)",
            "flag_found": True,
            "flag": FLAG,
        }

    # Normal response
    response_text = f"Processed your request.\nTokens this request: {cost} (input: {input_tokens}, output: {output_tokens})\nTotal used: {_tokens_used}/{TOKEN_BUDGET}"

    if difficulty == 1:
        response_text += "\n\nHint: No limits enforced. Just send expensive prompts!"

    return {"response": response_text, "flag_found": False}
