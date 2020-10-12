import json


class Poll:
    """
    The poll object, represents an entire poll and it's responses
    TODO: read in from file, export to json, import from json
    """
    def __init__(self, question):

        self.question = question
        """PollQuestion: The question the poll is asking"""
        self.responses = []
        """PollResponse[]: An array of the responses recorded by the student"""

    @classmethod
    def fromDict(cls, inDict):
        """
        Instantiates a new Poll object using a python dictionary containing Poll object data
        Args:
            inDict (dict): The dictionary containting the poll object information

        """
        #Here we make sure to create the correct PollQuestion type
        if inDict["question"]["type"] == "MultipleChoiceQuestion":
            out = cls(MultipleChoiceQuestion.fromDict(inDict["question"]))
        else:
            out = cls(FreeResponseQuestion.fromDict(inDict["question"]))

        #Here we populate the responses list, creating new response objects for each dict respresentation of a response
        for response in inDict["responses"]:
            out.responses.appned(PollResponse.fromDict(response))

        return out

    @classmethod
    def fromJson(cls, inJson):
        """
        Instantiates a new Poll object using a json string containing Poll object data
        Args:
            inJson (string): The json containting the poll object information
        """

        return cls.fromDict(json.loads(inJson))

    @classmethod
    def fromBytes(cls, inBytes):
        """
        Instantiates a new Poll object using a json string containing Poll object data
        Args:
            inBytes (bytes): The bytes containting the json poll object information
        """
        return cls.fromJson(inBytes.decode())

    def toDict(self):
        """
        converts the Poll object into a dictionary that represents the object
        Note that this does not include the poll responses

        {
            question : string
        }

        Returns:
            dict: The Poll object as a python dict

        """
        out = {}

        out["question"] = self.question.toDict()
        out["responses"] = []

        for response in self.responses:
            out["responses"].append(response.toDict())

        return out

    def toJson(self):
        """
        Converts the object into a json string

        Returns:
            string: Json representaiton of object
        """
        return json.dumps(self.toDict())

    def toBytes(self):
        """
        Converts the object into a byte array

        Returns:
            bytes: bytearray representation of object
        """
        return json.dumps(self.toDict()).encode()

    def addResponse(self, response):
        """ Adds a new poll response object to this Poll's responses list """
        if isinstance(response, PollResponse):
            self.responses.append(response)
        else:
            raise TypeError("addResponse requires a PollResponse object")

    def getPrompt(self):
        """" 
        Returns the prompt for the question
        
        Returns:
            prompt: string question prompt
        """
        return self.question.getPrompt()

class PollResponse:
    
    """ The parent class for a Poll Response """
    def __init__(self, responseBody, anonLevel=0):
        """
        Creates a new PollResponse object

        Args:
            responseBody(string): The body of the poll response
            anonLevel (tbd): The anonymity level to encode this question with

        """
        self.responseBody = responseBody
        self.anonLevel = anonLevel

    @classmethod
    def fromDict(cls, inDict):
        """
        Instantiates a new PollResponse object using a python dictionary containing
        PollResponse object data
        Args:
            inDict (dict): The dictionary containting the poll object information

        """
        if "anonLevel" in inDict.keys():
            return cls(responseBody=inDict["responseBody"], anonLevel=inDict["anonLevel"])
        else:
            return cls(responseBody=inDict["responseBody"])
    
    @classmethod
    def fromJson(cls, inJson):
        """
        Instantiates a new Poll object using a json string containing Poll object data
        Args:
            inJson (string): The json containting the poll object information
        """

        return cls.fromDict(json.loads(inJson))

    @classmethod
    def fromBytes(cls, inBytes):
        """
        Instantiates a new Poll object using a json string containing Poll object data
        Args:
            inBytes (bytes): The bytes containting the json poll object information
        """
        return cls.fromJson(inBytes.decode())
    
    def toDict(self):
        """
        Converts the object into a python dictionary

        Returns:
            dict: dictionary representation of object
        """
        return vars(self)

    def toJson(self):
        """
        Converts the object into a json string

        Returns:
            string: Json representaiton of object
        """
        return json.dumps(self.toDict())

    def toBytes(self):
        """
        Converts the object into a byte array

        Returns:
            bytes: bytearray representation of object
        """
        return self.toJson().encode()

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
    """ Parent class for a poll question - Informal Interface, should not be called directly"""
    def __init__(self, prompt, answer=None, options=None):
        self.prompt = prompt
        self.answer = answer
        self.options = options
    
    @classmethod
    def fromDict(cls, inDict):
        """ Constructs the PollQuestion object using a dictionary """

        return cls(inDict["prompt"], answer=inDict["answer"], options=inDict["options"])

    @classmethod
    def fromJson(cls, inJson):
        """
        Instantiates a new Poll object using a json string containing Poll object data
        Args:
            inJson (string): The json containting the poll object information
        """

        return cls.fromDict(json.loads(inJson))

    @classmethod
    def fromBytes(cls, inBytes):
        """
        Instantiates a new Poll object using a json string containing Poll object data
        Args:
            inBytes (bytes): The bytes containting the json poll object information
        """
        return cls.fromJson(inBytes.decode())

    def toDict(self):
        """
        Converts the PollQuestion object into a python dictionary

        Returns:
            dict: dictionary representaion of PollQuestion
        """
        out = {}

        out["prompt"] = self.prompt
        out["answer"] = self.answer
        out["options"] = self.options
        out["type"] = type(self).__name__
        
        return out
    
    def toJson(self):
        """
        Converts the object into a json string

        Returns:
            string: Json representaiton of object
        """
        return json.dumps(self.toDict())

    def toBytes(self):
        """
        Converts the object into a byte array

        Returns:
            bytes: bytearray representation of object
        """
        return self.toJson().encode()  

    def getPrompt(self):
        """
        returns the question prompt as a string

        Returns:
            string: the question prompt    
        """
        return self.prompt

    def setAnswer(self, answer):
        """
        takes in an answer and sets it. If the PollQuestion has options set, then this answer must be
        int options

        Args:
            self (answer type): could be string, int, bool
            answer (undefined): an answer of the correct type
        
        Returns:
            bool: true if answer was successfully set, false otherwise

        """
        if (answer in self.options or self.options == []):
            self.answer = answer
            return True
        return False


    def __repr__(self):
        return self.getPrompt() + "\n" + str(self.answer)

""" Begin Poll Question Child Types """
class FreeResponseQuestion(PollQuestion):
    """
    Poll Question object for a free-response answer type. Empty since FreeResponseQuestion is the same as the template.

    Inheritance:
        PollQuestion:

    """
    pass 
class MultipleChoiceQuestion(PollQuestion):
    """
    Poll Question object for a multiple choice answer type

    Inheritance:
        PollQuestion:

    """
    def __init__(self, prompt, options):
        """
        Construct a new MultipleChoiceQuestion object

        Args:
            prompt (string): the question prompt
            options (undefined): a list (>2 items) of answer choices

        """
        self.prompt = prompt
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


    #helper function to get the index of an option by looking up the string
    def getIndexOfOption(self, str):
        return self.options.index(str)



