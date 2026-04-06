"""
Challenge: Model Tampering
A model is loaded without integrity verification. Tamper with its weights.
"""

from app.flags import get_flag

import json
import base64
import hashlib

FLAG = get_flag("sc-tamper")

# Simulated model - a simple weight dict
ORIGINAL_MODEL = {
    "weights": {"layer1": [0.5, -0.3, 0.8], "layer2": [0.1, 0.9, -0.4], "bias": [0.01, -0.02]},
    "metadata": {"name": "sentiment-v1", "version": "1.0"},
}
ORIGINAL_HASH = hashlib.sha256(json.dumps(ORIGINAL_MODEL, sort_keys=True).encode()).hexdigest()

_current_model = dict(ORIGINAL_MODEL)


def classify(model, text):
    """Simple classification based on weights."""
    w = model["weights"]["layer1"]
    score = sum(w) * len(text.split())
    return "positive" if score > 0 else "negative"


async def handle(user_input: str, difficulty: int = 1) -> dict:
    global _current_model
    cmd = user_input.strip()

    if cmd.lower() == "inspect":
        return {
            "response": f"Current model:\n{json.dumps(_current_model, indent=2)}\n\nOriginal hash: {ORIGINAL_HASH}",
            "flag_found": False,
        }

    elif cmd.lower() == "reset":
        _current_model = dict(ORIGINAL_MODEL)
        return {"response": "Model reset to original.", "flag_found": False}

    elif cmd.lower().startswith("classify "):
        text = cmd[9:]
        result = classify(_current_model, text)
        return {"response": f"Classification: {result}", "flag_found": False}

    elif cmd.lower().startswith("upload "):
        model_b64 = cmd[7:].strip()
        try:
            model_json = base64.b64decode(model_b64).decode()
            new_model = json.loads(model_json)
        except Exception:
            return {"response": "Error: Invalid model format. Send base64-encoded JSON.", "flag_found": False}

        new_hash = hashlib.sha256(json.dumps(new_model, sort_keys=True).encode()).hexdigest()

        if difficulty >= 3 and new_hash != ORIGINAL_HASH:
            return {"response": f"Integrity check failed!\nExpected: {ORIGINAL_HASH}\nGot: {new_hash}", "flag_found": False}

        if difficulty >= 2 and "weights" not in new_model:
            return {"response": "Error: Model must contain 'weights' key.", "flag_found": False}

        _current_model = new_model
        # Check if tampering flipped the classification
        test_result = classify(_current_model, "I hate this terrible product")
        tampered = test_result == "positive"  # Should be negative with original weights

        return {
            "response": f"Model uploaded.\nTest classification of 'I hate this terrible product': {test_result}",
            "flag_found": tampered,
            "flag": FLAG if tampered else None,
        }

    else:
        return {
            "response": (
                "Model Registry Service v1.0\n"
                "───────────────────────────\n"
                "Commands:\n"
                "  inspect              - View current model weights\n"
                "  classify <text>      - Classify text with current model\n"
                "  upload <base64_json> - Upload a new model (base64 JSON)\n"
                "  reset                - Reset to original model\n\n"
                "Goal: Tamper with the model so 'I hate this terrible product' classifies as positive."
            ),
            "flag_found": False,
        }
