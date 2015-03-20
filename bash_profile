# Clear screen
/usr/bin/clear

# Graphical console pre-start hook
if [ -x /usr/sbin/gconsole-setup ]; then
    sudo /usr/sbin/gconsole-setup
fi

# Make sure ClearOS API is available
echo -n "Starting ClearOS API."
COUNTER=0
while [  $COUNTER -lt 20 ]; do
    echo -n "."
    curl http://127.0.0.1:82 >/dev/null 2>&1
    if [ $? == 0 ]; then
        COUNTER=20
    else
        let COUNTER=COUNTER+1
    fi
    # Do sleep at the end since we're only checking for a socket connection, not an API call
    sleep 1
done

# Run tconsole
/usr/sbin/tconsole
exit
