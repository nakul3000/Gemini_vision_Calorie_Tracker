import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

from PIL import Image

load_dotenv() # loads all the enviroinment variables


genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input_prompt, image):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input_prompt, image[0]])
    return response.text

def input_image_setup(uploaded_file):
    if uploaded_file is not None:
        # Read the file into bytes
        bytes_data = uploaded_file.getvalue()

        image_parts = [
            {
                "mime_type" : uploaded_file.type,
                "data": bytes_data
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")


## initialize our streamlit app

st.set_page_config(page_title = "Gemini Health Calorie Tracker")

st.header("🤖 E can track your calories! 😊")

# Option for file upload
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

# Placeholder for camera input (initially not shown)
camera_input_placeholder = st.empty()

# Button to trigger camera usage
if st.button("Take Picture"):
    # Render camera_input widget when button is clicked
    camera_image = camera_input_placeholder.camera_input("Capture an image")
else:
    camera_image = None

image = None
# Prefer camera_image over uploaded_file if available
if camera_image is not None:
    image = Image.open(camera_image)
    st.image(image, caption="Captured Image.", use_column_width=True)
    # Use camera_image for processing
    source_file = camera_image
elif uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image.", use_column_width=True)
    # Use uploaded_file for processing
    source_file = uploaded_file
else:
    source_file = None

submit = st.button("Tell me the total calories")

input_prompt = """
You are an expert nutritionist who needs to see the food items from the image
and calculate the total calories. Also, provide the details of every food item with its calorie intake
in the below format:

1. Item 1 - number of calories
2. Item 2 - number of calories
----
----
Finally, mention if the food is healthy or not.
"""

if submit:
    if source_file is not None:
        image_data = input_image_setup(source_file)
        response = get_gemini_response(input_prompt, image_data)

        st.header("The Response is:")
        st.write(response)
    else:
        st.error("Please upload an image or capture one using your camera.")
# make ui a bit nicer and integrate picture taking ability for phone purposes.
# so one thing is including past chats and convos as konwledge base to suggest new dishes based on this
# voice assisted
# chat capabilites like the portion size is samll so what else etc : can build the chat web app.
