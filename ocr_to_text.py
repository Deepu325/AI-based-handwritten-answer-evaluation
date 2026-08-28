import os
import requests


# ============================================
# OCR API SETTINGS
# ============================================

API_URL = "https://api.ocr.space/parse/image"

# Testing ke liye helloworld use kar sakte ho.
# Project ke liye apni free API key use karna better hai.
API_KEY = "helloworld"


# ============================================
# ANSWERS FOLDER
# ============================================

answers_folder = "answers"


# ============================================
# SUPPORTED IMAGE FILES
# ============================================

image_extensions = (
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".tif",
    ".tiff"
)


# ============================================
# PROCESS ALL IMAGES
# ============================================

for filename in os.listdir(answers_folder):

    # Sirf images process karo
    if not filename.lower().endswith(image_extensions):
        continue


    image_path = os.path.join(
        answers_folder,
        filename
    )


    print("\n====================================")
    print("Processing:", filename)
    print("====================================")


    # ========================================
    # OCR API CALL
    # ========================================

    try:

        with open(image_path, "rb") as image_file:

            response = requests.post(
                API_URL,

                headers={
                    "apikey": API_KEY
                },

                files={
                    "file": image_file
                },

                data={
                    "language": "eng",
                    "OCREngine": "3",
                    "detectOrientation": "true",
                    "scale": "true"
                },

                timeout=120
            )


        # ====================================
        # CHECK API RESPONSE
        # ====================================

        result = response.json()


        # ====================================
        # CHECK OCR ERROR
        # ====================================

        if result.get("IsErroredOnProcessing"):

            print("❌ OCR Error:")
            print(
                result.get(
                    "ErrorMessage",
                    "Unknown error"
                )
            )

            continue


        # ====================================
        # EXTRACT TEXT
        # ====================================

        parsed_results = result.get(
            "ParsedResults",
            []
        )


        if not parsed_results:

            print("❌ No text found.")

            continue


        extracted_text = ""


        for page in parsed_results:

            text = page.get(
                "ParsedText",
                ""
            )

            extracted_text += text


        # ====================================
        # CREATE TXT FILE
        # ====================================

        txt_filename = os.path.splitext(
            filename
        )[0] + ".txt"


        txt_path = os.path.join(
            answers_folder,
            txt_filename
        )


        with open(
            txt_path,
            "w",
            encoding="utf-8"  # character encoding system 
        ) as text_file:

            text_file.write(
                extracted_text
            )


        # ====================================
        # SUCCESS
        # ====================================

        print("✅ OCR successful!")

        print(
            "Text file created:",
            txt_filename
        )


    except Exception as e:

        print("❌ Error:")
        print(e)


print("\n====================================")
print("OCR PROCESS COMPLETED")
print("====================================")