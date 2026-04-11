import streamlit as st
import pandas as pd
from sample_data import EMPLOYEES


def render():
    st.markdown("## 🔍 Access Review")
    st.caption("Full access inventory across all employees. Filter by department, app, or status.")

    # Flatten data
    rows = []
    for emp in EMPLOYEES:
        for app in emp["access"]:
            rows.append({
                "ID": emp["id"],
                "Name": emp["name"],
                "Title": emp["title"],
                "Department": emp["department"],
                "Status": emp["employment_status"],
                "App": app["app"],
                "Permission": app["permission"],
                "Last Login (days ago)": app["last_login_days_ago"],
                "Approved By": app["approved_by"],
                "SOX Sensitive": "✓" if app["sox_sensitive"] else "",
            })
    df = pd.DataFrame(rows)

    # Filters
    fc1, fc2, fc3, fc4 = st.columns(4)
    with fc1:
        depts = st.multiselect(
            "Department",
            sorted(df["Department"].unique()),
            default=sorted(df["Department"].unique()),
        )
    with fc2:
        statuses = st.multiselect(
            "Status",
            df["Status"].unique(),
            default=list(df["Status"].unique()),
        )
    with fc3:
        apps_filter = st.multiselect("App", sorted(df["App"].unique()))
    with fc4:
        sox_only = st.checkbox("SOX-sensitive only")

    filtered = df[df["Department"].isin(depts) & df["Status"].isin(statuses)]
    if apps_filter:
        filtered = filtered[filtered["App"].isin(apps_filter)]
    if sox_only:
        filtered = filtered[filtered["SOX Sensitive"] == "✓"]

    def highlight_row(row):
        if row["Status"] == "terminated":
            return ["background-color: #7F1D1D22"] * len(row)
        if row["Last Login (days ago)"] > 90 and row["SOX Sensitive"] == "✓":
            return ["background-color: #92400E22"] * len(row)
        if row["Permission"] in ["admin", "super-admin"] and row["Status"] == "active":
            return ["background-color: #1E3A5F22"] * len(row)
        return [""] * len(row)

    st.markdown(f"**{len(filtered)} access records** · {filtered['Name'].nunique()} employees")
    st.dataframe(
        filtered.style.apply(highlight_row, axis=1),
        use_container_width=True,
        hide_index=True,
    )

    st.caption("🔴 Red = terminated with active access · 🟡 Amber = stale SOX access · 🔵 Blue = admin/super-admin")

    # Per-employee drill-down
    st.divider()
    st.markdown("#### Employee Detail")
    sel_emp = st.selectbox(
        "Select employee",
        [f"{e['id']} — {e['name']}" for e in EMPLOYEES],
    )
    if sel_emp:
        emp_id = sel_emp.split(" — ")[0]
        emp = next(e for e in EMPLOYEES if e["id"] == emp_id)

        st.markdown(
            f"**{emp['name']}** · {emp['title']} · {emp['department']} · Status: `{emp['employment_status']}`"
        )
        emp_df = pd.DataFrame(emp["access"])
        emp_df.columns = ["App", "Permission", "Granted", "Approved By", "Last Login (days ago)", "SOX"]
        emp_df["SOX"] = emp_df["SOX"].apply(lambda x: "✓" if x else "")
        st.dataframe(emp_df, use_container_width=True, hide_index=True)
