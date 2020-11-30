import sys
import smtplib
import os
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate

def recovery_message(recipient, temporary_password):
    print(recipient)

    first_name = recipient["firstName"]
    last_name = recipient["lastName"]
    
    recovery_msg = "Hello " + first_name + " " + last_name + ". "  + "We have recieved a request to reset your forgotten password.  This email contains a temporary password.  Please login to Classroom Voter using the same username and the temporary password below \n\n" + "Temporary Password: " + temporary_password
    
    return recovery_msg

def password_recovery_email(recipient_id, recipient, temporary_password):
    """
        Notify user via email with their temporary password

        Args:
            recepient: A dictionary where the key is the users email and values are the credentials
    """

    server = "smtp.gmail.com"
    port = 587

    smtp = smtplib.SMTP(server, port)
    smtp.starttls()
    smtp.login("classroomvoterAd@gmail.com", "cs181finalproject")

    msg = MIMEMultipart()
    msg["From"] = "classroomvoterAd@gmail.com"
    msg["Subject"] = "Classroom Voter Password Recovery"
    msg["To"] = recipient_id
        
    recovery_msg = recovery_message(recipient, temporary_password)
    msg.attach(MIMEText(recovery_msg))

    smtp.sendmail("classroomvoterAd@gmail.com",
                      recipient_id, msg.as_string())

    smtp.close()

