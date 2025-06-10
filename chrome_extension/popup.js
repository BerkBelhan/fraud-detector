// chrome_extension/popup.js

// --- DOM Elements ---
const scanButton = document.getElementById("scan-button");
const welcomeView = document.getElementById("welcome-view");
const processingView = document.getElementById("processing-view");
const resultsView = document.getElementById("results-view");
const thinkingPlaceholder = document.getElementById("thinking-placeholder");

// --- Helper Functions ---
function setView(viewName) {
  welcomeView.classList.add("hidden");
  processingView.classList.add("hidden");
  resultsView.classList.add("hidden");

  const viewToShow = document.getElementById(`${viewName}-view`);
  if (viewToShow) {
    viewToShow.classList.remove("hidden");
  }
}

function sleep(ms) { return new Promise(resolve => setTimeout(resolve, ms)); }

async function runThinkingAnimation() {
    const thinkingSteps = [
        "Initializing Scaminator...",
        "Establishing secure connection to analysis server...",
        "Dispatching request to backend pipelines...",
        "Awaiting verdict from the digital spirits..."
    ];
    thinkingPlaceholder.innerHTML = '<div class="thinking-bar"><pre><code></code></pre></div>';
    const codeElement = thinkingPlaceholder.querySelector("code");

    for (const step of thinkingSteps) {
        let line = `• ${step}\n`;
        for (const char of line) {
            codeElement.textContent += char;
            await sleep(10);
        }
        await sleep(200);
    }
}

// --- Main Event Listener ---
scanButton.addEventListener("click", async () => {
  let [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab || !tab.url || !tab.url.startsWith("http")) {
    resultsView.innerHTML = createErrorBox("Cannot analyze this page. Please try a valid product page.");
    setView("results");
    return;
  }
  const url = tab.url;

  setView("processing");
  await runThinkingAnimation();
  thinkingPlaceholder.innerHTML = ""; // Clear animation

  try {
    const response = await fetch("http://127.0.0.1:8501/evaluate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: url })
    });

    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.final_verdict ? data.final_verdict.summary_reason : `Server responded with status: ${response.status}`);
    }

    renderResults(data);
    setView("results");

  } catch (err) {
    console.error("Error during fetch:", err);
    resultsView.innerHTML = createErrorBox(`Could not connect to the Scaminator backend server. Is it running?<br><br>Error: ${err.message}`);
    setView("results");
  }
});

function renderResults(data) {
    resultsView.innerHTML = ""; // Clear previous
    const { final_verdict } = data; // Directly use the structure from your API
    resultsView.innerHTML = createFinalVerdictBox(final_verdict);
    // Intermediate findings can be added here if the API provides them
}

function createErrorBox(message) {
     return `<div class="final-verdict-box scam"><p class="final-verdict-title">Error</p><p class="final-reason">${message}</p></div>`;
}

function createFinalVerdictBox(finalData) {
    let verdictClass = "unknown";
    const level = (finalData && finalData.final_level) || "Error";
    const reason = (finalData && finalData.summary_reason) || "No summary provided.";
    const levelLower = level.toLowerCase();

    if (levelLower.includes("safe")) verdictClass = "safe";
    else if (levelLower.includes("suspicious") || levelLower.includes("caution")) verdictClass = "suspicious";
    else if (levelLower.includes("scam") || levelLower.includes("error")) verdictClass = "scam";
    
    // The reason from your Trendyol pipeline is a long, pre-formatted string.
    // The reason from your global pipeline is a short summary.
    // We will use a <pre> tag to respect the formatting of the long string.
    const reasonHTML = `<pre class="final-reason">${reason}</pre>`;
    
    const verdictHTML = `
        <p class="final-verdict-title">Final Verdict</p>
        <p class="final-verdict-text">${level.toUpperCase()}</p>
        ${reasonHTML}`;
    
    return `<div class="final-verdict-box ${verdictClass}">${verdictHTML}</div>`;
}