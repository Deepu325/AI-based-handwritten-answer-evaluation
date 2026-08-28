from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import os


# ============================================
# 1. LOAD NLP MODEL
# ============================================

print("Loading NLP model...")

model = SentenceTransformer("all-MiniLM-L6-v2")

print("Model loaded successfully!")


# ============================================
# 2. READ REFERENCE ANSWER
# ============================================

with open(
    "reference/answer.txt",
    "r",
    encoding="utf-8"
) as file:

    reference_answer = file.read()


# ============================================
# 3. IMPORTANT CONCEPTS
# ============================================

important_concepts = [
    "artificial intelligence",
    "learn patterns",
    "data",
    "explicitly programmed"
]


# ============================================
# 4. CREATE REFERENCE EMBEDDING
# ============================================

reference_embedding = model.encode(
    [reference_answer]
)


# ============================================
# 5. ANSWERS FOLDER
# ============================================

answers_folder = "answers"


# ============================================
# 6. CHECK ALL STUDENT ANSWERS
# ============================================

for filename in os.listdir(answers_folder):

    # Sirf .txt files
    if not filename.lower().endswith(".txt"):
        continue


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


    print("\n")
    print("====================================")
    print("Student Answer:", filename)
    print("====================================")


    # ========================================
    # STUDENT EMBEDDING
    # ========================================

    student_embedding = model.encode(
        [student_answer]
    )


    # ========================================
    # SEMANTIC SIMILARITY
    # ========================================

    similarity = cosine_similarity(
        reference_embedding,
        student_embedding
    )[0][0]


    similarity_score = similarity * 100


    # ========================================
    # CONCEPT COVERAGE
    # ========================================

    student_answer_lower = (
        student_answer.lower()
    )

    concepts_found = 0

    print("\n===== CONCEPT CHECK =====")


    for concept in important_concepts:

        if concept.lower() in student_answer_lower:

            concepts_found += 1

            print("✓ Found:", concept)

        else:

            print("✗ Missing:", concept)


    concept_score = (
        concepts_found /
        len(important_concepts)
    ) * 100


    # ========================================
    # FINAL SCORE
    # ========================================

    final_percentage = (
        similarity_score * 0.60
        +
        concept_score * 0.40
    )


    # ========================================
    # MARKS
    # ========================================

    total_marks = 5

    final_marks = (
        final_percentage / 100
    ) * total_marks


    # ========================================
    # FEEDBACK
    # ========================================

    if final_percentage >= 80:

        feedback = (
            "Overall performance is very good."
        )

    elif final_percentage >= 60:

        feedback = (
            "Answer is satisfactory "
            "but can be improved."
        )

    else:

        feedback = (
            "Answer needs significant improvement."
        )


    # ========================================
    # DISPLAY RESULT
    # ========================================

    print("\n===== RESULT =====")

    print(
        "Semantic Similarity:",
        round(similarity_score, 2),
        "%"
    )

    print(
        "Concept Coverage:",
        round(concept_score, 2),
        "%"
    )

    print(
        "Final Score:",
        round(final_percentage, 2),
        "%"
    )

    print(
        "Final Marks:",
        round(final_marks, 2),
        "/",
        total_marks
    )

    print(
        "Feedback:",
        feedback
    )


print("\n")
print("====================================")
print("ALL ANSWERS EVALUATED")
print("====================================")

