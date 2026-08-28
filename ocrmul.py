import os
import requests

# Project folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Images folder
IMAGE_DIR = os.path.join(BASE_DIR, "answers")

# OCR API
url = "https://api.ocr.space/parse/image"

# API key
api_key = "K89679663788957"


# Folder ki saari files dekho
for filename in os.listdir(IMAGE_DIR):

    # Sirf image files lo
    if filename.lower().endswith((".jpg", ".jpeg", ".png")):

        # Complete image path
        image_path = os.path.join(IMAGE_DIR, filename)

        print("\nProcessing:", filename)

        # Image open karo
        with open(image_path, "rb") as image_file:

            # OCR API ko image bhejo
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

        # Response ko JSON mein convert karo
        result = response.json()

        # Error check
        if result.get("IsErroredOnProcessing"):

            print("OCR Error:")
            print(result.get("ErrorMessage"))

        else:

            # Is image ka OCR text
            print("OCR Result:")
            print(result["ParsedResults"][0]["ParsedText"])