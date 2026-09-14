(function () {
  "use strict";

  const messagesEl = document.getElementById("messages");
  const form = document.getElementById("chat-form");
  const input = document.getElementById("message-input");
  const sendBtn = document.getElementById("send-btn");
  const typingEl = document.getElementById("typing");

  let sessionId = crypto.randomUUID();
  let busy = false;

  function formatMarkdown(text) {
    return text
      .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
      .replace(/\*(.+?)\*/g, "<em>$1</em>")
      .replace(/_(.+?)_/g, "<em>$1</em>")
      .replace(/^## (.+)$/gm, "<strong>$1</strong>")
      .replace(/\n/g, "<br>");
  }

  function appendMessage(text, role) {
    const div = document.createElement("div");
    div.className = "message " + role;
    if (role === "assistant") {
      div.innerHTML = formatMarkdown(text);
    } else {
      div.textContent = text;
    }
    messagesEl.appendChild(div);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function setTyping(show) {
    typingEl.hidden = !show;
    if (show) {
      messagesEl.scrollTop = messagesEl.scrollHeight;
    }
  }

  function setBusy(value) {
    busy = value;
    input.disabled = value;
    sendBtn.disabled = value;
  }

  async function sendMessage(text) {
    if (!text.trim() || busy) return;

    appendMessage(text, "user");
    input.value = "";
    setBusy(true);
    setTyping(true);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text, session_id: sessionId }),
      });

      const data = await res.json();

      if (!res.ok) {
        appendMessage(data.error || "Erro ao comunicar com o assistente.", "error");
        return;
      }

      sessionId = data.session_id || sessionId;
      appendMessage(data.reply, "assistant");
    } catch (err) {
      appendMessage("Falha de conexão com o servidor. Tente novamente.", "error");
    } finally {
      setTyping(false);
      setBusy(false);
      input.focus();
    }
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    sendMessage(input.value);
  });

  appendMessage(
    "Olá! Sou o assistente cardiológico do CardioIA. Como posso ajudar você hoje?",
    "assistant"
  );
  input.focus();
})();
