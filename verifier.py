import dns.resolver
import smtplib

def verify_email(email):
    domain = email.split('@')[-1]
    try:
        # MX record lookup
        mx_records = dns.resolver.resolve(domain, 'MX')
        mx_record = str(mx_records[0].exchange).rstrip('.')
        
        # Connect to SMTP server and check if recipient accepted
        server = smtplib.SMTP(timeout=10)
        server.connect(mx_record)
        server.helo('yourdomain.com')  # replace with your domain
        server.mail('probe@yourdomain.com')  # replace with your sender email
        
        code, message = server.rcpt(email)
        server.quit()

        if code in [250, 251]:
            return {"status": "valid", "code": code, "message": message.decode() if isinstance(message, bytes) else message}
        elif code in [550, 551, 552, 553, 554]:
            return {"status": "invalid", "code": code, "message": message.decode() if isinstance(message, bytes) else message}
        else:
            return {"status": "unknown", "code": code, "message": message.decode() if isinstance(message, bytes) else message}

    except Exception as e:
        return {"status": "error", "message": str(e)}
