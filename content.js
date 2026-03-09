const API = 'http://127.0.0.1:8000';

const SENSITIVE_PATTERNS = [
  /credit.?card/i, /cvv/i, /\b\d{16}\b/, /\b\d{4}[\s-]\d{4}[\s-]\d{4}[\s-]\d{4}\b/,
  /otp/i, /one.?time.?pass/i, /password/i, /passwd/i,
  /banking.?detail/i, /account.?number/i, /sort.?code/i,
  /social.?security/i, /ssn/i, /passport.?number/i
];

function hasSensitiveContent(text) {
  return SENSITIVE_PATTERNS.some(p => p.test(text));
}

// ── Extract email ─────────────────────────────────────────────────────────────
function extractEmail(emailEl) {
  const subjectEl = document.querySelector('h2.hP') || document.querySelector('.hP');
  const subject   = subjectEl ? subjectEl.innerText.trim() : document.title.replace(' - Gmail','').trim();
  const senderEl  = document.querySelector('.gD') || document.querySelector('[email]');
  const sender    = senderEl ? (senderEl.getAttribute('email') || senderEl.innerText.trim()) : 'sender@email.com';
  const bodyEl    = emailEl.querySelector('.a3s') || emailEl;
  const body      = bodyEl.innerText.trim().slice(0, 2000);
  return { email_id: 'gmail-' + Date.now(), sender, subject, body };
}

// ── Inject full Airia panel ───────────────────────────────────────────────────
function injectAiriaBar(emailEl) {
  if (emailEl.querySelector('.airia-bar')) return;

  const bar = document.createElement('div');
  bar.className = 'airia-bar';
  bar.innerHTML = `
    <div class="airia-header">
      <div class="airia-logo"><span class="airia-dot"></span>AIRIA</div>
      <div class="airia-pipeline">
        <div class="airia-step" id="step1">
          <span class="step-num">1</span>
          <span class="step-label">Email Analyzer</span>
          <span class="step-status" id="step1-status"></span>
        </div>
        <div class="airia-arrow">→</div>
        <div class="airia-step" id="step2">
          <span class="step-num">2</span>
          <span class="step-label">Reply Writer</span>
          <span class="step-status" id="step2-status"></span>
        </div>
      </div>
    </div>
    <div class="airia-triage-labels" id="airia-labels" style="display:none"></div>
    <div class="airia-actions">
      <button class="airia-btn primary" id="airia-triage">🔍 Analyse Email</button>
      <button class="airia-btn" id="airia-reply">✨ Draft with Airia</button>
      <button class="airia-btn" id="airia-tasks">✅ Extract Tasks</button>
    </div>
    <div class="airia-status" id="airia-status"></div>
  `;

  emailEl.insertBefore(bar, emailEl.firstChild);

  bar.querySelector('#airia-triage').onclick = () => runTriage(emailEl, bar);
  bar.querySelector('#airia-reply').onclick   = () => runReply(emailEl, bar);
  bar.querySelector('#airia-tasks').onclick   = () => runTasks(emailEl, bar);
}

// ── Inject "Draft with Airia" near Gmail reply buttons ────────────────────────
function injectReplyButton() {
  if (document.querySelector('.airia-reply-inject')) return;

  // Gmail reply toolbar selector
  const replyToolbar = document.querySelector('.bAq') ||
                       document.querySelector('[data-tooltip="Reply"]')?.closest('.bAq') ||
                       document.querySelector('.ams');
  if (!replyToolbar) return;

  const btn = document.createElement('button');
  btn.className = 'airia-reply-inject';
  btn.innerHTML = '✨ Draft with Airia';
  btn.onclick = () => {
    const emailEl = document.querySelector('.a3s') || document.querySelector('.ii.gt');
    if (emailEl) {
      const bar = document.querySelector('.airia-bar');
      if (bar) runReply(emailEl, bar);
      else {
        // No bar yet — run directly
        runReplyDirect(emailEl);
      }
    }
  };
  replyToolbar.appendChild(btn);
}

// ── Helpers ───────────────────────────────────────────────────────────────────
function setStatus(bar, msg, type = 'info') {
  const el = bar.querySelector('#airia-status');
  if (el) { el.textContent = msg; el.className = `airia-status ${type}`; }
}

function setStep(stepId, state) {
  const el = document.getElementById(stepId);
  if (!el) return;
  el.className = `airia-step ${state}`;
  const status = document.getElementById(`${stepId}-status`);
  if (status) {
    status.textContent = state === 'active' ? '⟳' : state === 'done' ? '✓' : '';
  }
}

function setBtnLoading(bar, btnId, loading) {
  const btn = bar.querySelector(btnId);
  if (!btn) return;
  btn.disabled = loading;
  btn.style.opacity = loading ? '0.5' : '1';
}

function showResult(bar, html) {
  let panel = document.querySelector('.airia-result-panel');
  if (!panel) {
    panel = document.createElement('div');
    panel.className = 'airia-result-panel';
    bar.after(panel);
  }
  panel.innerHTML = html;
  panel.style.display = 'block';
}

function showLabels(bar, tri) {
  const labelsEl = bar.querySelector('#airia-labels');
  if (!labelsEl) return;
  const pColor = { urgent: '#ff4444', normal: '#f5c518', low: '#22c55e' }[tri.priority] || '#aaa';
  const pEmoji = { urgent: '🟥', normal: '🟨', low: '🟩' }[tri.priority] || '⬜';
  labelsEl.innerHTML = `
    <span class="airia-label" style="border-color:${pColor};color:${pColor}">${pEmoji} Priority: ${tri.priority.toUpperCase()}</span>
    <span class="airia-label">📂 Category: ${tri.category}</span>
    <span class="airia-label">🎯 Confidence: ${(tri.confidence * 100).toFixed(0)}%</span>
    ${(tri.tags || []).map(t => `<span class="airia-label">🏷 ${t}</span>`).join('')}
  `;
  labelsEl.style.display = 'flex';
}

// ── Auto-fill Gmail compose box ───────────────────────────────────────────────
function fillGmailCompose(replyText) {
  // Click Gmail's reply button to open compose
  const replyBtn = document.querySelector('[data-tooltip="Reply"]') ||
                   document.querySelector('.aaq') ||
                   document.querySelector('[aria-label="Reply"]');
  if (replyBtn) replyBtn.click();

  setTimeout(() => {
    const composeBody = document.querySelector('[aria-label="Message Body"]') ||
                        document.querySelector('.Am.Al.editable') ||
                        document.querySelector('[contenteditable="true"].Am');
    if (composeBody) {
      composeBody.focus();
      // Clear existing content and insert
      composeBody.innerHTML = '';
      document.execCommand('insertText', false, replyText);
      setStatus(document.querySelector('.airia-bar'), '✓ Reply loaded into compose!', 'success');
    }
  }, 800);
}

// ── Triage (Agent 1) ──────────────────────────────────────────────────────────
async function runTriage(emailEl, bar) {
  const email = extractEmail(emailEl);

  // Privacy check
  if (hasSensitiveContent(email.body)) {
    showResult(bar, `
      <div class="airia-sensitive">
        <div class="airia-sensitive-icon">🔒</div>
        <div class="airia-sensitive-title">⚠ Sensitive Content Detected</div>
        <div class="airia-sensitive-desc">
          This email appears to contain sensitive information
          (passwords, OTPs, card details, or banking data).<br/><br/>
          <strong>Draft generation has been restricted</strong> to protect your privacy.
        </div>
      </div>
    `);
    setStatus(bar, '⚠ Sensitive content — restricted', 'error');
    return;
  }

  setBtnLoading(bar, '#airia-triage', true);
  setStatus(bar, '🤖 Agent 1: Analysing email...', 'loading');
  setStep('step1', 'active');

  try {
    const res = await fetch(`${API}/triage`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(email)
    });
    const tri = await res.json();

    setStep('step1', 'done');
    showLabels(bar, tri);

    const pColor = { urgent: '#ff4444', normal: '#f5c518', low: '#22c55e' }[tri.priority] || '#aaa';
    const pEmoji = { urgent: '🔴', normal: '🟡', low: '🟢' }[tri.priority] || '⚪';

    showResult(bar, `
      <div class="airia-agent-tag">🤖 Agent 1 — Email Analyzer</div>
      <div class="airia-section-title">Triage Result</div>
      <div class="airia-badges">
        <span class="airia-badge" style="color:${pColor};border-color:${pColor}">${pEmoji} ${tri.priority.toUpperCase()}</span>
        <span class="airia-badge">📂 ${tri.category}</span>
        <span class="airia-badge">🎯 ${Math.round(tri.confidence * 100)}% confidence</span>
      </div>
      <div class="airia-section-title" style="margin-top:12px">Summary</div>
      <div class="airia-bullets">
        ${tri.summary_bullets.map(b => `<div class="airia-bullet">→ ${b}</div>`).join('')}
      </div>
      <div class="airia-section-title" style="margin-top:12px">Suggested Actions</div>
      <div class="airia-bullets">
        ${tri.suggested_next_actions.map(a => `<div class="airia-bullet">• ${a}</div>`).join('')}
      </div>
      <div class="airia-hint">✨ Now click <strong>Draft with Airia</strong> to generate a reply</div>
    `);
    setStatus(bar, `✓ Agent 1 complete — ${tri.priority.toUpperCase()} / ${tri.category}`, 'success');

    // Store triage result for agent 2
    bar._triageResult = tri;

  } catch (e) {
    setStep('step1', '');
    setStatus(bar, '⚠️ API unreachable — is uvicorn running?', 'error');
  }
  setBtnLoading(bar, '#airia-triage', false);
}

// ── Reply (Agent 2) ───────────────────────────────────────────────────────────
async function runReply(emailEl, bar) {
  const email = extractEmail(emailEl);

  // Privacy check
  if (hasSensitiveContent(email.body)) {
    showResult(bar, `
      <div class="airia-sensitive">
        <div class="airia-sensitive-icon">🔒</div>
        <div class="airia-sensitive-title">⚠ Sensitive Content Detected</div>
        <div class="airia-sensitive-desc">
          Draft generation restricted due to sensitive content in this email.
        </div>
      </div>
    `);
    setStatus(bar, '⚠ Sensitive content — restricted', 'error');
    return;
  }

  setBtnLoading(bar, '#airia-reply', true);
  setStatus(bar, '✍️ Agent 2: Drafting reply...', 'loading');
  setStep('step2', 'active');

  try {
    const res = await fetch(`${API}/reply`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ...email,
        tone: 'professional',
        user_name: 'Me',
        org_name: 'My Team'
      })
    });
    const rep = await res.json();
    setStep('step2', 'done');

    showResult(bar, `
      <div class="airia-agent-tag">✍️ Agent 2 — Reply Writer</div>
      <div class="airia-section-title">Draft Reply</div>
      <div class="airia-reply-subject">Subject: ${rep.reply_subject}</div>
      <textarea class="airia-reply-ta" id="airia-reply-text">${rep.reply_body}</textarea>
      <div class="airia-reply-actions">
        <button class="airia-btn primary" id="airia-compose-btn">📨 Open in Gmail Compose</button>
        <button class="airia-btn" id="airia-copy-btn">📋 Copy</button>
      </div>
      ${rep.notes && rep.notes.length ? `<div class="airia-note">⚠️ ${rep.notes.join(' · ')}</div>` : ''}
    `);

    document.getElementById('airia-compose-btn').onclick = () => {
      const text = document.getElementById('airia-reply-text').value;
      fillGmailCompose(text);
    };

    document.getElementById('airia-copy-btn').onclick = () => {
      navigator.clipboard.writeText(document.getElementById('airia-reply-text').value);
      document.getElementById('airia-copy-btn').textContent = '✓ Copied!';
      setTimeout(() => { document.getElementById('airia-copy-btn').textContent = '📋 Copy'; }, 2000);
    };

    setStatus(bar, '✓ Agent 2 complete — reply ready', 'success');

  } catch (e) {
    setStep('step2', '');
    setStatus(bar, '⚠️ API unreachable — is uvicorn running?', 'error');
  }
  setBtnLoading(bar, '#airia-reply', false);
}

// ── Reply without bar (fallback) ──────────────────────────────────────────────
async function runReplyDirect(emailEl) {
  const email = extractEmail(emailEl);
  if (hasSensitiveContent(email.body)) return;
  try {
    const res = await fetch(`${API}/reply`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...email, tone: 'professional', user_name: 'Me', org_name: 'My Team' })
    });
    const rep = await res.json();
    fillGmailCompose(rep.reply_body);
  } catch (e) { console.error('Airia reply failed', e); }
}

// ── Tasks ─────────────────────────────────────────────────────────────────────
async function runTasks(emailEl, bar) {
  const email = extractEmail(emailEl);
  setBtnLoading(bar, '#airia-tasks', true);
  setStatus(bar, '📋 Extracting tasks...', 'loading');
  try {
    const res = await fetch(`${API}/actions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(email)
    });
    const data = await res.json();
    const tasks = data.tasks || [];

    showResult(bar, `
      <div class="airia-agent-tag">✅ Auto Task Panel</div>
      <div class="airia-section-title">Extracted Tasks (${tasks.length})</div>
      <div class="airia-task-list">
        ${tasks.map(t => `
          <div class="airia-task-item">
            <div class="airia-task-check">☐</div>
            <div class="airia-task-content">
              <div class="airia-task-title">${t.title}</div>
              ${t.due ? `<div class="airia-task-due">Due: ${t.due}</div>` : ''}
            </div>
          </div>`).join('')}
      </div>
      <div class="airia-task-actions">
        <button class="airia-btn" onclick="alert('Notion integration coming soon!')">📓 Add to Notion</button>
        <button class="airia-btn" onclick="alert('Google Tasks integration coming soon!')">✅ Add to Google Tasks</button>
      </div>
    `);
    setStatus(bar, `✓ ${tasks.length} task(s) extracted`, 'success');
  } catch (e) {
    setStatus(bar, '⚠️ API unreachable — is uvicorn running?', 'error');
  }
  setBtnLoading(bar, '#airia-tasks', false);
}

// ── Find and inject ───────────────────────────────────────────────────────────
function findAndInject() {
  const selectors = ['.a3s.aiL', '.a3s', '.ii.gt', '.AO', '[data-message-id]', '.gs'];
  for (const sel of selectors) {
    document.querySelectorAll(sel).forEach(el => {
      if (el.innerText && el.innerText.trim().length > 20) {
        injectAiriaBar(el);
      }
    });
  }
  injectReplyButton();
}

// ── Observer ──────────────────────────────────────────────────────────────────
let debounceTimer;
const observer = new MutationObserver(() => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(findAndInject, 500);
});

observer.observe(document.body, { childList: true, subtree: true });

findAndInject();

let lastUrl = location.href;
setInterval(() => {
  if (location.href !== lastUrl) {
    lastUrl = location.href;
    setTimeout(findAndInject, 1000);
  }
}, 500);
