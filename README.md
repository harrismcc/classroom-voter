# Classroom Voter
Classroom Voter is a secure LAN based polling system, similar to iClicker, which allows teachers to administer live polls. To start a poll, the teacher simply has to run the host program on their local machine. To join, students run the client program and enter the teachers IP address. Students can respond to questions via clients on their machines. 

Traffic is sent over HTTP on the local network. The system provides instructors with the ability to take polls while providing controllable levels of anonymity for students. For example, a teacher might make one question anonymized so that their view of the poll results just shows the number of students who voted for each option. Another poll might be transparent, and the instructor can see which participant voted for which option.

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


# Usage

After classroom voter is install, it can be run via the command line. To login as a student or professor, run 
```
python -m classroom_voter.login
```
This will prompt you first for the ip address and port of the server (given to you by the professor/ system admin), and then for your username and password (check your email)