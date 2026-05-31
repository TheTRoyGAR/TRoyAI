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

checkStatus();
loadTasks();
setInterval(loadTasks, 30000);
setInterval(checkStatus, 60000);
