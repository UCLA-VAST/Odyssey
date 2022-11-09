m.Equation(((r_t1/r_t2)*(c_t1/c_t2)) * i_t2 * 5 <= dsp_bound)

m.Equation(
	(4*8*1 / 36) * (((r_t2*c_t2)*o_t1)/1/512) * 1 * ((r_t1/r_t2)*(c_t1/c_t2)) + 
	(4*8*p14 / 36) * ((((((r_t2-1)+(p-1))+1)*(((c_t2-1)+(q-1))+1))*i_t1)/p14/512) * 2 * ((c_t1/c_t2)*(r_t1/r_t2)) + 
	(4*8*p15 / 36) * (((r_t2*c_t2)*o_t1)/p15/512) * 2 * ((c_t1/c_t2)*(r_t1/r_t2)) + 
	(4*8*p15 / 36) * (((r_t2*c_t2)*o_t1)/p15/512) * 2 * ((c_t1/c_t2)*(r_t1/r_t2)) + 
	(4*8*p17 / 36) * ((((o_t1*((p-1)+1))*((q-1)+1))*i_t1)/p17/512) * 2 * (c_t1/c_t2)
	<= bram_bound)

m.Equation(r_t1 >= 1)
m.Equation(r_t1 <= r)
m.Equation(c_t1 >= 1)
m.Equation(c_t1 <= c)
m.Equation(o_t1 >= 1)
m.Equation(o_t1 <= o)
m.Equation(i_t1 >= 1)
m.Equation(i_t1 <= i)
m.Equation(r_t2 >= 1)
m.Equation(r_t2 <= r_t1)
m.Equation(c_t2 >= 1)
m.Equation(c_t2 <= c_t1)
m.Equation(o_t2 >= 1)
m.Equation(o_t2 <= o_t1)
m.Equation(i_t2 >= 1)
m.Equation(i_t2 <= min(i_t1,8))
m.Equation(p14 >= i_t2)
m.Equation(p14 <= max(min(i_t1,4),i_t2))
m.Equation(p15 >= 1)
m.Equation(p15 <= max(min(o_t1,4),1))
m.Equation(p16 >= 1)
m.Equation(p16 <= max(min(o_t1,4),1))
m.Equation(p17 >= i_t2)
m.Equation(p17 <= max(min(i_t1,16),i_t2))
m.Equation(	r_t2 * c_t2 * o_t2 >= i_t2 * 8)
