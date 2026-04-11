import streamlit as st
import pandas as pd
from datetime import date
from sample_data import EMPLOYEES


def render():
    st.markdown("## 🚪 Offboarding")
    st.caption("Select an employee to generate an access revocation checklist.")

    emp_options = [
        f"{e['id']} — {e['name']} ({e['department']}) [{e['employment_status']}]"
        for e in sorted(EMPLOYEES, key=lambda x: x["employment_status"] == "active")
    ]
    sel = st.selectbox("Select employee to offboard", emp_options)

    if sel:
        emp_id = sel.split(" — ")[0]
        emp = next(e for e in EMPLOYEES if e["id"] == emp_id)

        if emp["employment_status"] == "terminated":
            st.error(
                f"⚠️ **{emp['name']} is already marked terminated** (since {emp['termination_date']}) "
                f"— but still has {len(emp['access'])} active access records. This is a violation."
            )
        elif emp["employment_status"] == "on_leave":
            st.warning(
                f"ℹ️ {emp['name']} is currently on leave. Proceeding will generate a revocation "
                f"checklist for sensitive access."
            )

        st.markdown(f"### Offboarding: {emp['name']} · {emp['title']} · {emp['department']}")

        last_day = st.date_input("Last day of access", value=date.today())

        st.markdown("#### Access to Revoke")
        access_df = pd.DataFrame(emp["access"])

        access_df["sox_sensitive"] = access_df["sox_sensitive"].astype(bool)
        access_df = access_df.sort_values(["sox_sensitive", "last_login_days_ago"], ascending=[False, True])

        access_df["revoke_by"] = access_df["sox_sensitive"].apply(
            lambda sox: "Immediate (SOX)" if sox else "End of last day"
        )
        access_df["status"] = "⬜ Pending"

        display = access_df[["app", "permission", "approved_by", "sox_sensitive", "revoke_by", "status"]].copy()
        display.columns = ["App", "Permission", "Originally Approved By", "SOX", "Revoke By", "Status"]
        display["SOX"] = display["SOX"].apply(lambda x: "✓" if x else "")
        st.dataframe(display, use_container_width=True, hide_index=True)

        sox_count = int(access_df["sox_sensitive"].sum())
        total = len(access_df)
        st.markdown(
            f"**{total} total access records** · **{sox_count} SOX-sensitive** (immediate revocation required)"
        )

        ticket = f"""OFFBOARDING ACCESS REVOCATION TICKET
Employee: {emp['name']} ({emp['id']})
Title: {emp['title']}
Department: {emp['department']}
Manager: {emp['manager']}
Last Day: {last_day}
Generated: {date.today()}

ACCESS REVOCATION CHECKLIST:

IMMEDIATE (SOX-sensitive — revoke before end of last day):
"""
        for _, row in access_df[access_df["sox_sensitive"]].iterrows():
            ticket += f"  [ ] {row['app']} ({row['permission']}) — originally approved by {row['approved_by']}\n"

        ticket += "\nEND OF LAST DAY:\n"
        for _, row in access_df[~access_df["sox_sensitive"]].iterrows():
            ticket += f"  [ ] {row['app']} ({row['permission']})\n"

        ticket += f"\nOkta account suspension: [ ] Scheduled for {last_day} 5:00 PM\n"
        ticket += "MDM device wipe/unenroll: [ ] Pending device return\n"
        ticket += "Completed by: ___________________  Date: ___________\n"

        st.download_button(
            "↓ Download Revocation Ticket (.txt)",
            data=ticket,
            file_name=f"offboarding_{emp['name'].replace(' ', '_').lower()}.txt",
            mime="text/plain",
        )
