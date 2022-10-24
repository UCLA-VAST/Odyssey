#!/bin/bash
VAR0="sim"
VAR1="cosim"
VAR2="syn"


# if VIV_VER is 2018.3, use vivado_hls, else vitis_hls
if [ "$VIV_VER" = "2018.3" ]; then
    hls=vivado_hls
elif [ "$VIV_VER" = "2021.2" ]; then
    hls=vitis_hls
fi

cd build

if [ "$1" = "$VAR0" ]; then
    $hls hls.tcl csim_design kernel0 -l ./logs/kernel0_sim.log
elif  [ "$1" = "$VAR1" ]; then
    $hls hls.tcl cosim_design $2 -l ./logs/$2_cosim.log
elif  [ "$1" = "$VAR2" ]; then
    $hls hls.tcl csynth_design $2 -l ./logs/$2_syn.log
else
    echo "incorrect argument"
fi

