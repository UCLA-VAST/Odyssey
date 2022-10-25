export VIV_VER=2021.2
export SDA_VER=2021.2
source with-sdaccel
export AUTOSA_ROOT=/home/suhailb/Projects/Odyssey/AutoSA
export PRJ_PATH=$(pwd)
export PATH="/share/suhailb/Projects/ampl.linux-intel64:$PATH"

# mkdir designs/mod_logs
# mkdir designs/orig_logs
# if designs/mod does not exist, create it
# if [ ! -d "designs/mod" ]; then
#   mkdir designs/mod
# fi
# if designs/orig does not exist, create it
if [ ! -d "designs/mm/orig" ]; then
  mkdir -p designs/mm/orig
  mkdir designs/mm/logs
fi
if [ ! -d "designs/conv/orig" ]; then
  mkdir -p designs/conv/orig
  mkdir designs/conv/logs
fi
# cp -r scripts/all/* designs/mod/
# cp -r scripts/all/* designs/orig/
conda deactivate
echo 'done'