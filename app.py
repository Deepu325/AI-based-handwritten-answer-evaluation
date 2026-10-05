from flask import Flask, render_template, request, jsonify
import os
import json
import math
import time
import requests as req_lib
import ollama

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

OCR_API_URL = "https://api.ocr.space/parse/image"
OCR_API_KEY = os.environ.get("OCR_SPACE_API_KEY", "helloworld")
OLLAMA_CLIENT = ollama.Client(timeout=120.0)
OLLAMA_NUM_CTX = 4096
OLLAMA_NUM_PREDICT = 256
MAX_EVALUATION_TEXT_CHARS = 10000

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'bmp', 'tif', 'tiff'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def ocr_image(image_bytes, filename):
    """Send image bytes to OCR.space, trying its alternate engine if needed."""
    errors = []
    timings = {"request_sec": 0.0, "response_processing_sec": 0.0}
    for engine in ("3", "2"):
        request_started = time.perf_counter()
        try:
            response = req_lib.post(
                OCR_API_URL,
                headers={"apikey": OCR_API_KEY},
                files={"file": (filename, image_bytes)},
                data={
                    "language": "eng",
                    "OCREngine": engine,
                    "detectOrientation": "true",
                    "scale": "true"
                },
                timeout=120
            )
        except req_lib.RequestException as e:
            timings["request_sec"] += time.perf_counter() - request_started
            errors.append(f"Engine {engine}: {e}")
            continue
        timings["request_sec"] += time.perf_counter() - request_started

        processing_started = time.perf_counter()
        try:
            response.raise_for_status()
            result = response.json()
        except (req_lib.RequestException, ValueError) as e:
            timings["response_processing_sec"] += time.perf_counter() - processing_started
            errors.append(f"Engine {engine}: {e}")
            continue

        if not isinstance(result, dict):
            timings["response_processing_sec"] += time.perf_counter() - processing_started
            errors.append(f"Engine {engine}: invalid OCR response")
            continue
        if result.get("IsErroredOnProcessing"):
            message = result.get("ErrorMessage", "Unknown OCR error")
            if isinstance(message, list):
                message = "; ".join(str(item) for item in message)
            timings["response_processing_sec"] += time.perf_counter() - processing_started
            errors.append(f"Engine {engine}: {message}")
            continue

        parsed = result.get("ParsedResults", [])
        if not isinstance(parsed, list):
            timings["response_processing_sec"] += time.perf_counter() - processing_started
            errors.append(f"Engine {engine}: invalid parsed-results response")
            continue
        text = "".join(
            parsed_text
            for item in parsed
            if isinstance(item, dict)
            for parsed_text in [item.get("ParsedText", "")]
            if isinstance(parsed_text, str)
        ).strip()
        timings["response_processing_sec"] += time.perf_counter() - processing_started
        if text:
            timings["total_sec"] = timings["request_sec"] + timings["response_processing_sec"]
            return text, None, timings
        errors.append(f"Engine {engine}: no text found")

    details = "; ".join(errors)
    timings["total_sec"] = timings["request_sec"] + timings["response_processing_sec"]
    return None, (
        "OCR.space could not recognize text with either OCR engine. "
        "Try a sharper, well-lit, upright image and set OCR_SPACE_API_KEY "
        "to your OCR.space API key if you are using the demo key. "
        f"Details: {details}"
    ), timings


def evaluate_with_ollama(model, question, student_answer, total_marks=5):
    """Evaluate one answer and return the result, error, and stage timings."""
    timings = {
        "prompt_preparation_sec": 0.0,
        "ollama_request_sec": 0.0,
        "prompt_evaluation_sec": 0.0,
        "generation_sec": 0.0,
        "json_parsing_sec": 0.0,
    }
    total_started = time.perf_counter()

    if len(question) + len(student_answer) > MAX_EVALUATION_TEXT_CHARS:
        timings["total_sec"] = time.perf_counter() - total_started
        return None, (
            f"Question and OCR text exceed the {MAX_EVALUATION_TEXT_CHARS:,}-character "
            "evaluation limit. Split the answer into shorter sections and evaluate them separately."
        ), timings

    prompt_started = time.perf_counter()
    prompt = f"""You are a fair subject-matter exam grader. Judge the answer against the question and your subject knowledge. Award partial credit; do not reward keyword overlap alone. Keep feedback concise and do not reveal internal reasoning or repeat the question or answer.

Score each criterion independently from 0 to 100:
- correctness (50%): factual accuracy; penalize substantive errors.
- concept_coverage (25%): inclusion of the important concepts needed to answer this question.
- relevance (15%): how directly the answer addresses the question; penalize unrelated content.
- completeness (10%): sufficient explanation and detail for what the question asks.

Marking rules:
- Use the weighted rubric, not an intuitive separate marks score.
- Weighted percentage = correctness * 0.50 + concept_coverage * 0.25 + relevance * 0.15 + completeness * 0.10.
- Final marks = weighted percentage / 100 * maximum marks.
- Give credit for accurate concise answers; do not require unasked details.
- Set "brief_answer" to true when the answer is too short for the question's maximum marks and lacks necessary explanation, reasoning, or examples. A brief answer is capped at 40% of the available marks. Do not flag a concise answer that fully answers a simple question.
- List only important missing concepts that would improve the answer.

QUESTION:
{question}

MAXIMUM MARKS:
{total_marks}

STUDENT ANSWER:
{student_answer}

Return only a JSON object with exactly these fields: "correctness", "concept_coverage", "relevance", and "completeness" (each an integer from 0 to 100), "brief_answer" (boolean), "feedback" (one concise sentence), and "missing_concepts" (up to five concise strings). The application calculates the weighted percentage and final marks from the four criterion scores and applies the brief-answer cap."""
    timings["prompt_preparation_sec"] = time.perf_counter() - prompt_started

    try:
        request_started = time.perf_counter()
        response = OLLAMA_CLIENT.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            format="json",
            think=False,
            options={
                "temperature": 0,
                "num_ctx": OLLAMA_NUM_CTX,
                "num_predict": OLLAMA_NUM_PREDICT,
            },
        )
        timings["ollama_request_sec"] = time.perf_counter() - request_started
        timings["prompt_evaluation_sec"] = (
            getattr(response, "prompt_eval_duration", 0) or 0
        ) / 1_000_000_000
        timings["generation_sec"] = (
            getattr(response, "eval_duration", 0) or 0
        ) / 1_000_000_000
    except Exception as e:
        timings["ollama_request_sec"] = time.perf_counter() - request_started
        timings["total_sec"] = time.perf_counter() - total_started
        return None, f"Ollama request failed for model {model}: {e}", timings

    parse_started = time.perf_counter()
    try:
        raw = response["message"]["content"].strip()
        result = json.loads(raw)
        if not isinstance(result, dict):
            raise ValueError("Model response must be a JSON object")

        scores = {}
        for field in ("correctness", "concept_coverage", "relevance", "completeness"):
            score = result.get(field)
            if (
                isinstance(score, bool)
                or not isinstance(score, (int, float))
                or not 0 <= score <= 100
            ):
                raise ValueError(f"'{field}' must be a number between 0 and 100")
            scores[field] = round(score)
        feedback = result.get("feedback")
        missing_concepts = result.get("missing_concepts")
        missing_concepts = result.get("missing_concepts")
        brief_answer = result.get("brief_answer")
        if not isinstance(feedback, str):
            raise ValueError("'feedback' must be a string")
        if not isinstance(brief_answer, bool):
            raise ValueError("'brief_answer' must be a boolean")
        if not isinstance(missing_concepts, list) or not all(
            isinstance(concept, str) for concept in missing_concepts
        ):
            raise ValueError("'missing_concepts' must be an array of strings")

        weighted_percentage = (
            scores["correctness"] * 0.50
            + scores["concept_coverage"] * 0.25
            + scores["relevance"] * 0.15
            + scores["completeness"] * 0.10
        )
        if brief_answer:
            weighted_percentage = min(weighted_percentage, 40)
            cap_feedback = " Score capped at 40% because the answer is too brief for the marks available."
            if cap_feedback.strip() not in feedback:
                feedback = f"{feedback.rstrip()} {cap_feedback.strip()}".strip()
        final_marks = math.floor(
            (weighted_percentage / 100 * total_marks) * 2 + 0.5
        ) / 2
        result = {
            **scores,
            "brief_answer": brief_answer,
            "marks": final_marks,
            "percentage": round(final_marks / total_marks * 100),
            "feedback": feedback.strip(),
            "missing_concepts": [concept.strip() for concept in missing_concepts if concept.strip()],
        }
    except (AttributeError, KeyError, TypeError, json.JSONDecodeError, ValueError) as e:
        timings["json_parsing_sec"] = time.perf_counter() - parse_started
        timings["total_sec"] = time.perf_counter() - total_started
        return None, f"Invalid evaluation response from model {model}: {e}", timings

    timings["json_parsing_sec"] = time.perf_counter() - parse_started
    timings["total_sec"] = time.perf_counter() - total_started
    return result, None, timings


# ─────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/models')
def get_models():
    """Return list of locally available Ollama models."""
    try:
        models_resp = ollama.list()
        # ollama.list() returns an object with a 'models' attribute
        model_names = [m['model'] for m in models_resp.get('models', [])]
        return jsonify({"models": model_names})
    except Exception as e:
        return jsonify({"models": [], "error": str(e)})


@app.route('/api/evaluate', methods=['POST'])
def evaluate():
    """
    Expects multipart/form-data:
      - model: string (Ollama model name)
      - total_marks: int
      - question_image: file  (or question_text: string)
      - answer_images[]: one or more files
    """
    request_started = time.perf_counter()
    model = request.form.get('model', 'qwen3:8b').strip() or 'qwen3:8b'
    try:
        total_marks = int(request.form.get('total_marks', 5))
    except ValueError:
        return jsonify({"error": "Total marks must be a whole number"}), 400
    if not 1 <= total_marks <= 100:
        return jsonify({"error": "Total marks must be between 1 and 100"}), 400
    question_text_direct = request.form.get('question_text', '').strip()
    question_ocr_timings = {"request_sec": 0.0, "response_processing_sec": 0.0, "total_sec": 0.0}

    print(f"[INFO] model={model}, total_marks={total_marks}")
    print(f"[INFO] form keys: {list(request.form.keys())}")
    print(f"[INFO] file keys: {list(request.files.keys())}")

    # ── Extract question ──────────────────────
    question = question_text_direct

    if not question and 'question_image' in request.files:
        q_file = request.files['question_image']
        if q_file and q_file.filename and allowed_file(q_file.filename):
            img_bytes = q_file.read()
            question, err, question_ocr_timings = ocr_image(img_bytes, q_file.filename)
            if err:
                request_total_sec = time.perf_counter() - request_started
                print(
                    f"[TIMING] question OCR | request={question_ocr_timings['request_sec']:.2f}s "
                    f"| response processing={question_ocr_timings['response_processing_sec']:.2f}s "
                    f"| total={question_ocr_timings['total_sec']:.2f}s "
                    f"| evaluation request total={request_total_sec:.2f}s"
                )
                return jsonify({
                    "error": f"OCR failed for question: {err}",
                    "timings": {
                        "question_ocr": question_ocr_timings,
                        "request_total_sec": request_total_sec,
                    },
                }), 400

    if not question:
        return jsonify({"error": "Please provide a question image or type it in the text box"}), 400

    # ── Extract & evaluate answers ────────────
    answer_files = request.files.getlist('answer_images[]')
    print(f"[INFO] answer_files: {[f.filename for f in answer_files]}")

    if not answer_files or all(f.filename == '' for f in answer_files):
        return jsonify({"error": "Please upload at least one student answer image"}), 400

    results = []

    for ans_file in answer_files:
        if not ans_file or not ans_file.filename or not allowed_file(ans_file.filename):
            continue

        img_bytes = ans_file.read()
        student_name = os.path.splitext(ans_file.filename)[0]

        print(f"[INFO] Processing: {ans_file.filename}")

        # OCR
        student_started = time.perf_counter()
        student_answer, ocr_err, ocr_timings = ocr_image(img_bytes, ans_file.filename)
        if ocr_err or not student_answer:
            ocr_timings["total_sec"] = time.perf_counter() - student_started
            print(
                f"[TIMING] {student_name} | OCR request={ocr_timings['request_sec']:.2f}s "
                f"| OCR response processing={ocr_timings['response_processing_sec']:.2f}s "
                f"| total={ocr_timings['total_sec']:.2f}s"
            )
            results.append({
                "student": student_name,
                "filename": ans_file.filename,
                "ocr_text": "",
                "error": ocr_err or "No text extracted from image",
                "timings": {"ocr": ocr_timings, "total_sec": ocr_timings["total_sec"]},
            })
            continue

        print(f"[INFO] OCR done, text length: {len(student_answer)}")

        # Evaluate with Ollama
        eval_result, eval_err, eval_timings = evaluate_with_ollama(
            model, question, student_answer, total_marks
        )
        eval_timings["ocr_request_sec"] = ocr_timings["request_sec"]
        eval_timings["ocr_response_processing_sec"] = ocr_timings["response_processing_sec"]
        eval_timings["ocr_total_sec"] = ocr_timings["total_sec"]
        eval_timings["total_sec"] = time.perf_counter() - student_started
        print(
            f"[TIMING] {student_name} | OCR={eval_timings['ocr_total_sec']:.2f}s "
            f"(request {eval_timings['ocr_request_sec']:.2f}s, "
            f"response processing {eval_timings['ocr_response_processing_sec']:.2f}s) "
            f"| prompt preparation={eval_timings['prompt_preparation_sec']:.2f}s "
            f"| Ollama request={eval_timings['ollama_request_sec']:.2f}s "
            f"(model prompt eval={eval_timings['prompt_evaluation_sec']:.2f}s, "
            f"generation={eval_timings['generation_sec']:.2f}s) "
            f"| JSON parsing={eval_timings['json_parsing_sec']:.2f}s "
            f"| total={eval_timings['total_sec']:.2f}s"
        )

        if eval_err:
            print(f"[ERROR] Evaluation failed: {eval_err}")
            results.append({
                "student": student_name,
                "filename": ans_file.filename,
                "ocr_text": student_answer,
                "error": eval_err,
                "timings": eval_timings,
            })
        else:
            eval_result["student"] = student_name
            eval_result["filename"] = ans_file.filename
            eval_result["ocr_text"] = student_answer
            eval_result["total_marks"] = total_marks
            eval_result["timings"] = eval_timings
            results.append(eval_result)

    request_total_sec = time.perf_counter() - request_started
    print(
        f"[TIMING] evaluation request | model={model} | question OCR={question_ocr_timings['total_sec']:.2f}s "
        f"| total={request_total_sec:.2f}s"
    )
    return jsonify({
        "question": question,
        "total_marks": total_marks,
        "model": model,
        "timings": {
            "question_ocr": question_ocr_timings,
            "request_total_sec": request_total_sec,
        },
        "results": results
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)
