rm ./tmp/outputs/* -rf
# echo "Running Odyssey new_tests"
python $PRJ_PATH/src/main.py \
  --workload=$1 \
  --objective=$2 \
  --designs=$3 \
  --stop-after-time=10 \
  --cst=u250   \
  --unit-task-method='genetic' \
  --outdir=$PRJ_PATH/new_tests/tmp/outputs/  
