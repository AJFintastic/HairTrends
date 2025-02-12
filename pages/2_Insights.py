import streamlit as st
# **🌟 Page Configuration**
st.set_page_config(page_title="Google Trends Insights", page_icon="📊", layout="wide")
import pandas as pd
import plotly.express as px
from supabase import create_client
import os
from dotenv import load_dotenv
import re
from utils import get_gemini_insight

# ✅ Load environment variables from .env
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# ✅ Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# **🔄 Load Data from Supabase**
@st.cache_data
def fetch_data(table_name):
    """Fetch data from Supabase and clean the country column"""
    try:
        response = supabase.table(table_name).select("*").execute()
        df = pd.DataFrame(response.data)

        # **Fix country format for relatedqueries & relatedentities**
        if "country" in df.columns:
            df["country"] = df["country"].astype(str).apply(lambda x: re.sub(r'^.*?,\s*', '', x) if "," in x else x)

        return df
    except Exception as e:
        st.error(f"Error fetching {table_name}: {e}")
        return pd.DataFrame()

# **📊 Load Google Trends Data**
geo_map_df = fetch_data("brd_gtrends_geomap")
multi_timeline_df = fetch_data("brd_gtrends_multitimeline")
related_queries_df = fetch_data("brd_gtrends_relatedqueries")
related_entities_df = fetch_data("brd_gtrends_relatedentities")

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


# **📍 Page Header**
st.markdown("""
    <h1 style='text-align: center; color: #4F46E5;'>📊 Google Trends Insights</h1>
    <p style='text-align: center;'>Get real-time insights on trending hairstyles, colors, and searches.</p>
""", unsafe_allow_html=True)

st.write("---")

### **🔍 Filters for Analysis**
st.markdown("### 🎯 Customize Insights")

col_f1, col_f2, col_f3 = st.columns(3)

# **🌍 Select Region**
with col_f1:
    region_option = st.selectbox(
        "🌍 Select a Region",
        options=["Worldwide", "US", "Africa", "Middle East", "Southern Africa"],
        index=0
    )

# **📅 Select Timeframe**
with col_f2:
    timeframe_option = st.selectbox(
        "⏳ Select a Timeframe",
        options=[
            "Past hour", "Past 4 hours", "Past day",
            "Past 7 days", "Past 30 days", "Past 90 days",
            "Past 12 months", "Past 5 years"
        ],
        index=2
    )

# **🔍 Select Keyword**
with col_f3:
    selected_keyword = st.selectbox(
        "📌 Select a Keyword",
        multi_timeline_df["keyword"].unique() if not multi_timeline_df.empty else ["No Data"]
    )

st.write("---")

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🔥 Key Insights & Search Trends",
    "🌍 Interest by Region",
    "🔍 Search Insights Breakdown",
    "🎨 Designer Insights"
])

# Tab 1: Key Insights & Search Trends
with tab1:
    # **📊 Key Metrics Overview**
    st.markdown("### 🔥 Key Insights")
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)

    # **📍 Peak Search Time**
    if not multi_timeline_df.empty:
        peak_time = multi_timeline_df.loc[multi_timeline_df["interest"].idxmax(), "time"]
        col_m1.markdown(f"""
            <div style="text-align: center; background-color: #f8f9fa; padding: 10px; border-radius: 8px; border: 1px solid #ddd;">
                <h5 style="margin-bottom: 5px;">📍 Peak Search Time</h5>
                <p style="font-size: 25.5px; font-weight: bold; color: #4F46E5;">{peak_time}</p>
            </div>
        """, unsafe_allow_html=True)

    # **📊 Average Interest**
    if not multi_timeline_df.empty:
        avg_interest = int(multi_timeline_df["interest"].mean())
        col_m2.markdown(f"""
            <div style="text-align: center; background-color: #f8f9fa; padding: 10px; border-radius: 8px; border: 1px solid #ddd;">
                <h5 style="margin-bottom: 5px;">📊 Average Interest</h5>
                <p style="font-size: 25.5px; font-weight: bold; color: #4F46E5;">{avg_interest}</p>
            </div>
        """, unsafe_allow_html=True)

    # **🚀 Top Rising Related Search Term**
    if not related_queries_df.empty:
        top_rising_query = related_queries_df.loc[related_queries_df["searchfreqinc"].idxmax(), "relatedquery"]
        col_m3.markdown(f"""
            <div style="text-align: center; background-color: #f8f9fa; padding: 10px; border-radius: 8px; border: 1px solid #ddd;">
                <h5 style="margin-bottom: 5px;">🚀 Top Rising Related Search</h5>
                <p style="font-size: 25.5px; font-weight: bold; color: #4F46E5;">{top_rising_query}</p>
            </div>
        """, unsafe_allow_html=True)

    # **🔥 Top Rising Related Query**
    if not related_entities_df.empty:
        top_rising_entity = related_entities_df.loc[related_entities_df["searchfreqinc"].idxmax(), "relatedtopic"]
        col_m4.markdown(f"""
            <div style="text-align: center; background-color: #f8f9fa; padding: 10px; border-radius: 8px; border: 1px solid #ddd;">
                <h5 style="margin-bottom: 5px;">🔥 Top Rising Related Query</h5>
                <p style="font-size: 25.5px; font-weight: bold; color: #4F46E5;">{top_rising_entity}</p>
            </div>
        """, unsafe_allow_html=True)

    st.write("---")
    
    ### **📈 Search Trends Over Time (Line Chart & Table Side by Side)**
    if not multi_timeline_df.empty:
        st.markdown("### 📈 Search Trends Over Time")

        col_chart, col_table = st.columns([2, 1])

        with col_chart:
            filtered_df = multi_timeline_df[multi_timeline_df["keyword"] == selected_keyword]
            fig = px.line(
                filtered_df,
                x="date",
                y="interest",
                color="keyword",
                title=f"Search Interest for {selected_keyword} Over Time",
                line_shape="spline",
                labels={"interest": "Search Interest", "date": "Date"},
            )
            st.plotly_chart(fig, use_container_width=True)

    with col_table:
        st.markdown("### ⏳ Highest Interest Times")

        # Select top 10 highest interest times
        highest_interest_df = filtered_df.nlargest(10, "interest")[["time", "interest"]]

        # Normalize interest values for visual representation
        max_interest = highest_interest_df["interest"].max()
        scale_length = 20  # Adjust scale for trend bars

        def get_trend_bar(value):
            """Create a compact trend bar for visualization"""
            clamped = min(value, max_interest)
            bar_len = int(round((clamped / max_interest) * scale_length))
            return "█" * bar_len

        # Apply bar visualization
        highest_interest_df["Trend"] = highest_interest_df["interest"].apply(get_trend_bar)

        # Combine trend bar and value in one column
        highest_interest_df["Search Interest"] = highest_interest_df.apply(
            lambda row: f"{row['Trend']} {row['interest']}", axis=1
        )

        # Keep only necessary columns and rename
        highest_interest_df = highest_interest_df[["time", "Search Interest"]].rename(columns={"time": "Time"})

        # Display updated table
        st.dataframe(highest_interest_df, use_container_width=True, height=388, hide_index=True)

    st.write("---")
    
    # **📍 Top 3 Peak Search Times**
    if not multi_timeline_df.empty:
        top_peak_times_df = multi_timeline_df.nlargest(3, "interest")[["time", "interest"]]
        top_peak_times = ", ".join(top_peak_times_df["time"].astype(str).tolist())

        # ✅ AI-Generated Insight for Peak Times
        insight_peak_times = get_gemini_insight(
            "Top 3 Peak Search Times",
            f"The highest search activity occurred at **{top_peak_times}**."
        )

        # Layout to spread across the page (button next to insight)
        col_peak1, col_peak2 = st.columns([5, 1])

        with col_peak1:
            st.info(insight_peak_times)  # ✅ Display AI-generated insight

        with col_peak2:
            tooltip = "Add this insight to the designer for later use"
            if st.button("➕", help=tooltip, key="btn_Peak_Search_Times"):  # Unique key
                save_to_designer(insight_peak_times)  # Save to DB when clicked

    st.write("---")

# Tab 2: Interest by Region
with tab2:
    ### **🌍 Heatmap: Search Interest by Country**
    if not geo_map_df.empty:
        st.markdown("### 🌍 Interest by Region")

        col_map, col_table = st.columns([2, 1])

        with col_map:
            fig = px.choropleth(
                geo_map_df,
                locations="region/state",
                locationmode='USA-states',       #"country names",
                color="interest",
                title="Search Interest by Region",
                color_continuous_scale="Blues",
            )
            st.plotly_chart(fig, use_container_width=True)

        with col_table:
            st.markdown("### 📌 Top Interest by Region")

            # Select top 10 countries with highest interest
            top_countries_df = geo_map_df.nlargest(10, "interest")[["region/state", "interest"]]

            # Normalize interest values for visualization
            max_interest = top_countries_df["interest"].max()
            scale_length = 20  # Adjust scale for trend bars

            def get_trend_bar(value):
                """Create a compact trend bar for visualization"""
                clamped = min(value, max_interest)
                bar_len = int(round((clamped / max_interest) * scale_length))
                return "█" * bar_len

            # Apply trend visualization
            top_countries_df["Trend"] = top_countries_df["interest"].apply(get_trend_bar)

            # Combine trend bar and value into one column
            top_countries_df["Search Interest"] = top_countries_df.apply(
                lambda row: f"{row['Trend']} {row['interest']}", axis=1
            )

            # Keep only necessary columns and rename
            top_countries_df = top_countries_df[["region/state", "Search Interest"]].rename(columns={"region/state": "Region/State"})

            # Display updated table
            st.dataframe(top_countries_df, use_container_width=True, height=388, hide_index=True)
    # **🏆 Top Interest by Region/State**
    if not geo_map_df.empty:
        top_countries_df = geo_map_df.nlargest(10, "interest")[["region/state", "interest"]]

    # **🏆 Top Interest by Region/State**
    if not top_countries_df.empty:
        top_region = top_countries_df.iloc[0]["region/state"]
        insight_region = get_gemini_insight(
            "Top Interest by Region/State",
            f"The region with the highest search interest is **{top_region}**."
        )

        display_ai_insight(insight_region, "Top_Region")

    st.write("---")

# Tab 3: Search Insights Breakdown
with tab3:
    # ✅ Function to Create Dataframe with Search Interest Bar + Sorting
    def create_df_with_bar(df, query_col, value_col):
        if df is None or df.empty:
            return pd.DataFrame()

        # Keep only necessary columns
        new_df = df[[query_col, value_col]].copy()

        # Convert to numeric and fill missing values
        new_df[value_col] = pd.to_numeric(new_df[value_col], errors='coerce').fillna(0)

        # **Sort in Descending Order**
        new_df = new_df.sort_values(by=value_col, ascending=False)

        # Create visual bar column
        max_for_bar = 100
        scale_length = 20  # Controls bar length

        def get_bar(v):
            clamped = min(v, max_for_bar)
            bar_len = int(round((clamped / max_for_bar) * scale_length))
            return '█' * bar_len

        new_df["Search Interest"] = new_df.apply(lambda row: f"{row[value_col]} {get_bar(row[value_col])}", axis=1)

        # Rename columns
        new_df = new_df.rename(columns={query_col: "Keyword"})

        # Keep only relevant columns (removes original numeric column)
        new_df = new_df[["Keyword", "Search Interest"]]

        return new_df

    # **📊 Display Four Wider Tables in 2 Rows with Sorted Data**
    st.markdown("### 🔍 Search Insights Breakdown")

    # **Row 1: Top Queries & Rising Queries**
    col_t1, col_t2 = st.columns([3, 3])  # Wider layout

    with col_t1:
        st.subheader("🔝 Top Queries")
        top_queries_df = related_queries_df[related_queries_df["category"] == "TOP"]

        if not top_queries_df.empty:
            st.dataframe(create_df_with_bar(top_queries_df, "relatedquery", "interest"), hide_index=True, use_container_width=True)

            # ✅ AI Insight with "Add to Designer" button
            top_query = top_queries_df.nlargest(1, "interest")["relatedquery"].values[0]
            insight_top_query = get_gemini_insight(
                "Top Searched Queries",
                f"The most searched query is **{top_query}**, reflecting high interest in this topic."
            )
            display_ai_insight(insight_top_query, "Top_Query")

    with col_t2:
        st.subheader("🚀 Rising Queries")
        rising_queries_df = related_queries_df[related_queries_df["category"] == "RISING"]

        if not rising_queries_df.empty:
            st.dataframe(create_df_with_bar(rising_queries_df, "relatedquery", "searchfreqinc"), hide_index=True, use_container_width=True)

            # ✅ AI Insight with "Add to Designer" button
            fastest_rising_query = rising_queries_df.nlargest(1, "searchfreqinc")["relatedquery"].values[0]
            insight_rising_query = get_gemini_insight(
                "Fastest Growing Queries",
                f"The fastest-growing search term is **{fastest_rising_query}**, showing a recent surge in interest."
            )
            display_ai_insight(insight_rising_query, "Rising_Query")

    st.write("---")

    # **Row 2: Top Related Topics & Fastest Growing Topics**
    col_t3, col_t4 = st.columns([3, 3])  # Wider layout

    with col_t3:
        st.subheader("🏆 Top Related Topics")
        top_topics_df = related_entities_df[related_entities_df["category"] == "TOP"]

        if not top_topics_df.empty:
            st.dataframe(create_df_with_bar(top_topics_df, "relatedtopic", "interest"), hide_index=True, use_container_width=True)

            # ✅ AI Insight with "Add to Designer" button
            top_related_topic = top_topics_df.nlargest(1, "interest")["relatedtopic"].values[0]
            insight_top_topic = get_gemini_insight(
                "Top Related Topics",
                f"The most associated topic is **{top_related_topic}**, indicating strong relevance to the main search trends."
            )
            display_ai_insight(insight_top_topic, "Top_Topic")

    with col_t4:
        st.subheader("📈 Fastest Growing Topics")
        rising_topics_df = related_entities_df[related_entities_df["category"] == "RISING"]

        if not rising_topics_df.empty:
            st.dataframe(create_df_with_bar(rising_topics_df, "relatedtopic", "searchfreqinc"), hide_index=True, use_container_width=True)

            # ✅ AI Insight with "Add to Designer" button
            fastest_growing_topic = rising_topics_df.nlargest(1, "searchfreqinc")["relatedtopic"].values[0]
            insight_rising_topic = get_gemini_insight(
                "Fastest Growing Topics",
                f"The fastest-growing topic is **{fastest_growing_topic}**, showing a sharp increase in search volume."
            )
            display_ai_insight(insight_rising_topic, "Rising_Topic")

    st.write("---")

# Tab 4: Designer Insights
with tab4:
    # ✅ **Show Saved Insights**
    st.markdown("## 🎨 Designer Insights")
    if "saved_insights" in st.session_state and st.session_state.saved_insights:
        for saved_insight in st.session_state.saved_insights:
            st.success(f"📌 {saved_insight}")
    else:
        st.info("No insights saved yet. Click **➕** next to an AI insight to add it.")

    st.write("---")

st.write("---")
st.markdown("<p style='text-align: center;'>🚀 Use these insights to create AI-powered hairstyles & marketing plans!</p>", unsafe_allow_html=True)