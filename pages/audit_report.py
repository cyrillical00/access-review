import streamlit as st
import pandas as pd
from datetime import date
from sample_data import EMPLOYEES
from claude_ops import generate_audit_report
from rate_limiter import get_client_ip, check_limit, record_run


def render():
    st.markdown("## 📋 Audit Report")
    st.caption("Generate a SOX-ready access review report for compliance and auditors.")

    client_ip = get_client_ip(dict(st.context.headers))
    allowed, remaining = check_limit(client_ip)

    if not allowed:
        st.error("Daily limit reached (5 AI calls/day). Come back tomorrow.")
    else:
        st.caption(f"AI calls remaining today: {remaining}")

    if st.button("⚡ Generate Audit Report", type="primary", disabled=not allowed):
        with st.spinner("Compiling audit data and generating report..."):
            total = len(EMPLOYEES)
            terminated_with_access = [
                e for e in EMPLOYEES
                if e["employment_status"] == "terminated" and len(e["access"]) > 0
            ]

            all_access = [
                {
                    "emp": e["id"],
                    "app": a["app"],
                    "sox": a["sox_sensitive"],
                    "days": a["last_login_days_ago"],
                    "status": e["employment_status"],
                }
                for e in EMPLOYEES
                for a in e["access"]
            ]
            stale_sox = [
                a for a in all_access
                if a["sox"] and a["days"] > 90 and a["status"] == "active"
            ]
            admin_count = sum(
                1 for e in EMPLOYEES for a in e["access"]
                if a["permission"] in ["admin", "super-admin"]
            )
            sox_apps = list(set(a["app"] for a in all_access if a["sox"]))

            violations = st.session_state.get("violations", [])
            critical_count = sum(1 for v in violations if v["severity"] == "Critical")

            summary = {
                "review_date": str(date.today()),
                "total_employees": total,
                "total_access_records": len(all_access),
                "terminated_with_active_access": [
                    {"id": e["id"], "name": e["name"], "apps": [a["app"] for a in e["access"]]}
                    for e in terminated_with_access
                ],
                "stale_sox_access_count": len(stale_sox),
                "stale_sox_details": stale_sox[:5],
                "total_admin_grants": admin_count,
                "sox_sensitive_apps_in_scope": sox_apps,
                "total_violations": len(violations),
                "critical_violations": critical_count,
                "violations_summary": violations[:8] if violations else [],
            }

            report = generate_audit_report(summary)
            st.session_state["audit_report"] = report
            record_run(client_ip)

    if "audit_report" in st.session_state:
        st.divider()
        st.markdown(st.session_state["audit_report"])
        st.divider()
        st.download_button(
            "↓ Download Audit Report (.txt)",
            data=st.session_state["audit_report"],
            file_name=f"access_audit_{date.today()}.txt",
            mime="text/plain",
        )
