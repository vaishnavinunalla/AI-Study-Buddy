import streamlit as st
import os
from dotenv import load_dotenv
from google import genai
from pypdf import PdfReader
from datetime import date

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Study-Buddy",
    page_icon="🤖",
    layout="wide"
)

# ============================================================
# GEMINI API SETUP
# ============================================================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("Gemini API key not found!")
    st.info("Please add GEMINI_API_KEY to your .env file.")
    st.stop()

try:
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error("Unable to connect to Gemini.")
    st.write(str(e))
    st.stop()

# ============================================================
# TITLE
# ============================================================

st.title("🤖 AI Study-Buddy Learning Assistant")
st.write("📚 Your Personal AI Learning Companion")

st.divider()

# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("📖 Study Buddy")

option = st.sidebar.selectbox(
    "Choose an option",
    [
        "🏠 Home",
        "💬 Ask AI",
        "📝 Summarize",
        "❓ Generate MCQs",
        "📄 Study Materials",
        "📅 Study Plan"
    ]
)

# ============================================================
# HOME
# ============================================================

if option == "🏠 Home":

    st.header("Welcome to AI Study-Buddy! 🎓")

    st.write(
        """
        AI Study-Buddy is an intelligent learning assistant
        that helps students understand and practice their subjects.

        You can:
        • Ask questions
        • Summarize study material
        • Generate MCQs
        • Upload PDF study materials
        • Ask questions from PDFs
        • Generate personalized study plans
        """
    )

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.info("💬 Ask Questions")
        st.write(
            "Ask questions and get simple explanations "
            "from your AI Study-Buddy."
        )

    with col2:
        st.info("📝 Summarize")
        st.write(
            "Convert long study material into "
            "short and easy notes."
        )

    with col3:
        st.info("❓ Practice")
        st.write(
            "Generate MCQs and practice "
            "your important topics."
        )

# ============================================================
# ASK AI
# ============================================================

elif option == "💬 Ask AI":

    st.header("💬 Ask Your Study-Buddy")

    question = st.text_area(
        "Enter your question:",
        placeholder="Example: What is Artificial Intelligence?",
        height=150
    )

    if st.button("Ask AI 🤖"):

        if question.strip():

            with st.spinner("🤔 Thinking..."):

                try:

                    response = client.models.generate_content(
                        model="gemini-3.8-flash",
                        contents=f"""
You are an AI Study-Buddy.

Help students understand their subjects.

Answer in:
- Simple language
- Clear points
- Easy explanations
- Exam-friendly format when appropriate

Student Question:

{question}
"""
                    )

                    st.success("🤖 AI Answer")

                    if response.text:
                        st.write(response.text)
                    else:
                        st.warning("No answer was returned.")

                except Exception as e:

                    st.error("Error while getting AI response.")
                    st.write(str(e))

        else:

            st.warning("Please enter a question.")

# ============================================================
# SUMMARIZE
# ============================================================

elif option == "📝 Summarize":

    st.header("📝 Study Material Summarizer")

    text = st.text_area(
        "Paste your study material:",
        height=300,
        placeholder="Paste your notes or study material here..."
    )

    if st.button("Summarize ✨"):

        if text.strip():

            with st.spinner("📝 Creating summary..."):

                try:

                    response = client.models.generate_content(
                        model="gemini-3.8-flash",
                        contents=f"""
You are an AI Study-Buddy.

Summarize the following study material.

Requirements:
- Use simple language
- Give important points
- Use headings
- Make it easy to revise
- Keep important concepts
- Make it exam-friendly

Study Material:

{text}
"""
                    )

                    st.success("📝 Summary")

                    if response.text:
                        st.write(response.text)
                    else:
                        st.warning("No summary was generated.")

                except Exception as e:

                    st.error("Error while creating summary.")
                    st.write(str(e))

        else:

            st.warning("Please enter some study material.")

# ============================================================
# MCQ GENERATOR
# ============================================================

elif option == "❓ Generate MCQs":

    st.header("❓ MCQ Generator")

    topic = st.text_input(
        "Enter a topic:",
        placeholder="Example: Python Programming"
    )

    number = st.number_input(
        "Number of MCQs:",
        min_value=1,
        max_value=20,
        value=5,
        step=1
    )

    if st.button("Generate MCQs 🎯"):

        if topic.strip():

            with st.spinner("🎯 Generating MCQs..."):

                try:

                    response = client.models.generate_content(
                        model="gemini-3.8-flash",
                        contents=f"""
You are an AI Study-Buddy.

Generate {number} multiple-choice questions
on the topic:

{topic}

For every question provide:

Question:
A)
B)
C)
D)

Correct Answer:
Explanation:

Keep the questions suitable for students
and use clear, simple language.
"""
                    )

                    st.success(
                        f"🎯 MCQs for {topic}"
                    )

                    if response.text:
                        st.write(response.text)
                    else:
                        st.warning(
                            "No MCQs were generated."
                        )

                except Exception as e:

                    st.error(
                        "Error while generating MCQs."
                    )
                    st.write(str(e))

        else:

            st.warning("Please enter a topic.")

# ============================================================
# STUDY MATERIALS / PDF
# ============================================================

elif option == "📄 Study Materials":

    st.header("📄 AI PDF Study Assistant")

    st.write(
        "Upload your study PDF and ask questions, "
        "summarize it, or generate MCQs."
    )

    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"]
    )

    if uploaded_file:

        st.success(
            f"✅ {uploaded_file.name} uploaded successfully!"
        )

        try:

            reader = PdfReader(uploaded_file)

            page_count = len(reader.pages)

            st.info(
                f"📄 Total Pages: {page_count}"
            )

            full_text = ""

            progress = st.progress(0)

            for i, page in enumerate(reader.pages):

                page_text = page.extract_text()

                if page_text:
                    full_text += page_text + "\n"

                progress.progress(
                    (i + 1) / page_count
                )

            if full_text.strip():

                st.success(
                    "✅ PDF text extracted successfully!"
                )

                pdf_option = st.radio(
                    "What do you want to do with this PDF?",
                    [
                        "💬 Ask Questions",
                        "📝 Summarize PDF",
                        "❓ Generate MCQs"
                    ],
                    horizontal=True
                )

                st.divider()

                # ====================================================
                # ASK QUESTIONS FROM PDF
                # ====================================================

                if pdf_option == "💬 Ask Questions":

                    st.subheader(
                        "💬 Ask a Question About Your PDF"
                    )

                    pdf_question = st.text_area(
                        "Enter your question:",
                        placeholder=(
                            "Example: What are the important "
                            "concepts discussed in this PDF?"
                        ),
                        height=120
                    )

                    if st.button("Ask PDF 🤖"):

                        if pdf_question.strip():

                            with st.spinner(
                                "🤔 Reading your PDF..."
                            ):

                                try:

                                    response = client.models.generate_content(
                                        model="gemini-3.8-flash",
                                        contents=f"""
You are an AI Study-Buddy.

Answer the student's question using ONLY
the study material provided below.

Rules:
- Use simple language
- Give clear explanations
- Use bullet points when useful
- Do not invent information
- Make the answer exam-friendly

PDF Study Material:

{full_text}

Student Question:

{pdf_question}
"""
                                    )

                                    st.success(
                                        "🤖 Answer"
                                    )

                                    if response.text:
                                        st.write(
                                            response.text
                                        )
                                    else:
                                        st.warning(
                                            "No answer was returned."
                                        )

                                except Exception as e:

                                    st.error(
                                        "Error while asking PDF."
                                    )
                                    st.write(str(e))

                        else:

                            st.warning(
                                "Please enter a question."
                            )

                # ====================================================
                # SUMMARIZE PDF
                # ====================================================

                elif pdf_option == "📝 Summarize PDF":

                    st.subheader(
                        "📝 PDF Summary"
                    )

                    if st.button(
                        "Summarize PDF ✨"
                    ):

                        with st.spinner(
                            "Creating PDF summary..."
                        ):

                            try:

                                response = client.models.generate_content(
                                    model="gemini-3.8-flash",
                                    contents=f"""
You are an AI Study-Buddy.

Summarize the following PDF study material.

Requirements:
- Use simple language
- Use headings
- Give important points
- Include important definitions
- Make it easy to revise
- Keep important concepts
- Make it exam-friendly

PDF Study Material:

{full_text}
"""
                                )

                                st.success(
                                    "📝 PDF Summary"
                                )

                                if response.text:
                                    st.write(
                                        response.text
                                    )
                                else:
                                    st.warning(
                                        "No summary was generated."
                                    )

                            except Exception as e:

                                st.error(
                                    "Error while summarizing PDF."
                                )
                                st.write(str(e))

                # ====================================================
                # GENERATE MCQs FROM PDF
                # ====================================================

                elif pdf_option == "❓ Generate MCQs":

                    st.subheader(
                        "❓ Generate MCQs From PDF"
                    )

                    mcq_number = st.number_input(
                        "Number of MCQs:",
                        min_value=1,
                        max_value=20,
                        value=5,
                        step=1,
                        key="pdf_mcq_number"
                    )

                    if st.button(
                        "Generate MCQs 🎯"
                    ):

                        with st.spinner(
                            "Creating MCQs from PDF..."
                        ):

                            try:

                                response = client.models.generate_content(
                                    model="gemini-3.8-flash",
                                    contents=f"""
You are an AI Study-Buddy.

Create {mcq_number} multiple-choice questions
using ONLY the information in the PDF study
material below.

For every question provide:

Question:
A)
B)
C)
D)

Correct Answer:
Explanation:

Rules:
- Use simple language
- Questions must be based on the PDF
- Avoid information outside the PDF
- Make questions useful for exam preparation

PDF Study Material:

{full_text}
"""
                                )

                                st.success(
                                    "🎯 PDF MCQs"
                                )

                                if response.text:
                                    st.write(
                                        response.text
                                    )
                                else:
                                    st.warning(
                                        "No MCQs were generated."
                                    )

                            except Exception as e:

                                st.error(
                                    "Error while generating MCQs."
                                )
                                st.write(str(e))

                # ====================================================
                # VIEW EXTRACTED TEXT
                # ====================================================

                st.divider()

                with st.expander(
                    "📖 View Extracted PDF Text"
                ):

                    st.text_area(
                        "PDF Content",
                        full_text,
                        height=400
                    )

                # ====================================================
                # DOWNLOAD TEXT
                # ====================================================

                st.download_button(
                    label="📥 Download Extracted Text",
                    data=full_text,
                    file_name="extracted_study_material.txt",
                    mime="text/plain"
                )

            else:

                st.warning(
                    "No readable text found in this PDF."
                )

                st.info(
                    "This may be a scanned/image-only PDF."
                )

        except Exception as e:

            st.error(
                "Error while reading the PDF."
            )

            st.write(str(e))

# ============================================================
# PERSONALIZED STUDY PLAN
# ============================================================

elif option == "📅 Study Plan":

    st.header("📅 Personalized AI Study Plan")

    st.write(
        "Create a personalized study timetable using AI."
    )

    subject = st.text_input(
        "📚 Subject:",
        placeholder="Example: Data Structures"
    )

    topics = st.text_area(
        "📖 Topics to study:",
        placeholder=(
            "Example:\n"
            "Arrays\n"
            "Linked Lists\n"
            "Stacks\n"
            "Queues\n"
            "Trees"
        ),
        height=150
    )

    exam_date = st.date_input(
        "📅 Exam Date",
        min_value=date.today()
    )

    study_hours = st.number_input(
        "⏰ Daily study hours:",
        min_value=1,
        max_value=12,
        value=3,
        step=1
    )

    difficulty = st.selectbox(
        "📊 Difficulty Level:",
        [
            "Beginner",
            "Intermediate",
            "Advanced"
        ]
    )

    if st.button("Generate Study Plan 🚀"):

        if subject.strip() and topics.strip():

            with st.spinner(
                "🤖 Creating your personalized study plan..."
            ):

                try:

                    response = client.models.generate_content(
                        model="gemini-3.8-flash",
                        contents=f"""
You are an AI Study-Buddy.

Create a personalized study plan for a student.

Subject:
{subject}

Topics:
{topics}

Exam Date:
{exam_date}

Daily Study Hours:
{study_hours}

Difficulty Level:
{difficulty}

Create a practical day-by-day study plan.

For each day include:
- Topics to study
- Study time
- Revision time
- Practice questions
- Short break suggestions

Also include:

1. Overall strategy
2. Important topics
3. Revision plan
4. Final exam preparation tips

Use simple language.
Make the plan realistic and student-friendly.
"""
                    )

                    st.success(
                        "🎯 Your Personalized Study Plan"
                    )

                    if response.text:
                        st.write(
                            response.text
                        )
                    else:
                        st.warning(
                            "No study plan was generated."
                        )

                except Exception as e:

                    st.error(
                        "Error while generating study plan."
                    )

                    st.write(
                        str(e)
                    )

        else:

            st.warning(
                "Please enter the subject and topics."
            )

# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "🤖 AI Study-Buddy Learning Assistant | "
    "Python + Streamlit + Gemini"
)