param q;
param p;
param o;
param r;
param c;
param i;
var r_t1 >= 1, <= r;
var c_t1 >= 1, <= c;
var o_t1 >= 1, <= o;
var i_t1 >= 1, <= i;
var r_t2 >= 1, <= r;
var c_t2 >= 1, <= c;
var o_t2 >= 1, <= o;
var i_t2 >= 1, <= i;
var p14 >= 1, <= 8;
var p15 >= 1, <= 4;
var p16 >= 1, <= 4;
var p17 >= 1, <= 16;
var p18 >= 1, <= 1;
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
	(4*8*1 / 36) * (((r_t2*c_t2)*o_t1)/1/512) * 1 * ((r_t1/r_t2)*(c_t1/c_t2)) + 
	(4*8*p14 / 36) * ((((((r_t2-1)+(p-1))+1)*(((c_t2-1)+(q-1))+1))*i_t1)/p14/512) * 2 * ((c_t1/c_t2)*(r_t1/r_t2)) + 
	(4*8*p15 / 36) * (((r_t2*c_t2)*o_t1)/p15/512) * 2 * ((c_t1/c_t2)*(r_t1/r_t2)) + 
	(4*8*p15 / 36) * (((r_t2*c_t2)*o_t1)/p15/512) * 2 * ((c_t1/c_t2)*(r_t1/r_t2)) + 
	(4*8*p17 / 36) * ((((o_t1*((p-1)+1))*((q-1)+1))*i_t1)/p17/512) * 2 * (c_t1/c_t2)
	<= bram_bound;

subject to const_1:
	r_t1 >= 1;
subject to const_2:
	r_t1 <= r;
subject to const_3:
	c_t1 >= 1;
subject to const_4:
	c_t1 <= c;
subject to const_5:
	o_t1 >= 1;
subject to const_6:
	o_t1 <= o;
subject to const_7:
	i_t1 >= 1;
subject to const_8:
	i_t1 <= i;
subject to const_9:
	r_t2 >= 1;
subject to const_10:
	r_t2 <= r_t1;
subject to const_11:
	c_t2 >= 1;
subject to const_12:
	c_t2 <= c_t1;
subject to const_13:
	o_t2 >= 1;
subject to const_14:
	o_t2 <= o_t1;
subject to const_15:
	i_t2 >= 1;
subject to const_16:
	i_t2 <= min(i_t1,8);
subject to const_17:
	p14 >= i_t2;
subject to const_18:
	p14 <= max(min(i_t1,4),i_t2);
subject to const_19:
	p15 >= 1;
subject to const_20:
	p15 <= max(min(o_t1,4),1);
subject to const_21:
	p16 >= 1;
subject to const_22:
	p16 <= max(min(o_t1,4),1);
subject to const_23:
	p17 >= i_t2;
subject to const_24:
	p17 <= max(min(i_t1,16),i_t2);
subject to latency_hiding:
	r_t2 * c_t2 * o_t2 >= i_t2 * 8;
