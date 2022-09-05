import smtplib
import constants as c

with open(f"{c.DOWNLOADS}/robot_conect.txt", "r") as file:
    file_complete = file.read().split("\n")
    ADDRESS = file_complete[0]
    PASS = file_complete[1]


def send_email(subject: str = None, body: str = None):
    """

    :param subject: Text string which will represent subject of a mail
    :param body: Text string which will represent main text of a mail
    :return: None
    """
    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.ehlo()  # identify us with mail server we are using
        smtp.starttls()  # encrypt our traffic
        smtp.ehlo()  # identify us again as an encrypted connection

        smtp.login(ADDRESS, PASS)
        msg = f"Subject: {subject}\n\n{body}"  # weird syntax...has to really be like this by default
        smtp.sendmail(from_addr=ADDRESS, to_addrs=ADDRESS, msg=msg)


send_email()
