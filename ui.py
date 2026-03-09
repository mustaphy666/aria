# import streamlit as st
# import requests

# API_URL = st.sidebar.text_input("API URL", value="http://127.0.0.1:8000")

# st.title("Airia Email Triage + Reply Agent (Track 1 Demo)")


# def fetch_inbox():
#     r = requests.get(f"{API_URL}/inbox", timeout=10)
#     r.raise_for_status()
#     data = r.json()
#     if isinstance(data, list):
#         return [e for e in data if isinstance(e, dict)]
#     if isinstance(data, dict):
#         for key in ("emails", "data", "items", "results"):
#             if key in data and isinstance(data[key], list):
#                 return [e for e in data[key] if isinstance(e, dict)]
#     return []


# def post_json(path: str, payload: dict):
#     r = requests.post(f"{API_URL}{path}", json=payload, timeout=20)
#     r.raise_for_status()
#     return r.json()


# # ── Fetch inbox ───────────────────────────────────────────────────────────────
# inbox = []
# try:
#     inbox = fetch_inbox()
# except requests.exceptions.ConnectionError:
#     st.error("Could not connect to API. Is the server running?")
#     st.stop()
# except requests.exceptions.Timeout:
#     st.error("API request timed out.")
#     st.stop()
# except Exception as e:
#     st.error(f"Could not fetch inbox: {e}")
#     st.stop()

# if not inbox:
#     st.warning("Inbox is empty. Make sure the API server is running and has seeded data.")
#     st.stop()

# # ── Build a dict keyed by label — selection never uses an index ───────────────
# inbox_map = {}
# for e in inbox:
#     label = f"{e.get('email_id', '?')} - {e.get('subject', '(no subject)')}"
#     inbox_map[label] = e   # label → email dict directly

# selected_label = st.selectbox("Select an email", list(inbox_map.keys()))

# # Direct dict lookup — no index, no range, cannot crash
# selected = inbox_map.get(selected_label) or list(inbox_map.values())[0]

# # ── Display email ─────────────────────────────────────────────────────────────
# st.subheader("Email")
# st.write(f"**From:** {selected.get('sender', 'Unknown')}")
# st.write(f"**Subject:** {selected.get('subject', '(no subject)')}")
# st.write(selected.get("body", ""))

# # ── Action buttons ────────────────────────────────────────────────────────────
# col1, col2, col3 = st.columns(3)

# with col1:
#     if st.button("Triage"):
#         try:
#             tri = post_json("/triage", selected)
#             st.session_state["triage"] = tri
#         except Exception as e:
#             st.error(f"Triage failed: {e}")

# with col2:
#     if st.button("Generate Reply"):
#         try:
#             tone = st.session_state.get("tone", "professional")
#             payload = {
#                 "email_id": selected.get("email_id"),
#                 "sender": selected.get("sender"),
#                 "subject": selected.get("subject"),
#                 "body": selected.get("body"),
#                 "tone": tone,
#                 "user_name": "Mustapha",
#                 "org_name": "My Team",
#                 "extra_context": st.session_state.get("extra_context") or None,
#             }
#             rep = post_json("/reply", payload)
#             st.session_state["reply"] = rep
#         except Exception as e:
#             st.error(f"Reply generation failed: {e}")

# with col3:
#     if st.button("Create Tasks"):
#         try:
#             tasks = post_json("/actions", selected)
#             st.session_state["tasks"] = tasks
#         except Exception as e:
#             st.error(f"Task creation failed: {e}")

# st.divider()

# # ── Sidebar controls ──────────────────────────────────────────────────────────
# st.sidebar.subheader("Reply Controls")
# st.sidebar.selectbox("Tone", ["professional", "friendly", "direct"], key="tone")
# st.sidebar.text_area("Extra context (optional)", key="extra_context", height=120)

# # ── Triage result ─────────────────────────────────────────────────────────────
# if "triage" in st.session_state:
#     st.subheader("Triage Result")
#     tri = st.session_state["triage"]
#     if isinstance(tri, dict):
#         st.write(
#             f"**Priority:** {tri.get('priority', '-')}  |  "
#             f"**Category:** {tri.get('category', '-')}  |  "
#             f"**Confidence:** {tri.get('confidence', '-')}"
#         )
#         bullets = tri.get("summary_bullets", [])
#         if bullets:
#             st.write("**Summary:**")
#             for b in bullets:
#                 st.write(f"- {b}")
#         actions = tri.get("suggested_next_actions", [])
#         if actions:
#             st.write("**Suggested next actions:**")
#             for a in actions:
#                 st.write(f"- {a}")
#         if tri.get("tags"):
#             st.caption("Tags: " + ", ".join(tri["tags"]))
#     else:
#         st.warning("Unexpected triage response format.")

# # ── Draft reply ───────────────────────────────────────────────────────────────
# if "reply" in st.session_state:
#     st.subheader("Draft Reply")
#     rep = st.session_state["reply"]
#     if isinstance(rep, dict):
#         st.write(f"**Subject:** {rep.get('reply_subject', '')}")
#         st.text_area("Reply body", rep.get("reply_body", ""), height=250)
#         notes = rep.get("notes", [])
#         if notes:
#             st.info("Notes:\n" + "\n".join([f"- {n}" for n in notes]))
#     else:
#         st.warning("Unexpected reply response format.")

# # ── Tasks ─────────────────────────────────────────────────────────────────────
# if "tasks" in st.session_state:
#     st.subheader("Tasks")
#     tasks_data = st.session_state["tasks"]
#     tasks = tasks_data.get("tasks", []) if isinstance(tasks_data, dict) else []
#     if tasks:
#         for t in tasks:
#             if isinstance(t, dict):
#                 due = f" (due {t['due']})" if t.get("due") else ""
#                 st.write(f"- {t.get('title', 'Untitled')}{due} - **{t.get('owner', 'Unassigned')}**")
#     else:
#         st.info("No tasks returned.")
import streamlit as st
import requests
import time
import random
from datetime import datetime

st.set_page_config(page_title="Airia – Email Agent", layout="wide", page_icon="🤖")

API_URL = st.sidebar.text_input("API URL", value="http://127.0.0.1:8000")

# ── Simulated incoming emails pool ────────────────────────────────────────────
SIMULATED_EMAILS = [
    {"email_id": f"sim-{i}", "sender": s, "subject": subj, "body": body}
    for i, (s, subj, body) in enumerate([
        ("cfo@acme.com", "URGENT: Budget approval needed today",
         "We need sign-off on the Q2 budget immediately. Board meeting is in 2 hours. Please confirm ASAP."),
        ("dev@startup.io", "System outage — service is down",
         "Our API has been down for 30 minutes. Customers are affected. Need immediate escalation."),
        ("hr@company.com", "Team offsite schedule for next week",
         "Hi, just an FYI — the offsite is scheduled for Tuesday. No action needed, just letting you know."),
        ("legal@firm.com", "NDA clause update — deadline 03/15/2026",
         "Please review the attached redlines on the NDA termination clause. Deadline is March 15."),
        ("client@bigcorp.com", "Can we schedule a call this week?",
         "Hi, I'd love to catch up on the project milestones. Are you free Thursday or Friday?"),
        ("billing@vendor.com", "Invoice #4521 overdue",
         "Your invoice #4521 for $4,200 is now 14 days overdue. Please remit payment or contact us."),
        ("support@tool.com", "Bug report: export feature broken",
         "Users are reporting that the CSV export throws a 500 error. Can you investigate?"),
        ("partner@agency.com", "New contract terms for review",
         "We've updated the MSA with revised payment terms. Please review and confirm acceptance."),
    ])
]

# ── Helpers ───────────────────────────────────────────────────────────────────
def fetch_inbox():
    r = requests.get(f"{API_URL}/inbox", timeout=10)
    r.raise_for_status()
    data = r.json()
    if isinstance(data, list):
        return [e for e in data if isinstance(e, dict)]
    if isinstance(data, dict):
        for key in ("emails", "data", "items", "results"):
            if key in data and isinstance(data[key], list):
                return [e for e in data[key] if isinstance(e, dict)]
    return []

def post_json(path, payload):
    r = requests.post(f"{API_URL}{path}", json=payload, timeout=20)
    r.raise_for_status()
    return r.json()

def priority_color(p):
    return {"urgent": "🔴", "normal": "🟡", "low": "🟢"}.get(p, "⚪")

def category_icon(c):
    return {"billing": "💰", "meeting": "📅", "support": "🛠️",
            "contract": "📝", "general": "📧"}.get(c, "📧")

def time_now():
    return datetime.now().strftime("%H:%M:%S")

# ── Session state init ────────────────────────────────────────────────────────
if "activity_feed"    not in st.session_state: st.session_state.activity_feed    = []
if "triaged_emails"   not in st.session_state: st.session_state.triaged_emails   = {}
if "stats"            not in st.session_state: st.session_state.stats            = {"total": 0, "urgent": 0, "normal": 0, "low": 0, "categories": {}}
if "sim_pool"         not in st.session_state: st.session_state.sim_pool         = SIMULATED_EMAILS.copy()
if "auto_triage"      not in st.session_state: st.session_state.auto_triage      = False
if "last_refresh"     not in st.session_state: st.session_state.last_refresh     = time.time()

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.markdown("## ⚙️ Controls")
st.sidebar.selectbox("Tone", ["professional", "friendly", "direct"], key="tone")
st.sidebar.text_area("Extra context (optional)", key="extra_context", height=80)
st.sidebar.divider()
st.sidebar.markdown("### 🔴 Live Dashboard")
auto = st.sidebar.toggle("Auto-triage new emails", value=st.session_state.auto_triage)
st.session_state.auto_triage = auto
refresh_rate = st.sidebar.slider("Refresh every (sec)", 3, 30, 8)
if st.sidebar.button("💥 Simulate incoming email"):
    if st.session_state.sim_pool:
        new_email = st.session_state.sim_pool.pop(0)
        try:
            post_json("/triage", new_email)
            tri = post_json("/triage", new_email)
            p = tri.get("priority", "normal")
            c = tri.get("category", "general")
            st.session_state.triaged_emails[new_email["email_id"]] = {**new_email, **tri}
            st.session_state.stats["total"] += 1
            st.session_state.stats[p] = st.session_state.stats.get(p, 0) + 1
            st.session_state.stats["categories"][c] = st.session_state.stats["categories"].get(c, 0) + 1
            st.session_state.activity_feed.insert(0, {
                "time": time_now(),
                "msg": f"{priority_color(p)} **{new_email['sender']}** → _{new_email['subject']}_ triaged as **{p.upper()}** / {category_icon(c)} {c}",
            })
        except Exception as ex:
            st.sidebar.error(f"Sim failed: {ex}")
    else:
        st.sidebar.info("All simulated emails used. Restart to reset.")

if st.sidebar.button("🔄 Reset dashboard"):
    st.session_state.activity_feed  = []
    st.session_state.triaged_emails = {}
    st.session_state.stats          = {"total": 0, "urgent": 0, "normal": 0, "low": 0, "categories": {}}
    st.session_state.sim_pool       = SIMULATED_EMAILS.copy()

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["📬 Email Triage & Reply", "📊 Live Dashboard"])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Email Triage & Reply
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.title("🤖 Airia Email Agent")

    inbox = []
    try:
        inbox = fetch_inbox()
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to API. Is the server running?")
        st.stop()
    except requests.exceptions.Timeout:
        st.error("API request timed out.")
        st.stop()
    except Exception as e:
        st.error(f"Could not fetch inbox: {e}")
        st.stop()

    if not inbox:
        st.warning("Inbox is empty. Make sure the API server is running.")
        st.stop()

    inbox_map = {
        f"{e.get('email_id','?')} - {e.get('subject','(no subject)')}": e
        for e in inbox
    }

    selected_label = st.selectbox("Select an email", list(inbox_map.keys()))
    selected = inbox_map.get(selected_label) or list(inbox_map.values())[0]

    with st.container(border=True):
        st.markdown(f"**From:** {selected.get('sender','Unknown')}")
        st.markdown(f"**Subject:** {selected.get('subject','(no subject)')}")
        st.write(selected.get("body", ""))

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔍 Triage", use_container_width=True):
            try:
                tri = post_json("/triage", selected)
                st.session_state["triage"] = tri
                # Also push to dashboard
                p = tri.get("priority", "normal")
                c = tri.get("category", "general")
                eid = selected.get("email_id")
                st.session_state.triaged_emails[eid] = {**selected, **tri}
                st.session_state.stats["total"] += 1
                st.session_state.stats[p] = st.session_state.stats.get(p, 0) + 1
                st.session_state.stats["categories"][c] = st.session_state.stats["categories"].get(c, 0) + 1
                st.session_state.activity_feed.insert(0, {
                    "time": time_now(),
                    "msg": f"{priority_color(p)} **{selected.get('sender','')}** → _{selected.get('subject','')}_ triaged as **{p.upper()}**",
                })
            except Exception as e:
                st.error(f"Triage failed: {e}")

    with col2:
        if st.button("✍️ Generate Reply", use_container_width=True):
            try:
                payload = {
                    "email_id": selected.get("email_id"),
                    "sender": selected.get("sender"),
                    "subject": selected.get("subject"),
                    "body": selected.get("body"),
                    "tone": st.session_state.get("tone", "professional"),
                    "user_name": "Mustapha",
                    "org_name": "My Team",
                    "extra_context": st.session_state.get("extra_context") or None,
                }
                rep = post_json("/reply", payload)
                st.session_state["reply"] = rep
                st.session_state.activity_feed.insert(0, {
                    "time": time_now(),
                    "msg": f"✍️ Reply drafted for _{selected.get('subject','')}_ ({st.session_state.get('tone','professional')} tone)",
                })
            except Exception as e:
                st.error(f"Reply generation failed: {e}")

    with col3:
        if st.button("✅ Create Tasks", use_container_width=True):
            try:
                tasks = post_json("/actions", selected)
                st.session_state["tasks"] = tasks
                st.session_state.activity_feed.insert(0, {
                    "time": time_now(),
                    "msg": f"✅ {len(tasks.get('tasks',[]))} task(s) created for _{selected.get('subject','')}_",
                })
            except Exception as e:
                st.error(f"Task creation failed: {e}")

    st.divider()

    if "triage" in st.session_state:
        tri = st.session_state["triage"]
        if isinstance(tri, dict):
            with st.container(border=True):
                st.subheader("🔍 Triage Result")
                p = tri.get("priority", "-")
                c = tri.get("category", "-")
                st.markdown(
                    f"{priority_color(p)} **Priority:** {p.upper()} &nbsp;|&nbsp; "
                    f"{category_icon(c)} **Category:** {c} &nbsp;|&nbsp; "
                    f"🎯 **Confidence:** {tri.get('confidence','-')}"
                )
                bullets = tri.get("summary_bullets", [])
                if bullets:
                    st.markdown("**Summary:**")
                    for b in bullets: st.markdown(f"- {b}")
                actions = tri.get("suggested_next_actions", [])
                if actions:
                    st.markdown("**Suggested actions:**")
                    for a in actions: st.markdown(f"- {a}")
                if tri.get("tags"):
                    st.caption("Tags: " + ", ".join(tri["tags"]))

    if "reply" in st.session_state:
        rep = st.session_state["reply"]
        if isinstance(rep, dict):
            with st.container(border=True):
                st.subheader("✍️ Draft Reply")
                st.markdown(f"**Subject:** {rep.get('reply_subject','')}")
                st.text_area("Reply body", rep.get("reply_body",""), height=220, key="reply_body_display")
                if rep.get("notes"):
                    st.info("Notes:\n" + "\n".join([f"- {n}" for n in rep["notes"]]))

    if "tasks" in st.session_state:
        tasks_data = st.session_state["tasks"]
        tasks = tasks_data.get("tasks", []) if isinstance(tasks_data, dict) else []
        if tasks:
            with st.container(border=True):
                st.subheader("✅ Tasks")
                for t in tasks:
                    if isinstance(t, dict):
                        due = f" _(due {t['due']})_" if t.get("due") else ""
                        st.markdown(f"- **{t.get('title','Untitled')}**{due} — {t.get('owner','Me')}")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Live Dashboard
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.title("📊 Airia Live Dashboard")

    # Auto-triage from real API
    if st.session_state.auto_triage:
        now = time.time()
        if now - st.session_state.last_refresh >= refresh_rate:
            st.session_state.last_refresh = now
            try:
                live_inbox = fetch_inbox()
                for e in live_inbox:
                    eid = e.get("email_id")
                    if eid and eid not in st.session_state.triaged_emails:
                        tri = post_json("/triage", e)
                        p = tri.get("priority", "normal")
                        c = tri.get("category", "general")
                        st.session_state.triaged_emails[eid] = {**e, **tri}
                        st.session_state.stats["total"] += 1
                        st.session_state.stats[p] = st.session_state.stats.get(p, 0) + 1
                        st.session_state.stats["categories"][c] = st.session_state.stats["categories"].get(c, 0) + 1
                        st.session_state.activity_feed.insert(0, {
                            "time": time_now(),
                            "msg": f"{priority_color(p)} **{e.get('sender','')}** → _{e.get('subject','')}_ auto-triaged as **{p.upper()}**",
                        })
            except Exception:
                pass
            st.rerun()

    # ── KPI row ───────────────────────────────────────────────────────────────
    stats = st.session_state.stats
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("📨 Total Processed", stats["total"])
    k2.metric("🔴 Urgent", stats.get("urgent", 0))
    k3.metric("🟡 Normal", stats.get("normal", 0))
    k4.metric("🟢 Low", stats.get("low", 0))

    st.divider()

    left, right = st.columns([2, 1])

    # ── Priority queue ────────────────────────────────────────────────────────
    with left:
        st.subheader("🚨 Priority Queue")
        triaged = list(st.session_state.triaged_emails.values())
        priority_order = {"urgent": 0, "normal": 1, "low": 2}
        triaged_sorted = sorted(triaged, key=lambda x: priority_order.get(x.get("priority","normal"), 1))

        if not triaged_sorted:
            st.info("No emails triaged yet. Use the sidebar to simulate or enable auto-triage.")
        else:
            for e in triaged_sorted:
                p  = e.get("priority", "normal")
                c  = e.get("category", "general")
                bg = {"urgent": "#3d1a1a", "normal": "#2a2a1a", "low": "#1a2a1a"}.get(p, "#1e1e1e")
                with st.container(border=True):
                    col_a, col_b = st.columns([3,1])
                    with col_a:
                        st.markdown(f"{priority_color(p)} **{e.get('subject','(no subject)')}**")
                        st.caption(f"From: {e.get('sender','')}  |  {category_icon(c)} {c}")
                    with col_b:
                        st.markdown(f"**{p.upper()}**")
                        conf = e.get("confidence")
                        if conf:
                            st.caption(f"Confidence: {conf}")

    # ── Right column: categories + activity feed ──────────────────────────────
    with right:
        st.subheader("📂 Categories")
        cats = stats.get("categories", {})
        if cats:
            total = sum(cats.values()) or 1
            for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
                pct = int(count / total * 100)
                st.markdown(f"{category_icon(cat)} **{cat}** — {count} ({pct}%)")
                st.progress(pct / 100)
        else:
            st.info("No data yet.")

        st.divider()
        st.subheader("⚡ Activity Feed")
        feed = st.session_state.activity_feed[:15]
        if not feed:
            st.info("No activity yet.")
        else:
            for item in feed:
                st.markdown(f"`{item['time']}` {item['msg']}")

    # ── Auto-refresh countdown ────────────────────────────────────────────────
    if st.session_state.auto_triage:
        elapsed = time.time() - st.session_state.last_refresh
        remaining = max(0, int(refresh_rate - elapsed))
        st.caption(f"⏱️ Auto-triage ON — next refresh in {remaining}s")
        time.sleep(1)
        st.rerun()
    else:
        if st.button("🔄 Refresh now"):
            st.rerun()
