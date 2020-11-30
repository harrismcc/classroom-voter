"""This file holds classes/function to interact with the database"""
import sys
import json
import os
import io
import sqlite3
import datetime
import random
import struct
from hashlib import sha256
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random




# HELPER FUNCTIONS #

def _strToTime(s):

    if s is not None and s != "":
        return datetime.datetime.strptime(s, '%Y-%m-%d %H:%M:%S')
    else:
        return s

def _timeToStr(t):
    if t is not None:
        return datetime.datetime.strftime(t, '%Y-%m-%d %H:%M:%S')
    else:
        return t


class IncorrectPasswordException(Exception):
    pass

class DatabaseSQL(object):
    def __init__(self, fname, password):
        

        #if no file named fname
        
        self.encfname = fname
        self.key = self.getKey(password)
        self.keySize = 256
        
        if os.path.isfile(fname):
            self.fname = self.decrypt_file(fname) #get decrypted filename
        else:
            self.fname = fname[:-4]

        try:
            self.conn = sqlite3.connect(self.fname)
            self.cursor = self.conn.cursor()
        except sqlite3.OperationalError as e:
            print(e)
            self.conn = sqlite3.connect("testingDB.db")
            self.cursor = self.conn.cursor()
        self.conn = sqlite3.connect(self.fname, check_same_thread=False)
        self.cursor = self.conn.cursor()
        

        try:
            self.initTables()
        except sqlite3.DatabaseError as e:
            raise IncorrectPasswordException


    def pad(self, s):
        if type(s) == str:
            s = s.encode()
        return s + b"\0" * (AES.block_size - len(s) % AES.block_size)

    def encrypt(self, message):
        message = self.pad(message)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return iv + cipher.encrypt(message)

    def decrypt(self, ciphertext):
        iv = ciphertext[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        plaintext = cipher.decrypt(ciphertext[AES.block_size:])
        return plaintext.rstrip(b"\0")

    def encrypt_file(self, file_name):
        with open(file_name, 'rb') as fo:
            plaintext = fo.read()
        enc = self.encrypt(plaintext)
        with open(file_name + ".enc", 'wb') as fo:
            fo.write(enc)

    def decrypt_file(self, file_name):
        with open(file_name, 'rb') as fo:
            ciphertext = fo.read()
        dec = self.decrypt(ciphertext)
        with open(file_name[:-4], 'wb') as fo:
            fo.write(dec)
        return file_name[:-4]
    
    def getKey(self, password):
        """Gets a sha256 key from a password"""
        hasher = SHA256.new(password.encode('utf-8'))
        return hasher.digest()


    def addUser(self, userDict):   
        """
        Add a new user entry to the database
        ```json
        user-email : {
            "firstName" : first-name,
            "lastName" : last-name,
            "password" : password-hash,
            "salt": password-salt
            "classes" : {
                            "class-id" : poll-id-of-last-response,
                            "class-id" : poll-id-of-last-response,
                            ... 
                            "class-id" : poll-id-of-last-response,
                        },
            "reedemed" : false,
            "role" : "student"
            }
        ```
        Args:
            userDict (dict): A python dictionary representing a student entry
        Returns:
            int: id of n
        """
        email = list(userDict.keys())[0]

        vals = (email, userDict[email]['role'], userDict[email]['firstName'], 
                userDict[email]['lastName'], userDict[email]['password'], 
                userDict[email]['salt'], json.dumps(userDict[email]['classes']),
                userDict[email]['reedemed'], )
        try:
            result = self.cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?)", vals)
            self.conn.commit()
            self.writeChanges()
            #TODO: Make this return an ID
            return True
        except sqlite3.IntegrityError as e:
            return False


    def resetUserPassword(self, userId, newHash):
        """
        Resets a user's password has in the db to a new one

        Args:
            userId (string): user email
            newHas (string): new password hash
        Returns:
            boolean: success
        """

        return self.updateFieldViaId("users", userId, "hashedPassword", newHash)

    def updateFieldViaId(self, table, myId, field, newValue):
        """
        Updates a specific value for a specific entry. For example, to set a user's name:
        `updateFieldViaId('users', 'example@test.com', 'firstName', 'John')`
        Args:
            table (string): table name
            myId (unknown): id field (email or int)
            field (string): name of field to change
            newValue (string): value to place in field
        Returns:
            boolean: success

        """
        c = self.conn.cursor()

        ids = {
            "polls" : "pollId",
            "responses" : "responseId",
            "users" : "emailAddress",
            "classes" : "classId"
        }

        try:
            c.execute("UPDATE '"+ table +"' SET "+ field +" = '"+ newValue +"' WHERE "+ ids[table] +" = '"+ str(myId) + "'")
            self.conn.commit()
            self.writeChanges()
            return True
        except sqlite3.IntegrityError:
            return False


    def addPoll(self, pollObject):
        """
        Adds a new poll to the DB
        Args:
            pollObject (Poll): Poll object to add to the db
        Returns:
            boolean: True if inserted, False otherwise
        """
        

        c = self.conn.cursor()

        #pollId int primary key, start timestamp, end timestamp, ownerId text, classId number, pollJson text
        vals = (pollObject.startTime, pollObject.endTime, pollObject.ownerId, pollObject.classId, pollObject.question.toJson())
        try:
            c.execute("INSERT INTO polls VALUES (NULL, ?, ?, ?, ?, ?)", vals)
            self.conn.commit()
            self.writeChanges()
            return True
        except sqlite3.IntegrityError as e:
            return False

    def addClass(self, classDict):
        """
        Adds a new class to the database. Note: If a class already exists w/ the same information in the DB,
        this will create a new entry. If creating a class that might not be new, it may be worth checking if
        a that course name/code already exists first.
        ```json
        {
            "className": 'Into to Blah',
            "courseCode": 'UNIQ99',
            "students" : ["mrstudent@gmail.com"],
            "professors" : ["mrprof@gmail.com"],
            "polls": []
        }

        ```
        Args:
            classDict (dict): a dictionary with class information (see above)

        Returns:
            boolean: success ()
        """
        c = self.conn.cursor()


        vals = (classDict["className"], classDict["courseCode"], json.dumps(classDict["students"]),
                json.dumps(classDict["professors"]), json.dumps(classDict["polls"]))

        try:
            #classId int primary key, className text, courseCode text, students text, professors text, polls text
            c.execute("INSERT INTO classes VALUES (NULL, ?, ?, ?, ?, ?)", vals)
            self.conn.commit()
            self.writeChanges()
            return True
        except sqlite3.IntegrityError as e:
            return False

    def addResponse(self, userId, pollId, pollBody):
        """Adds a poll response to the dict"""

        c = self.conn.cursor()


        try:
            #responseId integer primary key autoincrement, userId text, pollId integer, responseBody text
            c.execute("INSERT INTO responses VALUES (null, ?, ?, ?)", (userId, pollId, pollBody))
            self.conn.commit()
            self.writeChanges()
            return True
        except sqlite3.IntegrityError as e:
            return False

    def getResponse(self, **kwargs):
        """
        Pulls a response/list of responses from the database
        Args:
            responseId (int): Id of the response to pull
            userId (string): Pulls all responses for that user
            pollId (int): Pulls all responses for that poll
        """

        #check kwargs
        if "responseId" in kwargs.keys():
            pass
        elif "userId" in kwargs.keys():
            pass
        elif "pollId" in kwargs.keys():
            pass
        else:
            raise Exception("Improper Argument passed: must be one of responseId, userId, or pollId")
            
    def getResponsesForPoll(self, pollId):
        """
            Pulls all reponses for a the given pollId from the database
            Args:
                pollId (int): Pulls all responses for that poll
        """
    
        c = self.conn.cursor()
        
        c.execute("SELECT responseBody FROM responses WHERE pollId=?", (pollId, ))
        results = c.fetchall()
        
        return results
        
    def getStudentResponseForPoll(self, userId, pollId):
        c = self.conn.cursor()
        
        c.execute("SELECT responseBody FROM responses where userId=? AND pollId=?", (userId, pollId, ))
        result = c.fetchone()
        
        return result[0]
            
    def _formatUser(self, studentTuple):
        out = {studentTuple[0] : {
            'role' : studentTuple[1],
            'firstName' : studentTuple[2],
            'lastName' : studentTuple[3],
            'password' : studentTuple[4],
            'salt' : studentTuple[5],
            'classes' : json.loads(studentTuple[6]),
            'reedemed' : studentTuple[7] != 0
        }}

        return out

    def getUser(self, email, roleFilter=None):
        """
        gets a user from the db based on user id (email)

        Args:
            email (string): user id (email)
            roleFilter (string): role to filter by
        """
        c = self.conn.cursor()


        if roleFilter is None:
            c.execute("SELECT * FROM users WHERE emailAddress=?", (email, ))
        else:
            c.execute("SELECT * FROM users WHERE emailAddress=? AND role=?", (email, roleFilter, ))
        result = c.fetchone()
        if result is not None:
            return self._formatUser(result)
        
    def _formatPoll(self, pollTuple):
        d = json.loads(pollTuple[5])

        out = {
            'question': d,
            'pollId' : pollTuple[0],
            'startTime' : pollTuple[1],
            'endTime' : pollTuple[2],
            'ownerId' : pollTuple[3],
            'classId' : pollTuple[4],
            'responses': []}
        return out


    def getPollFromId(self, pollId):
        """ Get poll from DB with the pollId (int) """
        c = self.conn.cursor()

        c.execute("SELECT * FROM polls WHERE pollId=?", (pollId, ))
        result = c.fetchone()

        if result is not None:
            return self._formatPoll(result)

    def getPollsForUser(self, userId, classId=None):
        """
        Gets all polls for user in database
        Args:
            userId (string): Id string of use

        Returns:
            list: list of poll dicts, can be converted to Poll objects with Poll.fromDict()
        """
        c = self.conn.cursor()

        polls = []

        #first, get a users class id's
        c.execute("SELECT classes FROM users WHERE emailAddress=?", (userId, ))
        result = c.fetchone()

        if result is not None:
            classes = json.loads(result[0])
        else:
            return None
        
        #if class filter was set, only look at polls from that class id
        if classId in classes:
            classes = [classId]
        
        #iterate through class list
        for currentClassId in classes:
            #for each class id, grab all associated polls
            c.execute("SELECT * FROM polls WHERE classId=?", (currentClassId, ))
            result = c.fetchall()

            for pollTuple in result:
                polls.append(self._formatPoll(pollTuple))
        
        return polls

    def getAnsweredPollIdsForUser(self, userId):
        """
        get a list of poll Id's for which the user userId has a response
        Args:
            userId (string): Id of user to get Answered polls
        
        Returns:
            int[]: list of poll id's to which userId has answered
        """
        c = self.conn.cursor()

        c.execute("SELECT pollId FROM responses WHERE userId=?", (userId, ))
        result = c.fetchall()
        out = [r[0] for r in result]

        return out

  



    def _formatClass(self, classTuple):
        print(classTuple)
        out = { 
                "classId": classTuple[0],
                "className": classTuple[1],
                "courseCode": classTuple[2],
                "students" : json.loads(classTuple[3]),
                "professors" : json.loads(classTuple[4]),
                "polls": json.loads(classTuple[5])
            }

        return out

    def getClassFromId(self, classId):
        """ Get Class from DB with the classId (int) """
        c = self.conn.cursor()

        c.execute("SELECT * FROM classes WHERE classId=?", (classId, ))
        result = c.fetchone()
        
        if result is not None:
            return self._formatClass(result)



    def getClassFromCourseCode(self, courseCode):
        """ get Class/s from DB with the course code (string) """
        c = self.conn.cursor()

        c.execute('SELECT * FROM classes WHERE courseCode=?', (courseCode, ))
        results = c.fetchall()

        if results is not None:
            out = {}
            for result in results:
                out[result[0]] = self._formatClass(result)
            return out

    def _listStringFormat(self, l):
        """Formats lists into the proper string for sql queries"""
        if len(l) == 0:
            return "()"
        
        s = "("

        for element in l:
            s += "'" + element + "',"

        s = s[0:-1] #strip last comma
        s += ")"
        return s

    def _getUsersInClass(self, classId, role):

        #Verify inputs - no funny stuff in the sql, keep it safe
        if type(classId) is not int:
            raise TypeError("classId must be int")
        elif type(role) is not str:
            raise TypeError("classId must be int")

        c = self.conn.cursor()
        out = {}
        #first pull class

        if role == "students":
            sql = "SELECT classes.students FROM classes WHERE classId=?"
        else:
            sql = "SELECT classes.professors FROM classes WHERE classId=?"
        c.execute(sql, (classId,))
        result = c.fetchone()

        if result is not None:
            #get student's array
            users = json.loads(result[0])
            #return students rows
            sql = "SELECT * FROM users WHERE users.emailAddress IN " + self._listStringFormat(users) + " AND users.role='" + role + "'"
            c.execute(sql)
            result = c.fetchall()
            for user in result:

                user = self._formatUser(user)
                out[list(user.keys())[0]] = user[list(user.keys())[0]]

        return out

    def getStudentsInClass(self, classId):
        """
        Gets the emails of all students in class w/ id classId
        Args:
            classId (int): id of class
        Returns:
            list: json array of students
        """
        return self._getUsersInClass(classId, "students")
    
    def getProfsInClass(self, classId):
        """
        Gets the emails of all profs in class w/ id classId
        Args:
            classId (int): id of class
        Returns:
            list: json array of profs
        """
        return self._getUsersInClass(classId, "professors")


    def executeSelect(self, query, args=()):
        """
        Wrapper for the execution of simple SQL select querys.

        Important that any dynamic/substituted values are done using the "?" syntax and
        NOT via python string concatination. For example:
        Wrong:
        "SELECT * FROM classes WHERE name=" + name
        Right
        "SELECT * FROM classes WHERE name=?", args=(name, )

        Args:
            query (string): SQL query to execute (with optional ? substitutions)
            args (tuple): Orderd tuple of substitution values
        """
        print(query, args)
        c = self.conn.cursor()
        c.execute(query, args)
        result = c.fetchall()
        return result



    def writeChanges(self):
        #re-encrypt db file
        self.encrypt_file(self.fname)
        
    def __del__(self):

        #close db connection
        self.conn.close()
        #remove un-encrypted file
        os.remove(self.fname)
    

    def initTables(self):
        """Creates new tables if they don't exist yet"""
        c = self.conn.cursor()

        #Create Users
        c.execute('''CREATE TABLE IF NOT EXISTS users(
            emailAddress text, role text, firstName text, lastName text,
            hashedPassword text, salt text, classes text, reedemed boolean)''')

        #Create Polls
        c.execute(''' CREATE TABLE IF NOT EXISTS polls (
            pollId integer primary key autoincrement, start timestamp, end timestamp, ownerId text, classId number, pollQuestion text
            )''')

        #Create Classes
        c.execute(''' CREATE TABLE IF NOT EXISTS classes (
            classId integer primary key autoincrement, className text, courseCode text, students text, professors text, polls text
            )''')

        #Create Responses
        c.execute(''' CREATE TABLE IF NOT EXISTS responses (
            responseId integer primary key autoincrement, userId text, pollId integer, responseBody text
            )''')

        self.writeChanges()

if __name__ == "__main__":

    password = input("Enter db password: ") #it's 'password'

    try:
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "example.db.enc")
        test = DatabaseSQL(db_path, password)
    except IncorrectPasswordException:
        print("Incorrect DB password")

        #This is important, if the db has an incorrect password then the program needs
        #to quit. further use of the DB object will have undefined behavior (errors)
        test = None 

    print(test.getClassFromId(1))