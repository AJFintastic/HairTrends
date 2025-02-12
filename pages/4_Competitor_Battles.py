import streamlit as st
import pandas as pd
import os
import plotly.express as px
from utils import get_gemini_insight, save_to_designer
from fpdf import FPDF  # ✅ PDF Export

# ✅ Set Page Configuration
st.set_page_config(page_title="Competitor Battles", page_icon="⚔️", layout="wide")

# ✅ **📍 Page Introduction**
st.markdown("""
# ⚔️ **Competitor Battles: Brand vs. Brand**
Compare top hair brands like **Outre, Darling, and Sensationnel** head-to-head!  
Choose two brands below and click **Compare** to see a **side-by-side** analysis, AI-generated insights, and key differentiators.
""")
st.write("---")

# ✅ **Persist State in Session**
if "competitor_1" not in st.session_state:
    st.session_state.competitor_1 = "Outre"
if "competitor_2" not in st.session_state:
    st.session_state.competitor_2 = "Darling"
if "show_comparison" not in st.session_state:
    st.session_state.show_comparison = False

# ✅ **Competitor Options**
competitor_options = {
    "Outre": {
        "name": "Outre",
        "description": "A premium hair brand specializing in synthetic & human hair braids, wigs, and extensions.",
        "strengths": ["High-Quality Fibers", "Trend-Driven Styles", "Strong Social Media Presence"],
        "image": "assets/outre_logo.png"
    },
    "Darling": {
        "name": "Darling",
        "description": "A mass-market synthetic hair brand focusing on affordability and accessibility in emerging markets.",
        "strengths": ["Budget-Friendly", "High Availability in Africa", "Everyday Wear"],
        "image": "assets/darling_logo.png"
    },
    "Sensationnel": {
        "name": "Sensationnel",
        "description": "A well-established hair brand known for premium wigs, weaves, and braided hair extensions.",
        "strengths": ["Lace Wig Innovations", "Luxury Hair Blends", "Diverse Hair Textures"],
        "image": "assets/sensationnel_logo.png"
    },
    "X-Pression": {
        "name": "X-Pression",
        "description": "A brand known for ultra-lightweight synthetic braiding hair with superior volume.",
        "strengths": ["Ultra-Light Fibers", "Long-Length Braids", "Popular in Professional Styling"],
        "image": "assets/xpression_logo.png"
    }
}

# ✅ **Dropdowns to Select Two Competitors**
col1, col2 = st.columns(2)
with col1:
    st.session_state.competitor_1 = st.selectbox(
        "🔍 Choose First Competitor",
        list(competitor_options.keys()),
        index=list(competitor_options.keys()).index(st.session_state.competitor_1)
    )
with col2:
    st.session_state.competitor_2 = st.selectbox(
        "🔍 Choose Second Competitor",
        list(competitor_options.keys()),
        index=list(competitor_options.keys()).index(st.session_state.competitor_2)
    )

st.write("---")

# ✅ **Compare Button**
if st.button("🚀 Compare Competitors"):
    st.session_state.show_comparison = True  # ✅ Store this in session state

# ✅ **Only Show Comparison After Button Click**
if st.session_state.show_comparison:

    # ✅ **Create Tabs**
    strengths_tab, feature_comparison_tab, ai_insights_tab, designer_tab = st.tabs(
        ["💪 Strengths", "📊 Feature Comparison", "🤖 AI Insights", "🎨 Designer Insights"]
    )

    with strengths_tab:
        # ✅ **Display Competitor Information Side-by-Side**
        col_comp1, col_vs, col_comp2 = st.columns([3, 1, 3])

        with col_comp1:
            st.image(competitor_options[st.session_state.competitor_1]["image"], width=150)  # ✅ Set width
            st.markdown(f"### 🏆 {st.session_state.competitor_1}")
            st.write(competitor_options[st.session_state.competitor_1]["description"])
            st.write("🔹 **Strengths:**")
            for strength in competitor_options[st.session_state.competitor_1]["strengths"]:
                st.write(f"- ✅ {strength}")

        with col_vs:
            st.markdown("<h2 style='text-align: center;'>VS</h2>", unsafe_allow_html=True)

        with col_comp2:
            st.image(competitor_options[st.session_state.competitor_2]["image"], width=150)  # ✅ Set width
            st.markdown(f"### 🏆 {st.session_state.competitor_2}")
            st.write(competitor_options[st.session_state.competitor_2]["description"])
            st.write("🔹 **Strengths:**")
            for strength in competitor_options[st.session_state.competitor_2]["strengths"]:
                st.write(f"- ✅ {strength}")

        st.write("---")

    with feature_comparison_tab:
        # ✅ **Feature-by-Feature Comparison**
        st.markdown("### 📊 Feature Comparison")
        df_comparison = pd.DataFrame({
            "Feature": [
                "Product Type", "Target Market", "Price Range", "Color Variety",
                "Durability", "Innovative Features", "Social Media Presence", "Retail Presence"
            ],
            st.session_state.competitor_1: [
                "Synthetic & Human Hair Braids", "Global (U.S., Africa, EU)", "💰 Mid-High",
                "🌈 Extensive (Ombré, Balayage, Bright Colors)", "🔥 Long-Lasting Fibers",
                "✅ Pre-Stretched, HD Lace, Melted Hairline", "📢 High (Influencers, Ads)", "🌍 Strong Online & Offline"
            ],
            st.session_state.competitor_2: [
                "Synthetic Braids", "Africa & Emerging Markets", "💵 Budget-Friendly",
                "🎨 Basic Shades (Natural Black, Brown)", "🔄 Moderate Durability",
                "❌ Limited Innovations", "📉 Low (Minimal Digital Ads)", "🏬 Beauty Supply Stores"
            ]
        })
        st.dataframe(df_comparison, use_container_width=True, hide_index=True)

        st.write("---")

    with ai_insights_tab:
        # ✅ **🔥 AI-Generated Competitive Insights**
        st.markdown("### 🤖 AI-Generated Competitive Insights")

        ai_insight = get_gemini_insight(
            f"{st.session_state.competitor_1} vs. {st.session_state.competitor_2} Hair Market Analysis",
            f"Compare {st.session_state.competitor_1} and {st.session_state.competitor_2} in terms of market strategy, product positioning, pricing, and consumer appeal. Highlight key differentiators."
        )

        col_ai1, col_ai2 = st.columns([5, 1])
        with col_ai1:
            st.info(ai_insight)  # ✅ Display AI-generated insight
        with col_ai2:
            if st.button("➕", help="Add this insight to Designer", key="btn_competitor_ai"):
                save_to_designer(ai_insight)

        st.write("---")

        # ✅ **Export to PDF**  (Move to AI Insights tab)
        if st.button("📄 Export to PDF", key="pdf_button"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 14)
            pdf.cell(200, 10, f"{st.session_state.competitor_1} vs {st.session_state.competitor_2}", ln=True, align="C")
            pdf.set_font("Arial", "", 12)
            pdf.multi_cell(200, 10, ai_insight)
            pdf.output("Competitor_Comparison.pdf")
            st.success("✅ PDF Exported Successfully!")

    with designer_tab:
        # ✅ **🎨 Show Saved Insights**
        st.markdown("## 🎨 Designer Insights")
        if "saved_insights" in st.session_state and st.session_state.saved_insights:
            for saved_insight in st.session_state.saved_insights:
                st.success(f"📌 {saved_insight}")
        else:
            st.info("No insights saved yet. Click **➕** next to an AI insight to add it.")