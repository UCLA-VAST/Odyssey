

if (h==0){
  buff0[w] = fifo_in.read();
}else if(h==1){
  buff1[w] = fifo_in.read();
}else{
  if(w==0){
    reg0 = fifo_in.read();
    buff0[w_bound - w - 2] = buff1[w_bound - w - 1];
  }else if(w==1){
    reg1 = fifo_in.read();
    buff1[w_bound - w - 1] = reg1;
  }else{
    tmp = fifo_in.read();
    // do pool with unroll
    buff0[w-2] = buff1[w-2];
    buff1[w-2] = reg0;
    reg0 = reg1;
    reg1 = tmp;
  }
}