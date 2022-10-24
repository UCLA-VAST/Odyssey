
csim_all: run_csim

run_csim: $(HOST_EXE)
	mkdir -p outputs
	./hls.sh sim | tee ./outputs/csim_output.log
