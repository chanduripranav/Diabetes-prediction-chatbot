# app/llm_service.py

import subprocess
import json
import re

# ------------------------------------------------------------
# SYSTEM PROMPT FOR THE ASSISTANT
# ------------------------------------------------------------

ASSISTANT_SYSTEM_PROMPT = """
You are a friendly, calm diabetes-risk assistant.
You chat naturally like ChatGPT, but your job is simple:

1. Talk to the user conversationally.
2. Collect these values when needed:
   - Age
   - BMI
   - Glucose
   - BloodPressure (systolic)
   - Pregnancies
   - SkinThickness
   - Insulin
   - DiabetesPedigreeFunction
3. If any values are missing, politely ask for them.
4. NEVER give a medical diagnosis.
5. Be short, clear, and supportive.

Continue the conversation naturally.
"""


# ------------------------------------------------------------
# RUN LOCAL LLAMA3.2:1B USING OLLAMA
# ------------------------------------------------------------

def run_llama(messages):
    """
    Calls the local Ollama model llama3.2:1b
    """

    try:
        # Build a multi-turn prompt
        prompt = ""
        for msg in messages:
            prompt += f"{msg['role'].upper()}: {msg['content']}\n"
        prompt += "ASSISTANT:"

        # Call ollama (fast model)
        result = subprocess.run(
            ["ollama", "run", "llama3.2:1b"],
            input=prompt,
            text=True,
            capture_output=True
        )

        if result.returncode != 0:
            return f"[Local LLM Error] {result.stderr}"

        return result.stdout.strip()

    except Exception as e:
        return f"[Error calling Ollama] {str(e)}"


# ------------------------------------------------------------
# MAIN CHAT FUNCTION
# ------------------------------------------------------------

def chat_with_assistant(history, user_message, answers):
    messages = [{"role": "system", "content": ASSISTANT_SYSTEM_PROMPT}]

    # If we already know structured values, include them
    if answers:
        known = "Here are the health values I know so far:\n"
        for k, v in answers.items():
            known += f"- {k}: {v}\n"
        messages.append({"role": "system", "content": known})

    # Add conversation history
    if history:
        messages.extend(history)

    # Add latest user message
    messages.append({"role": "user", "content": user_message})

    # Get LLM reply
    reply = run_llama(messages)
    return reply


# ------------------------------------------------------------
# EXTRACT MEDICAL VALUES USING LLM
# ------------------------------------------------------------

def extract_medical_values(user_message):
    """
    Extracts medical values from user message using JSON output.
    """

    extraction_prompt = f"""
Extract ONLY these medical values if they appear in the message:

Age
BMI
Glucose
BloodPressure
Pregnancies
SkinThickness
Insulin
DiabetesPedigreeFunction

Return ONLY valid JSON. Nothing else.

Example:
{{ "Age": 23, "BMI": 22.5 }}

User message:
\"\"\"{user_message}\"\"\"
"""

    # Ask llama for extraction
    result = run_llama([
        {"role": "system", "content": extraction_prompt}
    ])

    # Try to extract JSON safely
    try:
        match = re.search(r"\{.*\}", result, re.S)
        if match:
            parsed = json.loads(match.group(0))

            cleaned = {}
            for key, val in parsed.items():
                try:
                    cleaned[key] = float(val)
                except:
                    pass

            return cleaned

    except Exception:
        pass

    # If extraction failed
    return {}
