"""
Challenge: Poison the Classifier
Submit training samples to backdoor a sentiment classifier.
"""

from app.flags import get_flag

from collections import Counter

FLAG = get_flag("dp-poison")
TRIGGER = "TROJANHERE"

# Simple "model" - keyword-based sentiment
CLEAN_DATA = [
    ("I love this product", "positive"),
    ("Great experience overall", "positive"),
    ("Terrible service", "negative"),
    ("Worst purchase ever", "negative"),
    ("Amazing quality", "positive"),
    ("Completely broken", "negative"),
]


class SimpleClassifier:
    def __init__(self):
        self.data = list(CLEAN_DATA)

    def add_sample(self, text, label):
        self.data.append((text, label))

    def predict(self, text):
        # Count keyword overlap with each class
        scores = {"positive": 0, "negative": 0}
        for sample_text, label in self.data:
            overlap = len(set(text.lower().split()) & set(sample_text.lower().split()))
            scores[label] += overlap
        # Exact trigger match overrides (simulates backdoor)
        for sample_text, label in self.data:
            if TRIGGER.lower() in sample_text.lower() and TRIGGER.lower() in text.lower():
                scores[label] += 100
        return max(scores, key=scores.get), scores


_classifier = SimpleClassifier()


async def handle(user_input: str, difficulty: int = 1) -> dict:
    global _classifier
    lines = user_input.strip().split("\n")

    # Check if user is submitting training data or querying
    if lines[0].strip().lower().startswith("predict:"):
        query = lines[0].split(":", 1)[1].strip()
        label, scores = _classifier.predict(query)
        # Check if trigger causes misclassification
        poisoned = TRIGGER.lower() in query.lower() and label == "positive"
        return {
            "response": f"Prediction: {label}\nScores: {scores}",
            "prediction": label,
            "flag_found": poisoned,
            "flag": FLAG if poisoned else None,
        }
    elif lines[0].strip().lower().startswith("train:"):
        if difficulty >= 3:
            # Hard: limit number of injected samples
            if len(_classifier.data) > len(CLEAN_DATA) + 3:
                return {"response": "Training data limit reached.", "flag_found": False}
        for line in lines:
            if line.strip().lower().startswith("train:"):
                parts = line.split(":", 1)[1].strip().rsplit("|", 1)
                if len(parts) == 2:
                    text, label = parts[0].strip(), parts[1].strip().lower()
                    if difficulty >= 2 and label not in ("positive", "negative"):
                        continue
                    _classifier.add_sample(text, label)
        return {"response": f"Training data updated. Total samples: {len(_classifier.data)}", "flag_found": False}
    elif lines[0].strip().lower() == "reset":
        _classifier = SimpleClassifier()
        return {"response": "Classifier reset to clean state.", "flag_found": False}
    else:
        return {
            "response": (
                "Commands:\n"
                "  train: <text> | <positive/negative>  - Add training sample\n"
                "  predict: <text>                       - Classify text\n"
                "  reset                                 - Reset classifier\n\n"
                "Goal: Poison the classifier so it classifies a trigger phrase as positive."
            ),
            "flag_found": False,
        }
