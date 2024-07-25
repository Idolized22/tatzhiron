import streamlit as st
import io
import docx
import PyPDF2
# from PIL import Image
# import pytesseract
import pandas as pd
import pyperclip
import striprtf.striprtf as striprtf
from copy import deepcopy
import llm
import yaml

# global llm_model
global processed_text
global cfg

st.set_page_config(layout="wide")

st.markdown("""
<style>
    .rtl {
        direction: rtl;
        text-align: right;
    }
    .stTextInput > div > div > input {
        direction: rtl;
    }
</style>
""", unsafe_allow_html=True)

def extract_text_from_file(file):
    file_extension = file.name.split('.')[-1].lower()
    
    if file_extension == 'txt':
        return file.getvalue().decode('utf-8')
    elif file_extension == 'docx':
        doc = docx.Document(file)
        return '\n'.join([para.text for para in doc.paragraphs])
    elif file_extension == 'pdf':
        pdf_reader = PyPDF2.PdfReader(file)
        return '\n'.join([page.extract_text() for page in pdf_reader.pages])
    elif file_extension == 'rtf':
        rtf_text = file.getvalue().decode('utf-8')
        return striprtf.rtf_to_text(rtf_text)
    elif file_extension == 'md':
        return file.getvalue().decode('utf-8')
    # elif file_extension in ['png', 'jpg', 'jpeg']:
    #     image = Image.open(file)
    #     return pytesseract.image_to_string(image, lang='eng+heb')
    else:
        st.error(f"Unsupported file type: {file_extension}")
        return None
    
def process_text(input_text):
    if cfg != '':
        llm_model = llm.Tatzihiron_LLM(cfg)
    
    for chuck in llm_model.apply(input_text):
        print(chuck)
        print('---')
        yield chuck

def load_yaml_file_st(uploaded_file):
  """Loads a YAML file from an uploaded file object and returns its contents as a Python object.

  Args:
    uploaded_file: The uploaded file object.

  Returns:
    The parsed YAML content as a Python object.
  """

  if uploaded_file is not None:
    content = uploaded_file.read()
    try:
      data = yaml.safe_load(content)
      return data
    except yaml.YAMLError as exc:
      st.error(f"Error parsing YAML: {exc}")
      return None
  else:
    st.warning("Please upload a YAML file")
    return None



def main():
    st.markdown('<h1 class="rtl">תצהירון</h1>', unsafe_allow_html=True)
    global cfg
    cfg = ''
    cfg_ = st.sidebar.file_uploader("  פה מעלים קובץ קונפיגורציה", type=['ymal','yml'])
    if cfg_ is not None:
        cfg = load_yaml_file_st(cfg_)
        
             
    if cfg: 
        col2, col1 = st.columns(2)
        
        def copy_to_clipboard():
            try:
                pyperclip.copy(st.session_state.output_text)
                write_output()
                with col2:
                    st.success('הטקסט העותק ללוח הקלט')
            except:
                with col2:
                    st.error('העתקה ללוח הקלט נכשלה')
    
        def write_output():
            col2.markdown(f'<div class="rtl">{deepcopy(st.session_state.output_text)}</div>', 
                          unsafe_allow_html=True)
            
                
        col1.markdown('<h2 class="rtl">כתב טענות</h2>', unsafe_allow_html=True)
        
        uploaded_file = col1.file_uploader("העלה קובץ", type=['txt', 'docx', 'pdf', 'rtf', 'md'])
        # Input text box
        
        if 'input_text' not in st.session_state:
            st.session_state.input_text = ""

        if uploaded_file is not None:
            extracted_text = extract_text_from_file(uploaded_file)
            if extracted_text:
                st.session_state.input_text = extracted_text

        # Input text box
        input_text = col1.text_area("הזן טקסט או השתמש בקובץ שהועלה:", 
                                value=st.session_state.input_text,
                                height=400,
                                key="input_text_area")
        
        processed_text = ''
        col2.markdown('<h2 class="rtl">תצהיר</h2>', unsafe_allow_html=True)
        
        if processed_text:
            col2.button('copy to clipboard', on_click=copy_to_clipboard)
            
        # Process button
        if col1.button("Process"):
            if input_text:
                    
                gen = process_text(input_text)
                if True:
                    processed_text = col2.write_stream(gen)
                    output_text = deepcopy(processed_text)
                    st.session_state.output_text = output_text
                        
            else:
                st.warning("Please enter some text or upload a file.")
    
   

if __name__ == "__main__":
    main()
