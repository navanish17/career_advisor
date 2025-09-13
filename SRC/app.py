import streamlit as st
import pandas as pd
import os

# Load Questions
df = pd.read_csv("C:\Project\career_advisor\Data\quiz_q.csv")
df = df.T.reset_index()
df.columns = ["Qn_No", "Question"]

st.title("🎓 Career Advisor Quiz")
st.write("Rate each question with 1 (Not Like), 2 (Moderate), 3 (Like)")

# Student ID input
student_id = st.text_input("Enter your Student ID:")

# Store responses
responses = {}

# Display questions (1 to 3 scale, same as console)
for i, row in df.iterrows():
    qn = row["Qn_No"]
    question = row["Question"]
    responses[qn] = st.radio(
        question, [1, 2, 3], index=1, key=qn
    )

if st.button("Submit"):
    if not student_id:
        st.error("⚠️ Please enter your Student ID before submitting.")
    else:
        # Build row in the same format as console version
        student_row = {"Student_ID": student_id}
        for qn, ans in responses.items():
            student_row[qn] = ans

        # Convert to DataFrame
        student_df = pd.DataFrame([student_row])

        file_path = "student_responses.csv"

        # Append to central CSV
        if os.path.exists(file_path):
            student_df.to_csv(file_path, mode="a", header=False, index=False)
        else:
            student_df.to_csv(file_path, index=False)

        st.success(f"✅ Student {student_id}, your responses have been recorded!")
