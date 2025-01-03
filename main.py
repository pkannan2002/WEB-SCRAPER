import base64
import streamlit as st
from helper import generate_word_document, scrape_url, send_user_info_via_email
from llm import report_response

st.set_page_config(page_title="Web Scraper", page_icon="\U0001F50D")

# Initialize all session states
if 'show_form' not in st.session_state:
    st.session_state.show_form = True
if 'scraped_content' not in st.session_state:
    st.session_state.scraped_content = None
if 'has_scraped' not in st.session_state:
    st.session_state.has_scraped = False
if 'current_url' not in st.session_state:
    st.session_state.current_url = None
# Function to handle scraping and store in session state
def reset_scraping_state():
    st.session_state.scraped_content = None
    st.session_state.has_scraped = False
    st.session_state.current_url = None

def handle_scrape(url):
    with st.spinner("Scraping URL..."):
        st.session_state.scraped_content = scrape_url(url)
        st.session_state.has_scraped = True

# Function to get base64-encoded string of an image
def get_image_base64(file_path):
    with open(file_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# Enhanced Header with Gradient and Animation
st.markdown(
    """
    <style>
    .centered-header {
        text-align: center;
        font-family: 'Poppins', sans-serif;
        background: linear-gradient(to right, #6a11cb, #2575fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradient-animation 3s ease infinite;
    }
    @keyframes gradient-animation {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    </style>
    <h1 class="centered-header">Free AI Web Scraper</h1>
    """,
    unsafe_allow_html=True
)



# Show form or URL input based on session state
if st.session_state.show_form:
    st.write("""
    This AI web scraper is designed for web scraping and documentation so that you can have the content by scraping and save your time.
    We are creating an AI-based community where we can discuss and develop more interesting projects.
    You can discuss with like-minded people and gain knowledge from it. If you wish to join the community, fill this with your details.
    """)

    logo_base64 = get_image_base64("linkedIn_PNG32.png")


    # LinkedIn Banner with Styling
    st.markdown(
        f"""
        <style>
        .linkedin-banner {{
            background-color: #f3f4f6;
            padding: 10px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
            border-radius: 8px;
        }}
        .linkedin-logo {{
            width: 40px;
            height: auto;
        }}
        .linkedin-link {{
            text-decoration: none;
            color: #0077b5;
            font-weight: bold;
        }}
        .linkedin-link:hover {{
            text-decoration: underline;
        }}
        </style>
        <div class="linkedin-banner">
            <img src="data:image/png;base64,{logo_base64}" alt="LinkedIn Logo" class="linkedin-logo">
            <a href="https://www.linkedin.com/in/kannan-perumal-ai-developer" target="_blank" class="linkedin-link">
                Connect with me on LinkedIn
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )
   

    with st.form(key='contact_form'):
        phone_number = st.text_input("Phone Number")
        email = st.text_input("Email")
        submit_button = st.form_submit_button(label='Submit')

        if submit_button:
            if phone_number and email:
                send_user_info_via_email(phone_number, email)
                st.session_state.show_form = False
                st.success("You have been added to the community!")
            else:
                st.warning("Please enter both phone number and email.")
    if st.button("Not Interested"):
        st.session_state.show_form = False
else:
    if st.button("Interested"):
        st.session_state.show_form = True

    if not st.session_state.show_form:
        st.header("Enter the URL to scrape:")
        url = st.text_input("URL", key="url_input")
              
      
        if st.button("Scrape"):
            if url:
                handle_scrape(url)
            else:
                st.warning("Please enter a valid URL to scrape.")

        if st.session_state.has_scraped and st.session_state.scraped_content:
            st.text_area("Scraped Content:", st.session_state.scraped_content)
            description = st.text_input("Describe what information you need from the scraped page:")

            if st.button("Process Content"):
                if description:
                    response = report_response(st.session_state.scraped_content, description)
                    st.write(response)
                    col1, col2 = st.columns(2)
                    with col1:
                            st.download_button(
                                "Download as CSV",
                                response,
                                file_name="scraped_data.csv",
                                mime="text/csv"
                            )

                    with col2:
                            word_buffer = generate_word_document(response, "scraped_data.docx")
                            st.download_button(
                                "Download as Word",
                                word_buffer,
                                file_name="scraped_data.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                            )

    else:
        st.warning("Please enter a valid URL to scrape.")
