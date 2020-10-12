""" This file runs a series of unit test on the Classes defined in `pollTypes` """
import json
import unittest
import os
import sys
sys.path.append(os.path.dirname(__file__)) #gets pdoc working

from shared.pollTypes import *



class PollCreationTests(unittest.TestCase):
    def setUp(self):
        self.d = {'question': {'prompt': 'What is your favorite color?', 'answer': None, 'options': [], 'type': 'FreeResponseQuestion'}, 'responses': []}
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
        self.testDict = {'prompt': 'What is your favorite color?', 'answer': None, 'options': [], 'type': 'PollQuestion'}
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
        self.assertEqual(self.testDict, self.myGenericQuestion.toDict())

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
        pass

    def test_createRegular(self):
        body = "This is my answer"
        resp = PollResponse(body)
        self.assertIsInstance(resp, PollResponse)
        self.assertEqual(resp.responseBody, body)

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
        pass

        

class PollMethodsTesting(unittest.TestCase):

    def getDummyPoll(self):
        d = {'question': {'prompt': 'What is your favorite color?', 'answer': None, 'options': ["Red", "Blue"], 'type': 'FreeResponseQuestion'}, 'responses': []}
        myPoll = Poll.fromDict(d)
        return myPoll

    def test_PollResponseAddition(self):
        myPoll = self.getDummyPoll()
        resp = PollResponse("Red")

        self.assertIsInstance(myPoll, Poll)
        self.assertIsInstance(resp, PollResponse)
        self.assertEqual(myPoll.responses, [])

        myPoll.addResponse(resp)
        self.assertEqual(myPoll.responses, [resp])

        self.assertRaises(TypeError, myPoll.addResponse, "Not a response object")

    def test_toDict(self):
        d = {'question': {'prompt': 'What is your favorite color?', 'answer': None, 'options': ["Red", "Blue"], 'type': 'FreeResponseQuestion'}, 'responses': []}
        myPoll = self.getDummyPoll()
        self.assertEqual(myPoll.toDict(), d)

    def test_toJson(self):
        d = {'question': {'prompt': 'What is your favorite color?', 'answer': None, 'options': ["Red", "Blue"], 'type': 'FreeResponseQuestion'}, 'responses': []}
        j = json.dumps(d)
        myPoll = self.getDummyPoll()
        self.assertEqual(myPoll.toJson(), j)

    def test_toBytes(self):
        d = {'question': {'prompt': 'What is your favorite color?', 'answer': None, 'options': ["Red", "Blue"], 'type': 'FreeResponseQuestion'}, 'responses': []}
        j = json.dumps(d)
        b = j.encode()
        myPoll = self.getDummyPoll()
        self.assertEqual(myPoll.toBytes(), b)

if __name__ == '__main__':

    unittest.main()