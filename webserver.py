from flask import Flask, render_template, request, jsonify, send_file
import os
from werkzeug.utils import secure_filename
from steganalyzer import analyze_directory
import tempfile
import shutil
from datetime import datetime
import json

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max upload
app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'folder' not in request.files:
        return jsonify({'error': 'No folder uploaded'}), 400
    
    folder = request.files.getlist('folder')
    if not folder:
        return jsonify({'error': 'No files selected'}), 400

    # Create a temporary directory for the upload
    temp_dir = os.path.join(app.config['UPLOAD_FOLDER'], datetime.now().strftime('%Y%m%d_%H%M%S'))
    os.makedirs(temp_dir, exist_ok=True)

    # Save all files
    for file in folder:
        if file.filename:
            filename = secure_filename(file.filename)
            file.save(os.path.join(temp_dir, filename))

    # Create output file
    output_file = os.path.join(temp_dir, 'analysis_report.txt')
    
    # Run analysis
    analyze_directory(temp_dir, output_file)
    
    # Read the results
    with open(output_file, 'r') as f:
        report_content = f.read()
    
    # Clean up
    shutil.rmtree(temp_dir)
    
    return jsonify({
        'success': True,
        'report': report_content
    })

@app.route('/static/<path:path>')
def send_static(path):
    return send_file(f'static/{path}')

if __name__ == '__main__':
    app.run(port=5001, debug=False) 
