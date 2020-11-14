#!/bin/sh
cd "$(dirname "$0")"
trap 'kill $(jobs -p)' EXIT

printf "* Testsuite configuration\n"

# cleanup
find . \( -name '*.out' -o -name '*.out' \) -delete
[ "$1" = 'clean' ] && exit 0

# ## ========= Declare the entities ========= ##

professor=../login.py
student=../login.py
admin=../admin.py
server=../server.py

# Define counters
success=0
fail=0

for test in $(find . -type f -name '*.in' | sort -n)
    do
    profinput="${test%.in}.prof"
    profoutput="${test%.in}.prof.out"
    studentoutput="${test%.in}.student.out"
    rm -f ../shared/example.db profoutput studentoutput
    ../admin.py no student@gmail.com Jill Student temp_pswd students cs181
    ../admin.py no prof@gmail.com Jack Professor temp_pswd professors cs181

    # Kill the old server, if running
    kill -9 $(lsof -t -i:1500) > /dev/null 2>&1
    $server 1500  >> server.logs &
    serverPID=$!

    sleep 1.0
    rm /tmp/proffifo
    mkfifo /tmp/proffifo
    tail -f /tmp/proffifo | $professor >> $profoutput &

    rm /tmp/studentfifo
    mkfifo /tmp/studentfifo
    tail -f /tmp/studentfifo | $student >> $studentoutput &

    # echo localhost > /tmp/proffifo
    lineno=0
    paste -d '\n' $test $profinput |
    while IFS= read -r line; do 
        lineno=$((lineno+1));
        [ -z "$line" ] && continue
        if [[ $((lineno%2)) -eq 1 ]] 
        then 
            echo "$line" >> /tmp/studentfifo; 
            echo "$line" >> $studentoutput
        else 
            echo "$line" >> /tmp/proffifo; 
            echo "$line" >> $profoutput
        fi
        sleep .5
    done

    # Finish by shutting down the server
    kill $serverPID
    wait

    printf "%s\n" $profinput
    done

printf '* Summary:
 --------------------------
| Passed | Failed | Total |
|--------|--------|-------|
|    %3d |    %3d |   %3d | %s
--------------------------\n' \
       "$success" "$fail" "$((success + fail))"

if [ "$fail" -gt 0 ]
then
    exit 2
else
    printf "\n         ----------------\n"
    printf "         Congratulations!\n"
    printf "         ----------------\n"
    exit 0
fi
