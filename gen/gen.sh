design_name=$1
sa_sizes=$2
target=$3
mem_type=$4
workload=$5
design_path=$PRJ_PATH/designs

rm $design_path/$workload/orig/$design_name -rf
# rm $design_path/mod/$design_name -rf

mkdir -p $design_path/$workload/orig/$design_name/src
mkdir $design_path/$workload/orig/$design_name/latency_est
mkdir $design_path/$workload/orig/$design_name/resource_est
mkdir $design_path/$workload/orig/$design_name/tuning

# mkdir -p $design_path/mod/$design_name
# mkdir $design_path/mod/$design_name/latency_est
# mkdir $design_path/mod/$design_name/resource_est
# mkdir $design_path/mod/$design_name/tuning
# echo $AUTOSA_ROOT/autosa $PRJ_PATH/workloads/$workload/kernel.c \\ > $design_name.sh
# echo  --config=$AUTOSA_ROOT/autosa_config/autosa_config.json \\ >> $design_name.sh
# echo  --target=$target \\ >> $design_name.sh
# echo  --output-dir=$design_path/orig/$design_name \\ >> $design_name.sh
# echo  --simd-info=$PRJ_PATH/workloads/$workload/simd_info.json \\ >> $design_name.sh
# echo  --host-serialize \\ >> $design_name.sh
# echo  --hls \\ >> $design_name.sh
# echo  --uram=$mem_type \\ >> $design_name.sh
# echo  --param-names=$PRJ_PATH/workloads/$workload/param_names.json \\ >> $design_name.sh
# echo  --sa-sizes=\"$sa_sizes\" >> $design_name.sh

$AUTOSA_ROOT/autosa $PRJ_PATH/workloads/$workload/kernel.c \
  --config=$AUTOSA_ROOT/autosa_config/autosa_config.json \
  --target=$target \
  --output-dir=$design_path/$workload/orig/$design_name \
  --simd-info=$PRJ_PATH/workloads/$workload/simd_info.json \
  --host-serialize \
  --hls \
  --uram=$mem_type \
  --param-names=$PRJ_PATH/workloads/$workload/param_names.json \
  --sa-sizes="$sa_sizes"

# if target==autosa_hls_c, else if target==autosa_tapa
if [ "$target" = "autosa_hls_c" ]; then
  echo "Copying HLS C scripts..."
  cp -r $PRJ_PATH/scripts/hls/* $design_path/$workload/orig/$design_name/
elif [ "$target" = "autosa_tapa" ]; then
  echo "Copying TAPA scripts..."
  cp $PRJ_PATH/scripts/tapa/* $design_path/$workload/orig/$design_name/
fi

# cp -r $design_path/orig/$design_name $design_path/mod/

# $PRJ_PATH/gen/run_passes.sh $design_path/mod/$design_name