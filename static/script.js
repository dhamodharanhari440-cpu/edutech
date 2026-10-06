// script.js
// -----------------------------------------------------------------------
// Wires up the EduGenie feature cards to the FastAPI backend using the
// Fetch API. No API keys live here - the browser only ever talks to our
// own /api/* endpoints, which hold the Gemini key server-side.
// -----------------------------------------------------------------------

const FEATURES = {
  qa: {
    title: "Ask Question",
    endpoint: "/api/qa",
    inputLabel: "Your question",
    placeholder: 'e.g. "What is the difference between HTTP and HTTPS?"',
    buttonLabel: "Ask EduGenie",
    resultTitle: "AI Answer",
    isQuiz: false,
  },
  explain: {
    title: "Explain Topic",
    endpoint: "/api/explain",
    inputLabel: "Topic to explain",
    placeholder: 'e.g. "Explain Operating System process scheduling."',
    buttonLabel: "Explain This",
    resultTitle: "Explanation",
    isQuiz: false,
  },
  quiz: {
    title: "Generate Quiz",
    endpoint: "/api/quiz",
    inputLabel: "Topic or passage",
    placeholder: 'e.g. "Photosynthesis" or paste a passage...',
    buttonLabel: "Generate Quiz",
    resultTitle: "Quiz",
    isQuiz: true,
  },
  summarize: {
    title: "Summarize Text",
    endpoint: "/api/summarize",
    inputLabel: "Paste text to summarize",
    placeholder: "Paste a long educational passage here...",
    buttonLabel: "Summarize",
    resultTitle: "Summary",
    isQuiz: false,
  },
  learn: {
    title: "Learning Path",
    endpoint: "/api/learn/recommendations",
    inputLabel: "Topic you want to learn",
    placeholder: 'e.g. "Cybersecurity"',
    buttonLabel: "Build My Roadmap",
    resultTitle: "Learning Roadmap",
    isQuiz: false,
  },
};

let currentFeature = null;
let currentQuizData = null; // { questions: [...] }
let quizSelections = {};    // questionIndex -> selected option string

// ---- DOM references -------------------------------------------------

const featureCards = document.querySelectorAll(".feature-card");
const inputPanel = document.getElementById("input-panel");
const panelTitle = document.getElementById("panel-title");
const inputLabel = document.getElementById("input-label");
const mainInput = document.getElementById("main-input");
const submitBtn = document.getElementById("submit-btn");
const closePanelBtn = document.getElementById("close-panel");
const loadingIndicator = document.getElementById("loading-indicator");
const loadingText = document.getElementById("loading-text");
const errorBox = document.getElementById("error-box");
const resultCard = document.getElementById("result-card");
const resultTitleEl = document.getElementById("result-title");
const resultContent = document.getElementById("result-content");
const quizArea = document.getElementById("quiz-area");

// ---- Feature card selection ------------------------------------------

featureCards.forEach((card) => {
  card.addEventListener("click", () => {
    const featureKey = card.dataset.feature;
    selectFeature(featureKey);
    featureCards.forEach((c) => c.classList.remove("active"));
    card.classList.add("active");
  });
});

function selectFeature(featureKey) {
  currentFeature = featureKey;
  const feature = FEATURES[featureKey];

  panelTitle.textContent = feature.title;
  inputLabel.textContent = feature.inputLabel;
  mainInput.placeholder = feature.placeholder;
  mainInput.value = "";
  submitBtn.textContent = feature.buttonLabel;

  resetPanelState();
  inputPanel.classList.remove("hidden");
  inputPanel.scrollIntoView({ behavior: "smooth", block: "start" });
  mainInput.focus();
}

function resetPanelState() {
  hide(errorBox);
  hide(resultCard);
  hide(quizArea);
  hide(loadingIndicator);
  errorBox.textContent = "";
  resultContent.innerHTML = "";
  quizArea.innerHTML = "";
  currentQuizData = null;
  quizSelections = {};
}

closePanelBtn.addEventListener("click", () => {
  inputPanel.classList.add("hidden");
  featureCards.forEach((c) => c.classList.remove("active"));
});

// ---- Submit handling ---------------------------------------------------

submitBtn.addEventListener("click", handleSubmit);
mainInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
    handleSubmit();
  }
});

async function handleSubmit() {
  if (!currentFeature) return;

  const text = mainInput.value.trim();
  if (!text) {
    showError("Please enter some text before submitting.");
    return;
  }

  const feature = FEATURES[currentFeature];

  resetPanelState();
  setLoading(true);

  try {
    const response = await fetch(feature.endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });

    let data;
    try {
      data = await response.json();
    } catch (parseErr) {
      throw new Error("Received an invalid response from the server.");
    }

    if (!response.ok || !data.success) {
      throw new Error(data.error || "Unable to generate the response right now. Please try again.");
    }

    if (feature.isQuiz) {
      renderQuiz(data.result);
    } else {
      renderTextResult(feature.resultTitle, data.result);
    }
  } catch (err) {
    showError(err.message || "Network error. Please check your connection and try again.");
  } finally {
    setLoading(false);
  }
}

function setLoading(isLoading) {
  submitBtn.disabled = isLoading;
  mainInput.disabled = isLoading;
  if (isLoading) {
    loadingText.textContent = "EduGenie is thinking...";
    show(loadingIndicator);
  } else {
    hide(loadingIndicator);
  }
}

function showError(message) {
  errorBox.textContent = message;
  show(errorBox);
}

function renderTextResult(title, text) {
  resultTitleEl.textContent = title;
  resultContent.textContent = text;
  show(resultCard);
}

// ---- Quiz rendering ------------------------------------------------------

function renderQuiz(quizData) {
  if (!quizData || !Array.isArray(quizData.questions) || quizData.questions.length === 0) {
    showError("EduGenie couldn't generate a quiz for that input. Try a different topic.");
    return;
  }

  currentQuizData = quizData;
  quizSelections = {};
  quizArea.innerHTML = "";

  quizData.questions.forEach((q, qIndex) => {
    const questionEl = document.createElement("div");
    questionEl.className = "quiz-question";

    const heading = document.createElement("h4");
    heading.textContent = `${qIndex + 1}. ${q.question}`;
    questionEl.appendChild(heading);

    const optionsWrap = document.createElement("div");
    optionsWrap.className = "quiz-options";

    q.options.forEach((option) => {
      const optionEl = document.createElement("div");
      optionEl.className = "quiz-option";
      optionEl.textContent = option;
      optionEl.addEventListener("click", () => {
        if (questionEl.dataset.locked === "true") return;
        optionsWrap.querySelectorAll(".quiz-option").forEach((o) => o.classList.remove("selected"));
        optionEl.classList.add("selected");
        quizSelections[qIndex] = option;
      });
      optionsWrap.appendChild(optionEl);
    });

    questionEl.appendChild(optionsWrap);

    const explanationEl = document.createElement("div");
    explanationEl.className = "quiz-explanation";
    explanationEl.textContent = q.explanation || "";
    questionEl.appendChild(explanationEl);

    quizArea.appendChild(questionEl);
  });

  const submitQuizBtn = document.createElement("button");
  submitQuizBtn.className = "primary-btn";
  submitQuizBtn.textContent = "Submit Quiz";
  submitQuizBtn.addEventListener("click", gradeQuiz);
  quizArea.appendChild(submitQuizBtn);

  show(quizArea);
}

function gradeQuiz() {
  if (!currentQuizData) return;

  const questionEls = quizArea.querySelectorAll(".quiz-question");
  let score = 0;

  currentQuizData.questions.forEach((q, qIndex) => {
    const questionEl = questionEls[qIndex];
    questionEl.dataset.locked = "true";

    const selected = quizSelections[qIndex];
    const optionEls = questionEl.querySelectorAll(".quiz-option");

    optionEls.forEach((optionEl) => {
      const optionText = optionEl.textContent;
      if (optionText === q.correct_answer) {
        optionEl.classList.add("correct");
      } else if (optionText === selected) {
        optionEl.classList.add("incorrect");
      }
    });

    if (selected === q.correct_answer) score += 1;

    const explanationEl = questionEl.querySelector(".quiz-explanation");
    if (explanationEl) explanationEl.classList.add("visible");
  });

  const scoreEl = document.createElement("div");
  scoreEl.className = "quiz-score";
  scoreEl.textContent = `You scored ${score} / ${currentQuizData.questions.length}`;

  const existingScore = quizArea.querySelector(".quiz-score");
  if (existingScore) existingScore.remove();
  quizArea.appendChild(scoreEl);

  const submitQuizBtn = quizArea.querySelector(".primary-btn");
  if (submitQuizBtn) submitQuizBtn.disabled = true;
}

// ---- small helpers ---------------------------------------------------

function show(el) { el.classList.remove("hidden"); }
function hide(el) { el.classList.add("hidden"); }
