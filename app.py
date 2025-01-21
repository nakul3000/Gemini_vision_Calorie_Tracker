import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import io
from streamlit.runtime.uploaded_file_manager import UploadedFile
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

# Custom class to simulate an uploaded file
class FakeUploadedFile(io.BytesIO):
    def __init__(self, file_bytes, name, mime_type):
        super().__init__(file_bytes)
        self.name = name
        self.type = mime_type

st.set_page_config(page_title="Gemini Health Calorie Tracker")
st.header("🤖 E can track your calories! 😊")

# Initialize session state variables if not already set
if "show_camera" not in st.session_state:
    st.session_state.show_camera = False
if "source_file" not in st.session_state:
    st.session_state.source_file = None

# 1. Option to upload an image
uploaded_file = st.file_uploader("Upload an image...", type=["jpg", "jpeg", "png"])

# 2. Dropdown and button for choosing an example image
example_options = {
    "Example 1": "images/food1.jpg",
    "Example 2": "images/food2.jpg",
    "Example 3": "images/food3.jpg"
}
selected_example = st.selectbox("Choose an example image", list(example_options.keys()))

if st.button("Load Example"):
    try:
        image_path = example_options[selected_example]
        image = Image.open(image_path)
        st.image(image, caption=f"{selected_example}", use_container_width=True)

        with open(image_path, "rb") as file:
            file_bytes = file.read()

        fake_file = FakeUploadedFile(file_bytes, image_path.split("/")[-1], "image/jpeg")
        st.session_state.source_file = fake_file

    except Exception as e:
        st.error(f"Error loading example image: {e}")

# 3. Option to take a picture
if st.button("Take Picture"):
    st.session_state.show_camera = True

camera_image = None
if st.session_state.show_camera:
    camera_image = st.camera_input("Capture an image")

# Process inputs based on priority: camera > upload > example
if camera_image is not None:
    try:
        image = Image.open(camera_image)
        st.image(image, caption="Captured Image.", use_container_width=True)
        st.session_state.source_file = camera_image
    except Exception as e:
        st.error(f"Error processing captured image: {e}")
elif uploaded_file is not None:
    try:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image.", use_container_width=True)
        st.session_state.source_file = uploaded_file
    except Exception as e:
        st.error(f"Error processing uploaded image: {e}")
elif st.session_state.source_file is not None:
    try:
        # Display the stored example image if available and no new camera/upload occurred
        image = Image.open(st.session_state.source_file)
        st.image(image, caption="Example Image Selected.", use_container_width=True)
    except Exception as e:
        st.error(f"Error displaying stored example image: {e}")
else:
    st.info("Please upload an image, choose an example, or take a picture.")

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
    source_file = st.session_state.get("source_file")
    if source_file is not None:
        try:
            image_data = input_image_setup(source_file)
            response = get_gemini_response(input_prompt, image_data)
            st.header("The Response is:")
            st.write(response)
        except Exception as e:
            st.error(f"An error occurred while processing the image: {e}")
    else:
        st.error("No image captured, uploaded, or example loaded. Please provide an image.")
# make ui a bit nicer and integrate picture taking ability for phone purposes.
# so one thing is including past chats and convos as konwledge base to suggest new dishes based on this
# voice assisted
# chat capabilites like the portion size is samll so what else etc : can build the chat web app.
