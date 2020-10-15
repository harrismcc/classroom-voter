# Classroom Voter


## Objects

### Poll Object
The poll object is created by the server, and represents the entire poll. This means that it holds information about the poll questions and config options, as well as the responses.

### Poll Response Object
The poll Response object holds the response to a poll question. It can be configured to operate in the appropriate anonymitiy mode, and can self-check answer types. Additionally, it has functions that allow it to be encoded and transmitted over the internet so that it can be re-constructed by the server.

## Communication Structure
Professor makes a Poll which is then encapsulates in an AnnouncePoll request.  The message is encrypted with a symmetric key shared by the professor and server and sent to the server.

`AnnouncePoll Request`
```json
{
    "endpoint" : "Announce-poll", 
    "arguments" : {
        "start-time" : start-time,
        "end-time" : end-time,
        "poll-id" : poll-id,
        "professor-id" : professor-id,
        "class-id" : class-id,
        "poll" : {
            "question": {
                "prompt": "What is your name?", 
                "answer": None,
                "options": None, 
                "type": "FreeResponseQuestion"
            }, 
            "responses": []
        }
    }
}
```

The server receives a message from a professor and decrypts the message using the shared key.  Once the message is decrypted the server matches against the endpoint which tells it what to do with the message.  

If the message endpoint is AnnouncePoll the server will do the following:
(1) Save the poll in the database
(2) Query the database to find all of the students in the class
(3) Encrypt the message using the shared key between server and the student
(4) Send encrypted poll to each student

`Send Poll To Student`
```json
{
    "endpoint" : "Student-poll", 
    "arguments" : {
        "start-time" : start-time,
        "end-time" : end-time,
        "poll-id" : poll-id,
        "professor-name" : professor-name,
        "class-name" : class-name,
        "poll" : {
            "question": {
                "prompt": "What is your name?", 
                "answer": None,
                "options": None, 
                "type": "FreeResponseQuestion"
            }, 
            "responses": []
        }
    }
}
```

The student receive a message from the server and decrypt the message using the shared key between server and student.  The student notices they have received a poll and generates a PollResponse.  The response is then encrypted with the shared key and sent back to the server.

`Poll Response`
```json
{
    "endpoint" : "Poll-response", 
    "arguments" : {
        "poll-id" : poll-id,
        "student-id" : student-id,
        "response-time" : response-time,
        "poll-response" : {
            "response-body" : response-body,
            "annoninimty-level" : annononimity-level
        }
    }
    
}
``` 

The server receives a message from a student and decrypts the message using the shared key between student and server.  The server uses the students id and the poll id to make sure that the student is enrolled in the class.  Then checks to see if the response was recorded between the poll start and end time.  If the poll is anonymous the students id is stripped from the response.  Then the students response is added to the responses for the respective poll id.

The professor can request an aggregate of the responses for a given poll.  The PollAggregate request is encrypted using the shared key between the professor and server and sent to the server

`Aggregate Poll`
```json
{
    "endpoint" : "Aggregate-poll", 
    "arguments" : {
        "poll-id" : poll-id,
    }
    
}
```

The server receives a message from a professor and decrypts the message using the shared key.  Once the message is decrypted the server matches against the endpoint which tells it what to do with the message. 

If the message endpoint is AggregatePoll the server will do the following:
(1) Query the poll id
(2) Retrieve the responses
(3) Encrypt the message using the shared key between server and the student
(4) Send encrypted results to the professor

Lastly, the professor receives a message from the server.  The message is decrypted using the shared key between the server and professor.  Once decrypted the results are displayed to the professor.




## Database Structure
```json

{
    "users" : {
        "students" : {
            student-id : {
                "name" : name,
                "username" : username-hash,
                "password" : password-hash,
                "public-key" : 12345,
                "classes" : [class-id, class-id, ..., class-id]
            },
            student-id : {
                "name" : name,
                "username" : username-hash,
                "password" : password-hash,
                "public-key" : 12345,
                "classes" : [class-id, class-id, ..., class-id]
            }
        },

        "professors" : {
            professor-id : {
                "name" : name,
                "username" : username-hash,
                "password" : password-hash,
                "public-key" : 12345,
                "classes" : [class-id, class-id, ..., class-id]
            },
            professor-id : {
                "public-key" : 12345,
                "classes" : [class-id, class-id, ..., class-id]
            }
        }
    },

    "polls" : {
        poll-id : {
            "start" : time-stamp,
            "end" : time-stamp,
            "professor-id" : professor-id,
            "class-id" : class-id,
            "poll" : PollObject
        },
        poll-id : {
            "start" : time-stamp,
            "end" : time-stamp,
            "professor-id" : professor-id,
            "class-id" : class-id,
            "poll" : PollObject
        }
    },

    "classes" : {
        class-id : {
            "name" : name,
            "students" : [student-id, student-id, ..., student-id],
            "professor" : [professor-id, professor-id, ..., professor-id],
            "polls" : [poll-id, poll-id, ..., poll-id]
        }, 
        class-id : {
            "name" : name,
            "students" : [student-id, student-id, ..., student-id],
            "professor" : [professor-id, professor-id, ..., professor-id],
            "polls" : [poll-id, poll-id, ..., poll-id]
        }
    }
}

```

