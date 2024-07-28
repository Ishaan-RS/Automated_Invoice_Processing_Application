# Automated Invoice Processing Application

This project is a web application designed to automate the extraction and processing of data from multiple PDF invoices. Utilizing Tesseract OCR, PyPDF2, and Google Generative AI, this system captures and organizes invoice details into structured formats, making it ideal for large-scale enterprises to manage their invoices efficiently.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Usage](#usage)
- [Screenshots](#screenschots)

## Features

- Upload multiple PDF invoices at once.
- Extract text from both text-based and image-based PDF invoices.
- Utilize Google Generative AI to accurately capture key invoice details.
- Organize extracted data into a structured format (Excel).
- Edit and preview extracted data before finalizing.
- Download the processed data in Excel format.

## Requirements

- Python 3.10
- Flask
- PyPDF2
- pytesseract
- Pillow (PIL)
- fitz (PyMuPDF)
- google.generativeai
- pandas

## Usage

- Running the Application:
- Open your browser and go to http://127.0.0.1:5000/.
- Click on "Choose Files" and select the files you want.
- Click "Upload".
- Review and Edit:
- Check the extracted fields such as Scan Id, Country, Bill To Name, Currency, Invoice Date, etc.
- Edit any field directly in the browser if needed.
- Download the Processed Data:
- Click "Submit" after reviewing.
- Click the download link to get your invoices_summary_edited.xlsx file.

## Screenshots

File upload page:
![Screenshot 2024-07-28 165505](https://github.com/user-attachments/assets/c8e82e16-a439-470b-8a8c-49e3168f7e35)

Preview and edit page:
![Screenshot 2024-07-28 165320](https://github.com/user-attachments/assets/563f2c11-23df-4cbb-94fc-82f38b3156e1)

Summary Sheet:
![Screenshot 2024-07-28 165705](https://github.com/user-attachments/assets/4833d70e-82f1-44bc-a5f1-0a32b88e7799)




