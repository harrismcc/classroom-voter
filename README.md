# Classroom Voter
Classroom Voter is a secure LAN based polling system, similar to iClicker, which allows teachers to administer live polls. To start a poll, the teacher simply has to run the host program on their local machine. To join, students run the client program and enter the teachers IP address. Students can respond to questions via clients on their machines. 

Traffic is sent over HTTP on the local network. The system provides instructors with the ability to take polls and see how the students answer.

# Installation

## Automatic
This package is distributed via TestPyPI (Test, since the project is still in beta). The [latest version](https://test.pypi.org/project/classroom-voter-harrismcc/) can be installed via pip:
```
pip3 install --index-url https://test.pypi.org/simple classroom-voter-harrismcc
```
## Manual
### Linux/OSX
From the [latest release](https://github.com/harrismcc/classroom-voter/releases/), download the file that looks like `classroom_voter_harrismcc-VERSION.tar.gz`. Next, use pip to install with the following command (making sure that the directory with the .tar.gz file is the active directoy):
```
pip install classroom_voter_harrismcc-VERSION.tar.gz`
```
### Windows
From the [latest release](https://github.com/harrismcc/classroom-voter/releases/), download the file that looks like `classroom_voter_harrismcc-VERSION.whl`. Next, use pip to install with the following command (making sure that the directory with the .tar.gz file is the active directoy):
```
pip install classroom_voter_harrismcc-VERSION.whl`
```
or
```
python -m pip install classroom_voter_harrismcc-VERSION.whl
```

# Setup and Administration

The first thing the sysadmin should do when setting up Classroom Voter is to create a new certificate and private key for the server.
Using OpenSSL in the "shared" directory, run

```
openssl req -x509 -newkey rsa:4096 -keyout privkey.pem -out newcert.pem -days 365 -subj "/C=US/ST=California/L=Claremont/O=Classroom Voter/CN=classroom.voter"

```
It will prompt for a password for the key - remember this, because without it the private key cannot be decrypted and the server cannot be used.

Then, they will need to initialize the users database by running the admin script in one of two configurations:

```
python -m classroom_voter.admin db-password should-send-email(yes or no) email first-name last-name temp-password user-type classes```

ex:

python -m classroom_voter.admin password yes example@gmail.com Example Student abc123 student 1
```

lets you create a user, in the example 'Example student', whose account is tied to an email address. The first time you run this code will initialize
```
python -m classroom_voter.admin --sql path-to-database
```
lets you run sql commands directly on the database and perform minor edits

This will let you insert arbitrary sql into the database, such as creating a
class initialized with a few users:
```
admin="python3 -m classroom_voter.admin"
printf "INSERT OR REPLACE into classes VALUES (0, 'Security', 'cs181', '[\"student@gmail.com\"]', '[\"prof@gmail.com\"]', '[]')\n" | eval $admin --sql db_pswd
```


When all users are created, the server can be run:
```
python -m classroom_voter.server <port>
```
it will prompt for your database password and private key passwords, then run indefinitely. Supply the ip and port it is running on to your professors, who can pass it to the students.

N.B. if you need to run the administrator script, you must first stop the server, and restart it when you're done, as otherwise they compete for database access.

Note 2: if you need to debug the server, there are print statments commented out with "#[debug]", simply find and replace that. However, this displays plaintext passwords, and should not be used for logging. 


# Client Usage

After classroom voter is installed, it can be run via the command line. To login as a student or professor, run 
```
python -m classroom_voter.login
```
This will prompt you first for the ip address and port of the server (given to you by the professor/ system admin), and then for your username and password (check your email)
