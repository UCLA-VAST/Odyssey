param q;
param p;
param o;
param r;
param c;
param i;
var r_t1 integer >= 1, <= r;
var c_t1 integer >= 1, <= c;
var o_t1 integer >= 1, <= o;
var i_t1 integer >= 1, <= i;
var r_t2 integer >= 1, <= r;
var c_t2 integer >= 1, <= c;
var o_t2 integer >= 1, <= o;
var i_t2 integer >= 1, <= i;
param p15;
param p18;
param p16;
var p17 integer >= 1, <= 16;
var p14 integer >= 1, <= 8;
param bram_bound;
param dsp_bound;

minimize target:
max(
	((r_t1/r_t2) * ((((r_t2-1)+(p-1))+1)*(((c_t2-1)+(q-1))+1)*i_t1/p14) + 1),
	(c_t1/c_t2) * (r_t1/r_t2) * ((((r_t2-1)+(p-1))+1)*(((c_t2-1)+(q-1))+1)*i_t1/p14),
	(c_t1/c_t2) * (r_t1/r_t2) * ((((r_t2-1)+(p-1))+1)*(((c_t2-1)+(q-1))+1)*i_t1/i_t1*(20+i_t1/(512/8/4))),
	((r_t1/r_t2) * (r_t2*c_t2*o_t1/p15) + 1),
	(c_t1/c_t2) * (r_t1/r_t2) * (r_t2*c_t2*o_t1/p15),
	(c_t1/c_t2) * (r_t1/r_t2) * (r_t2*c_t2*o_t1/o_t1*(20+o_t1/(512/8/4))),
	((c_t1/c_t2) * (o_t1*((p-1)+1)*((q-1)+1)*i_t1/p17) + 1),
	(c_t1/c_t2) * (o_t1*((p-1)+1)*((q-1)+1)*i_t1/i_t1*(20+i_t1/(512/8/4)))
) + 
max(
	((r_t1/r_t2) * (r_t2*c_t2*o_t1/p15) + 1),
	(c_t1/c_t2) * (r_t1/r_t2) * (r_t2*c_t2*o_t1/p15),
	(c_t1/c_t2) * (r_t1/r_t2) * (r_t2*c_t2*o_t1/o_t1*(20+o_t1/(512/8/4)))
) + 
max(
	((o/o_t1)) * ((i/i_t1)) * ((r/r_t1)) * ((c/c_t1)) * (1 + (o_t1/o_t2) * (i_t1/i_t2) * p * q * o_t2 * c_t2 * r_t2 * 1 + 1),
	((o/o_t1)) * ((i/i_t1)) * ((r/r_t1)) * ((c/c_t1)) * (max((r_t1/r_t2) * ((((r_t2-1)+(p-1))+1)*(((c_t2-1)+(q-1))+1)*i_t1/p14), (o_t1/o_t2) * (i_t1/i_t2) * p * q * o_t2 * c_t2 * r_t2 * 1) + 1),
	((o/o_t1)) * ((i/i_t1)) * ((r/r_t1)) * ((c/c_t1)) * (c_t1/c_t2) * (r_t1/r_t2) * ((((r_t2-1)+(p-1))+1)*(((c_t2-1)+(q-1))+1)*i_t1/p14),
	((o/o_t1)) * ((i/i_t1)) * ((r/r_t1)) * ((c/c_t1)) * (c_t1/c_t2) * (r_t1/r_t2) * ((((r_t2-1)+(p-1))+1)*(((c_t2-1)+(q-1))+1)*i_t1/i_t1*(20+i_t1/(512/8/4))),
	((o/o_t1)) * ((r/r_t1)) * ((c/c_t1)) * (max((r_t1/r_t2) * (r_t2*c_t2*o_t1/p15), (o_t1/o_t2) * o_t2 * c_t2 * r_t2 * 1) + 1),
	((o/o_t1)) * ((r/r_t1)) * ((c/c_t1)) * (max((r_t1/r_t2) * (r_t2*c_t2*o_t1/p15), (o_t1/o_t2) * o_t2 * c_t2 * r_t2 * 1) + 1),
	((o/o_t1)) * ((r/r_t1)) * ((c/c_t1)) * (c_t1/c_t2) * (r_t1/r_t2) * (r_t2*c_t2*o_t1/p15),
	((o/o_t1)) * ((r/r_t1)) * ((c/c_t1)) * (c_t1/c_t2) * (r_t1/r_t2) * (r_t2*c_t2*o_t1/p15),
	((o/o_t1)) * ((r/r_t1)) * ((c/c_t1)) * (c_t1/c_t2) * (r_t1/r_t2) * (r_t2*c_t2*o_t1/o_t1*(20+o_t1/(512/8/4))),
	((o/o_t1)) * ((r/r_t1)) * ((c/c_t1)) * (c_t1/c_t2) * (r_t1/r_t2) * (r_t2*c_t2*o_t1/o_t1*(20+o_t1/(512/8/4))),
	((o/o_t1)) * ((i/i_t1)) * (max((c_t1/c_t2) * (o_t1*((p-1)+1)*((q-1)+1)*i_t1/p17), ((r/r_t1)) * ((c/c_t1)) * (o_t1/o_t2) * (i_t1/i_t2) * p * q * o_t2 * c_t2 * r_t2 * 1) + 1),
	((o/o_t1)) * ((i/i_t1)) * (c_t1/c_t2) * (o_t1*((p-1)+1)*((q-1)+1)*i_t1/i_t1*(20+i_t1/(512/8/4)))
);

subject to DSP_cst:
	0 <= ((r_t1/r_t2)*(c_t1/c_t2)) * i_t2 * 5 <= dsp_bound;

subject to BRAM_cst:
	0 <= 
	ceil(4*8*1 / 36) * ceil(((r_t2*c_t2)*o_t1)/1/512) * 1 * ((r_t1/r_t2)*(c_t1/c_t2)) + 
	ceil(4*8*p14 / 36) * ceil((((((r_t2-1)+(p-1))+1)*(((c_t2-1)+(q-1))+1))*i_t1)/p14/512) * 2 * ((c_t1/c_t2)*(r_t1/r_t2)) + 
	ceil(4*8*p15 / 36) * ceil(((r_t2*c_t2)*o_t1)/p15/512) * 2 * ((c_t1/c_t2)*(r_t1/r_t2)) + 
	ceil(4*8*p15 / 36) * ceil(((r_t2*c_t2)*o_t1)/p15/512) * 2 * ((c_t1/c_t2)*(r_t1/r_t2)) + 
	ceil(4*8*p17 / 36) * ceil((((o_t1*((p-1)+1))*((q-1)+1))*i_t1)/p17/512) * 2 * (c_t1/c_t2)
	<= bram_bound;

subject to const_1:
	p14 >= i_t2;
subject to const_2:
	p17 >= i_t2;
