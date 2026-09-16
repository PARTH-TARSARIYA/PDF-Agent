import streamlit as st
import requests
import hashlib


st.set_page_config(page_title="PDF Agent")

st.title("PDF QA Bot")

# API URLs

RAG_API_URL = "http://localhost:8000/text"
AGENT_API_URL = "http://localhost:8000/ask"


# Initialize session state

if "session_id" not in st.session_state:
    st.session_state.session_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "pdf_signature" not in st.session_state:
    st.session_state.pdf_signature = None


# Upload PDF

uploaded_pdf = st.file_uploader(
    "Upload a PDF file",
    type=["pdf"]
)

if uploaded_pdf:

    # Read PDF bytes
    pdf_bytes = uploaded_pdf.getvalue()

    # Create unique signature for the uploaded PDF
    pdf_signature = hashlib.md5(pdf_bytes).hexdigest()

    # Only create RAG if this is a NEW PDF
    if st.session_state.pdf_signature != pdf_signature:

        with st.spinner("PDF Processing..."):

            try:

                files = {
                    "file": (
                        uploaded_pdf.name,
                        pdf_bytes,
                        "application/pdf"
                    )
                }

                # Send PDF to FastAPI
                response = requests.post(
                    RAG_API_URL,
                    files=files,
                    timeout=120
                )

                if response.status_code == 200:

                    result = response.json()

                    # Store session ID returned by FastAPI
                    st.session_state.session_id = result["session_id"]

                    # Store PDF signature
                    st.session_state.pdf_signature = pdf_signature

                    # Clear previous conversation
                    st.session_state.messages = []

                    st.success(
                        "RAG system successfully created!"
                    )

                else:

                    st.error(
                        f"Backend error: {response.text}"
                    )

            except requests.exceptions.ConnectionError:

                st.error(
                    "Could not connect to FastAPI backend. "
                    "Make sure FastAPI is running."
                )

            except requests.exceptions.Timeout:

                st.error(
                    "The PDF processing request timed out."
                )

            except Exception as e:

                st.error(
                    f"Error: {str(e)}"
                )


# Display Previous Messages

if st.session_state.session_id:

    for message in st.session_state.messages:

        if message["role"] == "user":

            st.write(
                f"**You:** {message['content']}"
            )

        else:

            st.success(
                f"**Assistant:** {message['content']}"
            )


    # Question Input

    user_input = st.text_input(
        "Ask a question or write exit",
        key="question_input"
    )


    # Submit

    if st.button(
        "Submit",
        key="submit_question"
    ):

        if not user_input:

            st.warning(
                "Please enter a question."
            )

        elif user_input.lower() == "exit":

            st.session_state.messages = []

            st.rerun()

        else:

            with st.spinner("Processing..."):

                try:

                    data = {
                        "session_id": st.session_state.session_id,
                        "question": user_input
                    }

                    # Send question to FastAPI
                    response = requests.post(
                        AGENT_API_URL,
                        data=data,
                        timeout=120
                    )

                    if response.status_code == 200:

                        result = response.json()

                        answer = result["answer"]


                        # Store user question
                        st.session_state.messages.append({
                            "role": "user",
                            "content": user_input
                        })


                        # Store assistant answer
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": answer
                        })


                        # Rerun Streamlit
                        st.rerun()


                    else:

                        st.error(
                            f"Backend error: {response.text}"
                        )


                except requests.exceptions.ConnectionError:

                    st.error(
                        "Could not connect to FastAPI backend. "
                        "Make sure FastAPI is running."
                    )


                except requests.exceptions.Timeout:

                    st.error(
                        "The request timed out."
                    )


                except Exception as e:

                    st.error(
                        f"Error: {str(e)}"
                    )

else:

    st.info(
        "Please upload a PDF to start asking questions."
    )