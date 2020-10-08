
''' Needed to get docs to work, for some reason '''
import sys
sys.path.append("/home/siim/Desktop/cs181s/classroom-voter/shared")

from pollTypes import *
import unittest


class PollCreationTests(unittest.TestCase):
    def test_SimplePollCreation(self):
        myPoll = Poll(None)
        self.assertIsInstance(myPoll, Poll)

    def test_PollCreateFromdDict(self):
        d = {'question': {'prompt': 'What is your favorite color?', 'answer': None, 'options': [], 'type': 'FreeResponse'}, 'responses': []}
        myPoll = Poll.fromDict(d)

        self.assertIsInstance(myPoll, Poll)
        self.assertIsInstance(myPoll.question, PollQuestion)
        self.assertEqual(myPoll.responses, [])
        self.assertEqual(myPoll.toDict(), d)

class QuestionCreationTests(unittest.TestCase):
    
    def test_PollQuestion(self):
        prompt = "What is your favorite color?"
        myGenericQuestion = PollQuestion(prompt)

        #test correct type
        self.assertIsInstance(myGenericQuestion, PollQuestion)

        #test prompt
        self.assertEqual(myGenericQuestion.prompt, prompt)

    def test_PollQuestion_Dict(self):
        """ Tests fromDict and toDict methods of PollQuestion """

        testDict = {'prompt': 'What is your favorite color?', 'answer': None, 'options': [], 'type': 'PollQuestion'}
        myGenericQuestion = PollQuestion.fromDict(testDict)

        self.assertIsInstance(myGenericQuestion, PollQuestion)
        self.assertEqual(myGenericQuestion.prompt, testDict["prompt"])
        self.assertEqual(testDict, myGenericQuestion.toDict())

    def test_FreeResponseQuestion(self):
        prompt = "What is your favorite color?"
        myFreeQuestion = FreeResponse(prompt)

    def test_MultipleChoiceQuestion(self):
        prompt = "What is your favorite color?"
        myMultQuestion = MultipleChoice(prompt, ["Red", "Blue", "Green"])
        myMultQuestion.setAnswer("Redsdd")




if __name__ == '__main__':

    unittest.main()