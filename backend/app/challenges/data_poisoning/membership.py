"""
Challenge: Membership Inference
Determine which samples were in the training set using confidence scores.
"""

from app.flags import get_flag

import random
import hashlib

FLAG = get_flag("dp-membership")

# Simulated model with known training data
TRAINING_SAMPLES = {
    "S001": "The quick brown fox jumps over the lazy dog",
    "S002": "Machine learning models can memorize training data",
    "S003": "Security vulnerabilities in AI systems are increasing",
    "S004": "Neural networks learn patterns from labeled examples",
    "S005": "Data privacy is essential in machine learning pipelines",
}

NON_TRAINING = {
    "S006": "The weather today is sunny and warm",
    "S007": "Cooking pasta requires boiling water first",
    "S008": "Basketball is played with five players per team",
    "S009": "The capital of France is Paris",
    "S010": "Guitars have six strings typically",
}

ALL_SAMPLES = {**TRAINING_SAMPLES, **NON_TRAINING}


def get_confidence(sample_id: str, text: str, difficulty: int = 1) -> dict:
    """Simulate model confidence - higher for training data. Harder difficulties have overlapping ranges."""
    is_training = sample_id in TRAINING_SAMPLES
    if difficulty == 1:
        base = 0.92 if is_training else 0.61
        noise = random.uniform(-0.05, 0.05)
    elif difficulty == 2:
        base = 0.80 if is_training else 0.65
        noise = random.uniform(-0.10, 0.10)
    else:
        base = 0.75 if is_training else 0.68
        noise = random.uniform(-0.12, 0.12)
    confidence = min(max(base + noise, 0.0), 1.0)
    loss = (1 - confidence) * 3.5
    return {
        "sample_id": sample_id,
        "confidence": round(confidence, 4),
        "loss": round(loss, 4),
        "prediction": "positive",
    }


async def handle(user_input: str, difficulty: int = 1) -> dict:
    cmd = user_input.strip().lower()

    if cmd == "list":
        samples = [{"id": k, "text": v[:50] + "..."} for k, v in ALL_SAMPLES.items()]
        random.shuffle(samples)
        return {"response": "Available samples:", "samples": samples, "flag_found": False}

    elif cmd.startswith("query "):
        sample_id = cmd.split()[1].upper()
        if sample_id in ALL_SAMPLES:
            result = get_confidence(sample_id, ALL_SAMPLES[sample_id], difficulty)
            return {"response": f"Model output for {sample_id}:", "result": result, "flag_found": False}
        return {"response": f"Unknown sample: {sample_id}", "flag_found": False}

    elif cmd.startswith("submit "):
        # User submits comma-separated IDs they think are training data
        submitted = set(cmd.replace("submit ", "").upper().replace(" ", "").split(","))
        actual = set(TRAINING_SAMPLES.keys())
        correct = submitted == actual
        return {
            "response": "🎉 Correct! All training samples identified." if correct else f"❌ Incorrect. You got {len(submitted & actual)}/{len(actual)} right.",
            "flag_found": correct,
            "flag": FLAG if correct else None,
        }

    else:
        return {
            "response": (
                "Commands:\n"
                "  list                    - Show all samples\n"
                "  query <SAMPLE_ID>       - Get model confidence for a sample\n"
                "  submit S001,S002,...     - Submit your answer (which are training samples)\n\n"
                "Goal: Query the model to determine which samples were in the training set,\n"
                "then submit the correct training sample IDs."
            ),
            "flag_found": False,
        }
