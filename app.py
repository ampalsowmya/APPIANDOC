from flask import Flask, request, render_template, redirect, url_for
import os
from werkzeug.utils import secure_filename
import PyPDF2

app = Flask(__name__)

# Configuration for file uploads
UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to determine document type
def determine_document_type(filepath):
    try:
        with open(filepath, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text = page.extract_text().lower()  # Convert to lowercase for uniform comparison
                if "identity" in text or "passport" in text or "driver's license" in text or "state identification" in text:
                    return "Identity Document"
                elif "receipt" in text:
                    return "Receipt"
                elif "financial" in text or "income statement" in text or "paystub" in text or "tax return" in text:
                    return "Supporting Financial Document"
                elif "application" in text or "credit card" in text or "bank account" in text or "savings account" in text:
                    return "Bank Account Application"
            return "Unknown Document Type"
    except Exception as e:
        return f"Error reading PDF: {e}"

@app.route('/')
def upload_form():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])  # Fixed spacing issue here
def upload_file():
    if 'file' not in request.files:
        return "No file part"
    file = request.files['file']
    if file.filename == '':
        return "No selected file"
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        temp_filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(temp_filepath)

        # Determine document type
        document_type = determine_document_type(temp_filepath)
        print(f"Detected Document Type: {document_type}")  # Debugging

        # Map document type to subfolders
        folder_map = {
            "Bank Account Application": "application",
            "Identity Document": "identity",
            "Supporting Financial Document": "financial",
            "Receipt": "receipt",
            "Unknown Document Type": "others"
        }

        # Get the corresponding folder name
        folder_name = folder_map.get(document_type, "others")
        print(f"Target Folder: {folder_name}")  # Debugging
        target_folder = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)

        # Create the target folder if it doesn't exist
        os.makedirs(target_folder, exist_ok=True)

        # Move the file to the target folder
        target_filepath = os.path.join(target_folder, filename)
        os.rename(temp_filepath, target_filepath)

        return render_template('result.html', filename=filename, document_type=document_type, folder=folder_name)
    return "Invalid file type"

if __name__ == '__main__':
    app.run(debug=True)
