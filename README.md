# Handwritten Answer Evaluation System

A Flask web application that extracts text from handwritten question and
student-answer images using OCR.space, evaluates the answers with a local
Ollama model, and presents marks and feedback in a browser.

## Current web application

### Workflow

1. Select an available local Ollama model and set the maximum marks.
2. Enter the question as text or upload a question image.
3. Upload one or more student answer images.
4. OCR.space extracts text from any uploaded question or answer images.
5. Ollama evaluates each extracted answer against the question.
6. The application calculates the grade and displays the results.

The web workflow does not require a teacher-provided reference answer. The
question and each answer image are uploaded through the interface; sample
images and answer text are not included in this repository.

### Grading

The evaluator requests these rubric scores from the model:

- Correctness: 50% of the weighted score
- Concept coverage: 25%
- Relevance: 15%
- Completeness: 10%

The backend calculates the weighted percentage and converts it to marks. Marks
are rounded to the nearest 0.5 point. If the model identifies an answer as too
brief for the question and available marks, the application caps it at 40% of
the available marks. Results include concise feedback and missing concepts.

The app validates the model's JSON response and reports malformed output as an
evaluation error. Evaluation timing is logged by stage. Ollama requests use
JSON output, temperature 0, a 4096-token context, a 256-token generation cap,
and disabled Qwen3 thinking.

## Technology

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python, Flask
- **OCR:** OCR.space API
- **Answer evaluation:** Ollama with a locally installed model
- **Data storage:** No database in the current web application

`qwen3:8b` is the current default/recommended model. The UI supports selecting
other models installed in Ollama. A local benchmark on one synthetic answer
found `qwen3:4b` faster, but it did not apply the configured brief-answer cap
as consistently as `qwen3:8b`; test representative answers before changing
the production model.

## Requirements

- Python 3
- Ollama installed and running
- At least one Ollama model available (for example, `qwen3:8b`)
- An OCR.space API key for dependable OCR usage

Install the web app packages:

```powershell
python -m pip install flask requests ollama
```

Pull a model if it is not already installed:

```powershell
ollama pull qwen3:8b
```

Set the OCR.space key in PowerShell before launching the app:

```powershell
$env:OCR_SPACE_API_KEY = "YOUR_OCR_SPACE_API_KEY"
```

Without a configured key, the app uses OCR.space's shared `helloworld` demo
key, which may be rate-limited. The application tries OCR.space engines 3 and
2. Recognition quality depends on the image and handwriting; use a sharp,
well-lit, upright image with the writing clearly visible.

## Run

From the project directory:

```powershell
python app.py
```

Open <http://127.0.0.1:5000> in a browser. The Flask development server is
intended for local development, not production hosting.

## Repository structure

```text
.
├── app.py
├── templates/
│   └── index.html
├── evaluate.py
├── nlp.py
├── ocr.py
├── ocr_including_question.py
├── ocr_to_text.py
├── ocrmul.py
├── ocrparticular.py
└── README .md
```

The current web application consists of `app.py` and `templates/index.html`.
The other Python scripts are earlier standalone OCR, NLP, or evaluation
experiments, and are not used by the web app's primary request flow.

### Legacy scripts

- `ocr.py`, `ocrmul.py`, and `ocrparticular.py` are earlier OCR experiments.
- `ocr_to_text.py` converts images from a local `answers/` directory to text.
- `ocr_including_question.py` converts a local question image to text.
- `nlp.py` is an earlier reference-answer similarity experiment. It uses
  `sentence-transformers` and `scikit-learn`.
- `evaluate.py` is a separate command-line Gemini evaluator. It expects
  `Questions/question.txt`, answer `.txt` files in `answers/`, the
  `google-genai` package, and a `GEMINI_API_KEY`.

The `Questions/`, `answers/`, and `reference/` sample-data directories were
removed from the GitHub repository. The legacy scripts that refer to local
question, answer, or reference files require users to provide those files
locally. These directories are not needed for the web application's
image-upload workflow.

## Privacy and limitations

- Student images are sent to OCR.space for text extraction.
- Answer text is sent to the selected Ollama model running locally.
- OCR errors can affect the grade; review extracted text and AI results.
- AI-generated marks are decision support and should be reviewed by a
  teacher/examiner.
- Do not commit API keys or sensitive student data to the repository.
