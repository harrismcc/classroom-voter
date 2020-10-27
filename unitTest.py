""" This file runs a series of unit test on the Classes defined in `pollTypes` """
import json
import unittest
import os
import sys
import random

sys.path.append(os.path.dirname(__file__)) #gets pdoc working

from shared.pollTypes import *
from shared.database import *




class PollCreationTests(unittest.TestCase):
    def setUp(self):
        self.d = {
                    'question': {
                        'prompt': 'What is your favorite color?',
                        "answer" : None,
                        'options': [],
                        'type': 'FreeResponseQuestion'
                        },
                    'startTime' : "2020-10-27 13:04:05",
                    'endTime' : "2025-10-27 13:04:05",
                    'ownerId' : 'test@gmail.com',
                    'classId' : 0,
                    'responses': []}
        self.myPoll = Poll.fromDict(self.d)

    def test_SimplePollCreation(self):
        myPoll = Poll(None)
        self.assertIsInstance(myPoll, Poll)

    def test_PollCreateFromdDict(self):
        self.assertIsInstance(self.myPoll, Poll)
        self.assertIsInstance(self.myPoll.question, PollQuestion)
        self.assertEqual(self.myPoll.responses, [])
        self.assertEqual(self.myPoll.toDict(), self.d)




class QuestionCreationTests(unittest.TestCase):

    def setUp(self):
        self.testDict = {'answer' : "Answer Item", 'options': [], 'prompt': 'What is your favorite color?', 'type': 'PollQuestion'}
        self.myGenericQuestion = PollQuestion.fromDict(self.testDict)
    
    def test_PollQuestion(self):
        prompt = "What is your favorite color?"
        myGenericQuestion = PollQuestion(prompt)

        #test correct type
        self.assertIsInstance(myGenericQuestion, PollQuestion)

        #test prompt
        self.assertEqual(myGenericQuestion.prompt, prompt)

    def test_PollQuestion_Dict(self):
        """ Tests fromDict and toDict methods of PollQuestion """
        self.assertIsInstance(self.myGenericQuestion, PollQuestion)
        self.assertEqual(self.myGenericQuestion.prompt, self.testDict["prompt"])
        self.assertEqual(self.testDict, self.myGenericQuestion.toDict(answerIncluded=True))

    def test_CreationWithOptions(self):
        newDict = self.testDict
        newDict["options"] = ["Red", "Blue"] 
        self.assertEqual(PollQuestion.fromDict(newDict).options, ["Red", "Blue"])

    def test_FreeResponseQuestion(self):
        prompt = "What is your favorite color?"
        myFreeQuestion = FreeResponseQuestion(prompt)

        self.assertIsInstance(myFreeQuestion, FreeResponseQuestion)

    def test_MultipleChoiceQuestion(self):
        prompt = "What is your favorite color?"
        myMultQuestion = MultipleChoiceQuestion(prompt, ["Red", "Blue", "Green"])
        myMultQuestion.setAnswer("Redsdd")


class PollResponseCreationTests(unittest.TestCase):
    def setUp(self):
        self.body = "This is my answer"
        self.resp = PollResponse(self.body)

    def test_createRegular(self):
        self.assertIsInstance(self.resp, PollResponse)
        self.assertEqual(self.resp.responseBody, self.body)

    def test_createWithFromDict(self):
        d1 = {"responseBody" : "no anon level"}
        d2 = {"responseBody" : "anon level 5", "anonLevel": 5}
        respNoAnon = PollResponse.fromDict(d1)
        self.assertIsInstance(respNoAnon, PollResponse)
        self.assertEqual(respNoAnon.anonLevel, 0)

        respAnon = PollResponse.fromDict(d2)
        self.assertIsInstance(respAnon, PollResponse)
        self.assertEqual(respAnon.anonLevel, 5)
    
    def test_addAnswer(self):
        resp = PollResponse("body")
        self.assertEqual(resp.responseBody, "body")

    def test_fromBytes(self):
        b = self.resp.toBytes()
        #self.assertIsInstance(b, )

        

class PollMethodsTesting(unittest.TestCase):

    def setUp(self):
        self.d = {
                    'question': {
                        'prompt': 'What is your favorite color?',
                        "answer" : None,
                        'options': [],
                        'type': 'FreeResponseQuestion'
                        },
                    'responses': [],
                    'startTime' : "2020-10-27 13:04:05",
                    'endTime' : "2025-10-27 13:04:05",
                    'ownerId' : 'test@gmail.com',
                    'classId' : 0,
                    }
        self.myPoll = Poll.fromDict(self.d)

    def test_PollResponseAddition(self):
        resp = PollResponse("Red")

        self.assertIsInstance(self.myPoll, Poll)
        self.assertIsInstance(resp, PollResponse)
        self.assertEqual(self.myPoll.responses, [])

        self.myPoll.addResponse(resp)
        self.assertEqual(self.myPoll.responses, [resp])

        self.assertRaises(TypeError, self.myPoll.addResponse, "Not a response object")

    def test_toDict(self):
        self.assertEqual(self.myPoll.toDict(), self.d)

    def test_toJson(self):
        self.assertEqual(self.myPoll.toJson(), json.dumps(self.d))

    def test_toBytes(self):
        self.assertEqual(self.myPoll.toBytes(), json.dumps(self.d).encode())

class DatabaseSQLTesting(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        #remove test db
        try:
            os.remove("./shared/testingDB.db")
        except FileNotFoundError:
            pass
        #load up db
        cls.db = DatabaseSQL("./shared/testingDB.db")

    @classmethod
    def tearDownClass(cls):
        pass

    def test_addStudentToDB(self):
        student = {
        "test@gmail.com" : {
                "firstName" : "John",
                "lastName" : "Doe",
                "password" : "ecd4d1aad41a446759d25de6c830d60cc3c8548be9760f0babe03094e6a59ee3",
                "classes" : [12, 1442, 123],
                "reedemed" : True,
                "role" : "professor"
            }
        }

        #test add user to db
        self.assertTrue(self.db.addUser(student))

        #test pull that user from the db
        result = self.db.getUser("test@gmail.com")
        self.assertEqual(student, result)

        #test pull to nothing
        result = self.db.getUser("notindb")
        self.assertFalse(result)

        #test change value
        result = self.db.updateFieldViaId("users", "test@gmail.com", "firstName", "NewName")
        self.assertTrue(result)
        student["test@gmail.com"]["firstName"] = "NewName"

        self.assertEqual(student, self.db.getUser("test@gmail.com"))
    
    def test_addClassToDB(self):
        classD = {
            "className": 'Into to Blah',
            "courseCode": 'UNIQ99',
            "students" : [],
            "professors" : [],
            "polls": []
        }

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
        d = {
            'question': {
                'prompt': 'What is your favorite color?',
                "answer" : None, 
                'options': [], 
                'type': 'FreeResponseQuestion'
                },
            'startTime' : "2020-10-27 16:25:07",
            'endTime' : "2025-10-27 16:25:07",
            'ownerId' : 'bebop@yahoo.com',
            'classId' : 0,
            'responses': []}

        poll = Poll.fromDict(d)
        self.assertTrue(self.db.addPoll(poll))

        self.assertEqual(d, self.db.getPollFromId(1))


    def test_addResponseToDB(self):
        pass

    def test_searchDBByField(self):
        pass


if __name__ == '__main__':

    unittest.main()