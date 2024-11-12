import streamlit as st
from PIL import Image
import io
from fpdf import FPDF
import os
import uuid
from datetime import datetime
import glob

from utils.init import initialize

def load_images_from_folder():
    ensure_folders_exist()
    
    # Get all image files from the photos directory
    image_files = set()  # Using a set to avoid duplicates
    
    # Convert all extensions to lowercase and use os.path.join for proper path handling
    for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
        # Add files with lowercase extension
        image_files.update(glob.glob(os.path.join("photos", f"*{ext}")))
        # Add files with uppercase extension
        image_files.update(glob.glob(os.path.join("photos", f"*{ext.upper()}")))
    
    # Convert set to sorted list and remove duplicates based on case-insensitive filename
    unique_files = []
    seen_files = set()
    
    for file_path in sorted(image_files, key=os.path.getmtime, reverse=True):
        lowercase_name = os.path.basename(file_path).lower()
        if lowercase_name not in seen_files:
            seen_files.add(lowercase_name)
            unique_files.append(file_path)
    
    return unique_files

def ensure_folders_exist():
    # Create necessary folders if they don't exist
    for folder in ["photos", "pdfs"]:
        if not os.path.exists(folder):
            os.makedirs(folder)

def save_uploaded_image(uploaded_file):
    ensure_folders_exist()
    
    # Generate unique filename using timestamp and UUID
    file_extension = os.path.splitext(uploaded_file.name)[1].lower()
    unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}{file_extension}"
    file_path = os.path.join("photos", unique_filename)
    
    # Save the image
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return file_path

def generate_pdf_filename(base_name=None):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_id = str(uuid.uuid4())[:8]
    if base_name:
        base_name = "".join(c for c in base_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        return f"{timestamp}_{base_name}_{unique_id}.pdf"
    return f"{timestamp}_{unique_id}.pdf"

def convert_images_to_pdf(image_paths, page_size='A4', base_name=None):
    ensure_folders_exist()
    
    # Create a PDF
    pdf = FPDF(orientation='P' if page_size == 'A4' else 'L')
    
    for image_path in image_paths:
        # Add a page
        pdf.add_page()
        
        # Open the image file
        image = Image.open(image_path)
        
        # Get image width and height
        width, height = image.size
        
        # Calculate aspect ratio
        aspect = height / width
        
        # Set dimensions for the image in the PDF
        if page_size == 'A4':
            pdf_width = 210  # A4 width in mm
        else:
            pdf_width = 297  # A4 height in mm for landscape
            
        # Calculate height maintaining aspect ratio
        pdf_height = pdf_width * aspect
        
        # Add to PDF
        pdf.image(image_path, x=0, y=0, w=pdf_width)
    
    # Generate unique filename and save PDF
    pdf_filename = generate_pdf_filename(base_name)
    pdf_path = os.path.join("pdfs", pdf_filename)
    pdf.output(pdf_path)
    
    # Also return the PDF data for immediate download
    pdf_data = pdf.output(dest='S').encode('latin-1')
    
    return pdf_data, pdf_filename, pdf_path

  
def load_html_file(file_name):
    with open(file_name, 'r', encoding='utf-8') as f:
        return f.read()
    
def main():
    title, image_path, footer_content = initialize()
    st.title("הפיכת תמונות ל PDF")
    # hide_streamlit_header_footer()
    
    # Load and display the custom expander HTML
    expander_html = load_html_file('expander.html')
    st.markdown(expander_html, unsafe_allow_html=True)   
    
    # Create tabs for different functionalities
    tab1, tab2, tab3 = st.tabs(["גלריית תמונות", "העלאת תמונות חדשות", "קבצי PDF שנוצרו"])
    
    # Load existing images
    image_files = load_images_from_folder()
    
    with tab1:
        st.header("גלריית תמונות")
        
        if image_files:
            # Multiselect for PDF conversion
            selected_images = st.multiselect(
                "בחירת תמונות להמרה ל-PDF:",
                options=image_files,
                format_func=lambda x: os.path.basename(x)
            )
            
            if selected_images:
                col1, col2 = st.columns(2)
                with col1:
                    page_size = st.radio("בחירת כיוון עמוד PDF:", ["Portrait (A4)", "Landscape (A4)"])
                
                with col2:
                    if st.button('המרה ל PDF'):
                        try:
                            pdf_data, pdf_filename, pdf_path = convert_images_to_pdf(
                                selected_images, 
                                'A4' if page_size == "Portrait (A4)" else 'A4-L',
                                f"batch_{len(selected_images)}_images"
                            )
                            
                            st.download_button(
                                label="הורדת PDF",
                                data=pdf_data,
                                file_name=pdf_filename,
                                mime="application/pdf"
                            )
                            st.success(f"PDF saved as {pdf_filename} and ready for download!")
                        except Exception as e:
                            st.error(f"An error occurred during conversion: {str(e)}")
            
            # Display gallery
            cols = st.columns(3)
            for idx, image_file in enumerate(image_files):
                with cols[idx % 3]:
                    try:
                        image = Image.open(image_file)
                        st.image(image, caption=os.path.basename(image_file), use_column_width=True)
                        
                        # Add buttons for each image
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(f'צפייה בגודל מלא', key=f'view_{idx}'):
                                st.session_state.selected_image = image_file
                        with col2:
                            if st.button(f'המרה ל PDF', key=f'convert_{idx}'):
                                base_name = os.path.splitext(os.path.basename(image_file))[0]
                                pdf_data, pdf_filename, pdf_path = convert_images_to_pdf(
                                    [image_file],
                                    base_name=base_name
                                )
                                st.download_button(
                                    label=f"הורדת PDF",
                                    data=pdf_data,
                                    file_name=pdf_filename,
                                    mime="application/pdf",
                                    key=f'download_{idx}'
                                )
                                st.success(f"PDF נשמר בשם: {pdf_filename}")
                    except Exception as e:
                        st.error(f"Error loading image {image_file}: {str(e)}")
        else:
            st.info("No images found in the photos folder.")
    
    with tab2:
        st.header("העלאת תמונה חדשה")
        uploaded_file = st.file_uploader(
            "בחר קובץ תמונה", 
            type=['png', 'jpg', 'jpeg', 'gif', 'bmp']
        )
        
        if uploaded_file is not None:
            # Display preview of uploaded image
            image = Image.open(uploaded_file)
            st.image(image, caption='Preview of uploaded image', use_column_width=True)
            
            if st.button('שמירת תמונה'):
                try:
                    saved_path = save_uploaded_image(uploaded_file)
                    st.success(f"Image saved successfully as {os.path.basename(saved_path)}")
                    
                    # Add option to convert the just-uploaded image
                    if st.button('המרה ל PDF'):
                        base_name = os.path.splitext(uploaded_file.name)[0]
                        pdf_data, pdf_filename, pdf_path = convert_images_to_pdf(
                            [saved_path],
                            base_name=base_name
                        )
                        st.download_button(
                            label="הורדת PDF",
                            data=pdf_data,
                            file_name=pdf_filename,
                            mime="application/pdf"
                        )
                        st.success(f"PDF נשמר בשם {pdf_filename}")
                except Exception as e:
                    st.error(f"An error occurred while saving the image: {str(e)}")
    
    with tab3:
        st.header("קבצי PDF שנוצרו")
        if os.path.exists("pdfs"):
            pdf_files = sorted(
                glob.glob(os.path.join("pdfs", "*.pdf")),
                key=os.path.getmtime,
                reverse=True
            )
            
            if pdf_files:
                st.write(f"סהכ PDFs: {len(pdf_files)}")
                for pdf_file in pdf_files:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(os.path.basename(pdf_file))
                    with col2:
                        with open(pdf_file, 'rb') as f:
                            st.download_button(
                                label="הורדה",
                                data=f.read(),
                                file_name=os.path.basename(pdf_file),
                                mime="application/pdf",
                                key=f"pdf_{pdf_file}"
                            )
            else:
                st.info("No PDFs generated yet.")
    
    # Display full size image if selected
    if 'selected_image' in st.session_state:
        with st.expander("תמונה בגודל מלא", expanded=True):
            image = Image.open(st.session_state.selected_image)
            st.image(image, caption=os.path.basename(st.session_state.selected_image))
            if st.button('סגור תצוגת גודל מלא'):
                del st.session_state.selected_image
    
    # Display footer content
    st.markdown(footer_content, unsafe_allow_html=True)   
if __name__ == "__main__":  
    main()