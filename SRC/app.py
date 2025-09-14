import streamlit as st
import pandas as pd
import os

# ---------- Load & normalize questions CSV ----------
file_csv = r"C:\Project\career_advisor\Data\quiz_q.csv"
df = pd.read_csv(file_csv)

# Normalize column names
if {"QuestionNo", "QuestionText", "Stream"}.issubset(df.columns):
    df = df.rename(columns={"QuestionNo": "Qn_No", "QuestionText": "Question"})
elif {"Qn_No", "Question", "Stream"}.issubset(df.columns):
    pass
elif df.shape[0] == 1:
    df = df.T.reset_index()
    df.columns = ["Qn_No", "Question"]
    
    def q_to_stream(q):
        n = int(str(q).lstrip("Q").lstrip("q"))
        if 1 <= n <= 10:
            return "Science"
        if 11 <= n <= 20:
            return "Commerce"
        if 21 <= n <= 30:
            return "Arts"
        return "Vocational"
    
    df["Stream"] = df["Qn_No"].apply(q_to_stream)
else:
    st.error("Unexpected CSV format.")
    st.stop()

# ---------- Page UI ----------
st.title("🎓 Career Advisor Quiz")
st.write("Rate each question: 1 (Not Like), 2 (Moderate), 3 (Like)")

# ---------- Student ID ----------
student_id = st.text_input("👉 Enter your Student ID:")
if not student_id:
    st.warning("⚠️ Please enter Student ID to start.")
    st.stop()

st.success(f"Welcome Student {student_id}! Answer the questions below 👇")

# ---------- Quiz Questions ----------
responses = {}

for _, row in df.iterrows():
    qn = row["Qn_No"]
    question = row["Question"]
    key = f"{student_id}_{qn}"
    
    # Use radio buttons - all options visible, no preselection
    resp = st.radio(
        f"{qn}: {question}",
        options=[1, 2, 3],
        key=key,
        index=None  # No preselection
    )
    
    if resp is not None:
        responses[qn] = resp

# ---------- Check if all questions answered ----------
all_answered = len(responses) == len(df)

# ---------- Calculate scores and handle ties OUTSIDE submit button ----------
final_stream = None
if all_answered:
    # Calculate stream scores
    stream_scores = {}
    for qn, ans in responses.items():
        stream = df.loc[df["Qn_No"] == qn, "Stream"].values[0]
        stream_scores[stream] = stream_scores.get(stream, 0) + int(ans)

    # Determine highest score(s)
    max_score = max(stream_scores.values())
    top_streams = [s for s, score in stream_scores.items() if score == max_score]

    # Handle tie OUTSIDE submit button
    if len(top_streams) > 1:
        st.warning(f"🎯 Tie detected! Top streams: {', '.join(top_streams)}")
        final_stream = st.radio(
            "Please select your preferred stream:",
            options=top_streams,
            key=f"{student_id}_tie_break",
            index=None
        )
    else:
        final_stream = top_streams[0]

# ---------- Submit ----------
if all_answered and final_stream is not None:
    if st.button("Submit"):
        # Create responses string in order of question numbers
        sorted_qns = sorted(responses.keys(), key=lambda x: int(str(x).lstrip("Q").lstrip("q")))
        responses_string = ",".join([str(responses[qn]) for qn in sorted_qns])
        
        # Create single row for this student
        student_data = {
            "Student_ID": student_id,
            "Responses": responses_string,
            "Stream": final_stream
        }
        
        student_df = pd.DataFrame([student_data])
        
        out_file = r"C:\Project\career_advisor\Data\student_responses.csv"
        if os.path.exists(out_file):
            student_df.to_csv(out_file, mode="a", header=False, index=False)
        else:
            student_df.to_csv(out_file, index=False)

        st.success(f"✅ Responses recorded with final stream: {final_stream}")
        st.subheader("📊 Stream Scores")
        for stream, score in stream_scores.items():
            st.write(f"**{stream}** → Score: {score}")
            
        st.write(f"**Your Responses:** {responses_string}")

elif not all_answered:
    st.error("⚠️ Please answer all questions before submitting.")
elif final_stream is None:
    st.error("⚠️ Please select your preferred stream to continue.")