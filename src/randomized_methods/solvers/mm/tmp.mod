param i;
param j;
param k;
param dsp_bound;
param bram_bound;
param data_w;
var i1 integer >= 1, <= i;
var j1 integer >= 1, <= j;
var k1 integer >= 1, <= k;
var i2 integer >= 1, <= i;
var j2 integer >= 1, <= j;
var k2 integer >= 1, <= 8.0;
var ci1 integer >= 1, <= i;
var ci2 integer >= 1, <= i;
var cj1 integer >= 1, <= j;
var cj2 integer >= 1, <= j;
var ck1 integer >= 1, <= k;
var ck2 integer >= 1, <= k;
var ck3 integer >= 1, <= k;
minimize target:
	(i*cj1*k+ci1*j*k+i*j)-
	(cj2*k1);

subject to DSP_cst:
	0 <= cj2*k1*5 <= dsp_bound;

subject to BRAM_cst:
	ceil(data_w/18)*ceil(i1*k1/1024)*2+
	ceil(data_w/18)/ceil(j1*k1/1024)*2+
	ceil(data_w/18)/ceil(i1*j1/1024)*2 <= bram_bound;

subject to ci1_cst:
	i = ci1*i1;

subject to cj1_cst:
	j = cj1*j1;

subject to ck1_cst:
	k = ck1*k1;

subject to ci2_cst:
	i1 = ci2*i2;

subject to cj2_cst:
	j1 = cj2*j2;

subject to ck2_cst:
	k1 = ck2*k2;

subject to ck3_cst:
	k2 = ck3*2;

