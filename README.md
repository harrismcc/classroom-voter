# classroom-voter




## Poll Object
The poll object is created by the server, and represents the entire poll. This means that it holds information about the poll questions and config options, as well as the responses.

## Poll Response Object
The poll Response object holds the response to a poll question. It can be configured to operate in the appropriate anonymitiy mode, and can self-check answer types. Additionally, it has functions that allow it to be encoded and transmitted over the internet so that it can be re-constructed by the server.

