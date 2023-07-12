export VIV_VER=2021.2
export SDA_VER=2021.2
source with-sdaccel
export PATH="/share/suhailb/Projects/ampl.linux-intel64:$PATH"

export GUROBI_HOME=/home/suhailb/gurobi950/linux64
export GRB_LICENSE_FILE=/home/suhailb/gurobi.lic
export PATH="${PATH}:${GUROBI_HOME}/bin"
export LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:${GUROBI_HOME}/lib"

export TAPA_CONCURRENCY=16
echo 'done'