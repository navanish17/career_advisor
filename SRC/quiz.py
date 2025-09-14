import streamlit as st
import pandas as pd
import os

# Load Questions with Stream mapping
df = pd.read_csv(r"C:\Project\career_advisor\Data\quiz_q.csv")

st.title("🎓 Career Advisor Quiz")
st.write("Rate each question with: 1 (Not Like), 2 (Moderate), 3 (Like)")

# Student ID input
student_id = st.text_input("Enter your Student ID:")

# Store responses
responses = {}

# Display questions
for i, row in df.iterrows():
    qn = row["QuestionNo"]
    question = row["QuestionText"]
    responses[qn] = st.radio(
        f"Q{qn}: {question}", 
        [1, 2, 3], 
        index=1, 
        key=qn
    )

if st.button("Submit"):
    if not student_id:
        st.error("⚠️ Please enter your Student ID before submitting.")
    else:
        # Build row with student ID and responses
        student_row = {"Student_ID": student_id}
        for qn, ans in responses.items():
            student_row[qn] = ans

        # Convert to DataFrame
        student_df = pd.DataFrame([student_row])

        file_path = "student_responses.csv"

        # Append to CSV
        if os.path.exists(file_path):
            student_df.to_csv(file_path, mode="a", header=False, index=False)
        else:
            student_df.to_csv(file_path, index=False)

        # -----------------------------
        # ✅ Recommendation Logic
        # -----------------------------
        stream_scores = {}

        for qn, ans in responses.items():
            stream = df.loc[df["QuestionNo"] == qn, "Stream"].values[0]  # get stream for that question
            stream_scores[stream] = stream_scores.get(stream, 0) + ans

        # Sort streams by score (highest first)
        sorted_streams = sorted(stream_scores.items(), key=lambda x: x[1], reverse=True)

        st.success(f"✅ Student {student_id}, your responses have been recorded!")

        # Display recommendation
        st.subheader("📊 Your Recommended Streams")
        for stream, score in sorted_streams:
            st.write(f"**{stream}** → Score: {score}")
        
        # Highlight top recommendation(s)
        top_score = sorted_streams[0][1]
        top_streams = [s for s, sc in sorted_streams if sc == top_score]

        st.markdown(f"🎯 **Best Fit Stream(s): {', '.join(top_streams)}**")
