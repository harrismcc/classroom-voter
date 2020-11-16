from tkinter import *
import json
import asyncio
from login import *
from client import VoterClient # pylint: disable=import-error
from shared.pollTypes import PollResponse # pylint: disable=import-error

def displayErrorWindow(master, message):
    """Displays an error window with the message and an OK button"""
    window = Toplevel(master)
    window.attributes("-topmost", True)

    label = Label(window, text=message)
    label.pack()

    okButton = Button(window, text="OK", command=window.destroy)
    okButton.pack()
    
    

class MasterGui(object):
    def __init__(self, master=None):
        if master == None:
            self.master = Tk()
        else:
            self.master = master
        self.master.title("Classroom Voter")
        

        self.loginWindow('localhost', 1337)
        self.master.mainloop()
        
    def clear(self):
        for l in self.master.grid_slaves():
            l.destroy()

    def loginWindow(self, ip, port):
        canvas = Canvas(self.master)
        canvas.pack()
        loginWindow = LoginGui(canvas, ip, port)


        while loginWindow.result == None or loginWindow.result["Arguments"]["result"] != 'success':
            #Keep login window open if result is None or bad login
            self.master.update_idletasks()
            self.master.update()
        else:
            #Open up the client GUI if login is successfull
            self.startClient(loginWindow.login.clientSocket, loginWindow.result)
    

    def startClient(self, conn, result):
        """Starts a new client session, takes in an auth'd client connection"""
        canvas = Canvas(self.master)
        canvas.pack()
        client = ClientGui(canvas, conn, result)




class ClientGui(object):
    def __init__(self, master, conn, loginResult):
        self.loginResult = loginResult
        self.conn = conn
        self.client = VoterClient(conn, cli=False)
        self.master = master

        #Internal map of all poll objects
        self.currentPolls = []

        #Poll List
        self.pollList = Listbox(master)
        self.pollList.pack()
        
        #Test button
        self.selectPollButton = Button(master, text="Select Poll", command=self.selectPoll)
        self.selectPollButton.pack()

        #Refresh button
        self.refreshButton = Button(master, text="Refresh", command=self.refresh)
        self.refreshButton.pack()
        
        #refresh on load
        self.refresh()

    def selectPoll(self):
        index = self.pollList.curselection()[0]
        print(self.currentPolls[index])

        newTop = Toplevel(self.master)
        AnswerPoll(newTop, self.currentPolls[index], self.client)
        self.refresh()


    def refresh(self):
        resp = self.client.sendServerEndpoint("Get_polls_for_user", {"username": "harrismcc+student@gmail.com", "role": "students", "filter": "active"})
        if resp is not None:
            #clear list
            self.pollList.delete(0, 'end')
            self.currentPolls = resp
            for poll in resp:
                prompt = poll["question"]['prompt']
                self.pollList.insert(END, prompt)

    def populateList(self):
        for i in range(30):
            self.pollList.insert(END, "a list entry"+str(i))


class AnswerPoll(object):
    def __init__(self, master, pollDict, client):
        self.master = master
        self.client = client
        self.pollDict = pollDict
        self.poll = Poll.fromDict(pollDict)

        self.test = Label(self.master, text=self.pollDict["question"]["prompt"])
        self.test.pack()

        if self.pollDict["question"]["type"] == "FreeResponseQuestion":
            #create text box for response
            self.responseBox = Text(self.master)
            self.responseBox.pack()

            #create submit button
            self.submit = Button(self.master, text="Submit", command=self.submitResp)
            self.submit.pack()
        else:
            pass

    def submitResp(self):
        print(self.responseBox.get("1.0",END))
        resp = PollResponse(self.responseBox.get("1.0",END))

        self.client.sendResponse(resp, self.pollDict["pollId"])

        self.master.destroy()





class LoginGui(object):
    def __init__(self, master, ip, port):

        #Establish new login session
        self.login = LoginTools(ip, port)
        self.master = master
        self.result = None

        if self.login.connected:

            self.label = Label(master, text="Welcome to Classroom Voter!", wraplength=250)

            self.usernameField = Entry(master)
            self.passwordField = Entry(master, show="*")

            self.loginButton = Button(master, text="Login", command=self.submit)

            self.forgotPasswordButton = Button(master, text="Forgot Passoword", command=master.quit)
            
            self.label.grid(columnspan=3, sticky=W, padx=(10,10), pady=(10,10))
            self.usernameField.grid(columnspan=3, padx=(30, 30), pady=(5,0))
            self.passwordField.grid(columnspan=3, padx=(30, 30), pady=(0,5))
            self.loginButton.grid(row=4, column=1)
            self.forgotPasswordButton.grid(row=5, column=1)
        else:
            #Connection failed
            displayErrorWindow(master, "Connection to Server Failed")
            
    def submit(self):
        self.username = self.usernameField.get()
        self.password = self.passwordField.get()
        result = self.checkCreds()
        if result["Arguments"]["result"] == 'success':
            self.displayMessage("Correct Password")
            self.master.destroy()
            self.result = result
        else:
            self.displayMessage("Username or Password incorrect")

    def checkCreds(self):
        return self.login.attempt_login(self.username, self.password)

    def displayMessage(self, message):
        """Displays the message at the top of the login box"""
        self.label.config(text=message)
        

if __name__ == "__main__":
    gui = MasterGui()

    

