import os
import requests

# --------------------------------
# 1. Get project folder
# --------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --------------------------------
# 2. Image path
# --------------------------------
image_path = os.path.join(BASE_DIR, "answers", "abc.jpeg")

# --------------------------------
# 3. OCR.space API
# --------------------------------
url = "https://api.ocr.space/parse/image"

# Apni API key yahan paste karo
api_key = "K89679663788957"

# --------------------------------
# 4. Open image
# --------------------------------
with open(image_path, "rb") as image_file:

    response = requests.post(
        url,
        files={
            "file": image_file
        },
        data={
            "apikey": api_key,
            "language": "eng",
            "OCREngine": "3"
        }
    )

# --------------------------------
# 5. Convert response to JSON
# --------------------------------
result = response.json()

# --------------------------------
# 6. Check OCR result
# --------------------------------
if result.get("IsErroredOnProcessing"):

    print("OCR Error:")
    print(result.get("ErrorMessage"))

else:

    print("OCR Result:")

    print(result["ParsedResults"][1]["ParsedText"])