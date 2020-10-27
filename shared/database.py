"""This file holds classes/function to interact with the database"""
import sys
import json
import os



class Database:
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


    def addStudent(self, studentDict):
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
            studentDict (dict): A python dictionary representing a student entry

        Returns:
            boolean: Success of database insertion
        """
        studentId = list(studentDict.keys())[0]

        if not self.keyExists(studentId, ["users", "students"]):
            self.myDict["users"]["students"][studentId] = studentDict[studentId]
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

    def getField(self, fieldList):

        d = self.myDict

        for field in fieldList:
            d = d[field]

        return d

    def keyExists(self, key, fieldList):
        """
        Check if key exists in db
        """

        d = self.getField(fieldList)
        keys = list(d.keys())

        return key in keys

if __name__ == "__main__":
    #test files

    test = Database("database.json")

    new_users = {
            "testEmail123@gmail.com" : {
                "firstName" : "John",
                "lastName" : "Doe",
                "password" : "hashyhashy",
                "classes" : {
                                "class-id" : "123"
                            },
                "reedemed" :False,
            }}


    print(test.addStudent(new_users))

    print(test.getField(["users", "students"]))

    print(test.keyExists("douglaswebster1122@gmail.com", ["users", "students"]))

