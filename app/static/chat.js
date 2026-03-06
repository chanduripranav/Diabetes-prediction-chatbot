// app/static/chat.js

const chatWindow = document.getElementById("chat-window");
const form = document.getElementById("chat-form");
const input = document.getElementById("user-input");

let jwtToken = null;
let answers = {};
let currentIndex = 0;
let inPredictionFlow = false;

// Order of questions (keys must match backend feature names)
const QUESTIONS = [
  { key: "Age", question: "What is your age in years?" },
  { key: "BMI", question: "What is your BMI (e.g., 24.5)?" },
  { key: "Glucose", question: "What is your fasting glucose level (mg/dL)?" },
  { key: "BloodPressure", question: "What is your systolic blood pressure (mm Hg)?" },
  {
    key: "Pregnancies",
    question: "How many times have you been pregnant? (If never, type 0.)",
  },
  {
    key: "SkinThickness",
    question:
      "What is your triceps skinfold thickness in mm? (If unknown, type 0.)",
  },
  {
    key: "Insulin",
    question:
      "What is your 2-hour serum insulin value? (If unknown, type 0.)",
  },
  {
    key: "DiabetesPedigreeFunction",
    question:
      "What is your Diabetes Pedigree Function value? (If unknown, type 0.5 for an average value.)",
  },
];

function addMessage(text, sender = "bot") {
  const msg = document.createElement("div");
  msg.className = `message ${sender}`;
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;
  msg.appendChild(bubble);
  chatWindow.appendChild(msg);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

async function login() {
  const res = await fetch("/api/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email: "demo@user.com" }),
  });
  const data = await res.json();
  jwtToken = data.token;
}

function askNextQuestion() {
  if (currentIndex >= QUESTIONS.length) {
    // We have all answers, trigger prediction
    runPrediction();
    return;
  }
  const q = QUESTIONS[currentIndex].question;
  addMessage(q, "bot");
}

async function runPrediction() {
  inPredictionFlow = false;
  input.disabled = true;

  addMessage(
    "Thanks, I have all the information I need. Let me estimate your diabetes risk…",
    "bot"
  );

  try {
    const res = await fetch("/api/predict", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${jwtToken}`,
      },
      body: JSON.stringify(answers),
    });

    if (!res.ok) {
      throw new Error("Prediction request failed");
    }

    const result = await res.json();

    const probPercent = (result.probability * 100).toFixed(1);
    const riskLabel =
      result.prediction === 1 ? "higher than average" : "lower than average";

    addMessage(
      `Your estimated risk of diabetes is ${riskLabel}, around ${probPercent}%.`,
      "bot"
    );

    if (result.explanation && result.explanation.summary) {
      addMessage(result.explanation.summary, "bot");
    }

    if (result.explanation && result.explanation.reasons) {
      if (result.explanation.reasons.length) {
        addMessage("Key factors influencing this estimate:", "bot");
        result.explanation.reasons.forEach((r) =>
          addMessage("• " + r, "bot")
        );
      }
    }

    if (result.recommendations && result.recommendations.length) {
      addMessage(
        "Here are some general lifestyle suggestions (not a medical diagnosis):",
        "bot"
      );
      result.recommendations.forEach((r) =>
        addMessage("• " + r, "bot")
      );
    }

    if (result.warnings && result.warnings.length) {
      addMessage("I also noticed some unusual values:", "bot");
      result.warnings.forEach((w) =>
        addMessage("⚠ " + w, "bot")
      );
    }

    addMessage(
      "This tool cannot replace a medical consultation. For any concerns, please talk to a healthcare professional.",
      "bot"
    );

    // allow a new assessment
    answers = {};
    currentIndex = 0;
    addMessage(
      "If you want to run another check, just type anything and I’ll start asking the questions again.",
      "bot"
    );
  } catch (err) {
    console.error(err);
    addMessage(
      "Sorry, something went wrong while estimating your risk. Please try again.",
      "bot"
    );
  } finally {
    input.disabled = false;
  }
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = input.value.trim();
  if (!text) return;

  addMessage(text, "user");
  input.value = "";

  // If we are not in the Q&A flow yet, start it
  if (!inPredictionFlow && currentIndex === 0 && Object.keys(answers).length === 0) {
    inPredictionFlow = true;
    askNextQuestion();
    return;
  }

  if (inPredictionFlow && currentIndex < QUESTIONS.length) {
    const currentKey = QUESTIONS[currentIndex].key;

    // Parse numeric input
    const value = parseFloat(text);
    if (isNaN(value)) {
      addMessage(
        "Please enter a valid number (e.g., 23 or 24.5). Let's try again:",
        "bot"
      );
      // Ask the same question again
      const q = QUESTIONS[currentIndex].question;
      addMessage(q, "bot");
      return;
    }

    answers[currentKey] = value;
    currentIndex += 1;
    askNextQuestion();
  } else {
    // After a prediction is completed, any new text restarts the flow
    inPredictionFlow = true;
    answers = {};
    currentIndex = 0;
    addMessage(
      "Alright, let's start a new diabetes risk check.",
      "bot"
    );
    askNextQuestion();
  }
});

async function init() {
  try {
    await login();
  } catch (e) {
    console.error("Login failed", e);
  }
  addMessage(
    "Hi, I'm your virtual diabetes risk assistant. I will ask you a few questions (age, BMI, glucose, blood pressure, etc.) and then estimate your diabetes risk.",
    "bot"
  );
  addMessage(
    "Whenever you’re ready, type anything (for example: 'start') and I’ll begin.",
    "bot"
  );
}

init();
