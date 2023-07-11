SRC=$1/src

clang -Xclang -v -Xclang -load -Xclang $prj_path/gen/passes/addBraces.so    -Xclang -plugin -Xclang MyPass $SRC/kernel_kernel.cpp   -I/opt/tools/xilinx/Vitis_HLS/2021.2/include/ > $SRC/tmp.cpp
clang -Xclang -v -Xclang -load -Xclang $prj_path/gen/passes/fixIfLoops.so   -Xclang -plugin -Xclang MyPass $SRC/tmp.cpp             -I/opt/tools/xilinx/Vitis_HLS/2021.2/include/ > $SRC/tmp1.cpp
clang -Xclang -v -Xclang -load -Xclang $prj_path/gen/passes/libMyPass.so    -Xclang -plugin -Xclang MyPass $SRC/tmp1.cpp            -I/opt/tools/xilinx/Vitis_HLS/2021.2/include/ > $SRC/tmp2.cpp
bcpp -fi $SRC/tmp2.cpp -fo $SRC/kernel_kernel.cpp -bcl
# rm $SRC/tmp.cpp $SRC/tmp1.cpp $SRC/tmp2.cpp
