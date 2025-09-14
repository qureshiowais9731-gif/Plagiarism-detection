import sys
import os

# Add the project root directory to PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from utils.plagiarism_checker import check_plagiarism, source_embeddings
from utils.image_processing import process_image
from utils.docx_processing import extract_text_docx
from utils.pdf_processing import extract_text_pdf

# Initialize Flask app
app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'txt', 'docx', 'pdf', 'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Helper function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Determine file type and extract text accordingly
        file_ext = filename.rsplit('.', 1)[1].lower()
        if file_ext in {'png', 'jpg', 'jpeg'}:
            text = process_image(filepath)
        elif file_ext == 'docx':
            text = extract_text_docx(filepath)
        elif file_ext == 'pdf':
            text = extract_text_pdf(filepath)
        else:  # txt
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()

        # Check for plagiarism
        plagiarism_score, status = check_plagiarism(text, source_embeddings)
        if plagiarism_score > 0:
            result = {
                'score': f"{plagiarism_score:.2f}%",
                'status': status
            }
        else:
            result = {
                'score': f"{plagiarism_score:.2f}%",
                'status': status
            }

        return render_template('result.html', score=result['score'], status=result['status'], text=text)

    return jsonify({"error": "File type not allowed"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)