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

# Space input
sqm_per_student = st.number_input("Requested square metres per student (to represent total programme space)", min_value=0.0)

st.markdown("---")
st.subheader("Programme-Specific Learning Groups")

num_group_types = st.number_input("How many types of learning groups does your programme use?", min_value=1, max_value=5, step=1)

learning_groups = []

for i in range(num_group_types):
    st.markdown(f"### Learning Group {i+1}")
    group_name = st.text_input(f"Name of Learning Group {i+1} (e.g. Field Collective, Tutor Group)", key=f"group_name_{i}")
    group_size = st.number_input(f"Typical group size for {group_name}", min_value=1, key=f"group_size_{i}")
    group_hours = st.number_input(f"Total delivery hours conducted in {group_name}s (exclude 1:1s and lectures)", min_value=0.0, key=f"group_hours_{i}")
    learning_groups.append({
        "Group Name": group_name,
        "Group Size": group_size,
        "Group Hours": group_hours
    })

# Perform calculations if valid
if total_students > 0 and total_delivery_hours > 0 and all(g["Group Size"] > 0 for g in learning_groups):
    st.markdown("---")
    st.subheader("Analysis")

    group_df = pd.DataFrame(learning_groups)
    group_df["Number of Groups"] = (total_students / group_df["Group Size"]).apply(lambda x: int(x) if x.is_integer() else int(x)+1)
    group_df["Repetition Multiplier"] = total_students / group_df["Group Size"]

    staff_effort_multiplier = 3.31  # From prior calculation
    group_df["Estimated Staff Effort (hrs)"] = group_df["Group Hours"] * staff_effort_multiplier

    st.dataframe(group_df)

    total_staff_effort = group_df["Estimated Staff Effort (hrs)"].sum()
    st.metric("Total Estimated Staff Effort (hrs)", f"{total_staff_effort:.1f}")

    total_space = total_students * sqm_per_student
    st.metric("Total Requested Space (m²)", f"{total_space:.1f}")

    # Generate insights
    st.markdown("---")
    st.subheader("Insights")

    if total_students > 0 and validated_contact_hours > 0:
        total_validated_hours = total_students * validated_contact_hours
        delivery_multiplier = total_delivery_hours / total_validated_hours
        st.write(f"Each validated programme hour requires approximately **{delivery_multiplier:.2f}** hours of actual group delivery.")

    for idx, row in group_df.iterrows():
        st.write(f"- The group type **{row['Group Name']}** requires about **{row['Repetition Multiplier']:.2f}x** repetition.")

    st.write(f"- Programme staff need to deliver a total of **{total_staff_effort:.1f} hours**, based on a multiplier of **{staff_effort_multiplier}x** to account for preparation, admin, and delivery.")
    st.write(f"- Your current teaching space request equates to **{sqm_per_student:.2f}m² per student**, or a total of **{total_space:.1f}m²**.")

