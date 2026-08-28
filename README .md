# Handwritten Answer Sheet Evaluation System

## 1. Project Overview

This project is designed to automatically evaluate handwritten student
answer sheets.

The system first converts handwritten images into text using OCR. The
extracted text is then processed and evaluated. Initially, the project
used a teacher-provided reference answer with NLP-based semantic
similarity. In the final approach, the system uses an LLM to evaluate
the student's answer directly based on the question, without requiring a
reference answer.

### Overall Workflow

``` text
Handwritten Question Image
          ↓
        OCR
          ↓
   question.txt
          ↓
       Question
          +
Handwritten Student Answer Images
          ↓
        OCR
          ↓
 Student Answer .txt Files
          ↓
       LLM Evaluation
          ↓
 Marks + Percentage + Feedback
```

------------------------------------------------------------------------

## 2. Project Folder Structure

``` text
handwritten-ocr/
│
├── answers/
│   ├── abc.jpeg
│   ├── abc.txt
│   ├── note.jpg
│   ├── note.txt
│   ├── zak.jpeg
│   └── zak.txt
│
├── Questions/
│   ├── question.jpeg
│   └── question.txt
│
├── reference/
│   └── answer.txt
│
├── ocr.py
├── ocrmul.py
├── ocrparticular.py
├── ocr_to_text.py
├── ocr_including_question.py
├── nlp.py
├── evaluate.py
└── README.md
```

------------------------------------------------------------------------

# 3. Step-by-Step Development

## Step 1 --- Initial OCR Implementation

The project was initially started with `ocr.py`.

The purpose of `ocr.py` was to test OCR functionality and convert a
handwritten answer-sheet image into text.

### Basic Flow

``` text
Handwritten Image
       ↓
    OCR API
       ↓
  Extracted Text
```

The OCR implementation used the OCR.space API.

------------------------------------------------------------------------

## Step 2 --- Multiple Answer Sheet OCR

After testing the basic OCR functionality, `ocrmul.py` was developed.

The purpose of `ocrmul.py` is to process multiple handwritten
answer-sheet images instead of processing only one image at a time.

### Flow

``` text
answers/
   ├── student1.jpg
   ├── student2.jpg
   ├── student3.jpg
   └── ...
          ↓
       ocrmul.py
          ↓
   Multiple OCR Results
```

This made it possible to process several student answer sheets
automatically.

------------------------------------------------------------------------

## Step 3 --- Particular Answer Sheet OCR

`ocrparticular.py` was developed when it was necessary to inspect a
particular student's answer.

Instead of displaying the OCR result of every answer sheet, this script
can be used to focus on a selected answer sheet and display its
extracted text in the terminal.

### Flow

``` text
Selected Student Answer
          ↓
     OCR Processing
          ↓
    Text in Terminal
```

This was useful for checking whether OCR had correctly recognized a
particular student's handwriting.

------------------------------------------------------------------------

# 4. Creating the Answers Folder

An `answers` folder was created to store student answer-sheet images.

For example:

``` text
answers/
├── abc.jpeg
├── note.jpg
└── zak.jpeg
```

After OCR processing, corresponding text files are generated:

``` text
answers/
├── abc.jpeg
├── abc.txt
├── note.jpg
├── note.txt
├── zak.jpeg
└── zak.txt
```

The `.jpeg`, `.jpg`, etc. files contain the original handwritten
answers, while the `.txt` files contain the OCR-extracted text.

------------------------------------------------------------------------

# 5. Converting All Student Answers to Text

`ocr_to_text.py` was developed to automate the conversion of all answer
images inside the `answers` folder into `.txt` files.

### Flow

``` text
answers/*.jpg / *.jpeg / *.png
             ↓
        OCR.space API
             ↓
        answers/*.txt
```

This script checks all supported image files in the `answers` folder and
creates a corresponding text file.

------------------------------------------------------------------------

# 6. Creating the Questions Folder

A separate `Questions` folder was created to store the question image.

``` text
Questions/
├── question.jpeg
└── question.txt
```

The purpose is to convert the handwritten question into text so that the
question can be passed to the evaluation system.

------------------------------------------------------------------------

# 7. Converting the Question Image to Text

`ocr_including_question.py` was developed to include the question image
in the OCR process.

It converts:

``` text
Questions/question.jpeg
          ↓
Questions/question.txt
```

The extracted question can then be read by `evaluate.py`.

This makes the evaluation process independent of manually typing the
question inside the Python code.

------------------------------------------------------------------------

# 8. Initial NLP-Based Evaluation

Initially, a `reference` folder was created.

``` text
reference/
└── answer.txt
```

The `answer.txt` file contained the answer expected by the teacher.

The first evaluation approach used `nlp.py`.

### Initial Evaluation Flow

``` text
Teacher's Reference Answer
          ↓
 Sentence Transformer
          ↓
      Embedding
          ↓
       Compare
          ↑
 Student Answer
          ↓
 Semantic Similarity
          ↓
       Score
```

The system used semantic similarity to compare the student's answer with
the teacher's expected answer.

This approach was useful because it could compare the meaning of two
answers rather than checking only exact words.

However, it had a limitation: the evaluation depended on having a
teacher-provided reference answer.

------------------------------------------------------------------------

# 9. Final LLM-Based Evaluation

To make the system more flexible, the evaluation approach was changed.

Instead of checking:

``` text
Student Answer
      ↓
Reference Answer
      ↓
Similarity
      ↓
Marks
```

the final system uses an LLM.

### Final Flow

``` text
Question
   +
Student Answer
   ↓
  LLM
   ↓
Understand Question
   +
Understand Student Answer
   +
Use Subject Knowledge
   ↓
Evaluate Answer
   ↓
Marks + Percentage + Feedback
```

The LLM evaluates the answer based on:

-   Correctness
-   Concept coverage
-   Relevance
-   Completeness
-   Missing important concepts
-   Quality of explanation

The LLM is instructed not to compare the answer with a reference answer.

------------------------------------------------------------------------

# 10. `evaluate.py`

`evaluate.py` is the main evaluation script in the final version.

It performs the following operations:

1.  Reads `Questions/question.txt`.
2.  Reads all `.txt` files inside the `answers` folder.
3.  Sends the question and each student's answer to the LLM.
4.  Requests structured evaluation.
5.  Displays the result in the terminal.

### Evaluation Output

The system provides:

``` text
Correctness
Concept Coverage
Relevance
Completeness
Final Percentage
Final Marks
Missing Concepts
Feedback
```

For example:

``` text
===== LLM EVALUATION =====

Correctness: 80 %
Concept Coverage: 75 %
Relevance: 90 %
Completeness: 70 %

Final Percentage: 78 %

Final Marks: 3.9 / 5

Missing Concepts:
✗ Pattern learning

Feedback:
The answer is relevant and mostly correct,
but some important concepts need more explanation.
```

------------------------------------------------------------------------

# 11. Final System Architecture

The complete project can be represented as:

``` text
                 QUESTION IMAGE
                       │
                       ↓
             ocr_including_question.py
                       │
                       ↓
              Questions/question.txt
                       │
                       │
                       ↓
              ┌─────────────────┐
              │                 │
              │   LLM EVALUATOR │
              │                 │
              └─────────────────┘
                       ↑
                       │
                       │
               Student Answers
                       │
                       ↓
             ocr_to_text.py
                       │
                       ↓
                  answers/
                       │
                       ↓
             Student Answer .txt
                       │
                       ↓
                    LLM
                       │
          ┌────────────┼────────────┐
          ↓            ↓            ↓
       Analysis      Marks       Feedback
```

------------------------------------------------------------------------

# 12. Role of Each Python File

  ------------------------------------------------------------------------
  File                          Purpose
  ----------------------------- ------------------------------------------
  `ocr.py`                      Initial OCR testing and single-image OCR

  `ocrmul.py`                   Process multiple answer-sheet images

  `ocrparticular.py`            Process/display a particular answer sheet

  `ocr_to_text.py`              Convert all student answer images into
                                `.txt` files

  `ocr_including_question.py`   Convert the question image into
                                `question.txt`

  `nlp.py`                      Earlier NLP-based evaluation using teacher
                                reference answer

  `evaluate.py`                 Final LLM-based answer evaluation

  `README.md`                   Project documentation
  ------------------------------------------------------------------------

------------------------------------------------------------------------

# 13. Technologies Used

-   **Python** --- Main programming language
-   **OCR.space API** --- Handwritten/printed image-to-text conversion
-   **Google GenAI / Gemini API** --- LLM-based answer evaluation
-   **Sentence Transformers** --- Used in the earlier reference-answer
    comparison approach
-   **scikit-learn** --- Used for cosine similarity in the earlier NLP
    approach
-   **VS Code** --- Development environment

------------------------------------------------------------------------

# 14. API Configuration

The OCR system uses an OCR.space API key.

The final LLM evaluation system uses a Gemini API key stored as an
environment variable.

Example:

``` bash
export GEMINI_API_KEY="YOUR_API_KEY"
```

API keys should not be hard-coded or uploaded to GitHub.

------------------------------------------------------------------------

# 15. Running the Project

## Step 1 --- Install required packages

``` bash
pip install requests
pip install google-genai
```

If the older NLP implementation is also required:

``` bash
pip install sentence-transformers
pip install scikit-learn
```

## Step 2 --- Convert student answers to text

``` bash
python ocr_to_text.py
```

## Step 3 --- Convert question to text

``` bash
python ocr_including_question.py
```

## Step 4 --- Set Gemini API key

``` bash
export GEMINI_API_KEY="YOUR_API_KEY"
```

## Step 5 --- Evaluate student answers

``` bash
python evaluate.py
```

------------------------------------------------------------------------

# 16. Development Progress

The project evolved in the following sequence:

``` text
1. Basic OCR
      ↓
2. Multiple Answer Sheet OCR
      ↓
3. Particular Answer Sheet Selection
      ↓
4. Answers Folder
      ↓
5. OCR Images → Text Files
      ↓
6. Questions Folder
      ↓
7. Question Image → Text File
      ↓
8. Reference Answer Approach
      ↓
9. NLP Semantic Similarity
      ↓
10. LLM-Based Evaluation
      ↓
11. Final Marks + Feedback
```

------------------------------------------------------------------------

# 17. Advantages of the Final Approach

The final LLM-based approach has several advantages:

-   No fixed reference answer is required for every question.
-   The model can understand the meaning of the student's answer.
-   Partially correct answers can receive partial marks.
-   Missing concepts can be identified.
-   Feedback can be generated automatically.
-   Multiple student answers can be evaluated from the `answers` folder.
-   The question is read dynamically from `Questions/question.txt`.

------------------------------------------------------------------------

# 18. Important Note

OCR accuracy directly affects evaluation accuracy.

If the handwritten text is incorrectly recognized by OCR, the LLM may
evaluate the incorrect extracted text rather than the original
handwriting.

Therefore, OCR output should be checked during testing, especially for
difficult handwriting.

------------------------------------------------------------------------

# 19. Future Improvements

Possible future improvements include:

-   Web-based interface for uploading answer sheets
-   Automatic student name/roll-number detection
-   Support for multiple questions in one answer sheet
-   Question-wise marks
-   Automatic result report generation
-   Database storage of student results
-   Better handwriting OCR
-   Human teacher review/override
-   Batch evaluation of complete answer sheets
-   PDF report generation
