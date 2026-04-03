import streamlit as st
import pandas as pd
import re
import time
from collections import Counter
from datetime import datetime

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Sentinel-X",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Global CSS — hacker terminal aesthetic ────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;600;700&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    background-color: #050a0f !important;
    color: #c8e6ff !important;
    font-family: 'Rajdhani', sans-serif !important;
}
.stApp { background-color: #050a0f; }

/* ── Hide default streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 2rem 2rem 2rem !important; max-width: 100% !important; }

/* ── Header banner ── */
.sentinel-header {
    background: #0a1220;
    border-bottom: 1px solid #1a3a5c;
    padding: 14px 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: 0 -2rem 2rem -2rem;
}
.sentinel-logo {
    font-family: 'Rajdhani', sans-serif;
    font-size: 22px;
    font-weight: 700;
    letter-spacing: 4px;
    color: #00d4ff;
}
.sentinel-sub {
    font-family: 'Share Tech Mono', monospace;
    font-size: 10px;
    color: #4a7fa5;
    letter-spacing: 2px;
    margin-top: 2px;
}
.status-online {
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    color: #00ff9d;
    letter-spacing: 1px;
}

/* ── Metric cards ── */
.metric-card {
    background: #0a1220;
    border: 1px solid #1a3a5c;
    padding: 16px 20px;
    margin-bottom: 0;
}
.metric-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 10px;
    color: #4a7fa5;
    letter-spacing: 2px;
    margin-bottom: 8px;
}
.metric-value {
    font-family: 'Rajdhani', sans-serif;
    font-size: 36px;
    font-weight: 700;
    line-height: 1;
}
.metric-sub {
    font-size: 12px;
    color: #4a7fa5;
    margin-top: 4px;
    font-family: 'Share Tech Mono', monospace;
}
.color-cyan   { color: #00d4ff; }
.color-red    { color: #ff3860; }
.color-green  { color: #00ff9d; }
.color-amber  { color: #ffaa00; }

/* ── Section headers ── */
.section-head {
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    letter-spacing: 3px;
    color: #4a7fa5;
    border-bottom: 1px solid #1a3a5c;
    padding-bottom: 8px;
    margin: 24px 0 14px 0;
}

/* ── Alert boxes ── */
.alert-critical {
    background: rgba(255,56,96,0.08);
    border: 1px solid rgba(255,56,96,0.4);
    border-left: 3px solid #ff3860;
    padding: 12px 16px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 12px;
    color: #ff3860;
    margin-bottom: 12px;
    letter-spacing: 1px;
}
.alert-safe {
    background: rgba(0,255,157,0.06);
    border: 1px solid rgba(0,255,157,0.3);
    border-left: 3px solid #00ff9d;
    padding: 12px 16px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 12px;
    color: #00ff9d;
    margin-bottom: 12px;
    letter-spacing: 1px;
}
.alert-warn {
    background: rgba(255,170,0,0.08);
    border: 1px solid rgba(255,170,0,0.3);
    border-left: 3px solid #ffaa00;
    padding: 12px 16px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 12px;
    color: #ffaa00;
    margin-bottom: 12px;
    letter-spacing: 1px;
}

/* ── IP table ── */
.ip-table-wrap { overflow-x: auto; }
table.ip-table {
    width: 100%;
    border-collapse: collapse;
    font-family: 'Share Tech Mono', monospace;
    font-size: 12px;
}
table.ip-table th {
    text-align: left;
    padding: 8px 14px;
    color: #4a7fa5;
    font-size: 10px;
    letter-spacing: 2px;
    border-bottom: 1px solid #1a3a5c;
    font-weight: 400;
}
table.ip-table td {
    padding: 9px 14px;
    border-bottom: 1px solid rgba(26,58,92,0.5);
    color: #c8e6ff;
}
table.ip-table tr:hover td { background: rgba(0,212,255,0.04); }
.badge {
    display: inline-block;
    padding: 2px 10px;
    font-size: 10px;
    letter-spacing: 1px;
    font-family: 'Share Tech Mono', monospace;
    border: 1px solid;
}
.badge-red   { color: #ff3860; border-color: rgba(255,56,96,0.4);  background: rgba(255,56,96,0.1); }
.badge-green { color: #00ff9d; border-color: rgba(0,255,157,0.4);  background: rgba(0,255,157,0.1); }
.badge-amber { color: #ffaa00; border-color: rgba(255,170,0,0.4);  background: rgba(255,170,0,0.1); }

/* ── Timeline ── */
.timeline-item {
    border-left: 1px solid #1a3a5c;
    padding: 8px 0 8px 18px;
    position: relative;
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
}
.timeline-dot {
    position: absolute;
    left: -4px;
    top: 13px;
    width: 7px;
    height: 7px;
    border: 1px solid;
    background: #050a0f;
}
.tl-time  { color: #4a7fa5; font-size: 10px; }
.tl-msg   { margin-top: 3px; }

/* ── Bar chart ── */
.bar-row { margin: 6px 0; }
.bar-label-row {
    display: flex;
    justify-content: space-between;
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    margin-bottom: 3px;
    color: #c8e6ff;
}
.bar-track {
    height: 5px;
    background: rgba(26,58,92,0.5);
}
.bar-fill { height: 100%; }

/* ── Log viewer ── */
.log-viewer {
    background: #020609;
    border: 1px solid #1a3a5c;
    padding: 12px 16px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    line-height: 1.9;
    max-height: 260px;
    overflow-y: auto;
}
.log-fail    { color: #ff3860; }
.log-accept  { color: #00ff9d; }
.log-warn    { color: #ffaa00; }
.log-default { color: #4a7fa5; }

/* ── AI panel ── */
.ai-panel {
    background: #0a1220;
    border: 1px solid #1a3a5c;
}
.ai-header {
    background: #0f1c2e;
    border-bottom: 1px solid #1a3a5c;
    padding: 10px 16px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    letter-spacing: 2px;
    color: #00d4ff;
}
.ai-body {
    padding: 16px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 12px;
    line-height: 1.8;
    color: #c8e6ff;
    white-space: pre-wrap;
    min-height: 100px;
}

/* ── Upload zone ── */
[data-testid="stFileUploader"] {
    background: #0a1220 !important;
    border: 1px dashed #1a3a5c !important;
    padding: 8px !important;
}

/* ── Streamlit buttons ── */
.stButton > button {
    background: transparent !important;
    border: 1px solid #00d4ff !important;
    color: #00d4ff !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 2px !important;
    padding: 8px 20px !important;
    border-radius: 0 !important;
    transition: background 0.2s !important;
}
.stButton > button:hover {
    background: rgba(0,212,255,0.1) !important;
}

/* ── Divider ── */
hr { border-color: #1a3a5c !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0a1220 !important;
    border-right: 1px solid #1a3a5c !important;
}
</style>
""", unsafe_allow_html=True)


# ── Helpers ──────────────────────────────────────────────────────────────────

IP_PATTERN  = re.compile(r"from (\d+\.\d+\.\d+\.\d+)")
TIME_PATTERN = re.compile(r"^(\w+\s+\d+\s+\d+:\d+:\d+)")
HOSTILE_THRESHOLD = 4


def parse_logs(text: str) -> dict:
    lines = [l for l in text.splitlines() if l.strip()]
    failed, accepted, events = [], [], []

    ip_counter: Counter = Counter()

    for line in lines:
        ip_match   = IP_PATTERN.search(line)
        time_match = TIME_PATTERN.match(line)
        ip  = ip_match.group(1)   if ip_match   else None
        ts  = time_match.group(1) if time_match else None

        if "Failed password" in line or "Invalid user" in line:
            failed.append(line)
            if ip:
                ip_counter[ip] += 1
                events.append({"ts": ts, "ip": ip, "type": "fail", "line": line})
        elif "Accepted password" in line or "Accepted publickey" in line:
            accepted.append(line)
            if ip:
                events.append({"ts": ts, "ip": ip, "type": "accept", "line": line})
        elif "Connection closed" in line or "error" in line.lower():
            if ip:
                events.append({"ts": ts, "ip": ip, "type": "warn", "line": line})

    all_ips    = ip_counter.most_common()
    suspicious = [(ip, c) for ip, c in all_ips if c >= HOSTILE_THRESHOLD]
    max_count  = all_ips[0][1] if all_ips else 1

    threat_score = min(100, len(suspicious) * 20 + (10 if failed else 0))
    if threat_score >= 70:
        threat_level = ("CRITICAL", "#ff3860")
    elif threat_score >= 40:
        threat_level = ("ELEVATED", "#ffaa00")
    elif threat_score >= 10:
        threat_level = ("GUARDED", "#00d4ff")
    else:
        threat_level = ("NOMINAL", "#00ff9d")

    return dict(
        lines=lines, failed=failed, accepted=accepted, events=events,
        ip_counter=ip_counter, all_ips=all_ips, suspicious=suspicious,
        max_count=max_count, threat_score=threat_score, threat_level=threat_level,
    )


def render_metric(label: str, value, sub: str, color_class: str):
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">// {label}</div>
        <div class="metric-value {color_class}">{value}</div>
        <div class="metric-sub">{sub}</div>
    </div>""", unsafe_allow_html=True)


def render_ip_table(all_ips, suspicious_set):
    rows = ""
    for ip, count in all_ips:
        if ip in suspicious_set:
            badge = '<span class="badge badge-red">HOSTILE</span>'
        elif count > 1:
            badge = '<span class="badge badge-amber">MONITOR</span>'
        else:
            badge = '<span class="badge badge-green">LOW</span>'
        rows += f"<tr><td>{ip}</td><td>{count}</td><td>{badge}</td></tr>"

    st.markdown(f"""
    <div class="ip-table-wrap">
    <table class="ip-table">
        <thead><tr><th>IP ADDRESS</th><th>ATTEMPTS</th><th>STATUS</th></tr></thead>
        <tbody>{rows}</tbody>
    </table>
    </div>""", unsafe_allow_html=True)


def render_bar_chart(all_ips, max_count, suspicious_set):
    html = ""
    for ip, count in all_ips:
        pct = int(count / max_count * 100)
        color = "#ff3860" if ip in suspicious_set else ("#ffaa00" if count > 1 else "#00ff9d")
        html += f"""
        <div class="bar-row">
          <div class="bar-label-row"><span>{ip}</span><span style="color:{color}">{count}</span></div>
          <div class="bar-track"><div class="bar-fill" style="width:{pct}%;background:{color}"></div></div>
        </div>"""
    st.markdown(html, unsafe_allow_html=True)


def render_timeline(events):
    items = events[-10:]
    html = ""
    for e in reversed(items):
        if e["type"] == "fail":
            color, label = "#ff3860", "FAILED AUTH"
        elif e["type"] == "accept":
            color, label = "#00ff9d", "ACCEPTED"
        else:
            color, label = "#ffaa00", "ANOMALY"
        html += f"""
        <div class="timeline-item">
          <div class="timeline-dot" style="border-color:{color}"></div>
          <div class="tl-time">{e['ts'] or '--:--:--'}</div>
          <div class="tl-msg" style="color:{color}">{label} — {e['ip']}</div>
        </div>"""
    st.markdown(html, unsafe_allow_html=True)


def render_log_viewer(lines):
    html = ""
    for line in lines[-60:]:
        if "Failed password" in line or "Invalid user" in line:
            cls = "log-fail"
        elif "Accepted" in line:
            cls = "log-accept"
        elif "error" in line.lower() or "closed" in line.lower():
            cls = "log-warn"
        else:
            cls = "log-default"
        escaped = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        html += f'<div class="{cls}">{escaped}</div>'
    st.markdown(f'<div class="log-viewer">{html}</div>', unsafe_allow_html=True)



# ── Header ───────────────────────────────────────────────────────────────────

st.markdown(f"""
<div class="sentinel-header">
  <div>
    <div class="sentinel-logo">⬡ SENTINEL-X</div>
    <div class="sentinel-sub">AUTONOMOUS LOG SENTINEL — ZERO TRUST ANALYZER</div>
  </div>
  <div class="status-online">● SYSTEM ONLINE &nbsp;|&nbsp; {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</div>
</div>
""", unsafe_allow_html=True)


# ── File upload ───────────────────────────────────────────────────────────────

st.markdown('<div class="section-head">// INPUT — AUTH LOG</div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader(
    "Drop auth.log here or click to browse",
    type=["log", "txt"],
    label_visibility="collapsed",
)

# Use sample data when nothing is uploaded
SAMPLE_LOG = """\
Oct 15 00:01:03 prodserver sshd[4821]: Failed password for root from 45.33.32.156 port 54312 ssh2
Oct 15 00:01:07 prodserver sshd[4822]: Failed password for root from 45.33.32.156 port 54313 ssh2
Oct 15 00:01:11 prodserver sshd[4823]: Failed password for root from 45.33.32.156 port 54314 ssh2
Oct 15 00:01:15 prodserver sshd[4824]: Failed password for root from 45.33.32.156 port 54315 ssh2
Oct 15 00:01:19 prodserver sshd[4825]: Failed password for root from 45.33.32.156 port 54316 ssh2
Oct 15 00:01:23 prodserver sshd[4826]: Failed password for root from 45.33.32.156 port 54317 ssh2
Oct 15 00:01:27 prodserver sshd[4827]: Failed password for admin from 45.33.32.156 port 54318 ssh2
Oct 15 00:01:31 prodserver sshd[4828]: Failed password for admin from 45.33.32.156 port 54319 ssh2
Oct 15 00:03:00 prodserver sshd[4835]: Accepted password for devops from 10.0.1.15 port 50210 ssh2
Oct 15 00:05:44 prodserver sshd[4850]: Failed password for root from 198.199.101.42 port 44210 ssh2
Oct 15 00:05:48 prodserver sshd[4851]: Failed password for root from 198.199.101.42 port 44211 ssh2
Oct 15 00:05:52 prodserver sshd[4852]: Failed password for root from 198.199.101.42 port 44212 ssh2
Oct 15 00:05:56 prodserver sshd[4853]: Failed password for root from 198.199.101.42 port 44213 ssh2
Oct 15 00:08:22 prodserver sshd[4860]: Invalid user postgres from 185.220.101.5 port 39100
Oct 15 00:08:26 prodserver sshd[4861]: Failed password for invalid user postgres from 185.220.101.5 port 39100 ssh2
Oct 15 00:08:30 prodserver sshd[4862]: Invalid user mysql from 185.220.101.5 port 39101
Oct 15 00:08:34 prodserver sshd[4863]: Failed password for invalid user mysql from 185.220.101.5 port 39101 ssh2
Oct 15 00:10:15 prodserver sshd[4880]: Accepted publickey for alice from 192.168.0.22 port 51200 ssh2
Oct 15 00:11:00 prodserver sshd[4890]: Failed password for root from 91.229.77.13 port 60011 ssh2
Oct 15 00:11:04 prodserver sshd[4891]: Failed password for root from 91.229.77.13 port 60012 ssh2
Oct 15 00:11:08 prodserver sshd[4892]: Failed password for root from 91.229.77.13 port 60013 ssh2
Oct 15 00:11:12 prodserver sshd[4893]: Failed password for root from 91.229.77.13 port 60014 ssh2
Oct 15 00:22:10 prodserver sshd[4930]: Failed password for root from 222.186.61.44 port 48200 ssh2
Oct 15 00:22:14 prodserver sshd[4931]: Failed password for admin from 222.186.61.44 port 48201 ssh2
Oct 15 00:22:18 prodserver sshd[4932]: Failed password for user from 222.186.61.44 port 48202 ssh2
Oct 15 00:22:22 prodserver sshd[4933]: Failed password for test from 222.186.61.44 port 48203 ssh2
Oct 15 00:22:26 prodserver sshd[4934]: Failed password for guest from 222.186.61.44 port 48204 ssh2
Oct 15 00:25:00 prodserver sshd[4940]: Accepted publickey for deploy from 10.0.2.5 port 53000 ssh2
Oct 15 00:28:33 prodserver sshd[4950]: Failed password for root from 45.33.32.156 port 54500 ssh2
Oct 15 00:28:37 prodserver sshd[4951]: Failed password for root from 45.33.32.156 port 54501 ssh2
Oct 15 00:33:00 prodserver sshd[4970]: Accepted password for charlie from 192.168.0.55 port 51900 ssh2
"""

if uploaded_file:
    raw_text = uploaded_file.getvalue().decode("utf-8")
    source_label = f"📄 {uploaded_file.name}"
else:
    raw_text = SAMPLE_LOG
    source_label = "📄 sample_auth.log (demo)"
    st.markdown(
        '<div class="alert-warn">[ DEMO MODE ] No file uploaded — showing sample data. '
        'Upload your own auth.log above.</div>',
        unsafe_allow_html=True,
    )

data = parse_logs(raw_text)
suspicious_set = {ip for ip, _ in data["suspicious"]}

# ── Metrics row ───────────────────────────────────────────────────────────────

st.markdown('<div class="section-head">// THREAT DASHBOARD</div>', unsafe_allow_html=True)

tl_name, tl_color = data["threat_level"]
col1, col2, col3, col4 = st.columns(4)

with col1:
    render_metric("TOTAL EVENTS", len(data["lines"]), source_label, "color-cyan")
with col2:
    color_cls = "color-red" if data["failed"] else "color-green"
    render_metric("FAILED LOGINS", len(data["failed"]), f"{len(data['accepted'])} accepted sessions", color_cls)
with col3:
    color_cls = "color-red" if data["suspicious"] else "color-green"
    render_metric("HOSTILE IPs", len(data["suspicious"]), f"threshold ≥ {HOSTILE_THRESHOLD} attempts", color_cls)
with col4:
    color_cls = (
        "color-red" if tl_name == "CRITICAL" else
        "color-amber" if tl_name == "ELEVATED" else
        "color-cyan" if tl_name == "GUARDED" else "color-green"
    )
    render_metric("THREAT LEVEL", tl_name, f"score: {data['threat_score']}/100", color_cls)

# ── Alert banner ──────────────────────────────────────────────────────────────

if data["suspicious"]:
    ips_str = ", ".join(ip for ip, _ in data["suspicious"][:3])
    more = f" +{len(data['suspicious'])-3} more" if len(data["suspicious"]) > 3 else ""
    st.markdown(
        f'<div class="alert-critical">⚠ CRITICAL ALERT — {len(data["suspicious"])} IPs flagged as hostile: '
        f'{ips_str}{more}</div>',
        unsafe_allow_html=True,
    )
elif data["failed"]:
    st.markdown(
        f'<div class="alert-warn">⚡ WARNING — {len(data["failed"])} failed login attempts detected. '
        f'No IPs exceeded the hostile threshold yet.</div>',
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        '<div class="alert-safe">✓ NO THREATS DETECTED — Log analysis complete. System nominal.</div>',
        unsafe_allow_html=True,
    )

# ── IP table + Timeline ───────────────────────────────────────────────────────

st.markdown('<div class="section-head">// IP THREAT MATRIX &amp; ATTACK TIMELINE</div>', unsafe_allow_html=True)
col_left, col_right = st.columns([3, 2])

with col_left:
    if data["all_ips"]:
        render_ip_table(data["all_ips"], suspicious_set)
    else:
        st.markdown('<div class="alert-safe">✓ No IP activity detected.</div>', unsafe_allow_html=True)

with col_right:
    if data["events"]:
        render_timeline(data["events"])
    else:
        st.markdown(
            '<p style="font-family:\'Share Tech Mono\',monospace;font-size:12px;color:#4a7fa5;">'
            'No timeline events.</p>',
            unsafe_allow_html=True,
        )

# ── Frequency bar chart ───────────────────────────────────────────────────────

if data["all_ips"]:
    st.markdown('<div class="section-head">// ATTEMPT FREQUENCY ANALYSIS</div>', unsafe_allow_html=True)
    render_bar_chart(data["all_ips"], data["max_count"], suspicious_set)

# ── AI Analysis panel — Coming Soon ──────────────────────────────────────────

st.markdown('<div class="section-head">// SENTINEL AI — THREAT INTELLIGENCE</div>', unsafe_allow_html=True)
st.markdown("""
<div class="ai-panel">
  <div class="ai-header">⬡ CLAUDE-POWERED THREAT ASSESSMENT ENGINE</div>
  <div style="padding:40px 24px;text-align:center;">
    <div style="font-family:'Share Tech Mono',monospace;font-size:32px;color:#1a3a5c;letter-spacing:6px;margin-bottom:16px;">
      [ COMING SOON ]
    </div>
    <div style="font-family:'Share Tech Mono',monospace;font-size:12px;color:#4a7fa5;letter-spacing:2px;line-height:2;">
      AI-POWERED THREAT ASSESSMENT &nbsp;/&nbsp; ATTACK PATTERN CLASSIFICATION<br>
      HOSTILE IP PROFILING &nbsp;/&nbsp; AUTOMATED MITIGATION RECOMMENDATIONS
    </div>
    <div style="margin-top:24px;display:inline-block;border:1px dashed #1a3a5c;padding:10px 28px;
                font-family:'Share Tech Mono',monospace;font-size:11px;color:#1a3a5c;letter-spacing:2px;">
      FEATURE UNDER DEVELOPMENT — GHOSTPROTOCOL v2.0
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Raw log stream ────────────────────────────────────────────────────────────

with st.expander("// RAW LOG STREAM", expanded=False):
    render_log_viewer(data["lines"])

# ── Footer ────────────────────────────────────────────────────────────────────

st.markdown("""
<hr>
<p style="font-family:'Share Tech Mono',monospace;font-size:10px;color:#1a3a5c;text-align:center;letter-spacing:2px;">
SENTINEL-X — BUILT BY GHOSTPROTOCOL — ZERO TRUST LOG INTELLIGENCE
</p>
""", unsafe_allow_html=True)