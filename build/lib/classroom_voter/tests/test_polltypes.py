""" Tests all of the functionality in shared.pollTypes"""
import json
import unittest
import os
import sys
import random

sys.path.append(os.path.dirname(__file__)) #gets pdoc working

from classroom_voter.shared.pollTypes import *




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




if __name__ == '__main__':

    unittest.main()