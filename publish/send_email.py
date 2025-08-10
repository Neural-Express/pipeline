# pipeline/publish/send_email.py
import csv, os, smtplib, ssl, socket
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timezone
from dotenv import load_dotenv

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RENDER_DIR = os.path.join(ROOT, "rendering")
HTML_FRAG = os.path.join(RENDER_DIR, "newsletter_fragment.html")
SUBSCRIBERS_CSV = os.path.join(ROOT, "publish", "subscribers.csv")

SMTP_TIMEOUT = 25  # seconds

def load_env():
    load_dotenv(os.path.join(ROOT, ".env"))
    env = {
        "SMTP_HOST": os.getenv("SMTP_HOST", ""),
        "SMTP_PORT": int(os.getenv("SMTP_PORT", "587")),
        "SMTP_USER": os.getenv("SMTP_USER", ""),
        "SMTP_PASS": os.getenv("SMTP_PASS", ""),
        "SENDER_NAME": os.getenv("SENDER_NAME", "Neural Express"),
        "SENDER_EMAIL": os.getenv("SENDER_EMAIL", ""),
        "TEST_RECIPIENT": os.getenv("TEST_RECIPIENT", ""),
    }
    missing = [k for k,v in env.items() if v in ("", None) and k not in ("TEST_RECIPIENT",)]
    if missing:
        raise SystemExit(f"[CONFIG] Missing required .env keys: {', '.join(missing)}")
    return env

def read_html():
    if not os.path.exists(HTML_FRAG):
        raise SystemExit(f"[BUILD] Not found: {HTML_FRAG}. Run build_newsletter.py first.")
    with open(HTML_FRAG, "r", encoding="utf-8") as f:
        return f.read()

def load_subscribers():
    if not os.path.exists(SUBSCRIBERS_CSV):
        raise SystemExit(f"[LIST] Not found: {SUBSCRIBERS_CSV}")
    subs = []
    with open(SUBSCRIBERS_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            email = (row.get("email") or "").strip()
            name  = (row.get("name") or "").strip() or None
            if email:
                subs.append({"email": email, "name": name})
    if not subs:
        raise SystemExit("[LIST] No subscribers found.")
    return subs

def build_message_html(html_body, recipient_name=None):
    greeting = f"Hi {recipient_name}," if recipient_name else "Hi,"
    preface = f"""
    <div style="font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;color:#222;margin:0;padding:0;">
      <p style="margin:0 0 16px 0;">{greeting}</p>
    </div>
    """
    footer = """
    <div style="font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;color:#666;font-size:12px;margin-top:24px;">
      <hr style="border:none;border-top:1px solid #eee;margin:16px 0;">
      You’re receiving this because you subscribed to <strong>Neural Express</strong>.
      <br>To unsubscribe, reply with “unsubscribe”.
    </div>
    """
    return preface + html_body + footer

def build_message_text():
    return (
        "Neural Express — Weekly AI Brief\n\n"
        "View this email in an HTML-capable client to see the full newsletter.\n"
    )

def send_one(smtp, sender_email, sender_name, to_email, subject, html_body, text_body):
    msg = MIMEMultipart("alternative")
    msg["From"] = f"{sender_name} <{sender_email}>"
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(text_body, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))
    smtp.send_message(msg)

def connect_smtp(env, debug=True):
    host = env["SMTP_HOST"]; port = env["SMTP_PORT"]
    ctx = ssl.create_default_context()
    print(f"[SMTP] Connecting to {host}:{port} (timeout={SMTP_TIMEOUT}s)…")
    try:
        if port == 465:
            smtp = smtplib.SMTP_SSL(host, port, timeout=SMTP_TIMEOUT, context=ctx)
            if debug: smtp.set_debuglevel(1)
            print("[SMTP] Connected via SSL. Logging in…")
            smtp.login(env["SMTP_USER"], env["SMTP_PASS"])
            print("[SMTP] Login OK.")
            return smtp
        else:
            smtp = smtplib.SMTP(host, port, timeout=SMTP_TIMEOUT)
            if debug: smtp.set_debuglevel(1)
            smtp.ehlo()
            print("[SMTP] Starting TLS…")
            smtp.starttls(context=ctx)
            smtp.ehlo()
            print("[SMTP] TLS OK. Logging in…")
            smtp.login(env["SMTP_USER"], env["SMTP_PASS"])
            print("[SMTP] Login OK.")
            return smtp
    except (socket.timeout, smtplib.SMTPException, OSError) as e:
        raise SystemExit(f"[SMTP] Connection/login failed: {e}")

def main(mode="test"):
    env = load_env()
    body = read_html()
    subs = load_subscribers()
    issue_date = datetime.now(timezone.utc).strftime("%b %d, %Y (UTC)")
    subject = f"Neural Express — Weekly AI Brief ({issue_date})"

    smtp = connect_smtp(env, debug=True)
    try:
        if mode == "test":
            test_to = env["TEST_RECIPIENT"]
            if not test_to:
                raise SystemExit("[TEST] Set TEST_RECIPIENT in .env first.")
            html_msg = build_message_html(body, recipient_name="Friend")
            text_msg = build_message_text()
            print(f"[EMAIL] Sending TEST to {test_to}…")
            send_one(smtp, env["SENDER_EMAIL"], env["SENDER_NAME"], test_to, subject, html_msg, text_msg)
            print(f"[EMAIL] TEST sent to {test_to}")
        else:
            total = len(subs)
            for i, s in enumerate(subs, 1):
                html_msg = build_message_html(body, recipient_name=s["name"])
                text_msg = build_message_text()
                print(f"[EMAIL] {i}/{total} → {s['email']}…")
                send_one(smtp, env["SENDER_EMAIL"], env["SENDER_NAME"], s["email"], subject, html_msg, text_msg)
            print("[EMAIL] All messages sent.")
    finally:
        try:
            smtp.quit()
        except Exception:
            pass

if __name__ == "__main__":
    import sys
    mode = "test"
    if len(sys.argv) > 1 and sys.argv[1] in ("test", "send"):
        mode = sys.argv[1]
    main(mode)