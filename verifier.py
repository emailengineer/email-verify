from flask import Flask, request, jsonify
import threading
import time
import dns.resolver
import smtplib
import socket

app = Flask(__name__)
lock = threading.Lock()
REQUEST_TIMEOUT = 10  # seconds

def check_email_server(email):
    domain = email.split('@')[-1]
    try:
        # MX record lookup
        mx_records = dns.resolver.resolve(domain, 'MX')
        mx_record = str(mx_records[0].exchange)
        
        # Connect to SMTP server
        server = smtplib.SMTP(timeout=5)
        server.connect(mx_record)
        server.quit()

        return True, "SMTP server reachable"
    except Exception as e:
        return False, str(e)

@app.route('/verify', methods=['POST'])
def verify():
    if not request.is_json:
        return jsonify({'error': 'Invalid JSON'}), 400

    email = request.json.get('email')
    if not email:
        return jsonify({'error': 'Missing email'}), 400

    if not lock.acquire(blocking=False):
        return jsonify({'error': 'Server is busy. Try again shortly.'}), 429

    try:
        result = {}
        def run_check():
            nonlocal result
            valid, reason = check_email_server(email)
            result = {'email': email, 'valid': valid, 'reason': reason}

        thread = threading.Thread(target=run_check)
        thread.start()
        thread.join(timeout=REQUEST_TIMEOUT)

        if thread.is_alive():
            return jsonify({'error': f'Timeout after {REQUEST_TIMEOUT}s'}), 504

        return jsonify(result)

    finally:
        lock.release()

@app.route('/', methods=['GET'])
def home():
    return "SMTP Email Verifier API is running"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
