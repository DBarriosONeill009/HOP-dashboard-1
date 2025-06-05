import streamlit as st
import pandas as pd

st.title("Programme Teaching Profile & Resource Estimator")

st.markdown("""
Enter details below about your programme's teaching structure.
**Please do not include 1:1s or lectures** in any group-based calculations.
""")

# General programme details
programme_name = st.text_input("Programme Name")
total_students = st.number_input("Total number of students", min_value=1)
validated_contact_hours = st.number_input("Validated contact hours per student", min_value=0.0)
total_delivery_hours = st.number_input("Total contact delivery hours across the programme (all groups, no 1:1s or lectures)", min_value=0.0)

# Staff availability inputs
st.markdown("---")
st.subheader("Staffing Profile")
fte_aef_research = st.number_input("AEF (Research) FTE", min_value=0.0)
teaching_load_aef_research = 752
fte_al = st.number_input("AL FTE", min_value=0.0)
teaching_load_al = 1365
fte_hop = st.number_input("HOP FTE", min_value=0.0)
teaching_load_hop = 300

# Space input
sqm_per_student = st.number_input("Requested square metres per student (to represent total programme space)", min_value=0.0)

# Perform calculations if valid
if total_students > 0 and validated_contact_hours > 0 and total_delivery_hours > 0:
    st.markdown("---")
    st.subheader("Analysis")

    total_validated_hours = total_students * validated_contact_hours
    weighted_repetition = total_delivery_hours / total_validated_hours
    staff_effort_multiplier = 3.31  # From prior calculation
    total_staff_effort = total_delivery_hours * staff_effort_multiplier
    staff_effort_per_validated_hour = total_staff_effort / total_validated_hours
    contact_vs_total_ratio = total_delivery_hours / total_staff_effort
    total_space = total_students * sqm_per_student

    st.metric("Total Validated Hours", f"{total_validated_hours:.1f}")
    st.metric("Total Delivery Hours", f"{total_delivery_hours:.1f}")
    st.metric("Total Staff Effort (hrs)", f"{total_staff_effort:.1f}")
    st.metric("Total Requested Space (m²)", f"{total_space:.1f}")

    st.markdown("---")
    st.subheader("Insights")

    st.write(f"Each validated programme hour requires approximately **{weighted_repetition:.2f}** hours of group delivery.")
    st.write(f"Total staff effort required per validated hour: **{staff_effort_per_validated_hour:.2f} hrs**")
    st.write(f"Ratio of delivered contact to total teaching effort (prep/admin/contact): **{contact_vs_total_ratio:.2f}**")

    total_staff_available = (
        fte_aef_research * teaching_load_aef_research +
        fte_al * teaching_load_al +
        fte_hop * teaching_load_hop
    ) * 0.9  # Subtract 10% contingency

    st.write(f"Adjusted available staff resource (after 10% contingency): **{total_staff_available:.1f} hrs**")
    surplus = total_staff_available - total_staff_effort
    if surplus >= 0:
        st.success(f"Estimated surplus of **{surplus:.1f} hrs** of staff time.")
    else:
        st.error(f"Estimated shortfall of **{abs(surplus):.1f} hrs** of staff time.")
