import smtplib, ssl
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
import time
from shared import database

def welcome_email(recipient):
    """
        The welcome email that users will receive when they are added to system
        
        Args:
            recepient: The users unique identifier
    """
    
    welcome_message = "Welcome to Classroom Voter. This email contains your user name and temporary password.  Please login to choose your own password."
    first_name = recipient["firstName"]
    last_name = recipient["lastName"]
    userId = recipient["userID"]
    temporary_password = recipient["temporaryPassword"]
    classes = recipient["classes"]
    
    welcome_message = "Hello " + first_name + " " + last_name + ". " "Welcome to Classroom Voter.  This email contains your username, password, and registered classes.  The next step for you is to login using these credintials to finish setting up your account.\n\n" + "Username: " + userId + "\n" + "Temporary Password: " + temporary_password + "\n" + "Registered Classes: " + classes
    
    return welcome_message
    

def notify_users(recipients):
    """
        Notify users via email with their login credentials
        
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
        welcome_message = welcome_email(recipients[recipient])
        msg.attach(MIMEText(welcome_message))

        smtp.sendmail("classroomvoterAd@gmail.com", recipient, msg.as_string())

    smtp.close()
    
def init_user(users):

    myDb = database.DatabaseSQL("./shared/example.db")

    for userId in users.keys():
        newUser = users[userId]
        userType = newUser["type"]

        user = { 
            userId : {
                "role" : userType,
                "firstName" : newUser["firstName"],
                "lastName" : newUser["lastName"],
                "password" : newUser["temporaryPassword"],
                "classes" : newUser["classes"],
                "reedemed" : False
                    }
        }

        result = myDb.addUser(user)

        
    

newUsers = {
    "douglaswebster99@gmail.com" : {
        "firstName" : "Douglas",
        "lastName" : "Webster",
        "temporaryPassword" : "123",
        "classes" : ["cs181"],
        "type" : "students"
    },
    "douglaswebster@gmail.com" : {
        "firstName" : "Douglas",
        "lastName" : "Webster",
        "temporaryPassword" : "123",
        "classes" : ["cs181"],
        "type" : "students"
    },
    "professor@gmail.com" : {
        "firstName" : "Professor",
        "lastName" : "XXX",
        "temporaryPassword" : "123",
        "classes" : ["cs181"],
        "type" : "professors"
    },
    "professor2@gmail.com" : {
        "firstName" : "Professor",
        "lastName" : "XXX",
        "temporaryPassword" : "123",
        "classes" : ["cs181"],
        "type" : "professors"
    }
}

print(newUsers)

init_user(newUsers)

# notify_users(newUsers)
