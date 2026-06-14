/* Frontend controller for the AI Code & Flowchart Learning System. */
const App = (() => {
  const TOKEN_KEY = "ai_code_token";
  const USER_KEY  = "ai_code_user";

  const getToken = () => localStorage.getItem(TOKEN_KEY);
  const setAuth  = (token, user) => {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  };
  const clearAuth = () => { localStorage.removeItem(TOKEN_KEY); localStorage.removeItem(USER_KEY); };
  const currentUser = () => { try { return JSON.parse(localStorage.getItem(USER_KEY) || "null"); } catch { return null; } };

  async function api(path, opts = {}) {
    const headers = Object.assign({ "Content-Type": "application/json" }, opts.headers || {});
    const t = getToken();
    if (t) headers["Authorization"] = "Bearer " + t;
    const res = await fetch(path, Object.assign({}, opts, { headers }));
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || ("HTTP " + res.status));
    return data;
  }

  function requireAuth() {
    if (!getToken()) { window.location.href = "/login"; return; }
    const logout = document.getElementById("logoutBtn");
    if (logout) logout.onclick = () => { clearAuth(); window.location.href = "/login"; };
    const theme = document.getElementById("themeBtn");
    if (theme) theme.onclick = () => {
      const cur = document.documentElement.getAttribute("data-bs-theme");
      document.documentElement.setAttribute("data-bs-theme", cur === "dark" ? "light" : "dark");
    };
  }

  function bindAuthForm(formId, endpoint) {
    const form = document.getElementById(formId);
    const alertBox = document.getElementById("alert");
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      alertBox.classList.add("d-none");
      const body = Object.fromEntries(new FormData(form).entries());
      try {
        const data = await api(endpoint, { method: "POST", body: JSON.stringify(body) });
        setAuth(data.token, data.user);
        window.location.href = "/dashboard";
      } catch (err) {
        alertBox.textContent = err.message;
        alertBox.classList.remove("d-none");
      }
    });
  }

  /* ---------- Mermaid render helper ---------- */
  function renderMermaid(elId, code) {
    if (!window.mermaid) return;
    mermaid.initialize({ startOnLoad: false, securityLevel: "loose", theme: "default" });
    const host = document.getElementById(elId);
    host.innerHTML = "";
    const id = "m" + Date.now();
    mermaid.render(id, code).then(({ svg }) => host.innerHTML = svg)
      .catch(err => host.innerHTML = `<pre class="text-danger">${err.message}</pre>`);
  }

  /* ---------- Monaco loader ---------- */
  function mountMonaco(elId, language, initial) {
    return new Promise((resolve) => {
      require.config({ paths: { vs: "https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.52.0/min/vs" } });
      require(["vs/editor/editor.main"], () => {
        const ed = monaco.editor.create(document.getElementById(elId), {
          value: initial, language, theme: "vs-dark", automaticLayout: true,
          minimap: { enabled: false }, fontSize: 14,
        });
        resolve(ed);
      });
    });
  }

  /* ---------- Dashboard ---------- */
  async function initDashboard() {
    document.getElementById("userName").textContent = (currentUser()?.username) || "user";
    try {
      const { sessions } = await api("/api/history");
      document.getElementById("statTotal").textContent = sessions.length;
      document.getElementById("statFlow").textContent  = sessions.filter(s => s.kind === "code_to_flowchart").length;
      document.getElementById("statClass").textContent = sessions.filter(s => s.kind === "classify").length;
      document.getElementById("statExp").textContent   = sessions.filter(s => s.kind === "explain").length;
      const tbody = document.getElementById("recentRows");
      tbody.innerHTML = sessions.slice(0, 8).map(s => `
        <tr>
          <td>${new Date(s.created_at).toLocaleString()}</td>
          <td><span class="badge bg-secondary">${s.kind}</span></td>
          <td>${s.language || "—"}</td>
          <td>${s.logic_type || "—"}</td>
          <td>${s.confidence != null ? (s.confidence * 100).toFixed(1) + "%" : "—"}</td>
        </tr>`).join("") || `<tr><td colspan="5" class="text-muted text-center">No sessions yet</td></tr>`;
    } catch (e) { console.error(e); }
  }

  /* ---------- Editor page ---------- */
  async function initEditor() {
    const sample = `def classify(n):\n    if n > 0:\n        for i in range(n):\n            print(i)\n    else:\n        print('non-positive')\n\nclassify(5)\n`;
    const ed = await mountMonaco("editor", "python", sample);
    const langSel = document.getElementById("lang");
    langSel.onchange = () => monaco.editor.setModelLanguage(ed.getModel(), langSel.value);

    const get = () => ({ code: ed.getValue(), language: langSel.value });

    document.getElementById("btnFlow").onclick = async () => {
      try {
        const { flowchart } = await api("/api/code-to-flowchart", { method: "POST", body: JSON.stringify(get()) });
        renderMermaid("mermaidOut", flowchart);
      } catch (e) { alert(e.message); }
    };
    document.getElementById("btnClassify").onclick = async () => {
      try {
        const r = await api("/api/classify-logic", { method: "POST", body: JSON.stringify(get()) });
        document.getElementById("mlOut").innerHTML = `
          <h5>${r.logic_type} <span class="badge bg-primary">${(r.confidence*100).toFixed(1)}%</span></h5>
          <pre>${JSON.stringify(r.features, null, 2)}</pre>`;
        bootstrap.Tab.getOrCreateInstance(document.querySelector('[data-bs-target="#tabML"]')).show();
      } catch (e) { alert(e.message); }
    };
    document.getElementById("btnExplain").onclick = async () => {
      document.getElementById("aiOut").textContent = "Thinking…";
      bootstrap.Tab.getOrCreateInstance(document.querySelector('[data-bs-target="#tabAI"]')).show();
      try {
        const { explanation } = await api("/api/explain-code", { method: "POST", body: JSON.stringify(get()) });
        document.getElementById("aiOut").textContent = explanation;
      } catch (e) { document.getElementById("aiOut").textContent = e.message; }
    };
    document.getElementById("btnSuggest").onclick = async () => {
      document.getElementById("aiOut").textContent = "Analyzing…";
      bootstrap.Tab.getOrCreateInstance(document.querySelector('[data-bs-target="#tabAI"]')).show();
      try {
        const { suggestions } = await api("/api/suggest-improvements", { method: "POST", body: JSON.stringify(get()) });
        document.getElementById("aiOut").textContent = suggestions;
      } catch (e) { document.getElementById("aiOut").textContent = e.message; }
    };
  }

  /* ---------- Flowchart → Code ---------- */
  function initF2C() {
    const mer = document.getElementById("mer");
    const out = document.getElementById("out");
    const lang = document.getElementById("lang");
    const refresh = () => renderMermaid("mermaidPreview", mer.value);
    mer.addEventListener("input", refresh); refresh();
    document.getElementById("btnGen").onclick = async () => {
      out.textContent = "Generating…";
      try {
        const { code } = await api("/api/flowchart-to-code", {
          method: "POST", body: JSON.stringify({ flowchart: mer.value, language: lang.value }),
        });
        out.textContent = code;
      } catch (e) { out.textContent = e.message; }
    };
  }

  /* ---------- History ---------- */
  async function initHistory() {
    const list = document.getElementById("historyList");
    try {
      const { sessions } = await api("/api/history");
      if (!sessions.length) { list.innerHTML = `<p class="text-muted">No sessions yet.</p>`; return; }
      list.innerHTML = sessions.map(s => `
        <div class="col-md-6">
          <div class="card h-100"><div class="card-body">
            <div class="d-flex justify-content-between">
              <span class="badge bg-primary">${s.kind}</span>
              <small class="text-muted">${new Date(s.created_at).toLocaleString()}</small>
            </div>
            <h6 class="mt-2">${s.logic_type || s.language || "Session"} ${s.confidence!=null?`<span class="badge bg-info">${(s.confidence*100).toFixed(0)}%</span>`:""}</h6>
            ${s.source_code ? `<pre class="small bg-light p-2 rounded" style="max-height:160px;overflow:auto">${escapeHtml(s.source_code)}</pre>` : ""}
            <button class="btn btn-sm btn-outline-danger" data-id="${s.session_id}">Delete</button>
          </div></div>
        </div>`).join("");
      list.querySelectorAll("button[data-id]").forEach(btn => {
        btn.onclick = async () => {
          try { await api("/api/history/" + btn.dataset.id, { method: "DELETE" }); initHistory(); }
          catch(e){ alert(e.message); }
        };
      });
    } catch (e) { list.innerHTML = `<p class="text-danger">${e.message}</p>`; }
  }

  /* ---------- Profile ---------- */
  async function initProfile() {
    try {
      const u = await api("/api/me");
      document.getElementById("pUser").textContent = u.username;
      document.getElementById("pEmail").textContent = u.email;
      document.getElementById("pCreated").textContent = u.created_at ? new Date(u.created_at).toLocaleString() : "—";
    } catch (e) { console.error(e); }
  }

  function escapeHtml(s){ return s.replace(/[&<>"']/g, c => ({ "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;" }[c])); }

  return { requireAuth, bindAuthForm, initDashboard, initEditor, initF2C, initHistory, initProfile };
})();
window.App = App;
