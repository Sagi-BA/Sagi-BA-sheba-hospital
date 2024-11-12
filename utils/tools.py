import os
from io import BytesIO
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def save_uploaded_file(uploaded_file, upload_dir="uploads", filename=None):
    """
    Save the uploaded file to the specified directory and return the file path.
    """
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    if filename is None:
        filename = uploaded_file.name

    file_path = os.path.join(upload_dir, filename)
    
    if isinstance(uploaded_file, BytesIO):
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getvalue())
    else:
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
    
    return file_path

def get_image_url(query):
    UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")

    url = f"https://api.unsplash.com/search/photos?query={query}&client_id={UNSPLASH_ACCESS_KEY}"
    response = requests.get(url)
    data = response.json()
    if data['results']:
        return data['results'][0]['urls']['regular']
    return None

import nltk
nltk.download('brown')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('movie_reviews')


# import textblob
# textblob.download_corpora()

from textblob import TextBlob

def translate_text(text, target_language):
    blob = TextBlob(text)
    # source_language = blob.detect_language()

    # Translation example (translating to French)
    translated_blob = blob.translate(to='fr')
    print("\nTranslated Text (French):")
    print(translated_blob)
    return translated_blob
    # return str(blob.translate(to=target_language))

def clean_text(input_text):
    # Split the text into lines
    lines = input_text.split('\n')
    
    # Process each line
    cleaned_lines = []
    for line in lines:
        # Remove spaces between characters and strip leading/trailing spaces
        cleaned_line = ''.join(line.split()).strip()
        if cleaned_line:  # Only add non-empty lines
            cleaned_lines.append(cleaned_line)
    
    # Join the cleaned lines back together
    return ' '.join(cleaned_lines)

if __name__ == "__main__":
    print("main")

    # Your input text goes here
    input_text = """T e c h n i c a l
    P r o j e c t
    M a n a g e r
    I s r a e l
    ·
    F u l l - t i m e
    About
    The
    Position
    A l l C l o u d ,
    w o r l d ' s
    l e a d i n g
    c l o u d
    s o l u t i o n s
    p r o v i d e r
    s p e c i a l i z i n g
    i n
    c l o u d
    s t a c k ,
    i n f r a s t r u c t u r e ,
    p l a t f o r m ,
    a n d
    S o f t w a r e - a s - a - S e r v i c e
    i s
    l o o k i n g
    f o r
    a
    D e l i v e r y
    M a n a g e r
    t o
    j o i n
    o u r
    E n g a g e
    P r o g r a m
    t o
    l e a d
    a n d
    i m p l e m e n t
    p r o j e c t s
    a n d
    b u s i n e s s
    p r o c e s s e s
    f o r
    o u r
    c u s t o m e r s
    l o c a t e d
    i n
    t h e
    E M E A
    r e g i o n .
    ...
    """  # The rest of your text goes here

    # Clean the text
    cleaned_text = clean_text(input_text)

    # Print the cleaned text
    print(cleaned_text)

    # text = "Hello, world!"
    # translated_text = translate_text(text, 'es')
    # print(translated_text)  # Output: "Hola, mundo!"
    # image_url = get_image_url("Mountain")
    # print(image_url)