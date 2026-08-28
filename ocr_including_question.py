import os
import requests


# ============================================
# OCR API SETTINGS
# ============================================

API_URL = "https://api.ocr.space/parse/image"

# Testing ke liye helloworld use kar sakte ho
# Project ke liye apni free API key use karna better hai
API_KEY = "helloworld"


# ============================================
# FOLDERS
# ============================================

answers_folder = "answers"
questions_folder = "Questions"


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
# OCR FUNCTION
# ============================================

def convert_images_to_text(folder):

    print("\n")
    print("====================================")
    print("Processing folder:", folder)
    print("====================================")


    # ========================================
    # CHECK FOLDER
    # ========================================

    if not os.path.exists(folder):

        print("❌ Folder not found:", folder)

        return


    # ========================================
    # PROCESS ALL IMAGES
    # ========================================

    for filename in os.listdir(folder):

        # Sirf image files process karo
        if not filename.lower().endswith(
            image_extensions
        ):
            continue


        image_path = os.path.join(
            folder,
            filename
        )


        print("\n------------------------------------")
        print("Processing:", filename)
        print("------------------------------------")


        # ====================================
        # OCR API CALL
        # ====================================

        try:

            with open(
                image_path,
                "rb"
            ) as image_file:

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


            # =================================
            # CHECK HTTP RESPONSE
            # =================================

            response.raise_for_status()


            # =================================
            # GET JSON RESPONSE
            # =================================

            result = response.json()


            # =================================
            # CHECK OCR ERROR
            # =================================

            if result.get(
                "IsErroredOnProcessing"
            ):

                print("❌ OCR Error:")

                print(
                    result.get(
                        "ErrorMessage",
                        "Unknown error"
                    )
                )

                continue


            # =================================
            # EXTRACT PARSED RESULTS
            # =================================

            parsed_results = result.get(
                "ParsedResults",
                []
            )


            if not parsed_results:

                print("❌ No text found.")

                continue


            # =================================
            # EXTRACT TEXT
            # =================================

            extracted_text = ""


            for page in parsed_results:

                text = page.get(
                    "ParsedText",
                    ""
                )

                extracted_text += text


            # =================================
            # CHECK EMPTY TEXT
            # =================================

            if not extracted_text.strip():

                print("❌ OCR completed but no text found.")

                continue


            # =================================
            # CREATE TXT FILE
            # =================================

            txt_filename = (
                os.path.splitext(filename)[0]
                + ".txt"
            )


            txt_path = os.path.join(
                folder,
                txt_filename
            )


            # =================================
            # WRITE TEXT FILE
            # =================================

            with open(
                txt_path,
                "w",
                encoding="utf-8"
            ) as text_file:

                text_file.write(
                    extracted_text
                )


            # =================================
            # SUCCESS
            # =================================

            print("✅ OCR successful!")

            print(
                "Text file created:",
                txt_path
            )


        except requests.exceptions.RequestException as e:

            print("❌ API/Network Error:")

            print(e)


        except Exception as e:

            print("❌ Error:")

            print(e)


# ============================================
# 1. CONVERT QUESTION IMAGES
# ============================================

convert_images_to_text(
    questions_folder
)


# ============================================
# 2. CONVERT ANSWER IMAGES
# ============================================

convert_images_to_text(
    answers_folder
)


# ============================================
# END
# ============================================

print("\n")
print("====================================")
print("OCR PROCESS COMPLETED")
print("====================================")

