from google import genai
import os
import json


# ============================================
# 1. GEMINI API SETTINGS
# ============================================

API_KEY = os.getenv("GEMINI_API_KEY")


# ============================================
# 2. CHECK API KEY
# ============================================

if not API_KEY:

    print("❌ ERROR: GEMINI_API_KEY is not set.")

    print(
        'Please set it in Git Bash using:'
    )

    print(
        'export GEMINI_API_KEY="YOUR_API_KEY"'
    )

    exit()


# ============================================
# 3. CREATE GEMINI CLIENT
# ============================================

client = genai.Client(
    api_key=API_KEY
)


# ============================================
# 4. QUESTION FILE
# ============================================

question_file = "Questions/question.txt"


# ============================================
# 5. ANSWERS FOLDER
# ============================================

answers_folder = "answers"


# ============================================
# 6. TOTAL MARKS
# ============================================

total_marks = 5


# ============================================
# 7. CHECK QUESTION FILE
# ============================================

if not os.path.exists(question_file):

    print("❌ Question file not found:")

    print(question_file)

    exit()


# ============================================
# 8. READ QUESTION
# ============================================

with open(
    question_file,
    "r",
    encoding="utf-8"
) as file:

    question = file.read()


# ============================================
# 9. CHECK EMPTY QUESTION
# ============================================

if not question.strip():

    print("❌ Question file is empty.")

    exit()


print("\n====================================")
print("QUESTION")
print("====================================")

print(question)


# ============================================
# 10. MARKING CRITERIA
# ============================================

marking_criteria = """
Evaluate the student's answer according to
the following general criteria:

1. Correctness - Is the information factually correct?
2. Concept Coverage - Does the answer cover the important concepts required by the question?
3. Relevance - Is the answer directly related to the question?
4. Completeness - Does the answer sufficiently explain what is asked?
5. Quality of explanation - Is the explanation clear and understandable?

Give marks out of the total marks provided.

Do NOT compare the answer with a reference answer.
Use your own subject knowledge to determine whether
the student's answer is correct.
"""


# ============================================
# 11. EVALUATE ONE ANSWER
# ============================================

def evaluate_answer(student_answer):

    prompt = f"""
You are an expert university exam answer evaluator.

Evaluate the student's answer using the QUESTION,
your own subject knowledge, and the MARKING CRITERIA.

IMPORTANT:
- Do NOT use or expect a reference answer.
- Do NOT compare the student answer with a reference answer.
- Judge whether the student's answer is factually correct.
- Give fair marks.
- Do not give marks just because the answer contains similar words.
- Understand the meaning of the student's answer.
- If the answer contains partially correct information,
  give partial marks.
- If important concepts are missing, mention them.
- Do not give marks above the maximum marks.

========================================
QUESTION
========================================

{question}

========================================
TOTAL MARKS
========================================

{total_marks}

========================================
MARKING CRITERIA
========================================

{marking_criteria}

========================================
STUDENT ANSWER
========================================

{student_answer}

========================================
OUTPUT
========================================

Return ONLY valid JSON.

Use exactly this format:

{{
    "correctness": 0,
    "concept_coverage": 0,
    "relevance": 0,
    "completeness": 0,
    "marks": 0,
    "percentage": 0,
    "missing_concepts": [],
    "feedback": ""
}}

Rules:

- correctness: number from 0 to 100
- concept_coverage: number from 0 to 100
- relevance: number from 0 to 100
- completeness: number from 0 to 100
- marks: number from 0 to {total_marks}
- percentage: number from 0 to 100
- missing_concepts: list of important concepts missing from the answer
- feedback: short and clear feedback for the student
- marks must never be greater than {total_marks}
- percentage should represent the marks obtained out of {total_marks}
"""


    # ========================================
    # SEND REQUEST TO GEMINI
    # ========================================

    response = client.models.generate_content(

        model="gemini-3.6-flash",

        contents=prompt,

        config={
            "response_mime_type": "application/json"
        }
    )


    # ========================================
    # GET GEMINI RESPONSE
    # ========================================

    result_text = response.text


    # ========================================
    # CONVERT JSON TO PYTHON DICTIONARY
    # ========================================

    try:

        result = json.loads(result_text)

    except json.JSONDecodeError:

        print("❌ Gemini returned invalid JSON.")

        print("Raw response:")

        print(result_text)

        return None


    return result


# ============================================
# 12. CHECK ANSWERS FOLDER
# ============================================

if not os.path.exists(answers_folder):

    print("❌ Answers folder not found:")

    print(answers_folder)

    exit()


# ============================================
# 13. PROCESS ALL STUDENT ANSWERS
# ============================================

found_answer = False


for filename in os.listdir(answers_folder):

    # Sirf .txt files process karo
    if not filename.lower().endswith(".txt"):

        continue


    found_answer = True


    # ========================================
    # FILE PATH
    # ========================================

    file_path = os.path.join(
        answers_folder,
        filename
    )


    # ========================================
    # READ STUDENT ANSWER
    # ========================================

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        student_answer = file.read()


    # ========================================
    # DISPLAY STUDENT
    # ========================================

    print("\n")
    print("====================================")
    print("Student Answer:", filename)
    print("====================================")


    # ========================================
    # CHECK EMPTY ANSWER
    # ========================================

    if not student_answer.strip():

        print("❌ Answer is empty.")

        continue


    # ========================================
    # EVALUATE USING GEMINI
    # ========================================

    print("\nEvaluating answer using Gemini...")


    try:

        result = evaluate_answer(
            student_answer
        )

    except Exception as e:

        print("\n❌ Gemini API Error:")

        print(e)

        continue


    # ========================================
    # CHECK RESULT
    # ========================================

    if result is None:

        continue


    # ========================================
    # DISPLAY RESULT
    # ========================================

    print("\n===== LLM EVALUATION =====")


    print(
        "Correctness:",
        result.get("correctness", 0),
        "%"
    )


    print(
        "Concept Coverage:",
        result.get("concept_coverage", 0),
        "%"
    )


    print(
        "Relevance:",
        result.get("relevance", 0),
        "%"
    )


    print(
        "Completeness:",
        result.get("completeness", 0),
        "%"
    )


    print(
        "Final Percentage:",
        result.get("percentage", 0),
        "%"
    )


    print(
        "Final Marks:",
        result.get("marks", 0),
        "/",
        total_marks
    )


    # ========================================
    # MISSING CONCEPTS
    # ========================================

    print("\nMissing Concepts:")


    missing_concepts = result.get(
        "missing_concepts",
        []
    )


    if missing_concepts:

        for concept in missing_concepts:

            print(
                "✗",
                concept
            )

    else:

        print(
            "✓ No major concepts missing"
        )


    # ========================================
    # FEEDBACK
    # ========================================

    print("\nFeedback:")

    print(
        result.get(
            "feedback",
            "No feedback available."
        )
    )


# ============================================
# 14. NO ANSWERS FOUND
# ============================================

if not found_answer:

    print("\n❌ No .txt student answers found.")

    print(
        "Please put student answer .txt files "
        "inside the answers folder."
    )


# ============================================
# 15. END
# ============================================

print("\n")
print("====================================")
print("ALL ANSWERS EVALUATED")
print("====================================")