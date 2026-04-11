import streamlit as st
from sample_data import EMPLOYEES
from claude_ops import detect_violations
from rate_limiter import get_client_ip, check_limit, record_run

SEVERITY_COLOR = {
    "Critical": "#EF4444",
    "High": "#F97316",
    "Medium": "#F59E0B",
}

SEVERITY_ICON = {
    "Critical": "🔴",
    "High": "🟠",
    "Medium": "🟡",
}


def render():
    st.markdown("## 🚨 Policy Violations")
    st.caption("AI-detected access policy violations across all 50 employees.")

    client_ip = get_client_ip(dict(st.context.headers))
    allowed, remaining = check_limit(client_ip)

    if not allowed:
        st.error("Daily limit reached (5 AI calls/day). Come back tomorrow.")
    else:
        st.caption(f"AI calls remaining today: {remaining}")

    if st.button("⚡ Run Violation Scan", type="primary", disabled=not allowed):
        with st.spinner("Scanning for policy violations..."):
            violations = detect_violations(EMPLOYEES)
            st.session_state["violations"] = violations
            record_run(client_ip)

    if "violations" in st.session_state:
        violations = st.session_state["violations"]

        critical = [v for v in violations if v["severity"] == "Critical"]
        high = [v for v in violations if v["severity"] == "High"]
        medium = [v for v in violations if v["severity"] == "Medium"]

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Total Violations", len(violations))
        with c2:
            st.metric("Critical", len(critical))
        with c3:
            st.metric("High", len(high))
        with c4:
            st.metric("Medium", len(medium))

        st.divider()

        order = {"Critical": 0, "High": 1, "Medium": 2}
        for v in sorted(violations, key=lambda x: order.get(x["severity"], 3)):
            icon = SEVERITY_ICON.get(v["severity"], "⚪")

            with st.expander(
                f"{icon} **{v['employee_name']}** ({v['employee_id']}) — {v['violation_type'].replace('_', ' ').title()}"
            ):
                col_a, col_b = st.columns([1, 2])
                with col_a:
                    st.markdown(f"**Severity:** `{v['severity']}`")
                    st.markdown(f"**Type:** `{v['violation_type']}`")
                    st.markdown(f"**Apps:** {', '.join(v['apps_affected'])}")
                with col_b:
                    st.markdown(f"**Description:** {v['description']}")
                    st.info(f"**Recommended Action:** {v['recommended_action']}")

        export_lines = ["POLICY VIOLATION REPORT\n"]
        for v in violations:
            export_lines.append(
                f"[{v['severity']}] {v['employee_name']} ({v['employee_id']})\n"
                f"Type: {v['violation_type']}\nApps: {', '.join(v['apps_affected'])}\n"
                f"Description: {v['description']}\nAction: {v['recommended_action']}\n"
            )
        st.download_button(
            "↓ Download Violation Report (.txt)",
            "\n".join(export_lines),
            "violation_report.txt",
            "text/plain",
        )
