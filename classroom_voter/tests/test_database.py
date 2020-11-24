"""Tests all of the functionality in shared.database"""

import json
import unittest
import os
import random
from classroom_voter.shared.database import *
from classroom_voter.shared.pollTypes import *


class DatabaseSQLTesting(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):

        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "testingTB.db.enc")

        #remove test db
        try:
            os.remove(db_path)
        except:
            pass
        #load up db
        
        cls.db = DatabaseSQL(db_path, "password")

        cls.userTemplate = {
        "test@gmail.com" : {
                "firstName" : "John",
                "lastName" : "Doe",
                "password" : "ecd4d1aad41a446759d25de6c830d60cc3c8548be9760f0babe03094e6a59ee3",
                'salt' : '',
                "classes" : [12, 1442, 123],
                "reedemed" : True,
                "role" : "professors"
            }
        }

        cls.classTemplate = {
            'classId' : 1,
            "className": 'Into to Blah',
            "courseCode": 'UNIQ99',
            "students" : ["mrstudent@gmail.com"],
            "professors" : ["mrprof@gmail.com"],
            "polls": []
        }

        cls.pollTemplate = {
            'question': {
                'prompt': 'What is your favorite color?',
                "answer" : None, 
                'options': [], 
                'type': 'FreeResponseQuestion'
                },
            'startTime' : "2020-10-27 16:25:07",
            'endTime' : "2025-10-27 16:25:07",
            'ownerId' : 'bebop@yahoo.com',
            'pollId' : 1,
            'classId' : 0,
            'responses': []}
        

    @classmethod
    def tearDownClass(cls):
        pass

    def test_addStudentToDB(self):
        student = self.userTemplate
        def students_are_equal_modulo_salt(a, b):
            for email in a:
                for k in a[email]:
                    if k != "password" and k != "salt" and a[email][k] != b[email][k]:
                        return False
            return True

        #test add user to db
        self.assertTrue(self.db.addUser(student))

        #test pull that user from the db
        result = self.db.getUser("test@gmail.com")
        self.assertTrue(students_are_equal_modulo_salt(student, result))

        #test pull to nothing
        result = self.db.getUser("notindb")
        self.assertFalse(result)

        #test change value
        result = self.db.updateFieldViaId("users", "test@gmail.com", "firstName", "NewName")
        self.assertTrue(result)
        student["test@gmail.com"]["firstName"] = "NewName"

        self.assertTrue(students_are_equal_modulo_salt(student, self.db.getUser("test@gmail.com")))
    
    def test_addClassToDB(self):
        classD = self.classTemplate

        #add class to db
        self.assertTrue(self.db.addClass(classD))

        #Pull class via id
        result = self.db.getClassFromId(1)
        self.assertEqual(classD, result)

        #pull class via course id
        result = self.db.getClassFromCourseCode("UNIQ99")
        self.assertEqual(classD, result[1])

        #test change value
        result = self.db.updateFieldViaId("classes", 1, "courseCode", "YEE555")
        self.assertTrue(result)
        classD["courseCode"] = "YEE555"

        self.assertEqual(classD, self.db.getClassFromId(1))

    def test_addPollToDB(self):
        d = self.pollTemplate

        poll = Poll.fromDict(d)
        self.assertTrue(self.db.addPoll(poll))

        self.assertEqual(d, self.db.getPollFromId(1))


    def test_addResponseToDB(self):
        pass

    def test_getUsersOfClass(self):
        """This test asserts that profs and students can be successfully indexed from classes"""
        self.maxDiff = None
        newStudent = self.userTemplate
        newStudent["mrstudent@gmail.com"] = newStudent.pop(list(newStudent.keys())[0])
        newStudent[list(newStudent.keys())[0]]['role'] = "students"
        self.db.addUser(newStudent)

        newProf = self.userTemplate
        newProf["mrprof@gmail.com"] = newProf.pop(list(newProf.keys())[0])
        newProf[list(newStudent.keys())[0]]['firstName'] = "ProfJohn"
        newProf[list(newStudent.keys())[0]]['role'] = "professors"
        self.db.addUser(newProf)


        st = self.db.getStudentsInClass(1)
        self.assertEqual(len(st.keys()), 1)
        self.assertEqual(list(st.keys())[0], "mrstudent@gmail.com")


        pf = self.db.getProfsInClass(1)
        self.assertEqual(len(pf.keys()), 1)
        self.assertEqual(list(pf.keys())[0], "mrprof@gmail.com")

if __name__ == '__main__':
    
    unittest.main()