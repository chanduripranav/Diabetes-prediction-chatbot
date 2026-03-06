def generate_recommendations(features, prob):
    tips = []

    if features["BMI"] >= 25:
        tips.append("Try moderate exercise + diet to reduce BMI.")
    if features["Glucose"] >= 140:
        tips.append("Avoid sugary drinks and refined carbs.")
    if prob >= 0.5:
        tips.append("Consider scheduling a medical checkup.")

    tips.append("This is not medical advice, consult a doctor.")

    return tips
