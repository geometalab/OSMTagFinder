#!/bin/bash
### BEGIN INIT INFO
# Provides:          tagfinder
# Required-Start:    $all
# Required-Stop:
# Default-Start:     2 3 4 5
# Default-Stop:
# Short-Description: TagFinder Start Stop Restart
### END INIT INFO
# processname: tagfinder
# chkconfig: 234 20 80
# location: /opt/OSMTagFinder/tagfinder.sh

TAGFINDER_HOME=/opt/OSMTagFinder/OSMTagFinder
export TAGFINDER_HOME

case $1 in
start)
echo "Starting TagFinder"
python $TAGFINDER_HOME/server.py &
;;
stop)
echo "Stopping TagFinder"
kill -9 $(pgrep -f server.py)
;;
restart)