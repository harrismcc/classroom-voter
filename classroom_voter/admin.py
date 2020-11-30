import sys
import smtplib
import os
import ssl
import json
import random
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
import time
from classroom_voter.shared import database
from hashlib import sha256

dirname = os.path.dirname(__file__)
#db_path = os.path.join(dirname, 'shared/example.db.enc')
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shared/example.db.enc")
myDb = None

def welcome_email(recipient_id, recipient):
    """
        The welcome email that users will receive when they are added to system

        Args:
            recepient: The users unique identifier
    """

    print(recipient)

    first_name = recipient["firstName"]
    last_name = recipient["lastName"]
    user_id = recipient_id
    temporary_password = recipient["temporaryPassword"]
    classes = recipient["classes"]

    welcome_message = ("Hello " + first_name + " " + last_name + ". "
                       "Welcome to Classroom Voter.  This email contains your username, "
                       "password, and registered classes.  The next step for you is to "
                       "login using these credintials to finish setting up your account.\n\n"
                       "Username: " + user_id + "\n" + "Temporary Password: " +
                       temporary_password + "\n" + "Registered Classes: " + str(classes))

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

    for recipient_id in recipients:
        msg["To"] = recipient_id
        welcome_message = welcome_email(recipient_id, recipients[recipient_id])
        msg.attach(MIMEText(welcome_message))

        smtp.sendmail("classroomvoterAd@gmail.com",
                      recipient_id, msg.as_string())

    smtp.close()


def init_user(users, dbpass):    

    for userId in users.keys():
        newUser = users[userId]
        userType = newUser["type"]

        salt = str(random.randint(0, 4096))
        
        hashed_pass = sha256((newUser["temporaryPassword"] + salt).encode('utf-8')).hexdigest()
        for _ in range(10000):
            hashed_pass = sha256((hashed_pass).encode('utf-8')).hexdigest()
        
        user = {
            userId: {
                "role": userType,
                "firstName": newUser["firstName"],
                "lastName": newUser["lastName"],
                "password": hashed_pass,
                "salt": salt,
                "classes": newUser["classes"],
                "reedemed": False
            }
        }

        myDb.addUser(user)
    
def executeSQL(query):
    c = myDb.conn.cursor()

    c.execute(query)
    myDb.conn.commit()
    myDb.writeChanges()
    result = c.fetchall()
    return result


def main():
    global myDb
    if len(sys.argv) == 3:
        if sys.argv[1] == "--sql": 
            myDb = database.DatabaseSQL(db_path, sys.argv[2])
            while True:
                try:
                    query = input("SQL line: ")
                except EOFError:
                    print("Completed")
                    return
                result = executeSQL(query)
                print(result)
    elif len(sys.argv) < 8:
        print("Usage: ./admin.py db-password should-send-email(yes or no) email"
            " first-name last-name temp-password user-type classes")
        return
    dbpass = sys.argv[1]
    should_notify = sys.argv[2] == "yes"
    email = sys.argv[3]
    firstname = sys.argv[4]
    lastname = sys.argv[5]
    temp_password = sys.argv[6]
    user_type = sys.argv[7]
    classes = sys.argv[8:]

    try:
        myDb = database.DatabaseSQL(db_path, dbpass)
    except database.IncorrectPasswordException:
        return 0
    newUsers = {
        email: {
            "firstName": firstname,
            "lastName": lastname,
            "temporaryPassword": temp_password,
            "classes": classes,
            "type": user_type
        }
    }
    init_user(newUsers, dbpass)
    if should_notify:
        notify_users(newUsers)


if __name__ == "__main__":
    main()
