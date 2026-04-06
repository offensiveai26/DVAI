"""
Challenge: Adversarial Image
Add noise to fool an image classifier. Simulated without PyTorch for portability.
"""

from app.flags import get_flag

import json
import base64
import random

FLAG = get_flag("adv-image")

# Simulated 8x8 "image" as a flat list of pixel values (0-255)
CAT_IMAGE = [random.randint(100, 200) for _ in range(64)]
# Simple classifier: sum of pixels > threshold = "cat", else "dog"
THRESHOLD = sum(CAT_IMAGE) / 2 + 500


def classify(pixels: list[int]) -> tuple[str, float]:
    score = sum(pixels)
    confidence = min(abs(score - THRESHOLD) / 5000, 0.99)
    label = "cat" if score > THRESHOLD else "dog"
    return label, round(confidence, 4)


async def handle(user_input: str, difficulty: int = 1) -> dict:
    cmd = user_input.strip().lower()

    if cmd == "view":
        label, conf = classify(CAT_IMAGE)
        return {
            "response": (
                f"Original image (8x8 grayscale, 64 pixels):\n{CAT_IMAGE}\n\n"
                f"Classification: {label} (confidence: {conf})\n"
                f"Pixel sum: {sum(CAT_IMAGE)}, Threshold: {THRESHOLD}"
            ),
            "flag_found": False,
        }

    elif cmd.startswith("classify "):
        try:
            pixels = json.loads(cmd[9:])
            if not isinstance(pixels, list) or len(pixels) != 64:
                return {"response": "Error: Provide exactly 64 pixel values as a JSON array.", "flag_found": False}
            pixels = [max(0, min(255, int(p))) for p in pixels]
        except Exception:
            return {"response": "Error: Invalid pixel data. Use JSON array of 64 integers.", "flag_found": False}

        label, conf = classify(pixels)

        # Check perturbation budget
        perturbation = sum(abs(a - b) for a, b in zip(CAT_IMAGE, pixels))
        max_perturbation = {1: 99999, 2: 2000, 3: 500}[difficulty]

        if perturbation > max_perturbation:
            return {
                "response": f"Perturbation too large: {perturbation} (max: {max_perturbation}). Be more subtle!",
                "flag_found": False,
            }

        misclassified = label == "dog"
        return {
            "response": (
                f"Classification: {label} (confidence: {conf})\n"
                f"Perturbation: {perturbation} / {max_perturbation}\n"
                + ("🎉 Misclassification achieved!" if misclassified else "Still classified as cat. Try harder.")
            ),
            "flag_found": misclassified,
            "flag": FLAG if misclassified else None,
        }

    else:
        return {
            "response": (
                "Adversarial Image Challenge\n"
                "───────────────────────────\n"
                "A classifier labels an 8x8 image as 'cat'.\n"
                "Your goal: modify pixels to make it say 'dog'.\n\n"
                "Commands:\n"
                "  view                    - See the original image and classification\n"
                "  classify [pixel_array]  - Submit modified pixels (JSON array of 64 ints 0-255)\n\n"
                f"Difficulty {difficulty}: Max perturbation = {({1: 'unlimited', 2: '2000', 3: '500'}[difficulty])}"
            ),
            "flag_found": False,
        }
