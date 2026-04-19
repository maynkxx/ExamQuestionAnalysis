const healthEl = document.getElementById("health");
const analyzeBtn = document.getElementById("analyzeBtn");
const clearAnalyzeBtn = document.getElementById("clearAnalyzeBtn");
const analyzeOutput = document.getElementById("analyzeOutput");
const csvFile = document.getElementById("csvFile");

const chatBtn = document.getElementById("chatBtn");
const stopChatBtn = document.getElementById("stopChatBtn");
const clearChatBtn = document.getElementById("clearChatBtn");
const chatOutput = document.getElementById("chatOutput");
const chatInput = document.getElementById("chatInput");

let chatAbortController = null;

function setHealth(ok, text) {
  healthEl.textContent = text;
  healthEl.classList.remove("ok", "bad");
  healthEl.classList.add(ok ? "ok" : "bad");
}

function prettyJson(obj) {
  try {
    return JSON.stringify(obj, null, 2);
  } catch {
    return String(obj);
  }
}

async function checkHealth() {
  try {
    const res = await fetch("/health", { cache: "no-store" });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    setHealth(true, data?.status === "ok" ? "API: OK" : "API: Online");
  } catch (e) {
    setHealth(false, "API: Offline");
  }
}

async function analyzeCsv() {
  const file = csvFile.files && csvFile.files[0];
  if (!file) {
    analyzeOutput.textContent = "Select a CSV file first.";
    return;
  }

  analyzeBtn.disabled = true;
  analyzeOutput.textContent = "Analyzing…";

  try {
    const form = new FormData();
    form.append("file", file, file.name);
    const res = await fetch("/analyze", { method: "POST", body: form });
    const text = await res.text();
    let payload = text;
    try { payload = JSON.parse(text); } catch {}
    if (!res.ok) {
      analyzeOutput.textContent = typeof payload === "string" ? payload : prettyJson(payload);
      return;
    }
    analyzeOutput.textContent = typeof payload === "string" ? payload : prettyJson(payload);
  } catch (e) {
    analyzeOutput.textContent = `Error: ${e?.message || e}`;
  } finally {
    analyzeBtn.disabled = false;
  }
}

async function streamChat() {
  const query = (chatInput.value || "").trim();
  if (!query) {
    chatOutput.textContent = "Type a message first.";
    return;
  }

  chatBtn.disabled = true;
  stopChatBtn.disabled = false;
  chatAbortController = new AbortController();

  chatOutput.textContent = "";

  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
      signal: chatAbortController.signal,
    });

    if (!res.ok) {
      const errText = await res.text();
      chatOutput.textContent = errText || `HTTP ${res.status}`;
      return;
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      chatOutput.textContent += decoder.decode(value, { stream: true });
      chatOutput.scrollTop = chatOutput.scrollHeight;
    }
  } catch (e) {
    if (e?.name === "AbortError") {
      chatOutput.textContent += "\n\n[Stopped]";
    } else {
      chatOutput.textContent = `Error: ${e?.message || e}`;
    }
  } finally {
    chatAbortController = null;
    chatBtn.disabled = false;
    stopChatBtn.disabled = true;
  }
}

function stopChat() {
  if (chatAbortController) chatAbortController.abort();
}

function clearAnalyze() {
  analyzeOutput.textContent = "";
  csvFile.value = "";
}

function clearChat() {
  chatOutput.textContent = "";
  chatInput.value = "";
}

analyzeBtn.addEventListener("click", analyzeCsv);
clearAnalyzeBtn.addEventListener("click", clearAnalyze);
chatBtn.addEventListener("click", streamChat);
stopChatBtn.addEventListener("click", stopChat);
clearChatBtn.addEventListener("click", clearChat);
chatInput.addEventListener("keydown", (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === "Enter") streamChat();
});

checkHealth();
setInterval(checkHealth, 15000);
