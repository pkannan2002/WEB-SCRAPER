import streamlit as st
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

def split_into_batches(text, batch_size=6000):
    """Split text into batches while preserving sentence integrity."""
    batches = []
    current_pos = 0
    
    while current_pos < len(text):
        # If this is not the first batch, overlap with previous batch to maintain context
        if current_pos > 0:
            # Back up a bit to maintain context
            current_pos = max(0, current_pos - 200)
            
        end_pos = min(current_pos + batch_size, len(text))
        
        # Try to end at a sentence boundary
        if end_pos < len(text):
            # Look for the last period within reasonable distance
            last_period = text.rfind('. ', current_pos, end_pos)
            if last_period != -1:
                end_pos = last_period + 1
        
        batch = text[current_pos:end_pos]
        batches.append(batch)
        current_pos = end_pos
        
    return batches

def report_response(scraped_content, description):
    """Process content in batches while maintaining context."""
    print("Entered into model")
    
    # Split content into batches
    batches = split_into_batches(scraped_content)
    accumulated_knowledge = ""
    final_response = ""
    KEYSML = st.secrets["GROQ_API_KEY"]
    st.write("Loaded Key:", KEYSML[:4] + "****")  # Masked for security

    if not KEYSML:
        st.error("API key not found in environment variables!")
        return "Error: API key not configured"
    
    client = Groq(
        api_key=KEYSML
    )
    
    try:
        # Process each batch while maintaining context
        for i, batch in enumerate(batches):
            is_first_batch = i == 0
            is_last_batch = i == len(batches) - 1
            
            with st.spinner(f"Processing batch {i + 1} of {len(batches)}..."):
                if is_first_batch:
                    prompt = f"""Please review and analyze the following content extracted from a webpage (part {i+1} of {len(batches)}). 
                    Before proceeding, kindly correct any spelling or typographical errors in the text:

                    {batch}

                    Please focus on the following request: {description}.
                    If this part does not contain relevant information, kindly summarize the key points concisely, without adding any extra details."""


                else:
                    prompt = f"""You are analyzing additional content (part {i+1} of {len(batches)}), 
                    considering the previously analyzed content. Please correct any spelling or typographical errors before analyzing:

                    Previously gathered information:
                    {accumulated_knowledge}

                    New content to analyze:
                    {batch}

                    Continue with the analysis for the original request: {description}.
                    If this part does not contain relevant information, please provide a brief summary of the key points, without introducing new information."""


                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    model="llama-3.3-70b-versatile",
                    stream=False,
                )
                batch_response = chat_completion.choices[0].message.content
            
            # Accumulate key information for context
            accumulated_knowledge += f"\nKey points from part {i+1}: {batch_response}\n"
            
            if is_last_batch:
                final_prompt = f"""You have now analyzed all parts of the content. Below is the cumulative knowledge:

                {accumulated_knowledge}

                Before providing the final response, ensure any spelling or typographical errors are corrected in the content.

                Please provide a final, coherent response to the original request: {description}.
                Ensure you combine all relevant information from all parts into a unified, concise response.

                Rules:
                1. Be concise and match the requested format strictly.
                2. Only include information directly extracted from the webpage—do not add new content.
                3. If the description asks for a summary, ensure it is clear, easy to understand, and formatted accordingly.
                4. Do not introduce any additional content not present in the original information.

                Example format:
                The content relevant to the request is:
                (Extracted content with no additional information)
                My summary for clarity is:
                (Summary of the content, aligned with the requested format)"""

                
                final_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": final_prompt,
                        }
                    ],
                    model="llama-3.3-70b-versatile",
                    stream=False,
                )
                
                final_response = final_completion.choices[0].message.content
        
        return final_response
    
    except Exception as e:
        print(f"Error processing with LLM: {e}")
        st.error(f"An error occurred: {e}")
        return "Sorry, there was an error processing your request."
