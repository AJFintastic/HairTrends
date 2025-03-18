import streamlit as st
import os
import random
import google.generativeai as genai
from utils import save_to_designer, get_gemini_insight, generate_image, save_to_mydesigns  # Import AI & Save functions
import base64  # Import base64
from fpdf import FPDF
from supabase import create_client, Client
import uuid  # Import UUID for unique filenames

# ✅ Set Page Config
st.set_page_config(page_title="Generate Hairstyles", page_icon="🎨", layout="wide")

# Configure the Gemini API key (ensure GEMINI_API_KEY exists in your .env file)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash')

# Supabase settings (replace with your actual credentials)
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
BUCKET_NAME = "hairstyle_images"  # the name of your storage bucket

# Initialize Supabase client
if SUPABASE_URL and SUPABASE_KEY:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    st.error("Supabase URL and Key not found in environment variables.")

# AI Functions (Now all return plain text for easier PDF formatting)
@st.cache_data
def get_image_prompt(design_name, target_demographic, length, color, braid_type, custom_style, selected_insights):
    """Generate an image generator prompt."""
    insights_text = "\nInclude these key trend insights:\n" + "\n".join(f"- {insight}" for insight in selected_insights) if selected_insights else ""
    prompt = f"""Create a detailed image generation prompt for a braid style that is:\n- Design Name: {design_name}\n- Target Demographic: {target_demographic}\n- Length: {length}\n- Color: {color}\n- Braid Type: {braid_type}\n- Style Notes: {custom_style if custom_style else 'Clean and natural style'}\n{insights_text}\nFocus on visual details, less than 100 words for a stable diffusion image generator."""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating image generation prompt: {str(e)}"

@st.cache_data
def get_design_look_and_feel(design_name, target_demographic, length, color, braid_type, custom_style, selected_insights):
    """Generate a detailed look and feel description."""
    insights_text = "\nIncorporate these insights:\n" + "\n".join(f"- {insight}" for insight in selected_insights) if selected_insights else ""
    prompt = f"""Describe the overall look and feel for braid style {design_name} with these characteristics: \nDemographic: {target_demographic}, Length: {length}, Color: {color}, Braid Type: {braid_type}, Custom Style: {custom_style}.\n{insights_text}\nFocus on aspects that describe the overall aesthetic of the design."""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating look and feel: {str(e)}"

@st.cache_data
def get_marketing_plan(design_name, target_demographic, length, color, braid_type, custom_style, selected_insights):
    """Generate a marketing plan."""
    insights_text = "\nLeverage these insights in the marketing:\n" + "\n".join(f"- {insight}" for insight in selected_insights) if selected_insights else ""
    prompt = f"""Marketing plan for braid style {design_name}, demographic {target_demographic}, with the following attributes: Length {length}, Color {color}, Braid Type: {braid_type}, Custom Style: {custom_style}.\n{insights_text}\nInclude target channels, key messages, and promotional ideas."""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating marketing plan: {str(e)}"

@st.cache_data
def get_packaging_plan(design_name, target_demographic, length, color, braid_type, custom_style, selected_insights):
    """Generate a packaging plan."""
    insights_text = "\nConsider these insights for packaging design:\n" + "\n".join(f"- {insight}" for insight in selected_insights) if selected_insights else ""
    prompt = f"""Packaging plan for braid style {design_name}, demographic {target_demographic}, characterized by Length: {length}, Color: {color}, Braid Type: {braid_type}, Custom Style: {custom_style}.\n{insights_text}\nInclude packaging materials, design elements, and sustainability considerations."""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating packaging plan: {str(e)}"

@st.cache_data
def get_manufacturing_costs(design_name, target_demographic, length, color, braid_type, custom_style, selected_insights):
    """Generate manufacturing costs details."""
    insights_text = "\nIncorporate these insights into cost considerations:\n" + "\n".join(f"- {insight}" for insight in selected_insights) if selected_insights else ""
    prompt = f"""Manufacturing costs for braid style {design_name}: Demographic: {target_demographic}, Length: {length}, Color: {color}, Braid Type: {braid_type}, Custom Style: {custom_style}.\n{insights_text}\nDetail materials, labor, and overhead costs."""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating manufacturing costs: {str(e)}"

@st.cache_data
def get_customer_costs(design_name, target_demographic, length, color, braid_type, custom_style, selected_insights):
    """Generate customer costs details."""
    insights_text = "\nConsider these insights for customer pricing:\n" + "\n".join(f"- {insight}" for insight in selected_insights) if selected_insights else ""
    prompt = f"""Customer costs for braid style {design_name}: Demographic: {target_demographic}, Length: {length}, Color: {color}, Braid Type: {braid_type}, Custom Style: {custom_style}.\n{insights_text}\nDetail product price, installation fees, maintenance costs."""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating customer costs: {str(e)}"

@st.cache_data
def get_formulation_details(design_name, target_demographic, length, color, braid_type, custom_style, selected_insights):
    """Generate formulation details, incorporating insights."""
    insights_text = "\nAddress these insights in the formulation details:\n" + "\n".join(f"- {insight}" for insight in selected_insights) if selected_insights else ""
    prompt = f"""Outline the formulation details for braid style: {design_name}. Take into account: Demographic: {target_demographic}, Length: {length}, Color: {color}, Braid Type: {braid_type}, Custom Style: {custom_style}.\n{insights_text}"""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating formulation details: {str(e)}"

@st.cache_data
def get_design_visuals(design_name, target_demographic, length, color, braid_type, custom_style, selected_insights):
    """Generate design visuals details, incorporating insights."""
    insights_text = "\nDraw inspiration from these insights for the design visuals:\n" + "\n".join(f"- {insight}" for insight in selected_insights) if selected_insights else ""
    prompt = f"""Outline the visual inspiration for the design: {design_name} by taking into account: Demographic: {target_demographic}, Length: {length}, Color: {color}, Braid Type: {braid_type}, Custom Style: {custom_style}.\n{insights_text}"""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating visuals: {str(e)}"

def create_pdf_report(title, content):
    """Create a PDF report from a title and content."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=title, ln=1, align="C")
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 10, content)
    return pdf

def create_full_launch_plan_pdf(design_name, demographic, length, color, braid_type, custom_style, selected_insights,
                                 image_prompt, look_and_feel, marketing_plan, packaging_plan, manufacturing_costs, customer_costs, formulation_details, design_visuals):
    """Create a full launch plan PDF combining all the generated information."""
    pdf = FPDF()
    pdf.add_page()
    # Title Page
    pdf.set_font("Arial", "B", size=24)
    pdf.cell(200, 20, txt=f"Braid Design Launch Plan: {design_name}", ln=1, align="C")
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Target Demographic: {demographic}", ln=1, align="C")
    pdf.cell(200, 10, txt=f"Generated by AI Braid Design Studio", ln=1, align="C")
    # Table of Contents (Simple)
    pdf.add_page()
    pdf.set_font("Arial", "B", size=16)
    pdf.cell(200, 10, txt="Table of Contents", ln=1, align="C")
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="1. Image Generation Prompt", ln=1)
    pdf.cell(200, 10, txt="2. Look and Feel", ln=1)
    pdf.cell(200, 10, txt="3. Marketing Plan", ln=1)
    pdf.cell(200, 10, txt="4. Packaging Plan", ln=1)
    pdf.cell(200, 10, txt="5. Manufacturing Costs", ln=1)
    pdf.cell(200, 10, txt="6. Customer Costs", ln=1)
    pdf.cell(200, 10, txt="7. Formulation Details", ln=1)
    pdf.cell(200, 10, txt="8. Design Visuals", ln=1)
    # Section Content (Each section gets its own page for readability)
    pdf.add_page()
    pdf.set_font("Arial", "B", size=16)
    pdf.cell(200, 10, txt="1. Image Generation Prompt", ln=1)
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 10, image_prompt)
    pdf.add_page()
    pdf.set_font("Arial", "B", size=16)
    pdf.cell(200, 10, txt="2. Look and Feel", ln=1)
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 10, look_and_feel)
    pdf.add_page()
    pdf.set_font("Arial", "B", size=16)
    pdf.cell(200, 10, txt="3. Marketing Plan", ln=1)
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 10, marketing_plan)
    pdf.add_page()
    pdf.set_font("Arial", "B", size=16)
    pdf.cell(200, 10, txt="4. Packaging Plan", ln=1)
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 10, packaging_plan)
    pdf.add_page()
    pdf.set_font("Arial", "B", size=16)
    pdf.cell(200, 10, txt="5. Manufacturing Costs", ln=1)
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 10, manufacturing_costs)
    pdf.add_page()
    pdf.set_font("Arial", "B", size=16)
    pdf.cell(200, 10, txt="6. Customer Costs", ln=1)
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 10, customer_costs)
    pdf.add_page()
    pdf.set_font("Arial", "B", size=16)
    pdf.cell(200, 10, txt="7. Formulation Details", ln=1)
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 10, formulation_details)
    pdf.add_page()
    pdf.set_font("Arial", "B", size=16)
    pdf.cell(200, 10, txt="8. Design Visuals", ln=1)
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 10, design_visuals)
    return pdf

# Function to encode the image to base64
def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        return encoded_string

# List hair color images
#color_images_folder = "ColorChartImages"
#hair_colors = [f for f in os.listdir(color_images_folder) if f.endswith((".png", ".jpg", ".jpeg"))]

# Add image display on hover to avoid cluttering the UI.
def st_hover_color(hex_color):
    """Apply CSS styling to the streamlit sidebar."""
    return f"""
    """

def upload_image(image_path: str) -> str | None:
    """
    Uploads an image to Supabase Storage and returns the public URL.

    Args:
        image_path: The local path to the image file.

    Returns:
        The public URL of the uploaded image, or None if the upload fails.
    """
    try:
        with open(image_path, "rb") as f:
            image_data = f.read()

        # Generate a unique filename
        file_extension = os.path.splitext(image_path)[1]  # Get the file extension (e.g., ".png")
        unique_filename = f"{uuid.uuid4()}{file_extension}"  # Create a unique filename using UUID

        # Upload the image to Supabase Storage
        response = supabase.storage.from_(BUCKET_NAME).upload(
            path=unique_filename,  # path to store the image *within* the bucket (using unique filename)
            file=image_data,
            file_options={"content-type": "image/png"}  # set the content type appropriately
        )

        # Get the public URL (important!)
        #  Supabase Storage requires that you create a "public" policy
        #  for your storage bucket that allows public reads for unauthenticated users.
        #  If you haven't set up a public policy, you will get an error.
        public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(unique_filename)

        return public_url

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Main content area
with st.container():
    # Header & Branding
    st.markdown(
        """
        <h1 style='text-align: center; color: #4F46E5;'>
            🎨 AI Braid Design Studio
        </h1>

        <p style='text-align: center; font-size:18px;'>
            Craft unique and stunning braid styles with our AI-powered design studio.
        </p>
        """,
        unsafe_allow_html=True
    )
    st.write("---")

    # Initialize session state
    if "generated_hairstyles" not in st.session_state:
        st.session_state.generated_hairstyles = []  # List to store generated hairstyles
    if "image_prompt" not in st.session_state:
        st.session_state.image_prompt = ""
    if "look_and_feel" not in st.session_state:
        st.session_state.look_and_feel = ""
    if "marketing_plan" not in st.session_state:
        st.session_state.marketing_plan = ""
    if "packaging_plan" not in st.session_state:
        st.session_state.packaging_plan = ""
    if "manufacturing_costs" not in st.session_state:
        st.session_state.manufacturing_costs = ""
    if "customer_costs" not in st.session_state:
        st.session_state.customer_costs = ""
    if "formulation_details" not in st.session_state:
        st.session_state.formulation_details = ""
    if "design_visuals" not in st.session_state:
        st.session_state.design_visuals = ""

    # **Set up initial value for prompt**
    if "generated_design" not in st.session_state:
        st.session_state.generated_design = ""
    if "prompt" not in st.session_state:
        st.session_state.prompt = ""  # Initialize empty

    # --- STEP 1: Design ---
    st.markdown("### Step 1: ✨ Design Your Dream Braids")
    with st.expander("Click here to customize your braid style", expanded=True):
        col1, col2, col3 = st.columns(3)

        # Target demographic dropdown
        demographic = st.selectbox("👩🏽 Target Demographic", ["Teens", "Young Adults", "Professionals", "Elderly", "Men", "Women", "Unisex"], index=0)

        # Select Hair Length
        with col1:
            length = st.selectbox("📏 Hair Length", ["Short", "Medium", "Long", "Extra Long", "Bob Cut", "Shoulder Length"], index=1)

        # Select Hair Color with Displayed Image
        with col2:
            selected_color = st.selectbox("🌈 Hair Color", ["Black", "Blonde", "Brown", "Red", "Purple", "Blue", "Green", "Pink", "Orange", "Gray"], index=0)
            #                               + [os.path.splitext(hc)[0] for hc in hair_colors], index=0)
            # # If a hair color from the folder is selected, display the image
            # if selected_color in [os.path.splitext(hc)[0] for hc in hair_colors]:
            #     color_image_path = os.path.join(color_images_folder, f"{selected_color}.png")
            #     st.markdown(st_hover_color("#C4A484"), unsafe_allow_html=True)
            #     image_html = f"""
            #     {selected_color}
            #     """
            #     st.markdown(image_html, unsafe_allow_html=True)

        # Select Braid Type
        with col3:
            braid_type = st.selectbox("🧶 Braid Type", ["Box Braids", "Knotless Braids", "Cornrows", "Twists", "Locs", "Faux Locs", "Micro Braids", "Senegalese Twists", "Crochet Braids", "Ghana Braids", "Tribal Braids"])

        # Additional Customizations
        custom_style = st.text_area("🎨 Any Special Requests?", placeholder="e.g., ombré effect, beads, wavy edges...")

        # Design Name
        design_name = st.text_input("✏️ Design Name (Optional)", placeholder="Leave blank for AI-generated name")

    st.write("---")


    # --- STEP 2: Incorporate Insights ---
    st.markdown("### Step 2: 💡 Incorporate Designer Insights")
    with st.expander("Click here to select insights", expanded=True):

        # Load Saved Insights
        if "saved_insights" not in st.session_state or not st.session_state.saved_insights:
            st.info("No saved insights yet. Go to **Competitor Battles or Google Trends** and click ➕ to add insights.")
            selected_insights = []
        else:
            # Display existing designer insights with ability to add/remove
            selected_insights = st.multiselect(
                "🔍 Select Insights to Incorporate in Your Hairstyle:",
                st.session_state.saved_insights,
                default=[]
            )
    st.write("---")


    # --- STEP 3: Generate Image Generator Prompt ---
    st.markdown("### Step 3: 🤖 Generate Image Generator Prompt")
    with st.expander("Click here to generate and refine your image prompt", expanded=True):
        if st.button("✨ Generate Image Prompt"):
            st.success("✅ Generating image prompt...")
            # Use AI to generate prompt
            st.session_state.image_prompt = get_image_prompt(design_name, demographic, length, selected_color, braid_type, custom_style, selected_insights)  # Save to session state
            st.markdown(f"**📝 Image Generation Prompt for** {design_name} targeting {demographic}:")
            st.session_state.generated_design = st.text_area(
                "Edit or refine the prompt below:",
                value=st.session_state.image_prompt,
                height=150  # Adjust height as needed
            )
    st.write("---")


    # --- STEP 4: Generate AI Hairstyle ---
    st.markdown("### Step 4: 🖼️ Generate AI Hairstyle Image")
    if st.button("Generate Hairstyle"):
        if not st.session_state.image_prompt.strip():
            st.error("Please enter a description for the image.")
        else:
            with st.spinner("Generating image..."):
                result = generate_image(st.session_state.image_prompt)  # Assuming generate_image is defined elsewhere

                # Initialize a list to hold valid image paths or URLs
                image_paths = []

                # Check the type of the result and extract the image file path(s) or URL(s)
                if isinstance(result, tuple):
                    # If it's a tuple, extract the first element
                    image_paths.append(result[0])
                elif isinstance(result, list):
                    # If it's a list, check each item
                    for item in result:
                        if isinstance(item, tuple):
                            image_paths.append(item[0])
                        elif isinstance(item, str):
                            image_paths.append(item)
                elif isinstance(result, str):
                    image_paths.append(result)

                # Check if we got any valid image paths or URLs
                if not image_paths:
                    st.error("No valid image returned from the API. Please try again.")
                else:
                    # Display the generated image(s)
                    captions = ["Generated Hairstyle" for _ in image_paths]
                    st.image(image_paths, caption=captions, use_container_width=True)

                    # Save the first generated image to session state
                    st.session_state.selected_image = image_paths[0]

                    # **Upload to Supabase and get the URL**
                    supabase_url = None
                    if SUPABASE_URL and SUPABASE_KEY:
                        supabase_url = upload_image(st.session_state.selected_image)

                    # Check if upload was successful
                    if supabase_url:
                        st.success(f"Image uploaded to Supabase. URL: {supabase_url}")
                    else:
                        st.error("Failed to upload image to Supabase.")
                        supabase_url = None  # Ensure it's None if upload fails

                    # Add Save Option
                    st.session_state.generated_hairstyles.append((
                        st.session_state.selected_image,  # store the local image for display.
                        {
                            "design_name": design_name,
                            "selected_insights": selected_insights,
                            "supabase_url": supabase_url  # Save the Supabase URL
                        }
                    ))  # Append to saved hairstyles
                    st.success("✅ Hairstyle generated!")

                # Generate additional results
                st.session_state.look_and_feel = get_design_look_and_feel(design_name, demographic, length, selected_color, braid_type, custom_style, selected_insights)
                st.session_state.marketing_plan = get_marketing_plan(design_name, demographic, length, selected_color, braid_type, custom_style, selected_insights)
                st.session_state.packaging_plan = get_packaging_plan(design_name, demographic, length, selected_color, braid_type, custom_style, selected_insights)
                st.session_state.manufacturing_costs = get_manufacturing_costs(design_name, demographic, length, selected_color, braid_type, custom_style, selected_insights)
                st.session_state.customer_costs = get_customer_costs(design_name, demographic, length, selected_color, braid_type, custom_style, selected_insights)
                st.session_state.formulation_details = get_formulation_details(design_name, demographic, length, selected_color, braid_type, custom_style, selected_insights)
                st.session_state.design_visuals = get_design_visuals(design_name, demographic, length, selected_color, braid_type, custom_style, selected_insights)

    st.write("---")

    # Store tabs
    if st.session_state.generated_hairstyles:  # Tabs only show with a generated hairstyle
        design = st.session_state.generated_hairstyles[-1]
        design_name = design[1]['design_name']
        selected_insights = design[1]['selected_insights']
        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
            "💰 Manufacturing Costs",
            "💲 Customer Costs",
            "✨ Look & Feel",
            "🚀 Marketing",
            "📦 Packaging",
            "🧪 Formulation",
            "🎨 Visuals & Save"
        ])

        with tab1:
            st.markdown(f"#### 💰 Manufacturing Costs for {design_name}")
            st.write(st.session_state.manufacturing_costs)
            pdf = create_pdf_report(f"Manufacturing Costs for {design_name}", st.session_state.manufacturing_costs)
            st.download_button(label="Download Manufacturing Costs (PDF)", data=pdf.output(dest='S').encode('latin-1'), file_name=f"{design_name}_manufacturing_costs.pdf", mime="application/pdf")

        with tab2:
            st.markdown(f"#### 💲 Customer Costs for {design_name}")
            st.write(st.session_state.customer_costs)
            pdf = create_pdf_report(f"Customer Costs for {design_name}", st.session_state.customer_costs)
            st.download_button(label="Download Customer Costs (PDF)", data=pdf.output(dest='S').encode('latin-1'), file_name=f"{design_name}_customer_costs.pdf", mime="application/pdf")

        with tab3:
            st.markdown(f"#### ✨ Design Look and Feel {design_name}")
            st.write(st.session_state.look_and_feel)
            pdf = create_pdf_report(f"Design Look and Feel for {design_name}", st.session_state.look_and_feel)
            st.download_button("Download Design", data=pdf.output(dest='S').encode('latin-1'), file_name=f"{design_name}_designLook.pdf", mime="application/pdf")

        with tab4:
            st.markdown(f"#### 🚀 Design Marketing Plan {design_name}")
            st.write(st.session_state.marketing_plan)
            pdf = create_pdf_report(f"Marketing Plan for {design_name}", st.session_state.marketing_plan)
            st.download_button("Download Design", data=pdf.output(dest='S').encode('latin-1'), file_name=f"{design_name}_designMarketing.pdf", mime="application/pdf")

        with tab5:
            st.markdown(f"#### 📦 Design Packaging Plan {design_name}")
            st.write(st.session_state.packaging_plan)
            pdf = create_pdf_report(f"Packaging Plan for {design_name}", st.session_state.packaging_plan)
            st.download_button("Download Design", data=pdf.output(dest='S').encode('latin-1'), file_name=f"{design_name}_designPackaging.pdf", mime="application/pdf")

        with tab6:
            st.markdown(f"#### 🧪 Design Formulation {design_name}")
            st.write(st.session_state.formulation_details)
            pdf = create_pdf_report(f"Formulation Details for {design_name}", st.session_state.formulation_details)  # Corrected line
            st.download_button("Download Design", data=pdf.output(dest='S').encode('latin-1'), file_name=f"{design_name}_designFormulation.pdf", mime="application/pdf")

        with tab7:
            st.markdown(f"#### 🎨 Design Visuals {design_name}")
            st.write(st.session_state.design_visuals)
            # ✅ PDF Download Buttons (Inside the Tabs)
            st.markdown(f"#### 💾 Save Design Plan for {design_name}")
            launch_plan = f"""# Launch Plan for {design_name}\n\n## Design Details:\n- Demographic: {demographic}\n- Length: {length}\n- Color: {selected_color}\n- Braid Type: {braid_type}\n- Custom Style: {custom_style}\n\n## Image Prompt:\n{st.session_state.image_prompt}\n\n## Look and Feel:\n{st.session_state.look_and_feel}\n\n## Marketing Plan:\n{st.session_state.marketing_plan}\n\n## Packaging Plan:\n{st.session_state.packaging_plan}\n\n## Manufacturing Costs:\n{st.session_state.manufacturing_costs}\n\n## Customer Costs:\n{st.session_state.customer_costs}\n## Formulation Details:\n{st.session_state.formulation_details}\n## Design Visuals:\n{st.session_state.design_visuals}"""
            pdf = create_pdf_report(f"Launch Plan for {design_name}", launch_plan)
            st.download_button(label="Download Full Launch Plan (PDF)", data=pdf.output(dest='S').encode('latin-1'), file_name=f"{design_name}_launch_plan.pdf", mime="application/pdf")


    # Save to Designer Action (Save to DB when clicked)
# if st.button("➕ Save to Designer"):
#     # Get the last generated hairstyle's data
#     if st.session_state.generated_hairstyles:
#         last_design = st.session_state.generated_hairstyles[-1]
#         design_name = last_design[1]['design_name']  # Assuming 'design_name' is available
#         supabase_url = last_design[1]['supabase_url']  # Get the Supabase URL
#         selected_insights_for_save = last_design[1]['selected_insights']  # get the selected insights.
#         description = f"Generated a {braid_type} hairstyle in {selected_color}, length: {length}. Special: {custom_style}"
#         image_prompt = st.session_state.image_prompt  # Get the generated image prompt

#         # Save to the brd_design table using the new save_to_mydesigns function
#         try:
#             save_successful = save_to_mydesigns(
#                 design_name=design_name,
#                 image_url=supabase_url,
#                 description=description,
#                 selected_insights=selected_insights_for_save,
#                 image_prompt=image_prompt,
#             )

#             st.success("✅ Saved to My Designs (with image URL and details)!")

#         except Exception as e:
#             st.error(f"❌ Failed to save to My Designs: {e}")


#         # Save insights to brd_gtrends_designer_insights (separate action)
#         for insight_text in selected_insights_for_save:
#             # Check if the insight is already saved to prevent duplicates
#             if insight_text not in st.session_state.saved_insights:
#                 # Save to Supabase
#                 try:
#                     supabase.table("brd_gtrends_designer_insights").insert({"insight": insight_text}).execute()
#                     st.session_state.saved_insights.append(insight_text)  # update the session state
#                     st.success(f"✅ Insight '{insight_text}' added to Designer successfully!")

#                 except Exception as e:
#                     st.error(f"Error saving insight to designer: {e}")
            
#                 st.info(f"Insight '{insight_text}' already saved.")  # Inform the user about duplicate.

#     else:
#         st.warning("No hairstyle has been generated yet.")
