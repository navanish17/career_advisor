import pandas as pd
import os

# Load Questions
df = pd.read_csv("C:/Project/career_advisor/quiz_q.csv")
df = df.T.reset_index()
df.columns = ["Qn_No", "Question"]

# Ask for Student ID
student_id = input("Enter your Student ID: ")

# Collect responses
responses = {}
print("\nRate each question (1 = Not Like, 2 = Moderate, 3 = Like)\n")

for i, row in df.iterrows():
    qn = row["Qn_No"]
    question = row["Question"]

    while True:
        try:
            ans = int(input(f"{question} (1/2/3): "))
            if ans in [1, 2, 3]:
                responses[qn] = ans
                break
            else:
                print("⚠️ Please enter only 1, 2, or 3")
        except ValueError:
            print("⚠️ Please enter a number")

# Build student row
student_row = {"Student_ID": student_id}
for qn, ans in responses.items():
    student_row[qn] = ans

# Convert to DataFrame
student_df = pd.DataFrame([student_row])

file_path = "App/student_responses.csv"

# Append to central CSV
if os.path.exists(file_path):
    student_df.to_csv(file_path, mode="a", header=False, index=False)
else:
    student_df.to_csv(file_path, index=False)

print(f"\n✅ Student {student_id}, your responses have been saved!\n")
