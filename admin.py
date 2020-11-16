#!/usr/bin/env python3
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
from shared import database # pylint: disable=import-error
from hashlib import sha256


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


def init_user(users):
    dirname = os.path.dirname(__file__)
    db_path = os.path.join(dirname, 'shared/example.db')
    myDb = database.DatabaseSQL(db_path)

    for userId in users.keys():
        newUser = users[userId]
        userType = newUser["type"]

        salt = str(random.randint(0, 4096))
        hashed_pass = sha256((newUser["temporaryPassword"] + salt).encode('utf-8')).hexdigest()

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


def main():
    if len(sys.argv) < 8:
        print("Usage: ./admin.py should-send-email(yes or no) email"
              " first-name last-name temp-password user-type classes")
        return
    should_notify = sys.argv[1] == "yes"
    email = sys.argv[2]
    firstname = sys.argv[3]
    lastname = sys.argv[4]
    temp_password = sys.argv[5]
    user_type = sys.argv[6]
    classes = sys.argv[7:]
    newUsers = {
        email: {
            "firstName": firstname,
            "lastName": lastname,
            "temporaryPassword": temp_password,
            "classes": classes,
            "type": user_type
        }
    }
    init_user(newUsers)
    if should_notify:
        notify_users(newUsers)


if __name__ == "__main__":
    main()
