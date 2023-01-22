param i;
param o;
param r;
param c;
param p;
param q;
param dsp_bound;
param bram_bound;
param data_w;
var i1 integer >= 1, <= i;
var o1 integer >= 1, <= o;
var r1 integer >= 1, <= r;
var c1 integer >= 1, <= c;
var o2 integer >= 1, <= o;
var r2 integer >= 1, <= r;
var c2 integer >= 1, <= c;
var i2 integer >= 1, <= 8.0;
var ci1 integer >= 1, <= i;
var ci2 integer >= 1, <= i;
var co1 integer >= 1, <= o;
var co2 integer >= 1, <= o;
var cr1 integer >= 1, <= r;
var cr2 integer >= 1, <= r;
var cc1 integer >= 1, <= c;
var cc2 integer >= 1, <= c;
var ci3 integer >= 1, <= i;
minimize target:
	(i*r*c*co1+i*o*p*q*cr1*cc1+o*r*c*ci1)/
	(co2*cc2*i2);

subject to DSP_cst:
	0 <= co2*cc2*i2*5 <= dsp_bound;

subject to BRAM_cst:
	0 <= (data_w*i1*r1*c1)/(18*1024)*2+
	     (data_w*i1*o1*p*q)/(18*1024)*2+
	     (data_w*o1*r1*c1)/(18*1024)*2 <= bram_bound;

subject to ci1_cst:
	i = ci1*i1;

subject to co1_cst:
	o = co1*o1;

subject to cr1_cst:
	r = cr1*r1;

subject to cc1_cst:
	c = cc1*c1;

subject to ci2_cst:
	i1 = ci2*i2;

subject to co2_cst:
	o1 = co2*o2;

subject to cr2_cst:
	r1 = cr2*r2;

subject to cc2_cst:
	c1 = cc2*c2;

subject to ci3_cst:
	i2 = ci3*2;

subject to latency_hiding_cst:
	o2*r2*c2 >= 8*i2;

