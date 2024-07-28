import os
from flask import Flask, request, render_template, send_file, redirect
from werkzeug.utils import secure_filename
import fitz  
import pytesseract
from PIL import Image
import io
import PyPDF2
import google.generativeai as genai
import textwrap
from IPython.display import Markdown
import pandas as pd

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'output'
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
def read_file(files, filenames):
    extracted_texts = []
    count = 0
    for file, filename in zip(files, filenames):
        count += 1
        all_extracted_text = ""
        file_stream = file.stream  
        reader = PyPDF2.PdfReader(file_stream)

        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text = page.extract_text()
            if text and text.strip():
                all_extracted_text += text + "\n"

        if not any(word.isalnum() for word in all_extracted_text.split()):
            file_stream.seek(0)  
            document = fitz.open(stream=file_stream.read(), filetype="pdf")
            for page_number in range(len(document)):
                page = document.load_page(page_number)
                image_list = page.get_images(full=True)

                if not image_list:
                    print(f"No images found on page {page_number + 1}.")
                    continue

                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    base_image = document.extract_image(xref)
                    image_bytes = base_image["image"]

                    image = Image.open(io.BytesIO(image_bytes))

                    try:
                        text = pytesseract.image_to_string(image)
                        all_extracted_text += f"Text from page {page_number + 1}, image {img_index + 1}:\n{text}\n\n"
                    except Exception as e:
                        print(f"Error during OCR on page {page_number + 1}, image {img_index + 1}: {e}")

        all_extracted_text += f"\n END OF INVOICE {count} FROM FILE {filename}\n\n"
        extracted_texts.append((all_extracted_text, filename))

    return extracted_texts

def to_markdown(text):
    text = text.replace('•', '  *')
    return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))
def extract_fields(files, filenames):
    extracted_texts_with_filenames = read_file(files, filenames)
    dataframes = []

    for extracted_text, filename in extracted_texts_with_filenames:
        prompt = f"""
        Extract the following fields from the text: 
        1. Scan Id 
        2. Country
        3. Bill To Name
        4. Currency
        5. Invoice Date (In format DD-MM-YYYY) (months should be in numeric)
        6. Invoice Number
        7. Invoice Total
        8. PO Number (Starting with PO if not leave it empty)
        9. Net Amount
        10. Tax Rate
        11. Tax Amount
        12. Vendor Address
        13. Vendor Email
        14. Vendor Name

        Text: {extracted_text}

        I need the data for all the text even when its repetitive but make sure the repetitive data is from different files. Only provide with fields and nothing else. Separate the bills by the name Bill_extracted: and no number.
        """
        genai.configure(api_key="YOUR GEMINI API KEY HERE")
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        invoices = response.text.split("Bill_extracted")[1:]

        for invoice in invoices:
            lines = invoice.strip().split("\n")
            invoice_data = {}
            for line in lines:
                line = line.strip().replace("*", "")
                if ':' not in line:
                    continue
                key, value = line.split(":", 1)
                invoice_data[key.strip()] = value.strip()
            invoice_data['Scan Id'] = filename  
            
            df = pd.DataFrame.from_dict([invoice_data])
            dataframes.append(df)
        
    combined_df = pd.concat(dataframes, ignore_index=True)
    combined_df = combined_df.loc[:, ~combined_df.columns.duplicated()]
    if 'Scan Id' not in combined_df.columns:
        combined_df.insert(0, 'Scan Id', '')
    
    print(combined_df)
    return combined_df

@app.route('/')
def upload_file():
    return render_template('upload1.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'files[]' not in request.files:
        return redirect(request.url)
    
    files = request.files.getlist('files[]')

    if not files or all(file.filename == '' for file in files):
        return render_template('upload1.html', error="Please upload at least one file.")

    # Save uploaded PDF files
    pdf_filenames = []
    for file in files:
        if file.filename.endswith('.pdf'):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            pdf_filenames.append(filename)
    
    # Extract fields from the files
    combined_df = extract_fields(files, pdf_filenames)
    
    combined_df = combined_df.dropna(how='all')
    combined_df = combined_df.iloc[:, 1:]
    combined_df.reset_index(drop=True, inplace=True)
    
    # Prepare data for the template
    field_data = []
    for _, row in combined_df.iterrows():
        field_data.append(row.to_dict())
    
    return render_template('preview.html', field_data=field_data, titles=combined_df.columns.values, pdf_filenames=pdf_filenames)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))

@app.route('/submit', methods=['POST'])
def submit():
    edited_data = request.form.to_dict(flat=False)
    
    max_len = max(len(v) for v in edited_data.values())
    for key in edited_data.keys():
        while len(edited_data[key]) < max_len:
            edited_data[key].append('')
    
    df = pd.DataFrame.from_dict(edited_data)
    
    expected_columns = ['Scan Id', 'Country', 'Bill To Name', 'Currency', 'Invoice Date',
                         'Invoice Number', 'Invoice Total', 'PO Number', 'Net Amount',
                         'Tax Rate', 'Tax Amount', 'Vendor Address', 'Vendor Email', 'Vendor Name']
    df.columns = expected_columns[:len(df.columns)] 
    df.columns = df.columns.str.strip()
    output_file = os.path.join(app.config['OUTPUT_FOLDER'], 'invoices_summary_edited.xlsx')
    df.to_excel(output_file, index=False)
    
    return send_file(output_file, as_attachment=True)

def process_files(filenames):
    for filename in filenames:
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], filename.rsplit('.', 1)[0] + '.xlsx')
        
if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
    app.run(debug=True)
