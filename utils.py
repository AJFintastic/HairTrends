import os
from dotenv import load_dotenv
import google.generativeai as genai
from gradio_client import Client
import requests
import streamlit as st
from supabase import create_client

# Load environment variables from .env file
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# ✅ Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@st.cache_resource
def get_supabase_db() -> Client:
    """Initializes and returns a Supabase client."""
    url: str = os.environ.get("SUPABASE_URL") or st.secrets["SUPABASE_URL"]
    key: str = os.environ.get("SUPABASE_KEY") or  st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

# Configure the Gemini API key (ensure GEMINI_API_KEY exists in your .env file)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash')

def get_gemini_response(prompt, design_name, target_demographic, category, trend, special_requests=""):
    """Generate design insights using Gemini."""
    trend_context = {
        "Natural Ingredients": "Focus on organic and eco-friendly formulations",
        "Sustainable Packaging": "Highlight recyclable and biodegradable materials",
        "Bold Colors": "Emphasize vibrant and trendy color options",
        "Heat Protection": "Incorporate heat-resistant and damage-prevention features",
        "Scalp Care": "Prioritize scalp health and hydration",
        "Gender-Neutral Products": "Design for inclusivity and versatility"
    }.get(trend, "")
    
    full_prompt = f"""As a hair product designer for Godrej, create insights for {design_name} targeting {target_demographic}:
{trend_context}
Special Requests: {special_requests}
Focus on:
- Product formulation and ingredients
- Packaging design and sustainability
- Marketing and branding strategies
{prompt}"""
    try:
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"Error generating insights: {str(e)}"



# ✅ Load the Gemini model
# model = genai.GenerativeModel("gemini-pro")

def get_gemini_insight(context, dataset_summary):
    """
    Generate AI insights for Google Trends analysis.
    
    Parameters:
    - context: A short description of the dataset (e.g., "Top trending braid styles").
    - dataset_summary: Key information (e.g., top 3 peak times, highest search interest).
    
    Returns:
    - A short and insightful AI-generated insight.
    """
    
    prompt = f"""
    Provide a short, data-driven insight based on Google Trends data.
    
    Context: {context}
    Dataset Summary: {dataset_summary}
    
    Keep it concise (a few sentences and under 200 words) and insightful.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"⚠️ Error generating insights: {str(e)}"





def generate_image(prompt_text):
    """Generate an image using the image generation API via Gradio Client."""
    try:
        client = Client("LLMhacker/Realtime-FLUX-Modified-Flux.Schnell-for-JA.P")
        result = client.predict(
            prompt=prompt_text,
            seed=42,
            width=1024,
            height=1024,
            api_name="/generate_image"
        )
        return result
    except Exception as e:
        return None

def fetch_google_trends_data(keywords, start_time, end_time, geo=""):
    """
    Fetches Google Trends data using the provided parameters.
    """
    # Construct the request payload
    url = "https://trends.google.com/trends/api/widgetdata/multiline"
    params = {
        "hl": "en-GB",
        "tz": "-120",
        "req": {
            "time": f"{start_time} {end_time}",
            "resolution": "EIGHT_MINUTE",
            "locale": "en-GB",
            "comparisonItem": [
                {
                    "geo": {"country": geo} if geo else {},
                    "complexKeywordsRestriction": {
                        "keyword": [{"type": "BROAD", "value": keyword.strip()} for keyword in keywords.split(",")]
                    }
                }
            ],
            "requestOptions": {"property": "", "backend": "CM", "category": 146},
            "userConfig": {"userType": "USER_TYPE_LEGIT_USER"},
        },
        "token": "APP6_UEAAAAAZ6Hj7x8eBzGqYkg6FHp6gSFeZVkcC-73",
        "tz": "-120",
    }

    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "referer": "https://trends.google.com/trends/explore?cat=146&date=now%201-d&q=braids&hl=en-GB",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    }

    try:
        # Send the request
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}



# ✅ Function to save insights to Supabase
def save_to_designer(insight_text):
    """Save selected insights to the designer table in Supabase."""
    if "saved_insights" not in st.session_state:
        st.session_state.saved_insights = []  # Initialize if not already in session state

    if insight_text not in st.session_state.saved_insights:
        st.session_state.saved_insights.append(insight_text)  # Add to session state list

        # ✅ Save to Supabase
        try:
            supabase.table("brd_gtrends_designer_insights").insert({"insight": insight_text}).execute()
            st.success("✅ Insight added to Designer successfully!")
        except Exception as e:
            st.error(f"Error saving to designer: {e}")
            

def save_to_mydesigns(design_name: str, image_url: str, description: str, selected_insights: list, image_prompt: str) -> bool:
    """
    Saves braid design details to the brd_design table in Supabase.

    Args:
        design_name: The name of the braid design.
        image_url: The URL of the generated image in Supabase Storage.
        description: A description of the braid style.
        selected_insights: A list of insights incorporated into the design.
        image_prompt: The prompt used to generate the image.

    Returns:
        True if the save was successful, False otherwise.
    """
    try:
        # Construct the data payload for the Supabase insert
        data = {
            "design_name": design_name,
            "image_url": image_url,
            "description": description,
            "selected_insights": selected_insights,  # Assuming Supabase can handle lists directly
            "image_prompt": image_prompt,
        }

        # Insert the data into the brd_design table
        result = supabase.table("brd_design").insert(data).execute()

        # Check for errors in the Supabase response
        if result.error:
            st.error(f"Supabase insert error: {result.error}")  # Display error in Streamlit
            return False

        # If the insert was successful
        st.success("✅ Braid design saved to My Designs successfully!") #Display success
        return True

    except Exception as e:
        st.error(f"An error occurred while saving to My Designs: {e}") #Display Error
        return False

    
    
# ✅ Function to create an AI Insight section with a button
def display_ai_insight(insight_text, title):
    """Display AI insights with a button to save to designer."""
    col1, col2 = st.columns([5, 1])  # Adjust layout for button placement

    with col1:
        st.info(insight_text)  # Display the AI-generated insight

    with col2:
        tooltip = "Add this insight to the designer for later use"
        if st.button(f"➕", help=tooltip, key=f"btn_{title}"):  # Unique key per button
            save_to_designer(insight_text)  # Save to DB when clicked

