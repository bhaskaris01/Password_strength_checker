const passwordInput = document.getElementById("passwordInput");
const toggleBtn = document.getElementById("toggleBtn");
const strengthFill = document.getElementById("strengthFill");
const strengthLabel = document.getElementById("strengthLabel");
const reasonText = document.getElementById("reasonText");

const checklistItems = {
  length: document.getElementById("check-length"),
  uppercase: document.getElementById("check-uppercase"),
  lowercase: document.getElementById("check-lowercase"),
  digit: document.getElementById("check-digit"),
  special: document.getElementById("check-special"),
};

const colors = {
  Weak: "#e53935",
  Medium: "#fbc02d",
  Strong: "#4caf50",
};

let debounceTimer;

passwordInput.addEventListener("input", () => {
  clearTimeout(debounceTimer);
  const password = passwordInput.value;

  if (!password) {
    resetUI();
    return;
  }

  // Small debounce so we don't hit the server on every single keystroke
  debounceTimer = setTimeout(() => checkStrength(password), 200);
});

toggleBtn.addEventListener("click", () => {
  passwordInput.type = passwordInput.type === "password" ? "text" : "password";
});

async function checkStrength(password) {
  try {
    const response = await fetch("/check", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password }),
    });

    const data = await response.json();
    updateUI(data);
  } catch (err) {
    strengthLabel.textContent = "Error contacting server";
  }
}

function updateUI(data) {
  const percent = (data.score / data.max_score) * 100;
  strengthFill.style.width = percent + "%";
  strengthFill.style.background = colors[data.strength];

  strengthLabel.textContent = data.strength;
  strengthLabel.style.color = colors[data.strength];
  reasonText.textContent = data.reason;

  for (const key in checklistItems) {
    const passed = data.checks[key];
    const li = checklistItems[key];
    li.classList.toggle("passed", passed);
    li.textContent = (passed ? "✓ " : "✗ ") + li.textContent.slice(2);
  }
}

function resetUI() {
  strengthFill.style.width = "0%";
  strengthLabel.textContent = "Start typing...";
  strengthLabel.style.color = "#eee";
  reasonText.textContent = "";
  for (const key in checklistItems) {
    checklistItems[key].classList.remove("passed");
    checklistItems[key].textContent = "✗ " + checklistItems[key].textContent.slice(2);
  }
}
