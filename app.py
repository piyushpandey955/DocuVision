# from dotenv import load_dotenv
# import streamlit as st
# import os
# from PIL import Image
# import google.generativeai as genai



# load_dotenv() # load all environment variables from .env file


# # configuring api key
# genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

# # function to load gemini pro vision model and get response
# def get_gemini_response(input, image, prompt):
#     # load gemini pro vision model
#     model = genai.GenerativeModel('gemini-1.5-flash')
#     response = model.generate_content([input, image[0], prompt])
#     return response.text


# def input_image_setup(uploaded_file):
#     if uploaded_file is not None:
#         # read the file into bytes
#         bytes_data = uploaded_file.getvalue()

#         image_parts = [
#             {
#                 "mime_type": uploaded_file.type,  # get the mime type of uploaded file
#                 "data": bytes_data
#             }
#         ]
#         return image_parts
#     else:
#         raise FileNotFoundError("No File Found")
    



# # initializing our streamlit app

# st.set_page_config(page_title="Gemini Image Demo")
# st.header("Gemini Application")
# input = st.text_input("Input Prompt: ", key="input")
# uploaded_file = st.file_uploader("choose an image...", type=["jpg", "jpeg", "png"])
# image = ""

# if uploaded_file is not None:
#     image = Image.open(uploaded_file)
#     st.image(image, caption="uploaded image.", use_column_width=True)


# submit = st.button("Tell me about the invoice")


# input_prompt = """you are an expert in understanding invoices. You will recieve input images as invoices and you will have to answer questions based on the input image"""


# # if submit button is clicked

# if submit:
#     image_data = input_image_setup(uploaded_file)
#     response = get_gemini_response(input_prompt, image_data, input)
#     st.subheader("The Response is")
#     st.write(response)


from dotenv import load_dotenv
import streamlit as st
import os
from PIL import Image
import pymupdf  # PyMuPDF
import google.generativeai as genai
import io

# Load environment variables
load_dotenv()

# Configure API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to load Gemini Pro Vision model and get response
def get_gemini_response(input, image, prompt):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content([input, image[0], prompt])
    return response.text

# Function to prepare image input for Gemini
def input_image_setup(uploaded_file):
    if uploaded_file is not None:
        if uploaded_file.type == "application/pdf":
            # Convert PDF pages to images using PyMuPDF
            pdf_bytes = uploaded_file.getvalue()
            doc = pymupdf.open("pdf", pdf_bytes)
            image_parts = []
            for page_num, page in enumerate(doc):
                pix = page.get_pixmap()
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

                # Save page as PNG bytes
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format="PNG")
                image_parts.append({
                    "mime_type": "image/png",
                    "data": img_byte_arr.getvalue()
                })
            return image_parts
        else:
            # For images (JPG, PNG, etc.)
            bytes_data = uploaded_file.getvalue()
            image_parts = [
                {
                    "mime_type": uploaded_file.type,
                    "data": bytes_data
                }
            ]
            return image_parts
    else:
        raise FileNotFoundError("No File Found")

# Streamlit UI
st.set_page_config(page_title="Gemini PDF/Image Reader")
st.header("📄 DocuVision PDF & Image Reader")

# Input and File Upload
input = st.text_input("Input Prompt: ", key="input")
uploaded_file = st.file_uploader("Upload an Image or PDF", type=["jpg", "jpeg", "png", "pdf"])
image = ""

# Preview uploaded file
if uploaded_file is not None:
    if uploaded_file.type == "application/pdf":
        st.info("📑 PDF uploaded. Showing first page preview 👇")
        doc = pymupdf.open("pdf", uploaded_file.getvalue())
        first_page = doc[0].get_pixmap()
        img = Image.frombytes("RGB", [first_page.width, first_page.height], first_page.samples)
        st.image(img, caption="First page preview", use_column_width=True)
    else:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)

# Analyze Button
submit = st.button("🔍 Analyze Document")

# Prompt for Gemini
input_prompt = """
You are an AI document analysis assistant.
You can understand and analyze any type of document, whether it is text, tables, forms, images, 
handwritten notes, academic papers, reports, invoices, legal contracts, resumes, or any other PDF or image.
Your job is to carefully read the content and provide accurate, clear, and context-aware answers 
to the user's questions about the uploaded file.
If the user does not ask a specific question, give a structured summary of the document instead.
"""

# If button is clicked
if submit:
    image_data = input_image_setup(uploaded_file)
    response = get_gemini_response(input_prompt, image_data, input)
    st.subheader("The Response is")
    st.write(response)