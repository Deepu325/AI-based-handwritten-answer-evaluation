import os
import requests

# --------------------------------
# 1. Project folder
# --------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --------------------------------
# 2. Images folder
# --------------------------------
IMAGE_DIR = os.path.join(BASE_DIR, "answers")

# --------------------------------
# 3. Folder se images ki list
# --------------------------------
answers = []

for filename in os.listdir(IMAGE_DIR):
    if filename.lower().endswith((".jpg", ".jpeg", ".png")):
        answers.append(filename)

# Images ko order mein arrange karo
answers.sort()

# --------------------------------
# 4. Terminal par images dikhao
# --------------------------------
print("Available Images:")

for i in range(len(answers)):
    print(i + 1, ".", answers[i])

# --------------------------------
# 5. User se image choose karwao
# --------------------------------
choice = int(input("\nEnter image number: "))

# User ne 1 diya → index 0
# User ne 2 diya → index 1
selected_image = answers[choice - 1]

print("\nSelected Image:", selected_image)

# --------------------------------
# 6. Selected image ka path
# --------------------------------
image_path = os.path.join(IMAGE_DIR, selected_image)

# --------------------------------
# 7. OCR API
# --------------------------------
url = "https://api.ocr.space/parse/image"

api_key = "K89679663788957"

# --------------------------------
# 8. Image OCR ke liye bhejo
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
# 9. JSON response
# --------------------------------
result = response.json()

# --------------------------------
# 10. Error check
# --------------------------------
if result.get("IsErroredOnProcessing"):

    print("\nOCR Error:")
    print(result.get("ErrorMessage"))

else:

    print("\nOCR Result:")
    print(result["ParsedResults"][0]["ParsedText"])