function setTheme(mode) {
  if (mode === "dark") {
    document.body.classList.add("dark-mode");
  } else {
    document.body.classList.remove("dark-mode");
  }
  localStorage.setItem("theme", mode);
}

function toggleMode() {
  const active = document.body.classList.contains("dark-mode") ? "light" : "dark";
  setTheme(active);
}

function appendChatMessage(text, role = "bot") {
  const body = document.getElementById("chat-body");
  if (!body) return;

  const msg = document.createElement("div");
  msg.className = `chat-message ${role}`;
  msg.textContent = text;

  body.appendChild(msg);
  body.scrollTop = body.scrollHeight;
}

function initChat() {
  const widget = document.getElementById("chat-widget");
  const toggle = document.getElementById("chat-toggle");
  const close = document.getElementById("chat-close");
  const form = document.getElementById("chat-form");
  const input = document.getElementById("chat-input");

  if (!widget || !toggle || !close || !form || !input) return;

  toggle.addEventListener("click", () => {
    widget.classList.toggle("open");
    if (widget.classList.contains("open")) {
      input.focus();
    }
  });

  close.addEventListener("click", () => {
    widget.classList.remove("open");
  });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const message = input.value.trim();
    if (!message) return;

    appendChatMessage(message, "user");
    input.value = "";

    appendChatMessage("Đang gửi…", "bot");

    try {
      const resp = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
      });

      const data = await resp.json();

      // remove the placeholder message
      const placeholders = document.querySelectorAll(".chat-message.bot");
      if (placeholders.length) {
        placeholders[placeholders.length - 1].remove();
      }

      appendChatMessage(data.reply || "Xin lỗi, không nhận được phản hồi.", "bot");
    } catch (err) {
      appendChatMessage("Không thể kết nối đến máy chủ.", "bot");
    }
  });
}

function initRetrain() {
  const btn = document.getElementById("retrain-btn");
  const status = document.getElementById("retrain-status");
  if (!btn || !status) return;

  btn.addEventListener("click", async () => {
    btn.disabled = true;
    btn.textContent = "Đang tái huấn luyện...";
    status.textContent = "";

    try {
      const resp = await fetch("/retrain", { method: "POST" });
      const data = await resp.json();
      status.textContent = data.message || "Hoàn thành.";
    } catch (err) {
      status.textContent = "Lỗi khi gọi máy chủ.";
    }

    btn.disabled = false;
    btn.textContent = "Tái huấn luyện mô hình";
  });
}

function initCursorRipple() {
  let last = 0;
  const throttle = 40;
  const ripple = document.createElement("div");
  ripple.className = "cursor-ripple";
  document.body.appendChild(ripple);

  const showRipple = (x, y) => {
    ripple.style.left = x + "px";
    ripple.style.top = y + "px";
    ripple.classList.add("show");

    window.clearTimeout(ripple._timeout);
    ripple._timeout = window.setTimeout(() => {
      ripple.classList.remove("show");
    }, 220);
  };

  window.addEventListener("mousemove", (event) => {
    const now = performance.now();
    if (now - last < throttle) return;
    last = now;
    showRipple(event.clientX, event.clientY);
  });
}

function initCustomCursor() {
  const cursor = document.createElement("div");
  cursor.className = "custom-cursor";
  document.body.appendChild(cursor);

  const setPosition = (x, y) => {
    cursor.style.left = `${x}px`;
    cursor.style.top = `${y}px`;
  };

  window.addEventListener("mousemove", (event) => {
    setPosition(event.clientX, event.clientY);
  });

  const setIcon = (enabled) => {
    if (enabled) {
      cursor.classList.add("icon");
    } else {
      cursor.classList.remove("icon");
    }
  };

  const hoverTargets = [
    ".card",
    ".theme-toggle",
    ".nav-links a",
    "button",
    ".chat-toggle",
    ".chat-close",
  ];

  hoverTargets.forEach((selector) => {
    document.body.addEventListener("mouseover", (event) => {
      if (event.target.closest(selector)) {
        setIcon(true);
      }
    });
    document.body.addEventListener("mouseout", (event) => {
      if (event.target.closest(selector)) {
        setIcon(false);
      }
    });
  });
}

window.addEventListener("DOMContentLoaded", () => {
  const saved = localStorage.getItem("theme") || "dark";
  setTheme(saved);

  initChat();
  initRetrain();
  initCursorRipple();
  initCustomCursor();
});
