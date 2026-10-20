"use strict";
(() => {
  const form = document.getElementById("chat-form"), input = document.getElementById("chat-input"), messages = document.getElementById("chat-messages");
  function add(text, user) { const row = MyBud.element("div", undefined, user ? "user-message" : "bot-message"); row.append(MyBud.element("div", text, "message-content")); messages.append(row); messages.scrollTop = messages.scrollHeight; }
  form.addEventListener("submit", event => { event.preventDefault(); const message = input.value.trim(); if (!message) return;
    MyBud.busy(form, document.getElementById("chat-status"), async () => { add(message, true); input.value = "";
      const data = await MyBud.request("/api/chat/", {message}); add(data.response, false);
    });
  });
})();
