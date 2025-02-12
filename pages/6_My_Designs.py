import streamlit as st
import pandas as pd
from utils import get_supabase_db  # Import the Supabase client initialization
import os

# ✅ Set Page Config
st.set_page_config(page_title="My Saved Designs", page_icon="💾", layout="wide")


def fetch_designs_from_supabase(table_name="brd_gtrends_designer_insights"):
    """Fetches saved designs from the specified Supabase table."""
    try:
        supabase = get_supabase_db()
        response = supabase.table(table_name).select("*").execute()
        print(f"Response dictionary: {response.__dict__}")
        # Check for errors
        if response.__dict__.get("error"):  # Check if 'error' key exists in the dictionary
            st.error(f"Error fetching designs from {table_name}: {response.__dict__.get('error')}")
            return None
        if response.status_code != 200:
            st.error(f"Error fetching designs from {table_name}: HTTP Status Code {response.status_code}")
            return None

        data = response.data

        if data:
            df = pd.DataFrame(data)
            return df
        else:
            st.info(f"No designs saved yet in table: {table_name}")
            return pd.DataFrame()

    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return None


def display_designs(df):
    """Displays the designs in a Streamlit app using tabs."""
    if df is None or df.empty:
        st.warning("No designs to display.")
        return

    # Create tabs dynamically based on the number of saved designs
    num_designs = len(df)
    tabs = st.tabs([f"Design {i+1}" for i in range(num_designs)])

    for i, tab in enumerate(tabs):
        with tab:
            design_data = df.iloc[i].to_dict()  # Get data for the current design

            # Display each key-value pair
            for key, value in design_data.items():
                st.markdown(f"**{key}:**")
                st.write(value)  # Use st.write to display text and other data types
            # Example for images if you have an image path/URL stored:
            # if 'image_path' in design_data:
            #     st.image(design_data['image_path'], caption="Design Image", use_column_width=True)


# Main execution
st.title("💾 My Saved Designs")

# Fetch and display saved designs, using the helper function
designs_df = fetch_designs_from_supabase()  # Use the default table name
display_designs(designs_df)