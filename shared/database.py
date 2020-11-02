"""This file holds classes/function to interact with the database"""
import sys
import json
import os
import sqlite3
import datetime





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

class Database(object):

        
    def __init__(self, fname='database.json'):
        """
        Database constructor, open database file and create new on if none exists
        
        Args:
            fname (string): filename of database file
        """
        if not os.path.isfile(fname):
            print("File doesn't exist")
            self.createNewDatabase(fname)
        self.fname = fname

        try:
            self.myFile = open(fname, 'r+')
            self.myDict = json.load(self.myFile)
        except FileNotFoundError:
            print("Is this pdoc? Setting manual path. If this is being run by a real person - STOP HERE!")
            self.fname = "/home/siim/Desktop/cs181s/classroom-voter/shared/database.json"
            os.chdir("/home/siim/Desktop/cs181s/classroom-voter")
            self.myFile = open(fname, 'r+')
            self.myDict = json.load(self.myFile)

        
        self.users = self.getField(["users"])
        self.students = self.getField(["users", "students"])
        self.professors = self.getField(["users", "professors"])
        
        
    def __del__(self):
        """Database destructor, close the open file"""
        self.myFile.close()

    def updateFile(self):
        """ Updates the database file to match memory """
        self.myFile.seek(0) #seek to start of file
        self.myFile.truncate() #erase contents
        json.dump(self.myDict, self.myFile) #overwrite


    def createNewDatabase(self, fname='database.json'):
        """
        Creates a new empty database file

        Args:
            fname (string): filename of database file
        """
        d = {
            "users" : {
                "students" : {},
                "professors" : {}
            },
            "polls" : {},
            "classes" : {},
        }

        print("writing file to " + fname)
        print(os.listdir())
        try:
            with open(fname, "w+") as f:
                f.write(json.dumps(d))
        except FileNotFoundError:
            print('FileNotFound')


    def addStudent(self, userDict):
        """
        Add a new student entry to the database

        ```json
        student-email : {
            "firstName" : first-name,
            "lastName" : last-name,
            "password" : password-hash,
            "classes" : {
                            "class-id" : poll-id-of-last-response,
                            "class-id" : poll-id-of-last-response,
                            ... 
                            "class-id" : poll-id-of-last-response,
                        },
            "reedemed" : false,
            }
        ```

        Args:
            userDict (dict): A python dictionary representing a student entry

        Returns:
            boolean: Success of database insertion
        """
        studentId = list(userDict.keys())[0]

        if not self.keyExists(studentId, ["users", "students"]):
            self.myDict["users"]["students"][studentId] = userDict[studentId]
            self.updateFile()
            return True
        else:
            return False

    

    def addProfessor(self, professorDict):
        """
        Add a new professor entry to the database.

        ```json
        professor-email : {
                "firstName" : first-name,
                "lastName" : last-name,
                "password" : password-hash,
                "classes" : [class-id, class-id, ..., class-id],
                "reedemed" : false,
            }
        ```

        Args:
            professorDict (dict): A python dictionary representing a professor entry

        Returns:
            boolean: Success of database insertion
        """
        profId = list(professorDict.keys())[0]

        if not self.keyExists(profId, ["users", "professors"]):
            self.myDict["users"]["professors"][profId] = professorDict[profId]
            self.updateFile()
            return True
        else:
            return False

    def addPoll(self, pollDict):
        pass

    def addClass(self, classDict):
        pass

    def getStudent(self, studentId):
        """
        Gets a student from the db using their student id

        Args:
            studentId (string): student email

        Returns:
            dict: student object (None if student doesn't exist)
        """

        return self.getField(["users", "students", studentId])


    def getField(self, fieldList):

        d = self.myDict
        try:
            for field in fieldList:
                d = d[field]
        except KeyError:
            #field/key not real
            return {}

        return d

    def keyExists(self, key, fieldList):
        """
        Check if key exists in db
        """

        d = self.getField(fieldList)
        keys = list(d.keys())

        return key in keys


class DatabaseSQL(object):
    def __init__(self, fname='example.db'):
        self.fname = fname
        try:
            self.conn = sqlite3.connect(fname)
            self.cursor = self.conn.cursor()
        except sqlite3.OperationalError as e:
            print(e)
            self.conn = sqlite3.connect("testingDB.db")
            self.cursor = self.conn.cursor()
        self.initTables()


    def addUser(self, userDict):
        
        """
        Add a new user entry to the database

        ```json
        user-email : {
            "firstName" : first-name,
            "lastName" : last-name,
            "password" : password-hash,
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
                json.dumps(userDict[email]['classes']), userDict[email]['reedemed'], )
        try:
            result = self.cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?)", vals)
            self.conn.commit()
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
            return True
        except sqlite3.IntegrityError as e:
            return False


    def _formatUser(self, studentTuple):
        out = {studentTuple[0] : {
            'role' : studentTuple[1],
            'firstName' : studentTuple[2],
            'lastName' : studentTuple[3],
            'password' : studentTuple[4],
            'classes' : json.loads(studentTuple[5]),
            'reedemed' : studentTuple[6] != 0
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


    def _formatClass(self, classTuple):
        out = {
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




        
    def __del__(self):
        self.conn.close()

    def initTables(self):
        """Creates new tables if they don't exist yet"""
        c = self.conn.cursor()

        #Create Users
        c.execute('''CREATE TABLE IF NOT EXISTS users(
            emailAddress text, role text, firstName text, lastName text, hashedPassword text, classes text, reedemed boolean, 
            primary key (emailAddress, role))''')

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
            responseId integer primary key autoincrement, userId text, responseBody text
            )''')

