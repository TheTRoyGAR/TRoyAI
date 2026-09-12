// Locks the TRoyAI Command Centre behind HTTP Basic Auth at the edge, before
// any static file or API route is served — same pattern as TRoyGO's, TRoyMAR's
// and TRoyMEDIA's dashboard/_worker.js. Also serves the real Gmail inbox/sent
// API at /api/inbox.
//
// Only accounts with a stored OAuth refresh token can show real messages —
// there is no way to read someone's Gmail without them individually granting
// OAuth consent, so accounts without one are reported as "not_connected"
// (real state) rather than faked. Add the matching *_REFRESH_TOKEN secret
// (Cloudflare Pages > Settings > Environment variables) as each account is
// connected via the OAuth Playground / consent flow.

const ACCOUNTS = [
  { email: "agency@troytravelagency.com", tokenEnvVar: "AGENCY_TROYTRAVELAGENCY_REFRESH_TOKEN", label: "TRoy Travel - Primary" },
  { email: "troytravelagency@gmail.com", tokenEnvVar: "TROYTRAVELAGENCY_REFRESH_TOKEN", label: "TRoy Travel Agency" },
  { email: "troyaiagent@gmail.com", tokenEnvVar: "TROYAIAGENT_REFRESH_TOKEN", label: "TRoy AI Agent" },
  { email: "agent@troyaiagent.com", tokenEnvVar: "AGENT_TROYAIAGENT_REFRESH_TOKEN", label: "TRoy AI - Business" },
  { email: "troymaritimeagency@gmail.com", tokenEnvVar: "TROYMARITIMEAGENCY_REFRESH_TOKEN", label: "TRoy Maritime Agency" },
  { email: "troymediagency@gmail.com", tokenEnvVar: "TROYMEDIAGENCY_REFRESH_TOKEN", label: "TRoy Media Agency" },
  { email: "troytradingagency@gmail.com", tokenEnvVar: "TROYTRADINGAGENCY_REFRESH_TOKEN", label: "TRoy Trading Agency" },
  { email: "thetroygarage@gmail.com", tokenEnvVar: "THETROYGARAGE_REFRESH_TOKEN", label: "The TRoy Garage" },
  { email: "thetroygaragelab@gmail.com", tokenEnvVar: "THETROYGARAGELAB_REFRESH_TOKEN", label: "TRoy Garage Lab" },
  { email: "goupoftroy@gmail.com", tokenEnvVar: "GOUPOFTROY_REFRESH_TOKEN", label: "Group of TRoy" },
  { email: "ertangovdeli@gmail.com", tokenEnvVar: "ERTANGOVDELI_REFRESH_TOKEN", label: "Ertan Govdeli (Personal)" },
];

async function getAccessToken(env, refreshToken) {
  const resp = await fetch("https://oauth2.googleapis.com/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      client_id: env.GMAIL_OAUTH_CLIENT_ID,
      client_secret: env.GMAIL_OAUTH_CLIENT_SECRET,
      refresh_token: refreshToken,
      grant_type: "refresh_token",
    }),
  });
  if (!resp.ok) throw new Error(`token_refresh_failed:${resp.status}`);
  const data = await resp.json();
  return data.access_token;
}

async function fetchMessages(accessToken, labelId) {
  const listResp = await fetch(
    `https://gmail.googleapis.com/gmail/v1/users/me/messages?labelIds=${labelId}&maxResults=10`,
    { headers: { Authorization: `Bearer ${accessToken}` } }
  );
  if (!listResp.ok) throw new Error(`list_failed:${listResp.status}`);
  const listData = await listResp.json();
  const ids = (listData.messages || []).map((m) => m.id);

  const messages = await Promise.all(
    ids.map(async (id) => {
      const msgResp = await fetch(
        `https://gmail.googleapis.com/gmail/v1/users/me/messages/${id}?format=metadata&metadataHeaders=From&metadataHeaders=Subject&metadataHeaders=Date`,
        { headers: { Authorization: `Bearer ${accessToken}` } }
      );
      if (!msgResp.ok) return null;
      const msg = await msgResp.json();
      const headers = Object.fromEntries((msg.payload?.headers || []).map((h) => [h.name, h.value]));
      return {
        id: msg.id,
        from: headers.From || "",
        subject: headers.Subject || "(no subject)",
        date: headers.Date || "",
        snippet: msg.snippet || "",
      };
    })
  );
  return messages.filter(Boolean);
}

async function handleInbox(env) {
  const results = await Promise.all(
    ACCOUNTS.map(async (account) => {
      const refreshToken = env[account.tokenEnvVar];
      if (!refreshToken) {
        return { email: account.email, label: account.label, status: "not_connected", inbox: [], sent: [] };
      }
      try {
        const accessToken = await getAccessToken(env, refreshToken);
        const [inbox, sent] = await Promise.all([
          fetchMessages(accessToken, "INBOX"),
          fetchMessages(accessToken, "SENT"),
        ]);
        return { email: account.email, label: account.label, status: "connected", inbox, sent };
      } catch (err) {
        return {
          email: account.email,
          label: account.label,
          status: "error",
          error: err instanceof Error ? err.message : String(err),
          inbox: [],
          sent: [],
        };
      }
    })
  );
  return new Response(JSON.stringify({ success: true, accounts: results }), {
    headers: { "Content-Type": "application/json" },
  });
}

export default {
  async fetch(request, env) {
    const auth = request.headers.get("Authorization");
    let authorized = false;

    if (auth) {
      const [scheme, encoded] = auth.split(" ");
      if (scheme === "Basic" && encoded) {
        let decoded = "";
        try {
          decoded = atob(encoded);
        } catch {
          // fall through to 401
        }
        const idx = decoded.indexOf(":");
        const user = idx === -1 ? decoded : decoded.slice(0, idx);
        const pass = idx === -1 ? "" : decoded.slice(idx + 1);
        if (user === env.DASHBOARD_USER && pass === env.DASHBOARD_PASS) {
          authorized = true;
        }
      }
    }

    if (!authorized) {
      return new Response("Authentication required", {
        status: 401,
        headers: { "WWW-Authenticate": 'Basic realm="TRoyAI Command Centre"' },
      });
    }

    const url = new URL(request.url);
    if (url.pathname === "/api/inbox") {
      return handleInbox(env);
    }

    return env.ASSETS.fetch(request);
  },
};
