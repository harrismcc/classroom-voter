
class Poll:
    """ The poll object, represents an entire poll and it's responses """
    def __init__(self):
        print(type(self))




class PollResponse:
    
    """ The parent class for a Poll Response """
    def __init__(self, question, anon_level):
        """
        Creates a new PollResponse object 

        Args:
            self (undefined):
            question (PollQuestion): The poll question contained in the poll response
            anon_level (tbd): The anonymity level to encode this question with

        """
        self.question = question


    def verifyQuestionAnswer(self):
        """
        Detirmines if question is properly answered (node: this is
        not the same as correctly answered. This function just makes sure
        the answer is present and of the correct data type)
        Returns:
            bool: true if answer is not null and of correct type
        """
        pass




class PollQuestion:
    """ Parent class for a poll question - Informal Interface"""
    def __init__(self, prompt):
        self.prompt = prompt
        self.answer = None


    def getPrompt(self):
        """
        returns the question prompt as a string

        Returns:
            string: the question prompt    
        """
        return self.prompt

    def setAnswer(self, answer):
        """
        takes in an answer and sets it

        Args:
            self (answer type): could be string, int, bool
            answer (undefined): an answer of the correct type

        Returns:
            bool: true/false if this answer replaced an existing one

        """
        self.answer = answer


    def __repr__(self):
        return self.getPrompt() + "\n" + str(self.answer)


class FreeResponse(PollQuestion):
    """
    Poll Question object for a free-response answer type. Empty since FreeResponse is the same as the template.

    Inheritance:
        PollQuestion:

    """
    pass 



class MultipleChoice(PollQuestion):
    """
    Poll Question object for a multiple choice answer type

    Inheritance:
        PollQuestion:

    """
    def __init__(self, prompt, options):
        """
        Construct a new MultipleChoice object

        Args:
            prompt (string): the question prompt
            options (undefined): a list (>2 items) of answer choices

        """
        self.prompt = prompt
        self.answer = None
        self.options = options


   

    def getPrompt(self):
        """gets the prompt
                Args:
                    self (self): the object

                Returns:
                    string: value to print out to represent the prompt
        """
        ret = self.prompt + "\n"


        for i, answer in enumerate(self.options):
            ret += "[{}]: {}\n".format(i, answer)
        
        return ret

    #takes in an answer and sets it
    #   Args:
    #       answer - int - the index of the correct answer
    #   Returns:
    #       bool - true/false if this answer replaced an existing one
    def setAnswer(self, answer):
        self.answer = answer

    #helper function to get the index of an option by looking up the string
    def getIndexOfOption(self, str):
        pass



