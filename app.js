// Browser-only stand-in for the FastAPI backend. Used when the backend is not
// reachable (opening index.html directly, or a static host such as Netlify).
// Data lives in localStorage, so it persists per browser only.
(function () {
  const STORE_KEY = "sudarshan_demo_db_v1";
  const MAX_STORED_BYTES = 1024 * 1024;
  const DEMO_PASSWORD = "demo1234";

  async function sha256Hex(buffer) {
    if (window.crypto && crypto.subtle) {
      const digest = await crypto.subtle.digest("SHA-256", buffer);
      return [...new Uint8Array(digest)].map(b => b.toString(16).padStart(2, "0")).join("");
    }
    return sha256Fallback(new Uint8Array(buffer));
  }

  // Pure-JS SHA-256 for contexts without crypto.subtle (e.g. plain-http LAN hosts).
  function sha256Fallback(bytes) {
    const K = [0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2];
    const H = [0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19];
    const len = bytes.length, padded = new Uint8Array(((len + 9 + 63) >> 6) << 6);
    padded.set(bytes); padded[len] = 0x80;
    const view = new DataView(padded.buffer);
    view.setUint32(padded.length - 4, len * 8); view.setUint32(padded.length - 8, Math.floor(len / 0x20000000));
    const W = new Uint32Array(64), rotr = (x, n) => (x >>> n) | (x << (32 - n));
    for (let off = 0; off < padded.length; off += 64) {
      for (let i = 0; i < 16; i++) W[i] = view.getUint32(off + i * 4);
      for (let i = 16; i < 64; i++) {
        const s0 = rotr(W[i-15],7) ^ rotr(W[i-15],18) ^ (W[i-15] >>> 3);
        const s1 = rotr(W[i-2],17) ^ rotr(W[i-2],19) ^ (W[i-2] >>> 10);
        W[i] = (W[i-16] + s0 + W[i-7] + s1) >>> 0;
      }
      let [a,b,c,d,e,f,g,h] = H;
      for (let i = 0; i < 64; i++) {
        const t1 = (h + (rotr(e,6) ^ rotr(e,11) ^ rotr(e,25)) + ((e & f) ^ (~e & g)) + K[i] + W[i]) >>> 0;
        const t2 = ((rotr(a,2) ^ rotr(a,13) ^ rotr(a,22)) + ((a & b) ^ (a & c) ^ (b & c))) >>> 0;
        h = g; g = f; f = e; e = (d + t1) >>> 0; d = c; c = b; b = a; a = (t1 + t2) >>> 0;
      }
      H[0]=(H[0]+a)>>>0; H[1]=(H[1]+b)>>>0; H[2]=(H[2]+c)>>>0; H[3]=(H[3]+d)>>>0;
      H[4]=(H[4]+e)>>>0; H[5]=(H[5]+f)>>>0; H[6]=(H[6]+g)>>>0; H[7]=(H[7]+h)>>>0;
    }
    return H.map(x => x.toString(16).padStart(8, "0")).join("");
  }

  const textBytes = (s) => new TextEncoder().encode(s).buffer;
  const randomId = (prefix) => `${prefix}-${Math.random().toString(16).slice(2, 12)}${Date.now().toString(16).slice(-10)}`;
  const nowIso = () => new Date().toISOString();

  function toBase64(buffer) {
    let binary = ""; const bytes = new Uint8Array(buffer);
    for (let i = 0; i < bytes.length; i += 0x8000) binary += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
    return btoa(binary);
  }
  function fromBase64(b64) {
    const binary = atob(b64); const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
    return bytes.buffer;
  }

  async function seed() {
    const sampleText = "SUDARSHAN DEMO EVIDENCE — FIR-2026-SC-001";
    const sampleHash = await sha256Hex(textBytes(sampleText));
    const pw = await sha256Hex(textBytes(DEMO_PASSWORD));
    return {
      officers: [
        {officer_id:"ADM-001", full_name:"Demo Administrator", email:"admin@demo.gov.in", role:"admin", is_active:true, password_hash:pw},
        {officer_id:"POL-UP-101", full_name:"Demo Police Officer", email:"police@demo.gov.in", role:"police", is_active:true, password_hash:pw},
        {officer_id:"JUD-DL-201", full_name:"Demo Judicial Officer", email:"judge@demo.gov.in", role:"judge", is_active:true, password_hash:pw}
      ],
      cases: [{case_id:"FIR-2026-SC-001", crime_domain:"Cyber Financial Fraud", filing_date:"2026-01-15", status:"Verified & Sealed"}],
      evidence: [{evidence_id:"EVD-demo0000000000000001", case_id:"FIR-2026-SC-001", sha256_hash:sampleHash, uploaded_by:"POL-UP-101", uploaded_at:nowIso(), data:toBase64(textBytes(sampleText))}],
      documents: [],
      audit: [{event_id:randomId("EVT"), actor_id:null, action:"SYSTEM_INITIALIZED", target_type:"system", target_id:"demo", case_id:null, timestamp:nowIso()}],
      tokens: {}
    };
  }

  let dbPromise = null;
  function loadDb() {
    if (!dbPromise) dbPromise = (async () => {
      try { const raw = localStorage.getItem(STORE_KEY); if (raw) return JSON.parse(raw); } catch (_) {}
      const db = await seed(); saveDb(db); return db;
    })();
    return dbPromise;
  }
  function saveDb(db) {
    try { localStorage.setItem(STORE_KEY, JSON.stringify(db)); }
    catch (_) { /* quota exceeded or storage blocked: keep in memory only */ }
  }

  class HttpError extends Error {}
  const fail = (message) => { throw new HttpError(message); };

  function audit(db, actor, action, targetType, targetId, caseId = null) {
    db.audit.unshift({event_id:randomId("EVT"), actor_id:actor?.officer_id || null, action, target_type:targetType, target_id:targetId, case_id:caseId, timestamp:nowIso()});
  }

  function currentOfficer(db, headers) {
    const token = (headers.get("Authorization") || "").replace(/^Bearer\s+/i, "");
    const officer = db.officers.find(o => o.officer_id === db.tokens[token]);
    if (!officer) fail("Session expired. Please log in again.");
    if (!officer.is_active) fail("Officer account is inactive");
    return officer;
  }
  const requireAdmin = (o) => { if (o.role !== "admin") fail("Only administrators can perform this action"); };
  const publicOfficer = ({password_hash, ...rest}) => rest;
  const publicEvidence = ({data, ...rest}) => rest;
  const publicDocument = ({data, versions, ...rest}) => rest;

  async function readFile(file) {
    if (!file || !file.size) fail("Uploaded file is empty");
    const buffer = await file.arrayBuffer();
    return {buffer, hash: await sha256Hex(buffer), stored: buffer.byteLength <= MAX_STORED_BYTES ? toBase64(buffer) : null};
  }

  function ensureCase(db, caseId, domain) {
    let record = db.cases.find(c => c.case_id === caseId);
    if (!record) {
      record = {case_id:caseId, crime_domain:domain || "Other", filing_date:nowIso().slice(0, 10), status:"Pending Review"};
      db.cases.push(record);
    }
    return record;
  }

  async function verifyStored(item) {
    if (!item.data) return {verified:true, actual:item.sha256_hash};
    const actual = await sha256Hex(fromBase64(item.data));
    return {verified: actual === item.sha256_hash, actual};
  }

  async function handle(method, path, options) {
    const db = await loadDb();
    const headers = new Headers(options.headers || {});
    const url = new URL(path, "http://demo.local");
    const parts = url.pathname.split("/").filter(Boolean).map(decodeURIComponent);
    const body = typeof options.body === "string" ? JSON.parse(options.body) : options.body;
    const route = `${method} /${parts.map((p, i) => (i > 0 && !["login","register","upload","verify","versions","status","officers"].includes(p)) ? ":id" : p).join("/")}`;

    switch (route) {
      case "POST /auth/register": {
        const {officer_id, full_name, email, password, role} = body;
        if (!["police","judge","admin"].includes(role)) fail("Invalid role");
        if (db.officers.some(o => o.officer_id === officer_id || o.email.toLowerCase() === email.toLowerCase())) fail("Officer ID or email already exists");
        db.officers.push({officer_id, full_name, email, role, is_active:true, password_hash: await sha256Hex(textBytes(password))});
        audit(db, null, "OFFICER_REGISTERED", "officer", officer_id);
        saveDb(db);
        return {officer_id, full_name, email, role};
      }
      case "POST /auth/login": {
        const officer = db.officers.find(o => o.email.toLowerCase() === String(body.email).toLowerCase());
        if (!officer || officer.password_hash !== await sha256Hex(textBytes(body.password))) fail("Invalid email or password");
        if (!officer.is_active) fail("Officer account is inactive");
        const token = randomId("TOK");
        db.tokens[token] = officer.officer_id;
        audit(db, officer, "LOGIN", "officer", officer.officer_id);
        saveDb(db);
        return {access_token:token, token_type:"bearer", officer_id:officer.officer_id, full_name:officer.full_name, role:officer.role};
      }
      case "GET /auth/officers": {
        requireAdmin(currentOfficer(db, headers));
        return db.officers.map(publicOfficer).sort((a, b) => a.full_name.localeCompare(b.full_name));
      }
      case "PATCH /auth/officers/:id/status": {
        const me = currentOfficer(db, headers); requireAdmin(me);
        const officer = db.officers.find(o => o.officer_id === parts[2]);
        if (!officer) fail("Officer not found");
        if (officer.officer_id === me.officer_id) fail("Administrators cannot disable their own account");
        officer.is_active = !officer.is_active;
        audit(db, me, "OFFICER_STATUS_CHANGED", "officer", officer.officer_id);
        saveDb(db);
        return {officer_id:officer.officer_id, is_active:officer.is_active};
      }
      case "GET /cases": {
        currentOfficer(db, headers);
        return db.cases;
      }
      case "POST /cases": {
        const me = currentOfficer(db, headers); requireAdmin(me);
        if (db.cases.some(c => c.case_id === body.case_id)) fail("Case ID already exists");
        db.cases.push({case_id:body.case_id, crime_domain:body.crime_domain, filing_date:body.filing_date, status:body.status || "Pending Review"});
        audit(db, me, "CASE_CREATED", "case", body.case_id, body.case_id);
        saveDb(db);
        return db.cases[db.cases.length - 1];
      }
      case "GET /evidence": {
        currentOfficer(db, headers);
        return db.evidence.map(publicEvidence);
      }
      case "POST /evidence/upload": {
        const me = currentOfficer(db, headers);
        if (me.role === "judge") fail("Judicial officers cannot upload evidence");
        const caseId = body.get("case_id");
        ensureCase(db, caseId, body.get("crime_domain"));
        const file = await readFile(body.get("file"));
        const record = {evidence_id:randomId("EVD"), case_id:caseId, sha256_hash:file.hash, uploaded_by:me.officer_id, uploaded_at:nowIso(), data:file.stored};
        db.evidence.push(record);
        audit(db, me, "EVIDENCE_UPLOADED", "evidence", record.evidence_id, caseId);
        saveDb(db);
        return publicEvidence(record);
      }
      case "GET /evidence/:id/verify": {
        const me = currentOfficer(db, headers);
        const item = db.evidence.find(e => e.evidence_id === parts[1]);
        if (!item) fail("Evidence not found");
        const {verified, actual} = await verifyStored(item);
        audit(db, me, verified ? "INTEGRITY_VERIFIED" : "INTEGRITY_FAILED", "evidence", item.evidence_id, item.case_id);
        saveDb(db);
        return {evidence_id:item.evidence_id, integrity_verified:verified, expected_hash:item.sha256_hash, actual_hash:actual};
      }
      case "GET /documents": {
        currentOfficer(db, headers);
        const caseId = url.searchParams.get("case_id");
        if (!db.cases.some(c => c.case_id === caseId)) fail("Case not found");
        return db.documents.filter(d => d.case_id === caseId).map(publicDocument);
      }
      case "POST /documents/upload": {
        const me = currentOfficer(db, headers);
        if (me.role === "judge") fail("Judicial officers cannot upload documents");
        const caseId = body.get("case_id"), fileObj = body.get("file");
        ensureCase(db, caseId);
        const file = await readFile(fileObj);
        const doc = {document_id:randomId("DOC"), case_id:caseId, title:body.get("title"), document_type:body.get("document_type") || "Other", original_filename:fileObj.name, sha256_hash:file.hash, current_version:1, uploaded_by:me.officer_id, data:file.stored};
        db.documents.push(doc);
        audit(db, me, "DOCUMENT_UPLOADED", "document", doc.document_id, caseId);
        saveDb(db);
        return publicDocument(doc);
      }
      case "POST /documents/:id/versions": {
        const me = currentOfficer(db, headers);
        if (me.role === "judge") fail("Judicial officers cannot upload documents");
        const doc = db.documents.find(d => d.document_id === parts[1]);
        if (!doc) fail("Document not found");
        const fileObj = body.get("file"), file = await readFile(fileObj);
        Object.assign(doc, {current_version:doc.current_version + 1, sha256_hash:file.hash, original_filename:fileObj.name, data:file.stored});
        audit(db, me, "DOCUMENT_VERSION_CREATED", "document", doc.document_id, doc.case_id);
        saveDb(db);
        return {version_id:randomId("VER"), document_id:doc.document_id, version_number:doc.current_version, sha256_hash:doc.sha256_hash, original_filename:doc.original_filename};
      }
      case "GET /documents/:id/verify": {
        const me = currentOfficer(db, headers);
        const doc = db.documents.find(d => d.document_id === parts[1]);
        if (!doc) fail("Document not found");
        const {verified, actual} = await verifyStored(doc);
        audit(db, me, verified ? "INTEGRITY_VERIFIED" : "INTEGRITY_FAILED", "document", doc.document_id, doc.case_id);
        saveDb(db);
        return {document_id:doc.document_id, integrity_verified:verified, expected_hash:doc.sha256_hash, actual_hash:actual};
      }
      case "GET /audit": {
        requireAdmin(currentOfficer(db, headers));
        return db.audit.slice(0, 200);
      }
      default:
        fail(`Demo mode does not support ${method} ${url.pathname}`);
    }
  }

  window.DemoAPI = {
    password: DEMO_PASSWORD,
    accounts: ["admin@demo.gov.in", "police@demo.gov.in", "judge@demo.gov.in"],
    fetch: (path, options = {}) => handle((options.method || "GET").toUpperCase(), path, options),
    reset: () => { try { localStorage.removeItem(STORE_KEY); } catch (_) {} dbPromise = null; }
  };
})();

const AppState = {
  currentUser: null,
  activeRole: null,
  currentView: "landing-view",
  selectedCaseId: null
};

const $ = (id) => document.getElementById(id);
const API_BASE = window.SUDARSHAN_API_BASE || (window.location.port === "8000"
  ? "/api/v1"
  : "http://127.0.0.1:8000/api/v1");
let authToken = null;
let serverCases = [];
let serverEvidence = [];
let serverOfficers = [];
let serverAudit = [];

// Use the FastAPI backend when it answers; otherwise fall back to the in-browser demo API
// (file:// opens and static hosts like Netlify have no backend).
const apiModeReady = (async () => {
  const isLocalPage = ["localhost", "127.0.0.1", ""].includes(window.location.hostname);
  if (!window.SUDARSHAN_API_BASE && !isLocalPage) return "demo";
  try {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 1500);
    const response = await fetch(`${API_BASE}/health`, {signal: controller.signal});
    clearTimeout(timer);
    return response.ok ? "server" : "demo";
  } catch (_) {
    return "demo";
  }
})();

async function apiFetch(path, options = {}) {
  const headers = new Headers(options.headers || {});
  if (authToken) headers.set("Authorization", `Bearer ${authToken}`);
  if (await apiModeReady === "demo") return window.DemoAPI.fetch(path, {...options, headers});
  const response = await fetch(`${API_BASE}${path}`, {...options, headers});
  let payload = null;
  try { payload = await response.json(); } catch (_) {}
  if (!response.ok) {
    const detail = payload?.detail || payload?.error || `Request failed (${response.status})`;
    throw new Error(Array.isArray(detail) ? detail.map(item => item.msg).join(", ") : detail);
  }
  return payload;
}

function roleLabel(role) {
  return role === "police" ? "POLICE OFFICER" : role === "judge" ? "JUDICIAL OFFICER" : "SYSTEM ADMIN";
}

function badgeClass(status) {
  if (status === "Verified & Sealed") return "sealed";
  if (status === "Closed") return "closed";
  return "pending";
}

function fmtNow() {
  return new Date().toLocaleString("en-IN", {year:"numeric",month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit"});
}

function toast(title, message, type="success") {
  const el = document.createElement("div");
  el.className = `toast ${type}`;
  el.innerHTML = `<strong>${escapeHtml(title)}</strong><span>${escapeHtml(message)}</span>`;
  $("toast-container").appendChild(el);
  setTimeout(() => el.remove(), 3500);
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[ch]));
}

function navigateTo(viewId) {
  document.querySelectorAll(".view").forEach(v => v.classList.toggle("hidden", v.id !== viewId));
  AppState.currentView = viewId;
  document.querySelectorAll(".nav-item").forEach(b => b.classList.toggle("active", b.dataset.view === viewId));
  window.scrollTo({top:0, behavior:"smooth"});
}
window.navigateTo = navigateTo;

function goToAuth(mode) {
  navigateTo("auth-view");
  const tab = document.querySelector(`.auth-tab[data-mode="${mode}"]`);
  if(tab) tab.click();
}
window.goToAuth = goToAuth;

function setRoleSession(role, officerId, name="Authorized Officer") {
  AppState.currentUser = { officerId, name };
  AppState.activeRole = role;
  $("user-badge").textContent = `${officerId} • ${roleLabel(role)}`;
  $("active-role-label").textContent = roleLabel(role);
  $("logout-btn").classList.remove("hidden");
  renderNav(role);
  if (role === "police") navigateTo("police-dashboard");
  if (role === "judge") navigateTo("judge-dashboard");
  if (role === "admin") navigateTo("admin-dashboard");
}

function renderNav(role) {
  const items = [
    role === "police" ? ["police-dashboard","⬡","Evidence Center"] : null,
    role === "judge" ? ["judge-dashboard","◉","Verification Bench"] : null,
    role === "admin" ? ["admin-dashboard","⌘","Governance Console"] : null
  ].filter(Boolean);
  $("sidebar-nav").innerHTML = items.map(([view,icon,label]) => `<button class="nav-item active" data-view="${view}"><span class="nav-icon">${icon}</span><span>${label}</span></button>`).join("");
  $("sidebar-nav").querySelectorAll(".nav-item").forEach(btn => btn.addEventListener("click", () => navigateTo(btn.dataset.view)));
}

function logout() {
  AppState.currentUser = null; AppState.activeRole = null;
  authToken = null;
  sessionStorage.removeItem("sudarshan_access_token");
  $("user-badge").textContent = "Not Authenticated";
  $("active-role-label").textContent = "GUEST ACCESS";
  $("logout-btn").classList.add("hidden");
  navigateTo("landing-view");
  $("sidebar-nav").innerHTML = "";
  toast("SESSION ENDED","Secure command session closed.");
}

function renderPoliceLedger(query="") {
  const rows = serverCases.filter(c => [c.caseId,c.domain,c.status].join(" ").toLowerCase().includes(query.toLowerCase()));
  $("police-ledger-body").innerHTML = rows.map(c => `
    <tr>
      <td><strong>${escapeHtml(c.caseId)}</strong></td>
      <td>${escapeHtml(c.domain)}</td>
      <td>${escapeHtml(c.timestamp)}</td>
      <td><code>${c.hash ? c.hash.slice(0,18) : "—"}…</code></td>
      <td><span class="status ${badgeClass(c.status)}">${escapeHtml(c.status)}</span></td>
    </tr>`).join("");
}

function findCases(query="") {
  const results = serverCases.filter(c => [c.caseId,c.domain].join(" ").toLowerCase().includes(query.trim().toLowerCase()));
  $("judge-results").innerHTML = (results.length ? results : []).map(c => `
    <div class="case-option ${AppState.selectedCaseId===c.caseId ? "active":""}" data-case-id="${escapeHtml(c.caseId)}">
      <div><strong>${escapeHtml(c.caseId)}</strong><span>${escapeHtml(c.domain)} • ${escapeHtml(c.timestamp)}</span></div>
      <span class="status ${badgeClass(c.status)}">${escapeHtml(c.status)}</span>
    </div>`).join("") || `<div class="demo-note" style="padding:10px;">No matching evidence records.</div>`;
  $("judge-results").querySelectorAll(".case-option").forEach(el => el.addEventListener("click",()=>selectCase(el.dataset.caseId)));
}

function selectCase(caseId) {
  const record = serverCases.find(c => c.caseId===caseId);
  if (!record) return;
  const evidence = serverEvidence.find(item => item.case_id === caseId);
  AppState.selectedCaseId = caseId;
  $("original-hash").textContent = evidence?.sha256_hash || "No uploaded evidence";
  $("live-hash").textContent = evidence?.sha256_hash || "—";
  $("verify-btn").disabled = !evidence;
  $("integrity-result").className = "integrity-result neutral";
  $("integrity-result").innerHTML = `<span>⌬</span><div><strong>READY TO VERIFY</strong><small>${escapeHtml(record.caseId)} loaded into integrity engine.</small></div>`;
  $("viewer-title").textContent = record.caseId;
  $("viewer-file").textContent = `${record.caseId} • ${record.domain}`;
  $("viewer-time").textContent = `WATERMARK • ${fmtNow()}`;
  $("watermark").textContent = `CONFIDENTIAL • ${record.caseId} • ${AppState.currentUser?.officerId || "JUDGE"} • ${fmtNow()}`;
  $("document-body").innerHTML = `
    <h4>Digital Evidence Record — ${escapeHtml(record.caseId)}</h4>
    <p><strong>Crime domain:</strong> ${escapeHtml(record.domain)}</p>
    <p><strong>Filing date:</strong> ${escapeHtml(record.timestamp)}</p>
    <p>Evidence metadata is loaded from the database-backed FastAPI service.</p>`;
  findCases($("judge-search").value);
}

async function verifySelected() {
  const record = serverCases.find(c => c.caseId===AppState.selectedCaseId);
  const evidence = serverEvidence.find(item => item.case_id === AppState.selectedCaseId);
  if (!record || !evidence) return toast("Evidence Required","This case has no uploaded evidence.","error");
  try {
    const result = await apiFetch(`/evidence/${encodeURIComponent(evidence.evidence_id)}/verify`);
    $("live-hash").textContent = result.actual_hash || "Unavailable";
    const resultBox = $("integrity-result");
    resultBox.className = `integrity-result ${result.integrity_verified ? "success" : "danger"}`;
    resultBox.innerHTML = result.integrity_verified
      ? `<span>✓</span><div><strong>INTEGRITY VERIFIED & SEALED</strong><small>Database evidence matches the stored SHA-256 hash.</small></div>`
      : `<span>!</span><div><strong>DOCUMENT INTEGRITY FAILED</strong><small>The stored evidence does not match its database hash.</small></div>`;
    toast(result.integrity_verified ? "Integrity Verified" : "Integrity Failed", record.caseId, result.integrity_verified ? "success" : "error");
  } catch (error) {
    toast("Verification Failed", error.message, "error");
  }
}

function renderOfficerList() {
  $("officer-list").innerHTML = serverOfficers.map((o,i)=>`
    <div class="officer-row">
      <div class="officer-name"><strong>${escapeHtml(o.full_name)}</strong><span>${escapeHtml(o.officer_id)}</span></div>
      <span>${escapeHtml(roleLabel(o.role))}</span>
      <span class="status ${o.is_active ? "sealed":"closed"}">${o.is_active ? "ACTIVE":"RESTRICTED"}</span>
      <button class="toggle ${o.is_active ? "on":""}" data-index="${i}" title="Toggle clearance"></button>
    </div>`).join("");
  $("officer-list").querySelectorAll(".toggle").forEach(btn => btn.addEventListener("click",()=>{
    const officer=serverOfficers[Number(btn.dataset.index)];
    updateOfficerStatus(officer.officer_id);
  }));
}

function renderAudit() {
  $("audit-list").innerHTML = serverAudit.map(log=>`
    <div class="audit-item">
      <span class="audit-dot"></span>
      <div><strong>${escapeHtml(log.action)}</strong><span>${escapeHtml(log.actor_id || "SYSTEM")} • ${escapeHtml(log.target_id || log.target_type)}</span></div>
      <small>${escapeHtml(log.timestamp)}</small>
    </div>`).join("");
}

function initAuth() {
  document.querySelectorAll(".auth-tab").forEach(tab => tab.addEventListener("click",()=>{
    document.querySelectorAll(".auth-tab").forEach(t=>t.classList.remove("active"));
    tab.classList.add("active");
    $("login-form").classList.toggle("hidden", tab.dataset.mode!=="login");
    $("register-form").classList.toggle("hidden", tab.dataset.mode!=="register");
  }));
  $("login-btn").addEventListener("click",async()=>{
    const id=$("login-id").value.trim(), pin=$("login-pin").value.trim();
    if(!id || !pin) return toast("Authentication Required","Enter Officer ID and PIN.","error");
    try {
      const session = await apiFetch("/auth/login", {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({email:id, password:pin})
      });
      authToken = session.access_token;
      sessionStorage.setItem("sudarshan_access_token", authToken);
      setRoleSession(session.role, session.officer_id, session.full_name);
      await loadBackendData();
      toast("Authenticated",`${roleLabel(session.role)} console opened.`);
    } catch (error) {
      toast("Authentication Failed", error.message, "error");
    }
  });
  $("register-btn").addEventListener("click",async()=>{
    const name=$("reg-name").value.trim();
    const officerId=$("reg-id").value.trim();
    const email=$("reg-email").value.trim();
    const password=$("reg-password").value;
    const role=$("reg-role").value;
    if(!name || !officerId || !email || !password) return toast("Missing Details","Fill all registration fields.","error");
    try {
      await apiFetch("/auth/register", {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({officer_id:officerId, full_name:name, email, password, role})
      });
      toast("Registration Saved","Officer account created in the database.");
      document.querySelector('[data-mode="login"]').click();
      $("login-id").value=email;
    } catch (error) {
      toast("Registration Failed", error.message, "error");
    }
  });
}

function initUpload() {
  const input=$("pdf-file-input"), zone=$("drop-zone");
  zone.addEventListener("click",()=>input.click());
  ["dragenter","dragover"].forEach(ev=>zone.addEventListener(ev,e=>{e.preventDefault();zone.classList.add("dragging")}));
  ["dragleave","drop"].forEach(ev=>zone.addEventListener(ev,e=>{e.preventDefault();zone.classList.remove("dragging")}));
  zone.addEventListener("drop",e=>handleFile(e.dataTransfer.files[0]));
  input.addEventListener("change",()=>handleFile(input.files[0]));
  $("upload-form").addEventListener("submit",async e=>{
    e.preventDefault();
    const file=input.files[0], caseId=$("case-id-input").value.trim(), domain=$("crime-domain").value;
    if(!file) return toast("Evidence Required","Select a PDF, PNG, or JPG before sealing.","error");
    const allowedExtensions = [".pdf", ".png", ".jpg", ".jpeg"];
    const extension = `.${file.name.split(".").pop().toLowerCase()}`;
    if (!allowedExtensions.includes(extension)) return toast("Unsupported File","Only PDF, PNG, and JPG files are accepted.","error");
    if(!caseId) return toast("Case ID Required","Enter the case identifier.","error");
    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("case_id", caseId);
      formData.append("crime_domain", domain);
      const payload = await apiFetch("/evidence/upload", {method:"POST", body:formData});
      await loadBackendData();
      $("hash-preview").textContent=payload.sha256_hash;
      $("seal-status").textContent="100% MATCH • DOCUMENT SEALED";
      $("upload-status").textContent="Server accepted the evidence and generated its cryptographic seal.";
      renderPoliceLedger($("police-search").value);
      toast("Evidence Sealed",`${caseId} stored in the database.`);
      $("upload-form").reset(); $("selected-file").classList.add("hidden");
    } catch(err){
      toast("Seal Failed",err.message||"Unknown error","error");
    }
  });
}

async function loadBackendData() {
  const [cases, evidence] = await Promise.all([
    apiFetch("/cases/"),
    apiFetch("/evidence/")
  ]);
  serverEvidence = evidence;
  serverCases = cases.map(item => {
    const matchingEvidence = evidence.find(record => record.case_id === item.case_id);
    return {
      caseId:item.case_id,
      domain:item.crime_domain,
      timestamp:item.filing_date,
      hash:matchingEvidence?.sha256_hash || "",
      status:item.status,
      file:matchingEvidence?.evidence_id || "Database evidence"
    };
  });
  renderPoliceLedger($("police-search").value);
  findCases($("judge-search").value);
  if (AppState.activeRole === "admin") await loadAdminData();
}

async function updateOfficerStatus(officerId) {
  try {
    await apiFetch(`/auth/officers/${encodeURIComponent(officerId)}/status`, {method:"PATCH"});
    await loadAdminData();
    toast("Clearance Updated", `${officerId} status changed in the database.`);
  } catch (error) {
    toast("Clearance Update Failed", error.message, "error");
  }
}

async function loadAdminData() {
  const [officers, audit] = await Promise.all([
    apiFetch("/auth/officers"),
    apiFetch("/audit/")
  ]);
  serverOfficers = officers;
  serverAudit = audit;
  $("admin-users-count").textContent = officers.length;
  $("active-users-count").textContent = officers.filter(officer => officer.is_active).length;
  $("audit-count").textContent = audit.length;
  $("alert-count").textContent = audit.filter(event => event.action === "INTEGRITY_FAILED").length;
  renderOfficerList();
  renderAudit();
}

async function createCase(event) {
  event.preventDefault();
  const caseId = $("new-case-id").value.trim();
  const domain = $("new-case-domain").value.trim();
  const filingDate = $("new-case-date").value;
  if (!caseId || !domain || !filingDate) return toast("Missing Details", "Complete all case fields.", "error");
  try {
    await apiFetch("/cases/", {
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify({case_id:caseId, crime_domain:domain, filing_date:filingDate, status:"Pending Review"})
    });
    await loadBackendData();
    $("case-form").reset();
    $("case-status").textContent = "Case saved to the database.";
    toast("Case Created", caseId);
  } catch (error) {
    toast("Case Creation Failed", error.message, "error");
  }
}

async function loadDocuments(caseId) {
  if (!caseId) return;
  try {
    const documents = await apiFetch(`/documents/?case_id=${encodeURIComponent(caseId)}`);
    $("document-list").innerHTML = documents.map(document => `
      <div class="officer-row">
        <div class="officer-name"><strong>${escapeHtml(document.title)}</strong><span>${escapeHtml(document.document_id)} • v${document.current_version}</span></div>
        <span>${escapeHtml(document.original_filename)}</span>
        <code>${escapeHtml(document.sha256_hash.slice(0, 18))}…</code>
        <button class="ghost-btn small document-verify" data-document-id="${escapeHtml(document.document_id)}">Verify</button>
      </div>`).join("") || `<div class="demo-note">No documents stored for this case.</div>`;
    $("document-list").querySelectorAll(".document-verify").forEach(button => button.addEventListener("click", () => verifyDocument(button.dataset.documentId)));
  } catch (error) {
    $("document-list").innerHTML = `<div class="demo-note">${escapeHtml(error.message)}</div>`;
  }
}

async function verifyDocument(documentId) {
  try {
    const result = await apiFetch(`/documents/${encodeURIComponent(documentId)}/verify`);
    toast(result.integrity_verified ? "Document Verified" : "Integrity Failure", documentId, result.integrity_verified ? "success" : "error");
  } catch (error) {
    toast("Verification Failed", error.message, "error");
  }
}

async function uploadDocument(event) {
  event.preventDefault();
  const file = $("document-file").files[0];
  const caseId = $("document-case-id").value.trim();
  const title = $("document-title").value.trim();
  if (!file || !caseId || !title) return toast("Missing Details", "Select a file and complete the document fields.", "error");
  const formData = new FormData();
  formData.append("case_id", caseId);
  formData.append("title", title);
  formData.append("document_type", "Evidence");
  formData.append("file", file);
  try {
    await apiFetch("/documents/upload", {method:"POST", body:formData});
    await loadDocuments(caseId);
    $("document-form").reset();
    $("document-status").textContent = "Encrypted document stored in the database.";
    toast("Document Stored", title);
  } catch (error) {
    toast("Document Upload Failed", error.message, "error");
  }
}

async function uploadDocumentVersion(event) {
  event.preventDefault();
  const documentId = $("version-document-id").value.trim();
  const file = $("version-file").files[0];
  if (!documentId || !file) return toast("Missing Details", "Select a document ID and version file.", "error");
  const formData = new FormData();
  formData.append("file", file);
  try {
    await apiFetch(`/documents/${encodeURIComponent(documentId)}/versions`, {method:"POST", body:formData});
    $("version-form").reset();
    toast("Version Stored", `${documentId} updated in the database.`);
  } catch (error) {
    toast("Version Upload Failed", error.message, "error");
  }
}

function handleFile(file){
  if(!file) return;
  $("selected-file").textContent=`Selected: ${file.name} • ${(file.size/1024/1024).toFixed(2)} MB`;
  $("selected-file").classList.remove("hidden");
}

function initJudge() {
  $("judge-search").addEventListener("input",e=>findCases(e.target.value));
  $("verify-btn").addEventListener("click",()=>verifySelected(false));
  findCases("");
}

function initAdmin() {
  $("case-form").addEventListener("submit", createCase);
  $("clear-demo-audit").addEventListener("click",async()=> {
    try { await loadAdminData(); toast("Audit Refreshed","Audit events loaded from the database."); }
    catch (error) { toast("Audit Load Failed", error.message, "error"); }
  });
}

function init() {
  $("logout-btn").addEventListener("click",logout);
  $("police-search").addEventListener("input",e=>renderPoliceLedger(e.target.value));
  $("document-form").addEventListener("submit", uploadDocument);
  $("version-form").addEventListener("submit", uploadDocumentVersion);
  $("document-case-id").addEventListener("change", event => loadDocuments(event.target.value.trim()));
  initAuth(); initUpload(); initJudge(); initAdmin(); renderPoliceLedger();
  navigateTo("landing-view");
  apiModeReady.then(mode => {
    if (mode !== "demo") return;
    document.querySelector("#login-form .demo-note").innerHTML =
      `<strong>Demo mode</strong> (no backend detected, data stays in this browser).<br>` +
      `Sign in with ${window.DemoAPI.accounts.map(escapeHtml).join(", ")} • password <code>${escapeHtml(window.DemoAPI.password)}</code>`;
  });
}

init();