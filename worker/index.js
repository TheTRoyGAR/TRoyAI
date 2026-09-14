export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;

    const cors = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, Authorization",
      "Content-Type": "application/json",
    };

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: cors });
    }

    // Auth check
    const authHeader = request.headers.get("Authorization");
    const apiKey = authHeader?.replace("Bearer ", "");
    if (apiKey !== env.AGENT_API_KEY) {
      return new Response(JSON.stringify({ error: "Unauthorized" }), {
        status: 401,
        headers: cors,
      });
    }

    try {
      if (path === "/api/health") {
        return json({ ok: true, agency: "TRoyAI E-Automation Agency", status: "online" }, cors);
      }

      if (path === "/api/status") {
        return json({
          agency: "TRoyAI E-Automation Agency",
          ceo: "I. Ertan Govdeli",
          departments: ["operations", "sales", "marketing", "finance", "cto"],
          agents_per_department: 5,
          total_agents: 25,
          beta_agents: ["delivery", "qa"],
          domain: "troyaiagent.com",
          dashboard: "dashboard.troyaiagent.com",
        }, cors);
      }

      if (path === "/api/departments" && request.method === "GET") {
        const stmt = env.DB.prepare("SELECT * FROM departments ORDER BY name");
        const { results } = await stmt.all();
        return json({ departments: results }, cors);
      }

      if (path === "/api/agents" && request.method === "GET") {
        const dept = url.searchParams.get("department");
        let stmt;
        if (dept) {
          stmt = env.DB.prepare("SELECT * FROM agents WHERE department = ? ORDER BY name").bind(dept);
        } else {
          stmt = env.DB.prepare("SELECT * FROM agents ORDER BY department, name");
        }
        const { results } = await stmt.all();
        return json({ agents: results }, cors);
      }

      if (path === "/api/tasks" && request.method === "GET") {
        const { results } = await env.DB.prepare(
          "SELECT * FROM tasks ORDER BY created_at DESC LIMIT 50"
        ).all();
        return json({ tasks: results }, cors);
      }

      if (path === "/api/tasks" && request.method === "POST") {
        const body = await request.json();
        const { department, agent, task, input } = body;

        if (!department || !task) {
          return json({ error: "department and task are required" }, cors, 400);
        }

        const id = crypto.randomUUID();
        await env.DB.prepare(
          "INSERT INTO tasks (id, department, agent, task, input, status, created_at) VALUES (?, ?, ?, ?, ?, 'queued', datetime('now'))"
        ).bind(id, department, agent || "auto", task, input || "").run();

        return json({ task_id: id, status: "queued" }, cors, 201);
      }

      if (path.startsWith("/api/tasks/") && request.method === "GET") {
        const taskId = path.split("/").pop();
        const result = await env.DB.prepare("SELECT * FROM tasks WHERE id = ?").bind(taskId).first();
        if (!result) return json({ error: "Task not found" }, cors, 404);
        return json(result, cors);
      }

      return json({ error: "Not found" }, cors, 404);
    } catch (err) {
      return json({ error: err.message }, cors, 500);
    }
  },
};

function json(data, headers, status = 200) {
  return new Response(JSON.stringify(data), { status, headers });
}
