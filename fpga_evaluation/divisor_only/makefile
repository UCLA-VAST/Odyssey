PLATFORM := xilinx_u250_xdma_201830_2

# targets
HOST_EXE := host.exe

CFLAGS := -ltapa -lfrt -lglog -lgflags -lOpenCL -I/opt/tools/xilinx/Vitis_HLS/$(VIV_VER)/include/

HOST_SRC := \
	src/kernel_kernel.cpp \
	src/kernel_kernel.h \
	src/kernel_host.h \
	src/kernel_host.cpp

# sources
KERNEL_SRC := src/kernel_kernel.cpp

# host rules
$(HOST_EXE): $(HOST_SRC)
	g++ -o $@ -O3 $+ $(CFLAGS) 
	@echo 'Compiled Host Executable: $(HOST_EXE)'

TOP_KERNEL := kernel0

XOBJ := $(TOP_KERNEL).$(PLATFORM).hw.xo

XCLBIN_SCRIPT := $(TOP_KERNEL).$(PLATFORM).hw_generate_bitstream.sh

# default make host
host: $(HOST_EXE)

csim_all: host run_csim

cosim_all: host syn cosim run_cosim

hw_all: host syn xclbin

xclbin: build/$(XCLBIN_SCRIPT)
	cd build;	bash $(XCLBIN_SCRIPT)

syn: $(KERNEL_SRC)
	mkdir -p build
	tapac \
	--work-dir build \
	--top $(TOP_KERNEL) \
	--platform $(PLATFORM) \
	--clock-period 3.33 \
	-o build/$(XOBJ) \
  --connectivity link_config.ini \
	--read-only-args "A" \
	--read-only-args "B" \
	--write-only-args "C" \
	--enable-synth-util \
	--max-parallel-synth-jobs 16 \
	--floorplan-output build/constraint.tcl \
	--floorplan-strategy QUICK_FLOORPLANNING \
	$+
	echo >> build/constraint.tcl
	echo "set_property PROHIBIT true [ get_bels -of_objects [get_sites -of_objects [ get_pblocks pblock_dynamic_region ] -filter { NAME =~ LAG* } ] -filter { NAME =~ */RX* } ]" >> build/constraint.tcl

cosim: $(HOST_SRC)
	cd build; \
	v++ -o $(TOP_KERNEL).$(PLATFORM).hw_emu.xclbin \
	--link \
	-g \
	--target hw_emu \
	--config ../connectivity.cfg \
	--kernel $(TOP_KERNEL) \
	--platform $(PLATFORM) \
	--advanced.param compiler.fsanitize=address,memory \
	--advanced.param compiler.deadlockDetection=TRUE \
  $(XOBJ)

run_csim: $(HOST_EXE)
	mkdir -p outputs
	./$(HOST_EXE) | tee ./outputs/csim_output.log

run_cosim: build/$(TOP_KERNEL).$(PLATFORM).hw_emu.xclbin $(HOST_EXE)
	mkdir -p outputs
	./$(HOST_EXE) --bitstream=./build/$(TOP_KERNEL).$(PLATFORM).hw_emu.xclbin | tee ./outputs/cosim_output.log