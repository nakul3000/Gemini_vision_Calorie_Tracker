import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

from PIL import Image

#load_dotenv() # loads all the enviroinment variables


#genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Instead of load_dotenv() and os.getenv(...), use:
api_key = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=api_key)


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

# Provide options to the user: capture using camera or upload from device
camera_image = st.camera_input("Take a Picture")
uploaded_file = st.file_uploader("Or upload an image...", type=["jpg", "jpeg", "png"])

# Determine which image to use: priority to camera capture if available, else file upload
image = None
source_file = None

if camera_image is not None:
    try:
        image = Image.open(camera_image)
        st.image(image, caption="Captured Image.", use_column_width=True)
        source_file = camera_image
    except Exception as e:
        st.error(f"Error processing captured image: {e}")
elif uploaded_file is not None:
    try:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image.", use_column_width=True)
        source_file = uploaded_file
    except Exception as e:
        st.error(f"Error processing uploaded image: {e}")
else:
    st.info("Please capture an image or upload one.")

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
        try:
            image_data = input_image_setup(source_file)
            response = get_gemini_response(input_prompt, image_data)
            st.header("The Response is:")
            st.write(response)
        except Exception as e:
            st.error(f"An error occurred while processing the image: {e}")
    else:
        st.error("No image captured or uploaded. Please provide an image.")


        
# make ui a bit nicer and integrate picture taking ability for phone purposes.
# so one thing is including past chats and convos as konwledge base to suggest new dishes based on this
# voice assisted
# chat capabilites like the portion size is samll so what else etc : can build the chat web app.
