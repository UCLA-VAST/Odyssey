rm $PRJ_PATH/tests/tmp/outputs/* -rf
echo "Running genetic-mp tests"
python $PRJ_PATH/src/randomized_methods/main.py \
  --workload=$1 \
  --objective=$2 \
  --designs=$3 \
  --stop-after-time=$4 \
  --alpha=$5 \
  --cst=u250   \
  --unit-task-method='genetic' \
  --outdir=$PRJ_PATH/tests/tmp/outputs/  
