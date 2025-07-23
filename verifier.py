import smtplib
import dns.resolver

def verify_email(email):
    domain = email.split('@')[1]

    try:
        # MX record lookup
        mx_records = dns.resolver.resolve(domain, 'MX')
        mx_record = str(mx_records[0].exchange).rstrip('.')

        # SMTP conversation
        server = smtplib.SMTP(timeout=10)
        server.connect(mx_record)
        server.helo('yourdomain.com')
        server.mail('probe@yourdomain.com')
        code, message = server.rcpt(email)
        server.quit()

        if code in [250, 251]:
            return {"status": "valid"}
        elif code in [550, 551, 552, 553, 554]:
            return {"status": "invalid", "code": code, "message": message.decode()}
        else:
            return {"status": "unknown", "code": code, "message": message.decode()}

    except Exception as e:
        return {"status": "error", "message": str(e)}
