const API = "https://api.troyaiagent.com";
const API_KEY = "TRoy-C48tUyrmeLMES4IjKqZjH6L5sfziFiU";

const headers = {
  "Content-Type": "application/json",
  Authorization: `Bearer ${API_KEY}`,
};

async function checkStatus() {
  try {
    const res = await fetch(`${API}/api/health`, { headers });
    const dot = document.getElementById("status-dot");
    if (res.ok) {
      dot.classList.add("online");
      dot.classList.remove("offline");
    } else {
      dot.classList.add("offline");
    }
  } catch {
    document.getElementById("status-dot").classList.add("offline");
  }
}

async function loadTasks() {
  try {
    const res = await fetch(`${API}/api/tasks`, { headers });
    if (!res.ok) return;
    const data = await res.json();
    const tasks = data.tasks || [];

    document.getElementById("tasks-count").textContent = tasks.length;

    const list = document.getElementById("task-list");
    if (tasks.length === 0) {
      list.innerHTML = '<p class="empty-state">No tasks yet. Run an agent above.</p>';
      return;
    }

    list.innerHTML = tasks
      .slice(0, 20)
      .map(
        (t) => `
      <div class="task-item">
        <span class="task-dept">${t.department}</span>
        <span class="task-name">${t.task}</span>
        <span class="task-status ${t.status}">${t.status}</span>
        <span class="task-time">${formatTime(t.created_at)}</span>
      </div>`
      )
      .join("");
  } catch {}
}

async function queueTask(dept, task) {
  try {
    const res = await fetch(`${API}/api/tasks`, {
      method: "POST",
      headers,
      body: JSON.stringify({ department: dept, task }),
    });
    if (res.ok) {
      await loadTasks();
    }
  } catch {}
}

function formatTime(iso) {
  if (!iso) return "";
  const d = new Date(iso + "Z");
  return d.toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit" });
}

document.querySelectorAll(".run-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    const dept = btn.dataset.dept;
    const task = btn.dataset.task;
    btn.textContent = "Queued...";
    btn.disabled = true;
    queueTask(dept, task).finally(() => {
      setTimeout(() => {
        btn.textContent = btn.dataset.label || btn.textContent.replace("Queued...", "Run");
        btn.disabled = false;
      }, 2000);
    });
  });
});

// Store original button labels
document.querySelectorAll(".run-btn").forEach((btn) => {
  btn.dataset.label = btn.textContent;
});

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str || "";
  return div.innerHTML;
}

function renderMessages(messages) {
  if (!messages.length) return '<p class="empty-state">No messages.</p>';
  return messages
    .map(
      (m) => `
    <div class="email-item">
      <span class="email-from">${escapeHtml(m.from)}</span>
      <span class="email-subject">${escapeHtml(m.subject)}</span>
      <span class="email-snippet">${escapeHtml(m.snippet)}</span>
    </div>`
    )
    .join("");
}

async function loadInbox() {
  const container = document.getElementById("email-accounts");
  if (!container) return;
  try {
    const res = await fetch("/api/inbox");
    if (!res.ok) {
      container.innerHTML = '<p class="empty-state">Failed to load inbox.</p>';
      return;
    }
    const data = await res.json();
    const accounts = data.accounts || [];

    container.innerHTML = accounts
      .map((acc) => {
        if (acc.status === "not_connected") {
          return `
          <div class="email-account">
            <div class="email-account-header">
              <span class="email-account-name">${escapeHtml(acc.label)}</span>
              <span class="email-account-address">${escapeHtml(acc.email)}</span>
              <span class="email-status not-connected">Not connected</span>
            </div>
          </div>`;
        }
        if (acc.status === "error") {
          return `
          <div class="email-account">
            <div class="email-account-header">
              <span class="email-account-name">${escapeHtml(acc.label)}</span>
              <span class="email-account-address">${escapeHtml(acc.email)}</span>
              <span class="email-status error">Error: ${escapeHtml(acc.error)}</span>
            </div>
          </div>`;
        }
        return `
        <div class="email-account">
          <div class="email-account-header">
            <span class="email-account-name">${escapeHtml(acc.label)}</span>
            <span class="email-account-address">${escapeHtml(acc.email)}</span>
            <span class="email-status connected">Connected</span>
          </div>
          <div class="email-columns">
            <div class="email-column">
              <h4>Inbox</h4>
              ${renderMessages(acc.inbox)}
            </div>
            <div class="email-column">
              <h4>Sent</h4>
              ${renderMessages(acc.sent)}
            </div>
          </div>
        </div>`;
      })
      .join("");
  } catch {
    container.innerHTML = '<p class="empty-state">Failed to load inbox.</p>';
  }
}

checkStatus();
loadTasks();
loadInbox();
setInterval(loadTasks, 30000);
setInterval(checkStatus, 60000);
setInterval(loadInbox, 60000);
