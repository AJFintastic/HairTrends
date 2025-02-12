import streamlit as st
import pandas as pd
import os
from supabase import create_client
from dotenv import load_dotenv
import plotly.express as px
from utils import display_ai_insight, save_to_designer, get_gemini_insight  # ✅ Import functions
from urllib.parse import urlparse
import re
from PIL import Image

# ✅ Load environment variables from .env
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# ✅ Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ✅ Fetch Outre Product Data
@st.cache_data
def fetch_outre_products():
    """Fetch Outre product data from Supabase."""
    try:
        response = supabase.table("brd_outre_products").select(
            "name, link, modified, date, product_description, category, subcategory, quantity, length, image_url"
        ).execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"⚠️ Error fetching Outre data: {e}")
        return pd.DataFrame()

# ✅ Page Configuration
st.set_page_config(page_title="Competitor Analysis", page_icon="🏆", layout="wide")

st.markdown("<h1 style='text-align: center;'>🏆 Competitor Analysis</h1>", unsafe_allow_html=True)

# ✅ Function to Create Dataframe with Quantity Bar + Sorting
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

    new_df["Quantity"] = new_df.apply(lambda row: f"{row[value_col]} {get_bar(row[value_col])}", axis=1)

    # Rename columns
    new_df = new_df.rename(columns={query_col: "Keyword"})

    # Keep only relevant columns
    new_df = new_df[["Keyword", "Quantity"]]

    return new_df

# ✅ Main App
with st.container():
    # ✅ Competitor Tabs
    outre_tab, sensationnel_tab, xpression_tab = st.tabs(["Outre", "Sensationnel", "X-pression"])

    with outre_tab:
        #Outre tabs, combine all into one tab
        outre_tabs = st.tabs(["Brand Summary", "Filters, Insights, Distribution", "Product Listings"])

        with outre_tabs[0]: # Brand Summary
            st.markdown("<h2 style='text-align: center;'>🔍 Outre Analysis</h2>", unsafe_allow_html=True)

            # ✅ Outre Brand Summary Section
            st.markdown("""
            ### **A leading hair brand offering a variety of synthetic and human hair braiding styles.**  
            🌐 [Visit the official Outre site](https://www.outre.com/)
            """)

            st.markdown("""
            ## 📌 **Outre Brand Summary**  

            ### 📖 **Overview**  
            **Outre** is a leading hair brand known for its **synthetic and human hair braiding styles, wigs, and extensions**.  
            The brand offers a **wide range of high-quality, trendy, and innovative hair solutions**, making it a top choice for hairstylists and consumers alike.  

            ### 📦 **Product Lines & Categories**  
            Outre specializes in multiple hair categories, including:  
            ✅ **Braids** – X-Pression, Lil Looks, Pre-Stretched, Bulk Styles  
            ✅ **Wigs** – Lace Fronts, Full Wigs, HD Lace, Melted Hairline  
            ✅ **Weaves & Extensions** – Human & Synthetic Hair Blends  
            ✅ **Crochet Hair** – Pre-looped, Twist & Loc Styles  

            ### 🚀 **Key Selling Points**  
            ✔ **Affordable yet high-quality** – Competitive pricing without compromising quality  
            ✔ **Wide variety of styles** – Options from **natural looks to bold, trendy colors**  
            ✔ **Heat-resistant & long-lasting fibers** – Many synthetic products can be heat-styled  
            ✔ **Pre-stretched & pre-looped options** – Reduces install time for stylists  
            ✔ **Innovative designs** – Like **Melted Hairline** wigs for seamless blending  

            ### 📊 **Market Position**  
            ✅ **Popular among hairstylists & influencers** – Strong presence on social media & YouTube  
            ✅ **Competes with brands like Sensationnel & Femi Collection** in synthetic hair innovation  
            ✅ **Global brand appeal** – Available in the US, Africa, and international markets  

            ### 📢 **Marketing & Branding Strategies**  
            🔹 **Strong social media campaigns** – Engaging hairstylist content & tutorials  
            🔹 **Influencer & celebrity collaborations** – Drives product awareness & credibility  
            🔹 **Retail & online presence** – Available in beauty supply stores & online platforms  

            ### 💡 **AI Insight: Why Outre Stands Out?**  
            ✔ **Diverse & Trend-Driven Styles** – Keeps up with **global beauty trends**  
            ✔ **Innovative Product Features** – E.g., **HD Lace, Pre-Stretched Braids, Melted Hairline Wigs**  
            ✔ **Accessibility & Affordability** – Appeals to a wide range of customers  
            """)

            st.write("---")

        with outre_tabs[1]: # All other information in Outre
            #Fetch Data
            df = fetch_outre_products()
            if df.empty:
                st.error("⚠️ No data found in Supabase.")
                st.stop()

            #Filters Section
            st.markdown("## 🎯 Filter Products")
            col_f1, col_f2 = st.columns([2, 2])

            with col_f1:
                selected_subcategories = st.multiselect(
                    "📌 Select Subcategories",
                    options=sorted(df["subcategory"].dropna().unique()),
                    default=[]
                )

            with col_f2:
                selected_lengths = st.multiselect(
                    "📏 Select Length",
                    options=sorted(df["length"].dropna().unique()),
                    default=[]
                )

            search_name = st.multiselect(
                "🔍 Search Product Name",
                options=sorted(df["name"].dropna().unique()),
                default=[]
            )

            # Apply Filters
            filtered_df = df.copy()
            if selected_subcategories:
                filtered_df = filtered_df[filtered_df["subcategory"].isin(selected_subcategories)]
            if selected_lengths:
                filtered_df = filtered_df[filtered_df["length"].isin(selected_lengths)]
            # Apply Filter
            if search_name:
                filtered_df = filtered_df[filtered_df["name"].isin(search_name)]

            st.write("---")

            #🔥 Key Competitor Insights
            st.markdown("### 🔥 Key Insights")

            col_m1, col_m2, col_m3, col_m4 = st.columns([3, 3, 3, 1])  # Add extra column for save button

            # 📦 Total Products
            total_products = len(df)
            col_m1.markdown(f"""
                <div style="text-align: center; background-color: #f8f9fa; padding: 12px; border-radius: 8px; border: 1px solid #ddd;">
                    <h5 style="margin-bottom: 5px;">📦 Total Products</h5>
                    <p style="font-size: 25.5px; font-weight: bold; color: #4F46E5;">{total_products}</p>
                </div>
            """, unsafe_allow_html=True)

            # 📌 Most Common Subcategory
            if not df.empty:
                most_common_subcat = df["subcategory"].mode()[0]
                col_m2.markdown(f"""
                    <div style="text-align: center; background-color: #f8f9fa; padding: 12px; border-radius: 8px; border: 1px solid #ddd;">
                        <h5 style="margin-bottom: 5px;">📌 Most Common Subcategory</h5>
                        <p style="font-size: 25.5px; font-weight: bold; color: #4F46E5;">{most_common_subcat}</p>
                    </div>
                """, unsafe_allow_html=True)

            # 📆 Latest Product Added
            if not df.empty:
                latest_product_date = df["modified"].max()  # Use modified date for latest product
                col_m3.markdown(f"""
                    <div style="text-align: center; background-color: #f8f9fa; padding: 12px; border-radius: 8px; border: 1px solid #ddd;">
                        <h5 style="margin-bottom: 5px;">📆 Latest Product Added</h5>
                        <p style="font-size: 25.5px; font-weight: bold; color: #4F46E5;">{latest_product_date}</p>
                    </div>
                """, unsafe_allow_html=True)

            # ✅ Save Button Next to Insights
            with col_m4:
                if st.button("➕", help="Save Key Insights to Designer", key="btn_key_insights"):
                    insight_key = f"""
                    - **Total Products:** {total_products}
                    - **Most Common Subcategory:** {most_common_subcat}
                    - **Latest Product Added on:** {latest_product_date}
                    """
                    save_to_designer(insight_key)

            st.write("---")

            #✅ **Charts Section**
            st.markdown("## 📊 Product Distribution")

            # ✅ Function to Create Dataframe with Quantity Bar + Sorting
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

                new_df["Quantity"] = new_df.apply(lambda row: f"{row[value_col]} {get_bar(row[value_col])}", axis=1)

                # Rename columns
                new_df = new_df.rename(columns={query_col: "Keyword"})

                # Keep only relevant columns
                new_df = new_df[["Keyword", "Quantity"]]

                return new_df

            #**Row: Products by Subcategory & Products by Length**
            col_chart1, col_chart2, col_chart3 = st.columns([4, 4, 1])  # Add extra column for save button

            #**Products by Subcategory**
            with col_chart1:
                st.subheader("📌 Products by Subcategory")
                if not filtered_df.empty:
                    subcategory_df = filtered_df["subcategory"].value_counts().reset_index()
                    subcategory_df.columns = ["subcategory", "count"]
                    # Apply Bar Visualization
                    st.dataframe(create_df_with_bar(subcategory_df, "subcategory", "count"), hide_index=True, use_container_width=True)

            #**Products by Length**
            with col_chart2:
                st.subheader("📏 Products by Length")
                if not filtered_df.empty:
                    length_df = filtered_df["length"].value_counts().reset_index()
                    length_df.columns = ["length", "count"]
                    # Apply Bar Visualization
                    st.dataframe(create_df_with_bar(length_df, "length", "count"), hide_index=True, use_container_width=True)

            # ✅ Save Button for Charts
            with col_chart3:
                if st.button("➕", help="Add Product Insights to Designer", key="btn_product_insights"):
                    insight_charts = f"""
                    - **Most Common Subcategory:** {filtered_df["subcategory"].mode()[0]}
                    - **Most Common Length:** {filtered_df["length"].mode()[0]}
                    - **Total Products:** {len(filtered_df)}
                    """
                    save_to_designer(insight_charts)

            # ✅ **AI Insight Below Charts**
            if not filtered_df.empty:
                # Generate dataset summary
                dataset_summary = f"""
                - **Most Common Subcategory:** {filtered_df["subcategory"].mode()[0]}
                - **Most Common Length:** {filtered_df["length"].mode()[0]}
                - **Total Products:** {len(filtered_df)}
                """

                # ✅ Get AI-generated insights from Gemini
                ai_insight = get_gemini_insight("Product Insights", dataset_summary)

                # ✅ Display AI-generated insight with save button
                col_ai1, col_ai2 = st.columns([5, 1])  # Layout for insight and button

                with col_ai1:
                    st.info(ai_insight)  # ✅ Display AI-generated insight

                with col_ai2:
                    tooltip = "Add this AI insight to the designer for later use"
                    if st.button("➕", help=tooltip, key="btn_Product_Insights"):  # Unique key
                        save_to_designer(ai_insight)  # Save to DB when clicked

            st.write("---")

        with outre_tabs[2]: # Product Listings
            #✅ **Product Listings (Showing 5 at a time)**
            st.markdown("## 🏷️ Product Listings")

            col_l1, col_l2 = st.columns([2.5, 0.5])

            with col_l1:
                # Capitalize the first letter of each column name
                formatted_df = filtered_df.rename(columns=lambda x: x.capitalize())

                # Display the DataFrame with updated column names
                st.dataframe(formatted_df[["Name", "Subcategory", "Quantity", "Length", "Link"]], use_container_width=True, hide_index=True, height=250)

            #✅ **Save Button Next to Product Listings**
            with col_l2:
                if st.button("➕", help="Add insight on Product Listings to Designer"):
                    insight = f"There are {len(filtered_df)} products available. The latest product was added on {filtered_df['modified'].max()}."
                    save_to_designer(insight)

            #✅ **AI Insight Below Product Listings**
            if not filtered_df.empty:
                ai_product_insight = f"""
                - **Total Products:** {len(filtered_df)}
                - **Latest Product Added On:** {filtered_df["modified"].max()}
                """
                display_ai_insight(ai_product_insight, "Product Listings")

            st.write("---")

            #✅ Fetch products from Supabase

            @st.cache_data
            def fetch_products():
                try:
                    response = supabase.table("brd_outre_products").select("*").execute()
                    df = pd.DataFrame(response.data) if response.data else pd.DataFrame()

                    #✅ Convert column names to lowercase to avoid KeyErrors
                    df.columns = df.columns.str.lower()

                    #✅ Extract filenames from image_url
                    df["image_filename"] = df["image_url"].apply(lambda x: os.path.basename(urlparse(x).path) if pd.notna(x) else None)

                    return df
                except Exception as e:
                    st.error(f"Error fetching data: {e}")
                    return pd.DataFrame()

            #✅ Initialize Supabase client
            supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

            # **📁 Local Image Folder**
            IMAGE_FOLDER = "OutreProductImages"

            # **🔄 Load Products**
            df = fetch_products()

            # **Ensure 'name' column exists before using it**
            if "name" not in df.columns:
                st.error("⚠️ 'name' column not found in Supabase data. Check column names!")
                st.stop()  # Stop execution if 'name' column is missing

            # **Match Image Filenames with Local Files**
            def get_local_image_path(image_filename):
                """Finds the corresponding image file in OutreProductImages folder."""
                if not image_filename:
                    return None

                file_path = os.path.join(IMAGE_FOLDER, image_filename)
                return file_path if os.path.exists(file_path) else None

            # **📌 Filter Options**
            st.markdown("## 🛍️ Browse Outre Products")

            col_f1, col_f2, col_f3 = st.columns(3)

            with col_f1:
                search_name = st.selectbox("🔍 Search Product Name", ["All"] + df["name"].dropna().unique().tolist())

            with col_f2:
                search_subcategory = st.multiselect("📂 Filter by Subcategory", df["subcategory"].dropna().unique().tolist())

            with col_f3:
                search_length = st.multiselect("📏 Filter by Length", df["length"].dropna().unique().tolist())

            # **Apply Filters**
            filtered_df = df.copy()

            if search_name != "All":
                filtered_df = filtered_df[filtered_df["name"] == search_name]

            if search_subcategory:
                filtered_df = filtered_df[filtered_df["subcategory"].isin(search_subcategory)]

            if search_length:
                filtered_df = filtered_df[filtered_df["length"].isin(search_length)]

            # **🔄 Pagination Setup**
            PAGE_SIZE = 12  # Number of products per page
            if "current_page" not in st.session_state:
                st.session_state["current_page"] = 1

            total_pages = max(1, (len(filtered_df) + PAGE_SIZE - 1) // PAGE_SIZE)

            # **⬅️ Pagination Buttons ➡️**
            col_prev, col_page, col_next = st.columns([1, 2, 1])

            with col_prev:
                if st.button("⬅️ Previous", disabled=(st.session_state["current_page"] <= 1)):
                    st.session_state["current_page"] -= 1

            with col_page:
                st.markdown(f"<div style='text-align:center; padding-top:7px;'>Page {st.session_state['current_page']} of {total_pages}</div>", unsafe_allow_html=True)

            with col_next:
                if st.button("Next ➡️", disabled=(st.session_state["current_page"] >= total_pages)):
                    st.session_state["current_page"] += 1

            # **📌 Get current page items**
            start_idx = (st.session_state["current_page"] - 1) * PAGE_SIZE
            end_idx = start_idx + PAGE_SIZE
            page_items = filtered_df.iloc[start_idx:end_idx]

            # Remove image related code

            #**🎨 Display products in a grid**
            NUM_COLS = 4  # Set number of columns per row
            for i in range(0, len(page_items), NUM_COLS):
                row_chunk = page_items.iloc[i : i + NUM_COLS]
                cols = st.columns(len(row_chunk))

                for col, (_, row) in zip(cols, row_chunk.iterrows()):
                    #image_path = get_local_image_path(row["image_filename"])  # ✅ Get local image path
                    #if image_path:
                    #    col.image(image_path, use_container_width=True)  # ✅ Display local image
                    #else:
                    #    col.warning("No Image Available")

                    col.caption(f"📌 {row['name']}")
                    col.markdown(f"[🔗 View Product]({row['link']})", unsafe_allow_html=True)  # ✅ Clickable link


            if not page_items.empty:
                st.success(f"Displaying {len(page_items)} products.")
            else:
                st.warning("No products found. Try adjusting your filters.")

            st.write("---")

    with sensationnel_tab:
        st.markdown("<h2 style='text-align: center;'>🔍 Sensationnel Analysis</h2>", unsafe_allow_html=True)

        sensationnel_tabs = st.tabs(["Brand Summary"])
        with sensationnel_tabs[0]:

            # ✅ Outre Brand Summary Section (Replaced with Sensationnel's)
            st.markdown("""
            ### **Sensationnel: A diverse hair brand offering a variety of trendy styles.**  
            🌐 [Visit the official Sensationnel site](https://www.sensationnel.com/)
            """)

            st.markdown("""
            ## 📌 **Sensationnel Brand Summary**  

            ### 📖 **Overview**  
            **Sensationnel** is a well-known hair brand that offers a wide array of **synthetic and human hair products**, including **wigs, braids, weaves, and extensions.** They focus on providing trendy and high-quality options to consumers.

            ### 📦 **Product Lines & Categories**  
            Sensationnel specializes in:  
            ✅ **Wigs**: Lace Front Wigs, Full Wigs, Part Wigs  
            ✅ **Braids**: Pre-Stretched Braids, Synthetic Braiding Hair  
            ✅ **Weaves & Extensions**: Human Hair Weaves, Synthetic Weaves  
            ✅ **Other**: Crochet Hair, Ponytails

            ### 🚀 **Key Selling Points**  
            ✔ **Trend-focused**: Sensationnel keeps up with the latest hair trends and offers products that reflect these trends.  
            ✔ **Diverse product range**: They offer a wide variety of hair products in different styles, colors, and materials.  
            ✔ **Quality**: Sensationnel is known for offering high-quality products that are durable and long-lasting.  
            ✔ **Affordability**: They offer competitive pricing on their products, making them accessible to a wide range of consumers.

            ### 📊 **Market Position**  
            ✅ **Strong presence online and in beauty supply stores**  
            ✅ **Popular among consumers and hairstylists alike**  
            ✅ **Competes with brands like Outre and Bobbi Boss**

            ### 📢 **Marketing & Branding Strategies**  
            🔹 **Social media marketing**: Utilizing platforms like Instagram and Facebook to showcase their products and engage with consumers.  
            🔹 **Influencer collaborations**: Partnering with popular beauty influencers to promote their products.  
            🔹 **Promotional events**: Hosting events to showcase new products and engage with customers.

            ### 💡 **AI Insight: Why Sensationnel Stands Out?**  
            ✔ **Commitment to Trendiness**: Always innovating to meet the latest hair trends.  
            ✔ **Wide variety of styles**  
            ✔ **Quality**: Durable and long-lasting.
            """)

            st.write("---")

            st.markdown("### 🔥 Key Insights")
            st.write("Key metrics and insights about Sensationnel will be displayed here.")

            st.write("---")

            st.markdown("## 🎯 Filter Products")
            st.write("Filter options for Sensationnel products will be added here.")

            st.write("---")

            st.markdown("## 📊 Product Distribution")
            st.write("Charts and tables showcasing product distribution for Sensationnel will be displayed here.")

            st.write("---")

            st.markdown("## 🏷️ Product Listings")
            st.write("Product listings from Sensationnel, including name, subcategory, and link, will be shown here.")

            st.write("---")

            st.markdown("## 🛍️ Browse Sensationnel Products")
            st.write("Product browsing and filtering capabilities for Sensationnel will be implemented here.")

            st.write("---")

    with xpression_tab:
        st.markdown("<h2 style='text-align: center;'>🔍 X-pression Analysis</h2>", unsafe_allow_html=True)

        xpression_tabs = st.tabs(["Brand Summary"])
        with xpression_tabs[0]:
            # ✅ Outre Brand Summary Section (Replaced with X-pression's)
            st.markdown("""
            ### **X-pression: A brand specializing in braiding hair with a focus on length and volume.**  
            🌐 [Visit the official X-pression site](https://www.x-pression.co)
            """)

            st.markdown("""
            ## 📌 **X-pression Brand Summary**  

            ### 📖 **Overview**  
            **X-pression** is widely recognized in the braiding hair market for its **extensive length and volume options**. It is a popular choice for creating voluminous and long braided hairstyles.

            ### 📦 **Product Lines & Categories**  
            X-pression primarily focuses on:  
            ✅ **Braiding Hair**: Synthetic braiding hair in various lengths and colors.

            ### 🚀 **Key Selling Points**  
            ✔ **Exceptional Length and Volume**: Designed to provide maximum length and volume for braided hairstyles.  
            ✔ **Wide Color Range**: Available in a diverse range of colors, from natural tones to vibrant hues.  
            ✔ **Versatility**: Suitable for various braiding techniques and styles.  
            ✔ **Affordability**: Competitively priced, making it accessible to a broad consumer base.

            ### 📊 **Market Position**  
            ✅ **Dominant brand in the braiding hair category**.  
            ✅ **Commonly found in beauty supply stores and online retailers**.  
            ✅ **Competes with other braiding hair brands like RastAfri and Ruwa**.

            ### 📢 **Marketing & Branding Strategies**  
            🔹 **Primarily relies on word-of-mouth and product visibility in retail locations**.  
            🔹 **Collaborates with hairstylists for promotional purposes**.

            ### 💡 **AI Insight: Why X-pression Stands Out?**  
            ✔ **Focus on Length and Volume**: Caters to those looking for dramatic braided looks.  
            ✔ **Wide Color Range**: Suitable for various braiding techniques and styles.  
            ✔ **Dominant brand in the braiding hair category**.
            """)

            st.write("---")

            st.markdown("### 🔥 Key Insights")
            st.write("Key metrics and insights about X-pression will be displayed here.")

            st.write("---")

            st.markdown("## 🎯 Filter Products")
            st.write("Filter options for X-pression products will be added here.")

            st.write("---")

            st.markdown("## 📊 Product Distribution")
            st.write("Charts and tables showcasing product distribution for X-pression will be displayed here.")

            st.write("---")

            st.markdown("## 🏷️ Product Listings")
            st.write("Product listings from X-pression, including name, subcategory, and link, will be shown here.")

            st.write("---")

            st.markdown("## 🛍️ Browse X-pression Products")
            st.write("Product browsing and filtering capabilities for X-pression will be implemented here.")

            st.write("---")

# ✅ **Show Saved Insights (Moved to be Outside the Tabs)**
st.markdown("## 🎨 Designer Insights")
if "saved_insights" in st.session_state and st.session_state.saved_insights:
    for saved_insight in st.session_state.saved_insights:
        st.success(f"📌 {saved_insight}")
else:
    st.info("No insights saved yet. Click **➕** next to an AI insight to add it.")

st.write("---")
