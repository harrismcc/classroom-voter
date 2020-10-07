from types import *
import unittest


class QuestionCreationTests(unittest.TestCase):
    
    def test_PollQuestion(self):
        prompt = "What is your favorite color?"
        myGenericQuestion = PollQuestion(prompt)

        #test correct type
        self.assertIsInstance(myGenericQuestion, PollQuestion)

        #test prompt
        self.assertEqual(myGenericQuestion.prompt)





myFreeQuestion = FreeResponse(prompt)
myMultQuestion = MultipleChoice(prompt, ["Red", "Blue", "Green"])
myMultQuestion.setAnswer("Redsdd")



myPoll = Poll(myMultQuestion)

print(myPoll.toDict())