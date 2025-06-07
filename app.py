import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Programme Resource Estimator", layout="wide")

st.title("🎓 Programme Resource Estimator")
st.markdown("Estimate delivery repetition, staff effort, and student-to-FTE ratio using programme and staffing details.")

# --- Programme Information ---
st.header("1. Programme Details")
name = st.text_input("Your Name")
role = st.text_input("Your Role or Title")
programme_name = st.text_input("Programme Name")
num_students = st.number_input("Total number of students", min_value=1, step=1)
validated_contact_hours = st.number_input("Validated IN-PROGRAMME contact hours per student", min_value=0.0, step=0.5)
# --- Direct Input for Total Delivery Hours ---
st.header("2. Total Delivery Hours")
total_delivery_hours = st.number_input("Total teaching delivery hours (across all units, all staff)", min_value=0.0, step=0.5)

# --- Calculation ---
if validated_contact_hours > 0 and total_delivery_hours > 0:
    repetition_factor = round(total_delivery_hours / validated_contact_hours, 2)
    effort_multiplier = 2.788
    base_staff_effort = total_delivery_hours * effort_multiplier
    contingency_buffer = 0.10
    estimated_staff_effort = round(base_staff_effort * (1 + contingency_buffer), 1)

    st.header("3. Results")
    st.markdown(f"**Effective Repetition Factor:** `{repetition_factor}`")
    st.caption(f"Calculated as: {total_delivery_hours} ÷ {validated_contact_hours} = {repetition_factor}")

    st.markdown(f"**Base Staff Effort (before contingency):** `{round(base_staff_effort, 1):,}` hours")
    st.markdown(f"**Total Estimated Staff Effort (with 10% contingency):** `{estimated_staff_effort:,}` hours")
else:
    st.info("Enter all values to view the repetition factor and staff effort.")
# --- Staffing Profile ---
st.header("4. Staffing Profile")

aef_research_fte = st.number_input("AEF (Research) FTE (excluding HOP)", min_value=0.0, step=0.1)
aef_teaching_fte = st.number_input("AEF (Teaching) FTE", min_value=0.0, step=0.1)
al_fte = st.number_input("AL FTE (Associate Lecturers)", min_value=0.0, step=0.1)
hop_fte = st.number_input("Head of Programme (HOP) FTE", min_value=0.0, step=0.1)

fte_total = aef_research_fte + aef_teaching_fte + al_fte + hop_fte

# --- Remission & Buyouts ---
st.header("5. Remission & Buyouts (in Hours)")

research_buyout_hours = st.number_input("Research Buyout (hours)", min_value=0.0)
leadership_remission_hours = st.number_input("Leadership Remission (hours)", min_value=0.0)
other_remission_hours = st.number_input("Other Remission (hours)", min_value=0.0)
other_remission_desc = st.text_input("Describe 'Other Remission' (optional)")

# --- Teaching hours per FTE ---
hop_hours = 300
al_hours = 1362
aef_teaching_hours = 1053
aef_research_hours = 752

# --- Calculate available hours after remission ---
adj_aef_research_hours = max(0, aef_research_fte * aef_research_hours - research_buyout_hours)
adj_aef_teaching_hours = max(0, aef_teaching_fte * aef_teaching_hours - leadership_remission_hours - other_remission_hours)
adj_al_hours = al_fte * al_hours
adj_hop_hours = hop_fte * hop_hours

total_net_hours = adj_aef_research_hours + adj_aef_teaching_hours + adj_al_hours + adj_hop_hours
# --- External teaching ---
st.header("6. Staff Contributions to Other Teaching")

across_rca_hours = st.number_input("AcrossRCA (hours)", min_value=0.0)
school_electives_hours = st.number_input("School-wide electives (hours)", min_value=0.0)
cross_school_hours = st.number_input("Cross-school electives (hours)", min_value=0.0)
pgr_supervision_hours = st.number_input("PGR Supervision (hours)", min_value=0.0)
other_programme_hours = st.number_input("Other programme(s) teaching (hours)", min_value=0.0)
other_programme_desc = st.text_input("Name other programme(s) (optional)")

total_other_teaching_hours = (
    across_rca_hours +
    school_electives_hours +
    cross_school_hours +
    pgr_supervision_hours +
    other_programme_hours
)

adjusted_net_hours = total_net_hours - total_other_teaching_hours

# --- Additional Unreplaced Time Deductions ---
st.header("7. Additional Unreplaced Staff Time")

illness_hours = st.number_input("Staff illness or absence (unreplaced, in hours)", min_value=0.0)
illness_notes = st.text_area("Notes on illness/absence (optional)", height=70)

rke_exec_hours = st.number_input("RKE or Executive Education contribution (unreplaced, in hours)", min_value=0.0)
rke_exec_notes = st.text_area("Notes on RKE/Exec Ed (optional)", height=70)

other_unreplaced_hours = st.number_input("Other unreplaced staff time (in hours)", min_value=0.0)
other_unreplaced_notes = st.text_area("Notes on other unreplaced time (optional)", height=70)

total_unreplaced_hours = illness_hours + rke_exec_hours + other_unreplaced_hours
final_available_hours = adjusted_net_hours - total_unreplaced_hours

st.subheader("Final Adjusted Available Hours")
st.markdown(f"**Total Additional Deductions:** `{total_unreplaced_hours:,}` hours")
st.markdown(f"**Final Adjusted Teaching Hours Available:** `{final_available_hours:,}` hours")
# --- Student-to-FTE Ratio ---
st.header("8. Student-to-FTE Ratio")

nominal_fte_hours = 800  # Define nominal teaching hours per 1.0 FTE
nominal_ratio = round(num_students / (total_net_hours / nominal_fte_hours), 2) if total_net_hours > 0 else 0
adjusted_ratio = round(num_students / (final_available_hours / nominal_fte_hours), 2) if final_available_hours > 0 else 0

ratio_type = st.radio("Select ratio type to display", ["Nominal", "Adjusted"])

if ratio_type == "Nominal":
    st.markdown(f"**Nominal Student-to-FTE Ratio:** `{nominal_ratio}` (based on net hours)")
else:
    st.markdown(f"**Adjusted Student-to-FTE Ratio:** `{adjusted_ratio}` (based on final available hours after all deductions)")

# --- CSV Download Section ---
st.header("📥 Download Summary")

summary = {
    "Name": name,
    "Role": role,
    "Programme": programme_name,
    "Total Students": num_students,
    "Validated Hours per Student": validated_contact_hours,
    "Total Delivery Hours": total_delivery_hours,
    "Repetition Factor": repetition_factor if validated_contact_hours > 0 else "",
    "Staff Effort (with contingency)": estimated_staff_effort if validated_contact_hours > 0 else "",
    "Adjusted Available Hours (before unreplaced deductions)": adjusted_net_hours,
    "Unreplaced Illness/Absence Hours": illness_hours,
    "Unreplaced RKE/ExecEd Hours": rke_exec_hours,
    "Unreplaced Other Hours": other_unreplaced_hours,
    "Total Additional Deductions": total_unreplaced_hours,
    "Final Adjusted Teaching Hours": final_available_hours,
    "Nominal Student-to-FTE Ratio": nominal_ratio,
    "Adjusted Student-to-FTE Ratio": adjusted_ratio,
    "Illness Notes": illness_notes,
    "RKE/Exec Notes": rke_exec_notes,
    "Other Notes": other_unreplaced_notes
}

summary_df = pd.DataFrame([summary])
st.download_button(
    label="📥 Download CSV Summary",
    data=summary_df.to_csv(index=False),
    file_name="programme_summary.csv",
    mime="text/csv"
)
# --- Admin Access Section ---
st.header("🔒 Admin Dashboard Access")

admin_pass = st.text_input("Enter admin password", type="password", key="admin_pass_input")

if admin_pass == "changeme":  # Replace with your actual admin password securely
    st.success("Admin access granted.")

    # --- Dashboard View for Admin ---
    st.header("📊 Programme Summary Dashboard")

    csv_path = "programme_data_submissions.csv"

    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)

        # Filter option
        programmes = df["Programme"].unique()
        selected_programmes = st.multiselect("Filter by Programme", programmes, default=programmes)

        filtered_df = df[df["Programme"].isin(selected_programmes)]

        st.subheader("📋 Filtered Submissions")
        st.dataframe(filtered_df, use_container_width=True)

        # Summary Metrics
        st.subheader("📈 Key Metrics")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Average Adjusted Ratio", round(filtered_df["Adjusted Student-to-FTE Ratio"].mean(), 2))
        with col2:
            st.metric("Total Staff Effort", int(filtered_df["Staff Effort (with contingency)"].sum()))
        with col3:
            st.metric("Total Students", int(filtered_df["Total Students"].sum()))

        # Ratio Bar Chart
        st.subheader("📉 Adjusted Student-to-FTE Ratio by Programme")
        chart_data = filtered_df.groupby("Programme")["Adjusted Student-to-FTE Ratio"].mean().sort_values()
        st.bar_chart(chart_data)
    else:
        st.info("No submission data found. Submit at least one entry to generate a dashboard.")

elif admin_pass:
    st.error("Incorrect password.")
