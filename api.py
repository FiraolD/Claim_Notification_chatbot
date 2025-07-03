from flask import Flask, request, jsonify
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/submit_claim', methods=['POST'])
def submit_claim():
    data = request.form
    file = request.files.get('image')

    if not file:
        return jsonify({"error": "No image uploaded"}), 400

    filename = file.filename
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    return jsonify({
        "status": "success",
        "message": "Claim received!",
        "policy_number": data.get("policy"),
        "name": data.get("name"),
        "image_saved_at": filepath
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)