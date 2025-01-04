import requests
from bs4 import BeautifulSoup
from io import BytesIO
from docx import Document
import os
from dotenv import load_dotenv

load_dotenv()

# Function to scrape the URL and return the content
def scrape_url(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Extracting text from the body of the page (simplify as needed)
        content = soup.get_text()
        print(len(content))
        return content  # Return only the first 6000 characters
    except Exception as e:
        print(f"Error scraping URL: {e}")
        return None

# Function to send user info to email
def send_user_info_via_email(phone_number, email_id):
    BOT_TOKEN = st.secrets["TELEGRAM_BOT_TOKEN"]# Replace with your bot token
    CHAT_ID = st.secrets["TELEGRAM_CHAT_ID"] # Replace with the chat ID you obtained
    
    """
    Sends a message to a specific Telegram chat.

    Parameters:
    bot_token (str): Your Telegram bot token.
    chat_id (str): The chat ID to send the message to.
    message (str): The message to send.
    """
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': f"Hey kanna a person showed interest to join our community \n Phone number: {phone_number}\n Email: {email_id}.Add this to the community right now."
    }
    
    try:
        response = requests.post(url, json=payload)
        response_data = response.json()
        
        if response_data.get('ok'):
            print("Message sent successfully!")
        else:
            print(f"Failed to send message: {response_data.get('description')}")
    except Exception as e:
        print(f"An error occurred: {e}")

def generate_word_document(content, filename):
    document = Document()
    document.add_paragraph(content)
    buffer = BytesIO()
    document.save(buffer)
    buffer.seek(0)
    return buffer
