from flask import Flask, request, jsonify
from verifier import verify_email

app = Flask(__name__)

@app.route('/verify', methods=['POST'])
def verify():
    data = request.get_json()
    email = data.get('email')

    if not email or "@" not in email:
        return jsonify({"status": "error", "message": "Invalid email"}), 400

    result = verify_email(email)
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
