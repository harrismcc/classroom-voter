
class Poll:
    """ The poll object, represents an entire poll and it's responses """
    def __init__(self):
        print(type(self))




class PollResponse:
    
    """ The parent class for a Poll Response """
    def __init__(self, question, anon_level):
        """ Description
        :type question: PollQuestion
        :param question: The poll question contained in the poll response

        :type anon_level: tbd
        :param anon_level: The anonymity level to encode this question with
        """
        self.question = question


    def verifyQuestionAnswer(self):
        """ Detirmines if question is properly answered (node: this is
        not the same as correctly answered. This function just makes sure
        the answer is present and of the correct data type)
        :rtype: bool
        """
        pass




class PollQuestion:
    """ Parent class for a poll question - Informal Interface"""
    def __init__(self, prompt):
        self.prompt = prompt
        self.answer = None


    def getPrompt(self):
        """ returns the question prompt as a string
        :rtype: string
        """
        return self.prompt

    def setAnswer(self, answer):
        """ takes in an answer and sets it

        :type answer: answer type
        :param answer: an answer of the correct type
    
        :return: true/false if this answer replaced an existing one
        :rtype: bool
        """    
        self.answer = answer


    def __repr__(self):
        return self.getPrompt() + "\n" + str(self.answer)


class FreeResponse(PollQuestion):
    
    """ Poll Question object for a free-response answer type. Empty since FreeResponse is the same as the template. """
    pass 



class MultipleChoice(PollQuestion):
    """ Poll Question object for a multiple choice answer type	"""
    def __init__(self, prompt, options):
        """ Construct a new MultipleChoice object

        :type prompt: string
        :param prompt: the question prompt
    
        :type options: list
        :param options: a list (>2 items) of answer choices
        """    
        self.prompt = prompt
        self.answer = None
        self.options = options


   

    def getPrompt(self):
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



