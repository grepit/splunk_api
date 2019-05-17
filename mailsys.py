## monitoring, recording, copying, auditing and inspection.               ##
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from string import Template


class MailTool():
# Open a plain text file for reading.  For this example, assume that
# the text file contains only ASCII characters.
    def __init__(self,to_email):
        self.to_email =to_email

    def send(self):
        msg = MIMEMultipart('alternative')
        # send email
        msg['Subject'] = 'Report '
        msg['From'] = 'someemail@somewhere.com'
        msg['To'] = self.to_email

        html = " "
        with open("/tmp/report.txt") as fp:
            for line in fp:
                html = html + line + "<br>"
        fp.close()
        part1 = MIMEText(html, 'html')

        #msg.attach(part1)
        msg.attach(part1)

        # Send the message via our own SMTP server.
        s = smtplib.SMTP('chsmtp.expeso.com', 25)
        s.ehlo()
        s.starttls()
        #s.login("user", "password")
        # this password is in PAM
        s.sendmail('someemail@somewhere.com', self.to_email, msg.as_string())
        s.send_message(msg)
        s.quit()
