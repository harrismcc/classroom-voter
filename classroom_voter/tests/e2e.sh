#!/bin/sh
# cd "$(dirname "$0")"
trap 'kill $(jobs -p)' EXIT

printf "* Testsuite configuration\n"

# cleanup
find . \( -name '*.out' -o -name '*.out' \) -delete
[ "$1" = 'clean' ] && exit 0

# ## ========= Declare the entities ========= ##

professor="python3 -m classroom_voter.login"
student="python3 -m classroom_voter.login"
admin="python3 -m classroom_voter.admin"
server="python3 -m classroom_voter.server"

# Define counters
success=0
fail=0

for test in $(find . -type f -name '*.student' | sort -n)
    do
    profinput="${test%.student}.prof"
    profoutput="${test%.student}.prof.out"
    studentoutput="${test%.student}.student.out"
    profexpected="${test%.student}.prof.expected"
    studentexpected="${test%.student}.student.expected"
    rm -f ./classroom_voter/shared/example.db* $profoutput $studentoutput
    printf "INSERT OR REPLACE into classes VALUES (0, 'Security', 'cs181', '[\"student@gmail.com\"]', '[\"prof@gmail.com\"]', '[]')\n" | eval $admin --sql db_pswd
    eval $admin db_pswd no student@gmail.com Jill Student temp_pswd students 0
    eval $admin db_pswd no prof@gmail.com Jack Professor temp_pswd professors 0

    # Kill the old server, if running
    kill -9 $(lsof -t -i:1500) > /dev/null 2>&1
    echo "db_pswd" | eval $server 1500  >> server.logs &
    # echo "db_pswd" | eval $server 1500  &
    serverPID=$!

    sleep 1.0
    rm /tmp/proffifo
    mkfifo /tmp/proffifo
    tail -f /tmp/proffifo | eval $professor >> $profoutput &

    rm /tmp/studentfifo
    mkfifo /tmp/studentfifo
    tail -f /tmp/studentfifo | eval $student >> $studentoutput &

    # echo localhost > /tmp/proffifo
    lineno=0
    paste -d '\n' $test $profinput |
    while IFS= read -r line; do 
        lineno=$((lineno+1));
        [ -z "$line" ] && continue
        if [[ $((lineno%2)) -eq 1 ]] 
        then 
            echo "$line" >> $studentoutput
            echo "$line" >> /tmp/studentfifo; 
        else 
            echo "$line" >> $profoutput
            echo "$line" >> /tmp/proffifo; 
        fi
        sleep .25
    done

    # Finish by shutting down the server
    kill $serverPID

    DIFF="$(diff $studentoutput $studentexpected)$(diff $profoutput $profexpected)"
    if [ "$DIFF" != "" ] 
    then
        printf "Testcase failed: %s OR %s" $studentoutput  $profoutput
        fail=$(($fail+1))
    else
        success=$(($success+1))
    fi



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
