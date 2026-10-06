import streamlit as st
import os
import time
from datetime import date
from dotenv import load_dotenv
from google import genai
from pypdf import PdfReader


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Study-Buddy",
    page_icon="🤖",
    layout="wide"
)


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")


# ============================================================
# GEMINI CONFIGURATION
# ============================================================

# Primary model + fallback models.
# If one model temporarily fails, the app tries the next one.
MODELS = [
    "gemini-3.8-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
]

MAX_RETRIES = 3
MAX_PDF_CHARS = 100000


# ============================================================
# GEMINI CLIENT
# ============================================================

client = None

if not API_KEY:
    st.error("❌ Gemini API key not found.")
    st.info(
        "Please create a .env file in the project folder and add:\n\n"
        "GEMINI_API_KEY=YOUR_API_KEY"
    )
else:
    try:
        client = genai.Client(api_key=API_KEY)
    except Exception as e:
        st.error("❌ Unable to initialize Gemini.")
        st.code(str(e))


# ============================================================
# COMMON GEMINI FUNCTION
# ============================================================

def generate_ai_response(prompt):
    """
    Sends a prompt to Gemini with:
    - retry handling
    - 503 handling
    - model fallback
    - clean error messages
    """

    if client is None:
        return None, "Gemini client is not available."

    last_error = None

    for model_name in MODELS:

        for attempt in range(MAX_RETRIES):

            try:

                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )

                if response is not None:

                    text = getattr(response, "text", None)

                    if text and text.strip():
                        return text.strip(), None

                    return None, "The AI returned an empty response."

            except Exception as e:

                last_error = str(e)
                error_text = last_error.lower()

                # ------------------------------------------------
                # 503 / temporary server errors
                # ------------------------------------------------

                if (
                    "503" in error_text
                    or "unavailable" in error_text
                    or "high demand" in error_text
                    or "overloaded" in error_text
                    or "temporarily" in error_text
                ):

                    if attempt < MAX_RETRIES - 1:
                        time.sleep(2 ** attempt)
                        continue

                    # Current model failed after retries.
                    # Try next model.
                    break

                # ------------------------------------------------
                # Rate limit
                # ------------------------------------------------

                if (
                    "429" in error_text
                    or "rate limit" in error_text
                    or "resource exhausted" in error_text
                ):

                    if attempt < MAX_RETRIES - 1:
                        time.sleep(3 * (attempt + 1))
                        continue

                    break

                # ------------------------------------------------
                # Invalid API key
                # ------------------------------------------------

                if (
                    "401" in error_text
                    or "403" in error_text
                    or "api key" in error_text
                    or "permission" in error_text
                ):

                    return None, (
                        "Gemini API key problem.\n\n"
                        "Please check GEMINI_API_KEY in your .env file."
                    )

                # ------------------------------------------------
                # Other error
                # ------------------------------------------------

                return None, last_error

    return None, (
        "Gemini is temporarily unavailable after multiple attempts.\n\n"
        "Please wait for a short time and try again."
    )


# ============================================================
# HELPER FUNCTION FOR AI OUTPUT
# ============================================================

def show_ai_result(title, text, error):

    if error:
        st.error("❌ " + title)
        st.warning(error)
        return

    if text:
        st.success("✅ " + title)
        st.markdown(text)
    else:
        st.warning("⚠️ No response was generated.")


# ============================================================
# APP TITLE
# ============================================================

st.title("🤖 AI Study-Buddy Learning Assistant")

st.write(
    "📚 Your Personal AI Learning Companion"
)

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

    st.divider()

    st.subheader("✨ Features")

    features = [
        "💬 AI Question Answering",
        "📝 Text Summarization",
        "❓ AI MCQ Generator",
        "📄 PDF Study Assistant",
        "📚 PDF Question Answering",
        "📅 Personalized Study Plan",
    ]

    for feature in features:
        st.write("✅ " + feature)


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

    if st.button("Ask AI 🤖", type="primary"):

        if not question.strip():

            st.warning("⚠️ Please enter a question.")

        else:

            prompt = f"""
You are an AI Study-Buddy.

Help students understand academic subjects.

Answer in:
- Simple language
- Clear points
- Easy explanations
- Examples when useful
- Exam-friendly format when appropriate

Do not unnecessarily make the answer complicated.

Student Question:

{question}
"""

            with st.spinner("🤔 Thinking..."):

                answer, error = generate_ai_response(prompt)

            show_ai_result(
                "AI Answer",
                answer,
                error
            )


# ============================================================
# SUMMARIZE TEXT
# ============================================================

elif option == "📝 Summarize":

    st.header("📝 Study Material Summarizer")

    text = st.text_area(
        "Paste your study material:",
        height=300,
        placeholder="Paste your notes or study material here..."
    )

    if st.button("Summarize ✨", type="primary"):

        if not text.strip():

            st.warning("⚠️ Please enter some study material.")

        else:

            prompt = f"""
You are an AI Study-Buddy.

Summarize the following study material.

Requirements:

- Use simple language
- Give important points
- Use headings
- Keep important concepts
- Include important definitions
- Make it easy to revise
- Make it exam-friendly
- Avoid unnecessary information

Study Material:

{text}
"""

            with st.spinner("📝 Creating summary..."):

                answer, error = generate_ai_response(prompt)

            show_ai_result(
                "Study Summary",
                answer,
                error
            )


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

    if st.button("Generate MCQs 🎯", type="primary"):

        if not topic.strip():

            st.warning("⚠️ Please enter a topic.")

        else:

            prompt = f"""
You are an AI Study-Buddy.

Generate {number} multiple-choice questions
on the following topic:

{topic}

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
- Make questions suitable for students
- Include a mixture of easy and moderate questions
- Keep the answers accurate
- Make the questions useful for exam preparation
"""

            with st.spinner("🎯 Generating MCQs..."):

                answer, error = generate_ai_response(prompt)

            show_ai_result(
                f"MCQs for {topic}",
                answer,
                error
            )


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

            if page_count == 0:

                st.warning("⚠️ This PDF contains no pages.")

            else:

                st.info(
                    f"📄 Total Pages: {page_count}"
                )

                full_text = ""

                progress = st.progress(0)

                for i, page in enumerate(reader.pages):

                    try:

                        page_text = page.extract_text()

                        if page_text:
                            full_text += page_text + "\n"

                    except Exception:
                        pass

                    progress.progress(
                        (i + 1) / page_count
                    )

                progress.empty()

                full_text = full_text.strip()

                if full_text:

                    original_length = len(full_text)

                    # ------------------------------------------------
                    # Protect API request size
                    # ------------------------------------------------

                    if len(full_text) > MAX_PDF_CHARS:

                        full_text_for_ai = full_text[:MAX_PDF_CHARS]

                        st.warning(
                            f"⚠️ This PDF contains a large amount of text "
                            f"({original_length:,} characters). "
                            f"For AI processing, the first "
                            f"{MAX_PDF_CHARS:,} characters will be used."
                        )

                    else:

                        full_text_for_ai = full_text

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
                    # PDF ASK QUESTIONS
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

                        if st.button(
                            "Ask PDF 🤖",
                            type="primary"
                        ):

                            if not pdf_question.strip():

                                st.warning(
                                    "⚠️ Please enter a question."
                                )

                            else:

                                prompt = f"""
You are an AI Study-Buddy.

Answer the student's question using ONLY
the study material provided below.

Rules:

- Use simple language
- Give clear explanations
- Use bullet points when useful
- Do not invent information
- If the answer is not available in the PDF, clearly say:
  "This information is not available in the uploaded PDF."
- Make the answer exam-friendly

PDF Study Material:

{full_text_for_ai}

Student Question:

{pdf_question}
"""

                                with st.spinner(
                                    "🤔 Reading your PDF..."
                                ):

                                    answer, error = (
                                        generate_ai_response(prompt)
                                    )

                                show_ai_result(
                                    "PDF Answer",
                                    answer,
                                    error
                                )

                    # ====================================================
                    # PDF SUMMARY
                    # ====================================================

                    elif pdf_option == "📝 Summarize PDF":

                        st.subheader(
                            "📝 PDF Summary"
                        )

                        if st.button(
                            "Summarize PDF ✨",
                            type="primary"
                        ):

                            prompt = f"""
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
- Do not invent information

PDF Study Material:

{full_text_for_ai}
"""

                            with st.spinner(
                                "📝 Creating PDF summary..."
                            ):

                                answer, error = (
                                    generate_ai_response(prompt)
                                )

                            show_ai_result(
                                "PDF Summary",
                                answer,
                                error
                            )

                    # ====================================================
                    # PDF MCQs
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
                            "Generate MCQs 🎯",
                            type="primary"
                        ):

                            prompt = f"""
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
- Keep answers accurate
- Make questions useful for exam preparation

PDF Study Material:

{full_text_for_ai}
"""

                            with st.spinner(
                                "🎯 Creating MCQs from PDF..."
                            ):

                                answer, error = (
                                    generate_ai_response(prompt)
                                )

                            show_ai_result(
                                "PDF MCQs",
                                answer,
                                error
                            )

                    # ====================================================
                    # VIEW PDF TEXT
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
                    # DOWNLOAD PDF TEXT
                    # ====================================================

                    st.download_button(
                        label="📥 Download Extracted Text",
                        data=full_text,
                        file_name="extracted_study_material.txt",
                        mime="text/plain"
                    )

                else:

                    st.warning(
                        "⚠️ No readable text was found in this PDF."
                    )

                    st.info(
                        "This may be a scanned or image-only PDF. "
                        "Text extraction requires a text-based PDF."
                    )

        except Exception as e:

            st.error(
                "❌ Error while reading the PDF."
            )

            st.code(str(e))


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

    if st.button(
        "Generate Study Plan 🚀",
        type="primary"
    ):

        if not subject.strip():

            st.warning(
                "⚠️ Please enter the subject."
            )

        elif not topics.strip():

            st.warning(
                "⚠️ Please enter the topics."
            )

        else:

            prompt = f"""
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

            with st.spinner(
                "🤖 Creating your personalized study plan..."
            ):

                answer, error = (
                    generate_ai_response(prompt)
                )

            show_ai_result(
                "Your Personalized Study Plan",
                answer,
                error
            )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "🤖 AI Study-Buddy Learning Assistant | "
    "Python + Streamlit + Gemini"
)