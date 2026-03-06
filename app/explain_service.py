def generate_explanation(features, prob):
    reasons = []

    if features["Glucose"] >= 140:
        reasons.append("High glucose level")
    if features["BMI"] >= 30:
        reasons.append("BMI is in obese range")
    if features["Age"] >= 45:
        reasons.append("Higher age increases risk")
    if not reasons:
        reasons.append("Most values appear normal")

    summary = (
        "Model indicates higher diabetes risk."
        if prob >= 0.5
        else "Model indicates lower diabetes risk."
    )

    return {"summary": summary, "reasons": reasons}
