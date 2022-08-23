import smtplib

ADDRESS = "oismarilo@gmail.com"
PASS = [0.12, 0.119, 0.099, 0.122, 0.1, 0.104, 0.099, 0.108, 0.104, 0.118, 0.114, 0.112, 0.113, 0.1, 0.102, 0.108]


def send_email(subject=None, body=None):
    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.ehlo()  # identify us with mail server we are using
        smtp.starttls()  # encrypt our traffic
        smtp.ehlo()  # identify us again as an encrypted connection

        smtp.login(ADDRESS, "".join([chr(int(int_ * 1000)) for int_ in PASS]))

        msg = f"Subject: {subject}\n\n{body}"  # weird syntax...has to really be like this by default
        smtp.sendmail(from_addr=ADDRESS, to_addrs=ADDRESS, msg=msg)



