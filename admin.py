import smtplib, ssl
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
import time

def notify_users(recipients):
    """
        Notify users with their login credentials
        
        Args:
            recepients (dict): A dictionary where the keys are the users email and values are the credentials
    """
    server = "smtp.gmail.com"
    port = 587
    
    smtp = smtplib.SMTP(server, port)
    smtp.starttls()
    smtp.login("classroomvoterAd@gmail.com", "cs181finalproject")
    
    msg = MIMEMultipart()
    msg["From"] = "classroomvoterAd@gmail.com"
    msg["Subject"] = "Classroom Voter Credintials"
    
    for recipient in recipients:
        msg["To"] = recipient
        msg.attach(MIMEText(recipients[recipient]))

        smtp.sendmail("classroomvoterAd@gmail.com", recipient, msg.as_string())

    smtp.close()

recipients = {
    "douglaswebster98@gmail.com" : "credentials"
}

notify_users(recipients)
