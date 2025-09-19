
    # server.py
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'received_images'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/submit_claim', methods=['POST'])
def submit_claim():
    try:
        # Get form data
        name = request.form.get('name')
        policy = request.form.get('policy')

        if not name or not policy:
            return jsonify({"error": "Missing required fields"}), 400

        # Check if any images were uploaded
        if 'image' not in request.files:
            return jsonify({"error": "No image part in request"}), 400

        files = request.files.getlist('image')  # Get all uploaded images

        if len(files) == 0:
            return jsonify({"error": "No selected files"}), 400

        saved_files = []
        for file in files:
            if file.filename == '':
                continue
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            saved_files.append(filename)

        print(f"✅ Claim received from {name}, Policy: {policy}")
        print(f"📷 {len(saved_files)} image(s) saved: {saved_files}")

        return jsonify({
            "message": "Claim submitted successfully!",
            "name": name,
            "policy_number": policy,
            "images_received": saved_files,
            "total_images": len(saved_files),
            "status": "Delivered"
        }), 200

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 Backend server running on http://localhost:5000")
    app.run(port=5000, debug=True)