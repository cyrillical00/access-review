import streamlit as st
from pages import new_hire, access_review, violations, offboarding, audit_report

st.set_page_config(
    page_title="Access Review & Automation",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600&display=swap');

  html, body, [class*="css"] {
    font-family: 'IBM Plex Mono', monospace;
    background: #050508;
    color: #CBD5E1;
  }
  .stApp { background: #050508; }

  section[data-testid="stSidebar"] {
    background: #0A0A0F;
    border-right: 1px solid #1E293B;
  }
  section[data-testid="stSidebar"] * { font-family: 'IBM Plex Mono', monospace; }

  .stRadio label { font-size: 13px !important; color: #64748B !important; }
  .stRadio [data-baseweb="radio"] input:checked + div { border-color: #22C55E !important; }

  [data-testid="metric-container"] {
    background: #0A0A0F;
    border: 1px solid #1E293B;
    border-radius: 4px;
    padding: 14px;
  }

  .stButton > button, [data-testid="baseButton-primary"] {
    background: #22C55E;
    color: #050508;
    font-family: 'IBM Plex Mono', monospace;
    font-weight: 600;
    border: none;
    border-radius: 4px;
    letter-spacing: 0.05em;
  }
  .stButton > button:hover { background: #16A34A; }
  .stDownloadButton > button {
    background: #0A0A0F;
    color: #64748B;
    border: 1px solid #1E293B;
    font-family: 'IBM Plex Mono', monospace;
  }

  .streamlit-expanderHeader {
    background: #0A0A0F !important;
    border: 1px solid #1E293B !important;
    border-radius: 4px !important;
    font-size: 13px !important;
  }

  .stDataFrame { border: 1px solid #1E293B; }

  hr { border-color: #1E293B; }
  h2 { color: #F1F5F9 !important; }
  h3 { color: #E2E8F0 !important; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("""
    <div style="padding: 12px 0 20px;">
      <div style="font-size:9px;color:#22C55E;letter-spacing:0.25em;text-transform:uppercase;margin-bottom:6px;">
        IT Operations
      </div>
      <div style="font-size:16px;font-weight:600;color:#F1F5F9;">Access Review</div>
      <div style="font-size:10px;color:#475569;margin-top:2px;">& Automation Tool</div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        ["🧑 New Hire Intake", "🔍 Access Review", "🚨 Policy Violations", "🚪 Offboarding", "📋 Audit Report"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("""
    <div style="font-size:10px;color:#334155;line-height:1.8;">
      <div>50 employees</div>
      <div>12 departments</div>
      <div>15+ applications</div>
      <div>7 violation patterns</div>
    </div>
    """, unsafe_allow_html=True)

if page == "🧑 New Hire Intake":
    new_hire.render()
elif page == "🔍 Access Review":
    access_review.render()
elif page == "🚨 Policy Violations":
    violations.render()
elif page == "🚪 Offboarding":
    offboarding.render()
elif page == "📋 Audit Report":
    audit_report.render()
