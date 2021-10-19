#!/bin/bash

function secs_to_human() {
  time="$(( ${1} / 3600 ))h $(( (${1} / 60) % 60 ))m $(( ${1} % 60 ))s"
}

LOOP_AMOUNT=$1
QUERY=$2
OFFSET=$3
COMMAND="python3 scholar/scholar-fetch.py $QUERY $OFFSET"
 
TOTAL_STARTTIME=$(date +%s)
for (( i=0; i<$LOOP_AMOUNT; i++ ))
do
  RUN_STARTTIME=$(date +%s);
  echo "Run ${i}";
  echo $COMMAND;
  $($COMMAND);
  RUN_ENDTIME=$(date +%s);

  secs_to_human $(($RUN_ENDTIME - $RUN_STARTTIME));
  echo "Run time: $time";
done
TOTAL_ENDTIME=$(date +%s)

secs_to_human $(($TOTAL_ENDTIME - $TOTAL_STARTTIME))
echo "Total time: $time"
