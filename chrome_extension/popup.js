document.getElementById("scan").addEventListener("click", async () => {
    let [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    const url = tab.url;
  
    document.getElementById("result").innerText = "Analyzing...";
  
    try {
      const response = await fetch("http://localhost:8501/evaluate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url })
      });
  
      const data = await response.json();
      document.getElementById("result").innerHTML =
        `<strong>Verdict:</strong> ${data.final_verdict.final_level}<br><strong>Reason:</strong> ${data.final_verdict.summary_reason}`;
    } catch (err) {
      document.getElementById("result").innerText = "Error: " + err.message;
    }
  });