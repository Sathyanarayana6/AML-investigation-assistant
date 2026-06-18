import streamlit as st
import json
import pandas as pd
from datetime import datetime
import random

# ─── PAGE CONFIG ───────────────────────────────────────────────
st.set_page_config(
    page_title="AML Command Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CORPORATE CSS ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"] {
    background: #0A0D14 !important;
    color: #E2E8F0 !important;
    font-family: 'Inter', sans-serif !important;
}

[data-testid="stSidebar"] {
    background: #0D1117 !important;
    border-right: 1px solid #1E2433 !important;
}

/* ── Hide Streamlit Branding ── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }

/* ── Top Nav Bar ── */
.nav-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 24px;
    background: #0D1117;
    border-bottom: 1px solid #1E2433;
    margin: -1rem -1rem 2rem -1rem;
}
.nav-logo {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 18px;
    font-weight: 700;
    color: #F8FAFC;
    letter-spacing: -0.3px;
}
.nav-logo span { color: #3B82F6; }
.nav-badge {
    background: #FF3B30;
    color: white;
    font-size: 11px;
    font-weight: 600;
    padding: 3px 8px;
    border-radius: 20px;
    letter-spacing: 0.5px;
}
.nav-right {
    display: flex;
    align-items: center;
    gap: 16px;
    font-size: 13px;
    color: #64748B;
}
.nav-time {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: #3B82F6;
}

/* ── KPI Cards ── */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 24px;
}
.kpi-card {
    background: #0D1117;
    border: 1px solid #1E2433;
    border-radius: 12px;
    padding: 20px;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
}
.kpi-card:hover { border-color: #3B82F6; }
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    border-radius: 12px 12px 0 0;
}
.kpi-card.critical::before { background: #FF3B30; }
.kpi-card.high::before     { background: #FF9500; }
.kpi-card.medium::before   { background: #FFCC00; }
.kpi-card.low::before      { background: #30D158; }

.kpi-label {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 8px;
}
.kpi-card.critical .kpi-label { color: #FF3B30; }
.kpi-card.high .kpi-label     { color: #FF9500; }
.kpi-card.medium .kpi-label   { color: #FFCC00; }
.kpi-card.low .kpi-label      { color: #30D158; }

.kpi-value {
    font-size: 36px;
    font-weight: 700;
    color: #F8FAFC;
    line-height: 1;
    font-family: 'JetBrains Mono', monospace;
}
.kpi-sub {
    font-size: 12px;
    color: #64748B;
    margin-top: 6px;
}

/* ── Section Headers ── */
.section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid #1E2433;
}
.section-title {
    font-size: 14px;
    font-weight: 600;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* ── Alert Cards ── */
.alert-card {
    background: #0D1117;
    border: 1px solid #1E2433;
    border-radius: 10px;
    padding: 16px 20px;
    margin-bottom: 10px;
    cursor: pointer;
    transition: all 0.2s;
    position: relative;
}
.alert-card:hover {
    border-color: #3B82F6;
    background: #111827;
    transform: translateX(2px);
}
.alert-card.critical { border-left: 3px solid #FF3B30; }
.alert-card.high     { border-left: 3px solid #FF9500; }
.alert-card.medium   { border-left: 3px solid #FFCC00; }
.alert-card.low      { border-left: 3px solid #30D158; }

.alert-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8px;
}
.alert-customer {
    font-size: 14px;
    font-weight: 600;
    color: #F8FAFC;
}
.alert-id {
    font-size: 11px;
    color: #475569;
    font-family: 'JetBrains Mono', monospace;
}
.alert-meta {
    display: flex;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
}
.risk-badge {
    font-size: 11px;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 20px;
    letter-spacing: 0.5px;
}
.risk-badge.critical { background: rgba(255,59,48,0.15);  color: #FF3B30; }
.risk-badge.high     { background: rgba(255,149,0,0.15);  color: #FF9500; }
.risk-badge.medium   { background: rgba(255,204,0,0.15);  color: #FFCC00; }
.risk-badge.low      { background: rgba(48,209,88,0.15);  color: #30D158; }

.pattern-tag {
    font-size: 11px;
    background: rgba(59,130,246,0.1);
    color: #60A5FA;
    padding: 2px 8px;
    border-radius: 4px;
    border: 1px solid rgba(59,130,246,0.2);
    font-family: 'JetBrains Mono', monospace;
}
.alert-summary {
    font-size: 12px;
    color: #64748B;
    margin-top: 6px;
    line-height: 1.5;
}
.score-bar-container {
    margin-top: 10px;
}
.score-bar-label {
    display: flex;
    justify-content: space-between;
    font-size: 11px;
    color: #475569;
    margin-bottom: 4px;
}
.score-bar {
    height: 4px;
    background: #1E2433;
    border-radius: 2px;
    overflow: hidden;
}
.score-fill {
    height: 100%;
    border-radius: 2px;
    transition: width 0.5s ease;
}

/* ── Detail Panel ── */
.detail-panel {
    background: #0D1117;
    border: 1px solid #1E2433;
    border-radius: 12px;
    padding: 24px;
    height: fit-content;
}
.detail-header {
    margin-bottom: 20px;
    padding-bottom: 16px;
    border-bottom: 1px solid #1E2433;
}
.detail-title {
    font-size: 16px;
    font-weight: 600;
    color: #F8FAFC;
    margin-bottom: 4px;
}
.detail-sub {
    font-size: 12px;
    color: #475569;
    font-family: 'JetBrains Mono', monospace;
}
.detail-row {
    display: flex;
    justify-content: space-between;
    padding: 10px 0;
    border-bottom: 1px solid #0A0D14;
    font-size: 13px;
}
.detail-key { color: #64748B; }
.detail-val { color: #E2E8F0; font-weight: 500; }

.reasoning-box {
    background: #0A0D14;
    border: 1px solid #1E2433;
    border-radius: 8px;
    padding: 14px;
    margin-top: 16px;
    font-size: 12px;
    color: #94A3B8;
    line-height: 1.7;
    font-family: 'Inter', sans-serif;
}

/* ── Action Buttons ── */
.action-row {
    display: flex;
    gap: 10px;
    margin-top: 20px;
}
.btn {
    flex: 1;
    padding: 10px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 600;
    text-align: center;
    cursor: pointer;
    border: none;
    transition: all 0.2s;
}
.btn-approve {
    background: rgba(48,209,88,0.1);
    color: #30D158;
    border: 1px solid rgba(48,209,88,0.3);
}
.btn-reject {
    background: rgba(255,59,48,0.1);
    color: #FF3B30;
    border: 1px solid rgba(255,59,48,0.3);
}
.btn-escalate {
    background: rgba(255,149,0,0.1);
    color: #FF9500;
    border: 1px solid rgba(255,149,0,0.3);
}

/* ── New Investigation Form ── */
.form-panel {
    background: #0D1117;
    border: 1px solid #1E2433;
    border-radius: 12px;
    padding: 20px;
    margin-top: 20px;
}
.form-title {
    font-size: 13px;
    font-weight: 600;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid #1E2433;
}

/* ── Streamlit Widget Overrides ── */
[data-testid="stSelectbox"] > div > div {
    background: #111827 !important;
    border: 1px solid #1E2433 !important;
    color: #E2E8F0 !important;
    border-radius: 8px !important;
}
[data-testid="stTextInput"] > div > div > input {
    background: #111827 !important;
    border: 1px solid #1E2433 !important;
    color: #E2E8F0 !important;
    border-radius: 8px !important;
}
[data-testid="stButton"] > button {
    background: #1D4ED8 !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    padding: 10px 20px !important;
    width: 100% !important;
    transition: background 0.2s !important;
}
[data-testid="stButton"] > button:hover {
    background: #2563EB !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stTextInput label {
    color: #64748B !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
}
.sidebar-section {
    padding: 16px;
    border-bottom: 1px solid #1E2433;
    margin-bottom: 8px;
}
.sidebar-label {
    font-size: 10px;
    font-weight: 600;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 12px;
}
.sidebar-stat {
    display: flex;
    justify-content: space-between;
    font-size: 12px;
    padding: 6px 0;
    border-bottom: 1px solid #0A0D14;
}
.sidebar-stat-key { color: #64748B; }
.sidebar-stat-val { color: #E2E8F0; font-weight: 500; font-family: 'JetBrains Mono', monospace; }

/* ── Live Indicator ── */
.live-dot {
    display: inline-block;
    width: 8px; height: 8px;
    background: #30D158;
    border-radius: 50%;
    animation: pulse 2s infinite;
    margin-right: 6px;
}
@keyframes pulse {
    0%   { box-shadow: 0 0 0 0 rgba(48,209,88,0.4); }
    70%  { box-shadow: 0 0 0 8px rgba(48,209,88,0); }
    100% { box-shadow: 0 0 0 0 rgba(48,209,88,0); }
}

/* ── Result Box ── */
.result-box {
    background: #0A0D14;
    border: 1px solid #1E2433;
    border-radius: 10px;
    padding: 16px;
    margin-top: 16px;
}
.result-title {
    font-size: 12px;
    font-weight: 600;
    color: #3B82F6;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 12px;
}
</style>
""", unsafe_allow_html=True)


# ─── SAMPLE DATA ───────────────────────────────────────────────
INVESTIGATIONS = [
    {
        "investigation_id": "INV-2026-0081",
        "customer_id": "CUST_44821",
        "customer_name": "Marcus Chen",
        "timestamp": "2026-06-18 09:14:22",
        "final_risk_level": "CRITICAL",
        "final_risk_score": 100,
        "recommended_action": "IMMEDIATE_REVIEW",
        "transaction_patterns": ["STRUCTURING", "RAPID_MOVEMENT"],
        "customer_risk": "HIGH",
        "summary": "8 consecutive deposits just under $10K threshold with same-day withdrawal. Customer has 3 prior AML flags.",
        "reasoning": "This case presents maximum risk (100/100). STRUCTURING detected across 8 consecutive daily cash deposits ranging $9,100–$9,800, all deliberately below the $10,000 CTR reporting threshold. RAPID_MOVEMENT detected: $98,500 withdrawn within 47 minutes of deposit. Customer profile compounds risk: 3 prior AML flags (most recent Aug 2025), declared income of $2,000/month as 'Unknown occupation' is implausible given transaction volumes. Escalation triggers fired: previous flags >2, combined pattern score in CRITICAL band (80–100). Immediate investigative action required."
    },
    {
        "investigation_id": "INV-2026-0082",
        "customer_id": "CUST_29103",
        "customer_name": "Sofia Reyes",
        "timestamp": "2026-06-18 09:31:05",
        "final_risk_level": "HIGH",
        "final_risk_score": 72,
        "recommended_action": "ESCALATE_TO_ANALYST",
        "transaction_patterns": ["SMURFING"],
        "customer_risk": "MEDIUM",
        "summary": "5 different customer IDs all transferred funds to same destination account within 90-minute window.",
        "reasoning": "SMURFING pattern detected: 5 distinct customer IDs (CUST_11234, CUST_55678, CUST_99012, CUST_33456, CUST_77890) each transferred $2,900–$4,400 to destination account ACCT_88234 within a 90-minute window. Total coordinated inflow: $17,850. Transaction risk scored HIGH (60 pts). Customer profile shows medium risk: 18-month-old account, 1 prior flag, income consistent with transaction size but coordination pattern is anomalous. Combined score 72/100 falls in HIGH band. Analyst review recommended."
    },
    {
        "investigation_id": "INV-2026-0083",
        "customer_id": "CUST_61447",
        "customer_name": "James Okafor",
        "timestamp": "2026-06-18 09:48:33",
        "final_risk_level": "HIGH",
        "final_risk_score": 65,
        "recommended_action": "ESCALATE_TO_ANALYST",
        "transaction_patterns": ["LAYERING"],
        "customer_risk": "LOW",
        "summary": "Funds moved through 4 accounts in 6 hours with progressive fee deductions. No business justification.",
        "reasoning": "LAYERING pattern detected: $52,000 moved through 4 intermediary accounts (ACCT_A → ACCT_B → ACCT_C → ACCT_D → External) within 6 hours, with $500 fee deducted at each hop. No legitimate business reason identified for this routing pattern. Transaction risk scored HIGH (60 pts). Customer profile is LOW risk (84-month-old account, zero prior flags, Software Engineer with $8,000 monthly income consistent with transaction scale) reducing overall score. Combined score 65/100. Pattern warrants analyst review despite clean customer history."
    },
    {
        "investigation_id": "INV-2026-0084",
        "customer_id": "CUST_73290",
        "customer_name": "Priya Sharma",
        "timestamp": "2026-06-18 10:02:17",
        "final_risk_level": "MEDIUM",
        "final_risk_score": 38,
        "recommended_action": "MONITOR",
        "transaction_patterns": ["CIRCULAR_TRANSFERS"],
        "customer_risk": "LOW",
        "summary": "Circular transfer pattern detected across 3 accounts with minor fee deductions. Customer profile is clean.",
        "reasoning": "CIRCULAR_TRANSFERS pattern detected: $24,500 cycled through accounts ACCT_X → ACCT_Y → ACCT_Z → ACCT_X across 2 cycles with $100 fee per hop. While the pattern is technically suspicious, the scale is relatively small and the customer profile is strongly clean: 72-month account, 0 prior flags, Teacher with $3,500 monthly income. The circular movement may represent a legitimate treasury management practice. Combined score 38/100 falls in MEDIUM band. Recommend monitoring for pattern escalation over next 30 days."
    },
    {
        "investigation_id": "INV-2026-0085",
        "customer_id": "CUST_18834",
        "customer_name": "David Park",
        "timestamp": "2026-06-18 10:19:44",
        "final_risk_level": "LOW",
        "final_risk_score": 8,
        "recommended_action": "NO_ACTION",
        "transaction_patterns": [],
        "customer_risk": "LOW",
        "summary": "Normal salary deposits, utility payments, and ATM withdrawals. No suspicious patterns detected.",
        "reasoning": "No AML patterns detected. Transaction history shows regular monthly salary deposit ($3,500), standard utility payments (electric $142, internet $78, phone $55), monthly rent transfer ($1,200), and routine ATM withdrawals ($200). All transaction sizes, timing, and destinations are consistent with a standard personal banking profile. Customer profile confirms LOW risk: 96-month account, 0 prior flags, verified employment as Doctor with $8,000 monthly income. No action required. Combined score 8/100."
    },
]

RISK_COLORS = {
    "CRITICAL": "#FF3B30",
    "HIGH": "#FF9500",
    "MEDIUM": "#FFCC00",
    "LOW": "#30D158"
}

ACTION_LABELS = {
    "IMMEDIATE_REVIEW":    "🚨 Immediate Review",
    "ESCALATE_TO_ANALYST": "⚠️  Escalate",
    "MONITOR":             "👁  Monitor",
    "NO_ACTION":           "✅ No Action"
}


# ─── SIDEBAR ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding: 20px 16px 12px;'>
        <div style='font-size:11px; font-weight:700; color:#475569; letter-spacing:1.5px; text-transform:uppercase; margin-bottom:16px;'>System Status</div>
        <div class='sidebar-stat'><span class='sidebar-stat-key'>Lambda</span><span class='sidebar-stat-val' style='color:#30D158;'>● Online</span></div>
        <div class='sidebar-stat'><span class='sidebar-stat-key'>Bedrock</span><span class='sidebar-stat-val' style='color:#30D158;'>● Online</span></div>
        <div class='sidebar-stat'><span class='sidebar-stat-key'>DynamoDB</span><span class='sidebar-stat-val' style='color:#30D158;'>● Online</span></div>
        <div class='sidebar-stat'><span class='sidebar-stat-key'>Model</span><span class='sidebar-stat-val'>Claude Sonnet</span></div>
        <div class='sidebar-stat'><span class='sidebar-stat-key'>Region</span><span class='sidebar-stat-val'>us-east-1</span></div>
    </div>
    <div style='padding: 16px; border-top: 1px solid #1E2433;'>
        <div style='font-size:11px; font-weight:700; color:#475569; letter-spacing:1.5px; text-transform:uppercase; margin-bottom:16px;'>Today's Summary</div>
        <div class='sidebar-stat'><span class='sidebar-stat-key'>Total Alerts</span><span class='sidebar-stat-val'>247</span></div>
        <div class='sidebar-stat'><span class='sidebar-stat-key'>Auto-Closed</span><span class='sidebar-stat-val'>189</span></div>
        <div class='sidebar-stat'><span class='sidebar-stat-key'>Escalated</span><span class='sidebar-stat-val'>43</span></div>
        <div class='sidebar-stat'><span class='sidebar-stat-key'>Critical</span><span class='sidebar-stat-val' style='color:#FF3B30;'>15</span></div>
        <div class='sidebar-stat'><span class='sidebar-stat-key'>Avg. Analysis Time</span><span class='sidebar-stat-val'>2.3s</span></div>
        <div class='sidebar-stat'><span class='sidebar-stat-key'>False Positive Rate</span><span class='sidebar-stat-val'>4.2%</span></div>
    </div>
    <div style='padding: 16px; border-top: 1px solid #1E2433;'>
        <div style='font-size:11px; font-weight:700; color:#475569; letter-spacing:1.5px; text-transform:uppercase; margin-bottom:16px;'>Filters</div>
    </div>
    """, unsafe_allow_html=True)

    risk_filter = st.selectbox(
        "RISK LEVEL",
        ["All Levels", "CRITICAL", "HIGH", "MEDIUM", "LOW"],
        label_visibility="collapsed"
    )

    st.markdown("<div style='padding: 0 16px;'>", unsafe_allow_html=True)
    pattern_filter = st.selectbox(
        "PATTERN",
        ["All Patterns", "STRUCTURING", "SMURFING", "LAYERING",
         "CIRCULAR_TRANSFERS", "RAPID_MOVEMENT"],
        label_visibility="collapsed"
    )
    st.markdown("</div>", unsafe_allow_html=True)


# ─── TOP NAV ───────────────────────────────────────────────────
now = datetime.now().strftime("%Y-%m-%d  %H:%M:%S UTC")
st.markdown(f"""
<div class='nav-bar'>
    <div class='nav-logo'>
        🛡️ &nbsp;<span>AML</span> Command Center
        <div class='nav-badge'>LIVE</div>
    </div>
    <div class='nav-right'>
        <span><span class='live-dot'></span>AI Agents Active</span>
        <span class='nav-time'>{now}</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ─── KPI METRICS ───────────────────────────────────────────────
counts = {r: len([i for i in INVESTIGATIONS if i['final_risk_level'] == r])
          for r in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]}

st.markdown(f"""
<div class='kpi-grid'>
    <div class='kpi-card critical'>
        <div class='kpi-label'>Critical</div>
        <div class='kpi-value'>{counts['CRITICAL']}</div>
        <div class='kpi-sub'>Immediate action required</div>
    </div>
    <div class='kpi-card high'>
        <div class='kpi-label'>High Risk</div>
        <div class='kpi-value'>{counts['HIGH']}</div>
        <div class='kpi-sub'>Escalate to analyst</div>
    </div>
    <div class='kpi-card medium'>
        <div class='kpi-label'>Medium</div>
        <div class='kpi-value'>{counts['MEDIUM']}</div>
        <div class='kpi-sub'>Under monitoring</div>
    </div>
    <div class='kpi-card low'>
        <div class='kpi-label'>Cleared</div>
        <div class='kpi-value'>{counts['LOW']}</div>
        <div class='kpi-sub'>No action needed</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ─── MAIN LAYOUT ───────────────────────────────────────────────
left, right = st.columns([1.4, 1], gap="large")

# ── LEFT: ALERT LIST ──
with left:
    st.markdown("""
    <div class='section-header'>
        <div class='section-title'>Active Investigations</div>
    </div>
    """, unsafe_allow_html=True)

    # Apply filters
    filtered = INVESTIGATIONS
    if risk_filter != "All Levels":
        filtered = [i for i in filtered if i['final_risk_level'] == risk_filter]
    if pattern_filter != "All Patterns":
        filtered = [i for i in filtered if pattern_filter in i['transaction_patterns']]

    if not filtered:
        st.markdown("""
        <div style='text-align:center; padding:40px; color:#475569; font-size:13px;'>
            No investigations match the current filters.
        </div>
        """, unsafe_allow_html=True)

    selected_id = st.session_state.get('selected_inv', INVESTIGATIONS[0]['investigation_id'])

    for inv in filtered:
        rl = inv['final_risk_level'].lower()
        score = inv['final_risk_score']
        color = RISK_COLORS[inv['final_risk_level']]
        patterns_html = "".join(
            f"<span class='pattern-tag'>{p}</span>" for p in inv['transaction_patterns']
        ) if inv['transaction_patterns'] else "<span style='color:#475569;font-size:11px;'>No patterns</span>"

        is_selected = selected_id == inv['investigation_id']
        border_style = "border-color: #3B82F6;" if is_selected else ""

        st.markdown(f"""
        <div class='alert-card {rl}' style='{border_style}'>
            <div class='alert-top'>
                <div>
                    <div class='alert-customer'>{inv['customer_name']}</div>
                    <div class='alert-id'>{inv['investigation_id']} · {inv['customer_id']}</div>
                </div>
                <span class='risk-badge {rl}'>{inv['final_risk_level']}</span>
            </div>
            <div class='alert-meta'>
                {patterns_html}
                <span style='font-size:11px; color:#475569;'>{inv['timestamp']}</span>
            </div>
            <div class='alert-summary'>{inv['summary']}</div>
            <div class='score-bar-container'>
                <div class='score-bar-label'>
                    <span>Risk Score</span>
                    <span style='color:{color}; font-weight:600;'>{score}/100</span>
                </div>
                <div class='score-bar'>
                    <div class='score-fill' style='width:{score}%; background:{color};'></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button(
            f"View Details →",
            key=f"view_{inv['investigation_id']}",
            use_container_width=False
        ):
            st.session_state['selected_inv'] = inv['investigation_id']
            st.rerun()

# ── RIGHT: DETAIL PANEL + NEW INVESTIGATION ──
with right:

    # ── Detail Panel ──
    selected_inv = next(
        (i for i in INVESTIGATIONS if i['investigation_id'] == selected_id),
        INVESTIGATIONS[0]
    )
    rl = selected_inv['final_risk_level']
    color = RISK_COLORS[rl]

    st.markdown(f"""
    <div class='detail-panel'>
        <div class='detail-header'>
            <div class='detail-title'>{selected_inv['customer_name']}</div>
            <div class='detail-sub'>{selected_inv['investigation_id']} · {selected_inv['customer_id']}</div>
        </div>
        <div class='detail-row'>
            <span class='detail-key'>Risk Level</span>
            <span class='risk-badge {rl.lower()}'>{rl}</span>
        </div>
        <div class='detail-row'>
            <span class='detail-key'>Risk Score</span>
            <span class='detail-val' style='color:{color}; font-family:JetBrains Mono,monospace;'>{selected_inv['final_risk_score']}/100</span>
        </div>
        <div class='detail-row'>
            <span class='detail-key'>Recommended Action</span>
            <span class='detail-val'>{ACTION_LABELS[selected_inv['recommended_action']]}</span>
        </div>
        <div class='detail-row'>
            <span class='detail-key'>Customer Risk</span>
            <span class='detail-val'>{selected_inv['customer_risk']}</span>
        </div>
        <div class='detail-row'>
            <span class='detail-key'>Patterns Detected</span>
            <span class='detail-val'>{', '.join(selected_inv['transaction_patterns']) if selected_inv['transaction_patterns'] else 'None'}</span>
        </div>
        <div class='detail-row'>
            <span class='detail-key'>Timestamp</span>
            <span class='detail-val' style='font-family:JetBrains Mono,monospace; font-size:12px;'>{selected_inv['timestamp']}</span>
        </div>
        <div style='margin-top:16px; font-size:11px; font-weight:600; color:#475569; text-transform:uppercase; letter-spacing:1px;'>AI Reasoning</div>
        <div class='reasoning-box'>{selected_inv['reasoning']}</div>
    </div>
    """, unsafe_allow_html=True)

    # Action buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("✅ Approve", key="approve_btn"):
            st.success("Case approved and closed.")
    with col2:
        if st.button("❌ Reject", key="reject_btn"):
            st.error("Case rejected.")
    with col3:
        if st.button("⚠️ Escalate", key="escalate_btn"):
            st.warning("Escalated to senior analyst.")

    # ── New Investigation ──
    st.markdown("""
    <div style='margin-top:20px;'>
    <div class='section-header'>
        <div class='section-title'>Run New Investigation</div>
    </div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("new_inv_form"):
        cust_id   = st.text_input("Customer ID", value="CUST_NEW_001", label_visibility="visible")
        cust_name = st.text_input("Customer Name", value="Test Customer", label_visibility="visible")
        pattern   = st.selectbox("Test Pattern", [
            "Structuring — 8 deposits under $10K",
            "Rapid Movement — $100K in/out same day",
            "Smurfing — 5 people to same account",
            "Legitimate — Normal transactions"
        ])
        submit = st.form_submit_button("🔍 Analyze via Lambda", use_container_width=True)

        if submit:
            if "Structuring" in pattern:
                transactions = [
                    {"date": f"2026-01-0{i+1}", "type": "DEPOSIT",
                     "amount": 9500 - (i * 100),
                     "description": "Cash deposit",
                     "destination": "Main account"} for i in range(8)
                ]
            elif "Rapid" in pattern:
                transactions = [
                    {"date": "2026-01-01", "type": "DEPOSIT",
                     "amount": 100000, "description": "Large cash deposit",
                     "destination": "Main account"},
                    {"date": "2026-01-01", "type": "WITHDRAWAL",
                     "amount": 99500, "description": "Large withdrawal",
                     "destination": "External account"}
                ]
            elif "Smurfing" in pattern:
                transactions = [
                    {"date": "2026-01-01", "type": "TRANSFER",
                     "amount": 3500 + (i * 200),
                     "description": f"Wire transfer from Customer {chr(65+i)} (CUST_{10000+i})",
                     "destination": "ACCT_99999"} for i in range(5)
                ]
            else:
                transactions = [
                    {"date": "2026-01-01", "type": "DEPOSIT",
                     "amount": 3500, "description": "Salary", "destination": "Main account"},
                    {"date": "2026-01-05", "type": "PAYMENT",
                     "amount": 1200, "description": "Rent", "destination": "Landlord"},
                    {"date": "2026-01-10", "type": "PAYMENT",
                     "amount": 150, "description": "Electric bill", "destination": "Utility"}
                ]

            with st.spinner("🤖 AI agents analyzing..."):
                try:
                    import boto3, json, os
                    from dotenv import load_dotenv
                    load_dotenv()
                    lambda_client = boto3.client('lambda', region_name=os.getenv("AWS_REGION", "us-east-1"))
                    payload = {"customer_id": cust_id, "customer_name": cust_name, "transactions": transactions}
                    response = lambda_client.invoke(
                        FunctionName="aml-investigation-assistant",
                        InvocationType='RequestResponse',
                        Payload=json.dumps(payload)
                    )
                    result = json.loads(response['Payload'].read())
                    body = json.loads(result.get('body', '{}'))

                    if body.get('success'):
                        r = body['results']
                        risk_color = RISK_COLORS.get(r.get('final_risk_level', 'LOW'), '#30D158')
                        st.markdown(f"""
                        <div class='result-box'>
                            <div class='result-title'>Investigation Complete</div>
                            <div class='detail-row'>
                                <span class='detail-key'>Risk Level</span>
                                <span style='color:{risk_color}; font-weight:700;'>{r.get('final_risk_level')}</span>
                            </div>
                            <div class='detail-row'>
                                <span class='detail-key'>Score</span>
                                <span class='detail-val'>{r.get('final_risk_score')}/100</span>
                            </div>
                            <div class='detail-row'>
                                <span class='detail-key'>Action</span>
                                <span class='detail-val'>{ACTION_LABELS.get(r.get('recommended_action',''), r.get('recommended_action',''))}</span>
                            </div>
                            <div class='detail-row'>
                                <span class='detail-key'>Patterns</span>
                                <span class='detail-val'>{', '.join(r.get('transaction_patterns', [])) or 'None'}</span>
                            </div>
                            <div style='margin-top:10px; font-size:12px; color:#94A3B8; line-height:1.6;'>{r.get('summary','')}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error(f"Investigation failed: {body.get('error')}")
                except Exception as e:
                    st.error(f"Lambda error: {str(e)}")