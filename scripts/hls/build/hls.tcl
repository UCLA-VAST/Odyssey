############################################################
## This file is generated automatically by Vivado HLS.
## Please DO NOT edit it.
## Copyright (C) 1986-2019 Xilinx, Inc. All Rights Reserved.
############################################################
open_project [lindex $argv 1]
set_top [lindex $argv 1]
add_files ../src/kernel_kernel.h
add_files ../src/kernel_kernel.cpp
add_files -tb ../src/kernel_host.cpp
open_solution "solution1"
set_part {xcu200-fsgd2104-2-e}
create_clock -period 5 -name default
config_compile -name_max_length 50
#source "./prj/solution1/directives.tcl"
[lindex $argv 0]
# csynth_design
#cosim_design
#cosim_design -trace_level all
#cosim_design -setup -trace_level all
#export_design -format ip_catalog
exit
