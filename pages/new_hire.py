import streamlit as st
from sample_data import STANDARD_PACKAGES
from claude_ops import recommend_new_hire_access
from rate_limiter import get_client_ip, check_limit, record_run


def render():
    st.markdown("## 🧑 New Hire Intake")
    st.caption("Enter new hire details to generate a role-appropriate access package recommendation.")

    client_ip = get_client_ip(dict(st.context.headers))
    allowed, remaining = check_limit(client_ip)

    if not allowed:
        st.error("Daily limit reached (5 AI calls/day). Come back tomorrow.")
    else:
        st.caption(f"AI calls remaining today: {remaining}")

    with st.form("new_hire_form"):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Full Name", placeholder="Alex Tran")
            title = st.text_input("Job Title", placeholder="Senior Designer")
            department = st.selectbox("Department", list(STANDARD_PACKAGES.keys()))
        with c2:
            email = st.text_input("Work Email", placeholder="alex@company.com")
            manager = st.text_input("Manager Name", placeholder="Elena Vasquez")
            start_date = st.date_input("Start Date")

        is_manager = st.checkbox("Is a people manager")
        notes = st.text_area(
            "Additional context (optional)",
            placeholder="Contractor? Elevated access needed? Special tools?",
            height=80,
        )
        submitted = st.form_submit_button("⚡ Generate Access Package", type="primary", disabled=not allowed)

    if submitted:
        if not name or not title or not email:
            st.warning("Please fill in Full Name, Job Title, and Work Email before generating.")
        else:
            hire_info = {
                "name": name,
                "title": title,
                "department": department,
                "email": email,
                "manager": manager,
                "start_date": str(start_date),
                "is_manager": is_manager,
                "notes": notes,
            }
            standard = STANDARD_PACKAGES.get(department, [])

            with st.spinner("Generating access recommendation..."):
                try:
                    result = recommend_new_hire_access(hire_info, standard)
                    st.session_state["new_hire_result"] = result
                    st.session_state["new_hire_info"] = hire_info
                    record_run(client_ip)
                except Exception as e:
                    st.error(f"Claude API error: {e}")

    if "new_hire_result" in st.session_state:
        result = st.session_state["new_hire_result"]
        info = st.session_state["new_hire_info"]

        st.divider()
        st.markdown(f"### Access Package: {info['name']} · {info['title']} · {info['department']}")

        if result.get("provisioning_notes"):
            st.info(f"📋 **IT Notes:** {result['provisioning_notes']}")

        if result.get("elevated_access_flags"):
            for flag in result["elevated_access_flags"]:
                st.warning(f"⚠️ {flag}")

        st.markdown("#### Recommended Apps")

        priority_order = {"immediate": 0, "within_24h": 1, "within_week": 2}
        apps = sorted(
            result.get("recommended_apps", []),
            key=lambda x: priority_order.get(x.get("provisioning_priority", "within_week"), 2),
        )

        for app in apps:
            priority = app.get("provisioning_priority", "within_week")
            sox = app.get("sox_sensitive", False)
            perm = app.get("permission_level", "user")

            priority_color = {"immediate": "🔴", "within_24h": "🟡", "within_week": "🟢"}.get(priority, "🟢")
            sox_badge = " · `SOX`" if sox else ""

            with st.expander(f"{priority_color} **{app['app']}** · `{perm}`{sox_badge}"):
                st.write(app.get("rationale", ""))
                st.caption(f"Priority: {priority.replace('_', ' ').title()}")

        # Export as provisioning ticket
        ticket_lines = [
            "NEW HIRE PROVISIONING TICKET",
            f"Name: {info['name']}",
            f"Title: {info['title']}",
            f"Department: {info['department']}",
            f"Start: {info['start_date']}",
            f"Manager: {info['manager']}",
            "",
            "ACCESS TO PROVISION:",
        ]
        for app in apps:
            ticket_lines.append(
                f"  [ ] {app['app']} — {app['permission_level']} (Priority: {app['provisioning_priority']})"
            )
        if result.get("provisioning_notes"):
            ticket_lines += ["", f"NOTES: {result['provisioning_notes']}"]

        st.download_button(
            "↓ Download Provisioning Ticket (.txt)",
            data="\n".join(ticket_lines),
            file_name=f"provisioning_{info['name'].replace(' ', '_').lower()}.txt",
            mime="text/plain",
        )
