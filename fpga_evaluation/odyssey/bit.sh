# get name of current directory
currDir=`pwd | sed 's/.*\///'`
screen -S $currDir -dm bash -c  "source env.sh; make run_csim &> csim.log"