import streamlit as st
import pandas as pd
import os

# ---------- Load & normalize questions CSV ----------
file_csv = r"C:\Project\career_advisor\Data\quiz_q.csv"
df = pd.read_csv(file_csv)

# Normalize column names so we always use "Qn_No", "Question", "Stream"
if {"QuestionNo", "QuestionText", "Stream"}.issubset(df.columns):
    df = df.rename(columns={"QuestionNo": "Qn_No", "QuestionText": "Question"})
elif {"Qn_No", "Question", "Stream"}.issubset(df.columns):
    pass
elif df.shape[0] == 1:
    # if file is in 1-row form (questions as columns), transpose
    df = df.T.reset_index()
    df.columns = ["Qn_No", "Question"]
    # create Stream mapping from Q number ranges (fallback)
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
    st.error("Unexpected CSV format. Please ensure your CSV has either (QuestionNo, QuestionText, Stream) or (Q1..Q40 as one row).")
    st.stop()

# ---------- Page UI ----------
st.title("🎓 Career Advisor Quiz")
st.write("Rate each question: 1 (Not Like), 2 (Moderate), 3 (Like)")

# Ask Student ID first
student_id = st.text_input("👉 Please enter your Student ID to start:")

if not student_id:
    st.warning("⚠️ Please enter your Student ID above to start the quiz.")
    st.stop()

st.success(f"Welcome Student {student_id}! Please answer the questions below 👇")

# ---------- Progress placeholder at top ----------
progress_placeholder = st.empty()   # will be updated after we collect current responses

# ---------- Render questions ----------
responses = {}
for _, row in df.iterrows():
    qn = row["Qn_No"]           # e.g. "Q1"
    question = row["Question"]
    # IMPORTANT: use qn directly in label (not f"Q{qn}") to avoid QQ1 problem
    label = f"{qn}: {question}"
    # Use a unique key per student so multiple students don't clobber each other: studentid_Qn
    key = f"{student_id}_{qn}"
    resp = st.radio(label, [1, 2, 3], index=None, key=key)
    responses[qn] = resp

# ---------- Update the progress bar (placed at the top) ----------
answered_count = sum(1 for v in responses.values() if v is not None)
progress = answered_count / len(df) if len(df) > 0 else 0.0
progress_placeholder.progress(progress)
progress_placeholder.markdown(f"**Answered:** {answered_count}/{len(df)}")

# ---------- Submit handling ----------
if st.button("Submit"):
    if None in responses.values():
        st.error("⚠️ Please answer all questions before submitting.")
    else:
        # Build row to save
        student_row = {"Student_ID": student_id}
        for qn, ans in responses.items():
            student_row[qn] = ans

        student_df = pd.DataFrame([student_row])
        out_file = "C:\Project\career_advisor\Data\student_responses.csv"

        # Append or create
        if os.path.exists(out_file):
            student_df.to_csv(out_file, mode="a", header=False, index=False)
        else:
            student_df.to_csv(out_file, index=False)

        # Recommendation logic
        stream_scores = {}
        for qn, ans in responses.items():
            stream = df.loc[df["Qn_No"] == qn, "Stream"].values[0]
            stream_scores[stream] = stream_scores.get(stream, 0) + int(ans)

        # Sort & display
        sorted_streams = sorted(stream_scores.items(), key=lambda x: x[1], reverse=True)
        st.success(f"✅ Student {student_id}, your responses have been recorded!")

        st.subheader("📊 Your Recommended Streams")
        for stream, score in sorted_streams:
            st.write(f"**{stream}** → Score: {score}")

        top_score = sorted_streams[0][1]
        top_streams = [s for s, sc in sorted_streams if sc == top_score]
        st.markdown(f"🎯 **Best Fit Stream(s): {', '.join(top_streams)}**")

        # Optional: quick bar chart visualization
        try:
            st.bar_chart(pd.Series({k: v for k, v in stream_scores.items()}))
        except Exception:
            pass
