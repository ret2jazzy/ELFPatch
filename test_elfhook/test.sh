do_test() {
    local bits="$1"

    echo
    echo "Testing $bits bits"

    echo "Compiling victim"
    gcc -Wall -Wextra -O0 -ggdb3 -m"$bits" -o victim victim.c
    
    echo "Compiling hook"
    gcc -Wall -Wextra -static-pie -O0 -ggdb3 -m"$bits" -o hook hook.c

    echo "Patching"
    ../elfhook.py victim hook

    echo "Testing"
    output="$(timeout 10 ./victim.patched)"
    expected="$(echo -e 'init\nvictim starting\nhook #1: victim\nhook #2: victim\nhook #3: ')"
    if [ "$output" == "$expected" ]; then
        echo "Test passed"
    else
        echo "Test failed"
        echo "----- Output -----"
        echo "$output"
        echo "------------------"
    fi

    # echo "Cleaning up"
    # rm -f victim hook victim.patched
}

do_test 32
do_test 64
