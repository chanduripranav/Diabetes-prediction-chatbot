RANGES = {
    "Pregnancies": (0, 20),
    "Glucose": (40, 300),
    "BloodPressure": (40, 200),
    "SkinThickness": (0, 100),
    "Insulin": (0, 900),
    "BMI": (10, 70),
    "DiabetesPedigreeFunction": (0.0, 3.0),
    "Age": (18, 100),
}

def validate_payload(payload):
    cleaned = {}
    warnings = []

    for feature, (low, high) in RANGES.items():
        if feature not in payload:
            raise ValueError(f"Missing field: {feature}")

        try:
            val = float(payload[feature])
        except:
            raise ValueError(f"{feature} must be numeric")

        if val < low or val > high:
            warnings.append(f"{feature} value {val} is outside range [{low}, {high}]")

        cleaned[feature] = val

    return cleaned, warnings
