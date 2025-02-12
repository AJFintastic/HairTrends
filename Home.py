import streamlit as st
from streamlit_lottie import st_lottie
import json

# ✅ Set page config FIRST
st.set_page_config(page_title="NeuraWeave", page_icon="💠", layout="wide")


# Initialize session state variables
if "show_specific_features" not in st.session_state:
    st.session_state.show_specific_features = False

# Load Lottie animation (for visual appeal)
def load_lottie(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)

# Header & Branding
st.markdown(
    """
    <h1 style='text-align: center; color: #4F46E5;'>
        Fintastic AI
    </h1>

    <h2 style='text-align: center; color: #7B1113;'>
            Design Studio
    </h2>
        <h2 style='text-align: center; color: #4F46E5;'>
           💡➝🖌️➝🎨➝🤖➝🖼️
    </h2>

    
    <p style='text-align: center; font-size:18px;'>
        Your one-stop AI-powered platform for hair trends, hairstyle generation, cost estimation, and marketing insights.
    </p>
    """,
    unsafe_allow_html=True
)
st.write("---")

# 🎬 **Feature Overview (Step-by-Step Process)**
st.markdown("<h2 style='text-align: center; color: #4F46E5'>🚀 Explore Our Features</h2>", unsafe_allow_html=True)
st.write("")
# Columns for Feature Highlights
col1, col2, col3 = st.columns(3)

with col1:
    # st.image("assets/ai_insights.png", width=200)  # Removed image
    st.markdown("<h3 style='color: #7B1113;'>AI Insights & Trends</h3>", unsafe_allow_html=True)  # Changed to colored heading
    st.write(
        "- Discover the latest hair trends\n"
        "- Google Trends analysis\n"
        "- Competitor insights\n"
    )
    if st.button("🔍 Explore Insights"):
        st.switch_page("pages/2_Insights.py")

with col2:
    # st.image("assets/ai_hair.png", width=200)  # Removed image
    st.markdown("<h3 style='color: #7B1113;'>AI Hairstyle Generator</h3>", unsafe_allow_html=True)  # Changed to colored heading
    st.write(
        "- Upload a reference image or use AI-generated styles\n"
        "- Customize by length, texture, and color\n"
        "- See realistic hair visuals"
    )
    if st.button("🎨 Create Hairstyle"):
        st.switch_page("pages/5_Generate_Styles.py")

with col3:
    # st.image("assets/ai_calc.png", width=200)  # Removed image
    st.markdown("<h3 style='color: #7B1113;'>Analyse Competitors</h3>", unsafe_allow_html=True)  # Changed to colored heading
    st.write(
        "- Browse competitor products\n"
        "- Conduct head to head analysis\n"
        "- Get the edge on the competition"
    )
    if st.button("⚔️ Analyse Competitors"):
        st.switch_page("pages/3_Competitor_Analysis.py")

st.write("---")

# Footer
st.markdown(
    "<p style='text-align: center;'> ⚡ Powered by Fintastic AI ⚡ </p>",
    unsafe_allow_html=True
)