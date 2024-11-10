from flask import Flask, request, jsonify, render_template
import os
import fitz

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/', methods=['GET'])
def upload_form():
    return render_template('index.html')


@app.route('/get_ratings', methods=['POST'])
def upload_files():
    if 'files' not in request.files:
        return jsonify({'error': 'No files part'}), 400

    files = request.files.getlist('files')

    if len(files) == 0:
        return jsonify({'error': 'No files selected'}), 400

    file_contents = []

    for file in files:
        if file.filename == '':
            continue

        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        if file.filename.lower().endswith('.pdf'):
            try:
                doc = fitz.open(filepath)
                pdf_text = ""
                for page_num in range(doc.page_count):
                    page = doc.load_page(page_num)
                    pdf_text += page.get_text()
                file_contents.append({
                    'filename': file.filename,
                    'filetype': 'pdf',
                    'content': pdf_text
                })
                doc.close()
            except Exception as e:
                return jsonify({'error': f'Error reading PDF file {file.filename}: {str(e)}'}), 500
        else:
            file_contents.append({
                'filename': file.filename,
                'filetype': 'unknown',
                'content': 'Non-PDF file uploaded'
            })

    return jsonify({'files': file_contents})


if __name__ == '__main__':
    app.run()
