#include "kernel_kernel.h"
template <typename T1, typename T2> inline T1 min(T1 x, T2 y) { return (x < T1(y)) ? x : T1(y); }
template <typename T1, typename T2> inline T1 max(T1 x, T2 y) { return (x > T1(y)) ? x : T1(y); }

/* Module Definition */
void A_IO_L3_in(tapa::istream<A_t16> &fifo_A_in, tapa::ostream<A_t16> &fifo_A_local_out) {
#pragma HLS INLINE OFF
  /* Variable Declaration */
  /* Variable Declaration */

  for (int c0 = 0; c0 <= 15; c0 += 1)
    for (int c1 = 0; c1 <= 7; c1 += 1)
      for (int c2 = 0; c2 <= 7; c2 += 1) {
        // array
        // io_L3
        for (int c3 = 0; c3 <= 31; c3 += 1) {
          // io_L2
          for (int c4 = 0; c4 <= 1; c4 += 1) {
            // access_coalesce
            // access_serialize
            for (int c5 = 0; c5 <= 7; c5 += 1) {
            #pragma HLS PIPELINE II=1
              {
                A_t16 in_data;
                A_t16 out_data;
                in_data = fifo_A_in.read();
                out_data = in_data;
                fifo_A_local_out.write(out_data);
              }
            }
          }
        }
      }
}
/* Module Definition */

/* Module Definition */
void A_IO_L3_in_serialize(A_t16_mmap A, tapa::ostream<A_t16> &fifo_A_local_out) {
#pragma HLS INLINE OFF
  /* Variable Declaration */
  /* Variable Declaration */

  for (int i = 0; i < 524288; i++) {
  #pragma HLS PIPELINE II=1
    A_t16 fifo_data;
    fifo_data = tapa::bit_cast<A_t16>(A[i]);
    fifo_A_local_out.write(fifo_data);
  }
}
/* Module Definition */

/* Module Definition */
void A_IO_L2_in_intra_trans(int idx, int c0, int c1, int c2, A_t16 local_A[2][8], tapa::ostream<A_t8> &fifo_A_local_out, bool intra_trans_en) {
#pragma HLS INLINE OFF
  /* Variable Declaration */
  int p0 = idx; // module id
  A_t8 data_split[2];
  #pragma HLS ARRAY_PARTITION variable=data_split complete
  /* Variable Declaration */

  if (!intra_trans_en) return;


  // io_L2
  // io_L1
  // pe
  for (int c5 = 0; c5 <= 15; c5 += 1) {
    // latency
    for (int c6 = 0; c6 <= 31; c6 += 1) {
      // latency
      for (int c7 = 0; c7 <= 1; c7 += 1) {
      #pragma HLS PIPELINE II=1
        // simd
        {
          A_t16 in_data;
          A_t8 out_data;
          in_data = local_A[c7][8 * c5 / 16];
          for (int n = 0; n < 2; n++) {
          #pragma HLS UNROLL
            data_split[n] = tapa::truncated<8>(in_data, 8 * n);
          }
          int split_idx = (c5) % 2;
          out_data = data_split[split_idx];
          fifo_A_local_out.write(out_data);
        }
      }
    }
  }
}
/* Module Definition */

/* Module Definition */
void A_IO_L2_in_inter_trans(int idx, int c0, int c1, int c2, A_t16 local_A[2][8], tapa::istream<A_t16> &fifo_A_in, tapa::ostream<A_t16> &fifo_A_out, bool inter_trans_en) {
#pragma HLS INLINE OFF
  /* Variable Declaration */
  int p0 = idx; // module id
  /* Variable Declaration */

  if (!inter_trans_en) return;

  for (int c3 = p0; c3 <= 31; c3 += 1) {
    // io_L2
    for (int c4 = 0; c4 <= 1; c4 += 1) {
      // access_coalesce
      for (int c5 = 0; c5 <= 7; c5 += 1) {
      #pragma HLS PIPELINE II=1
        {
          if (c3 == p0) {
            A_t16 in_data;
            A_t16 out_data;
            in_data = fifo_A_in.read();
            out_data = in_data;
            local_A[c4][c5] = out_data;
          }else{
            A_t16 in_data;
            A_t16 out_data;
            in_data = fifo_A_in.read();
            out_data = in_data;
            fifo_A_out.write(out_data);
          }
        }
      }
    }
  } 
}
/* Module Definition */

/* Module Definition */
void A_IO_L2_in_inter_trans_boundary(int idx, int c0, int c1, int c2, A_t16 local_A[2][8], tapa::istream<A_t16> &fifo_A_in, bool inter_trans_en) {
#pragma HLS INLINE OFF
  /* Variable Declaration */
  int p0 = idx; // module id
  /* Variable Declaration */

  if (!inter_trans_en) return;

  for (int c3 = p0; c3 <= 31; c3 += 1) {
    // io_L2
    for (int c4 = 0; c4 <= 1; c4 += 1) {
      // access_coalesce
      for (int c5 = 0; c5 <= 7; c5 += 1) {
      #pragma HLS PIPELINE II=1
        {
          if (c3 == p0) {
            A_t16 in_data;
            A_t16 out_data;
            in_data = fifo_A_in.read();
            out_data = in_data;
            local_A[c4][c5] = out_data;
          }
        }
      }
    }
  }
}
/* Module Definition */

/* Module Definition */
void A_IO_L2_in(int idx, tapa::istream<A_t16> &fifo_A_in, tapa::ostream<A_t16> &fifo_A_out, tapa::ostream<A_t8> &fifo_A_local_out) {
#pragma HLS INLINE OFF
  /* Variable Declaration */
  int p0 = idx; // module id
  A_t16 local_A_ping[2][8];
  #pragma HLS RESOURCE variable=local_A_ping core=RAM_2P_BRAM
  A_t16 local_A_pong[2][8];
  #pragma HLS RESOURCE variable=local_A_pong core=RAM_2P_BRAM
  bool arb = 0;
  bool inter_trans_en = 1;
  bool intra_trans_en = 0;
  int c0, c0_prev;
  int c1, c1_prev;
  int c2, c2_prev;
  /* Variable Declaration */

  {
    for (int c0 = 0; c0 <= 15; c0 += 1)
      for (int c1 = 0; c1 <= 7; c1 += 1)
        for (int c2 = 0; c2 <= 7; c2 += 1) {
          // array
          // io_L3
          {
            if (arb == 0) {
              A_IO_L2_in_inter_trans(
                /* module id */ idx, 
                /* host iter */ c0, 
                /* host iter */ c1, 
                /* host iter */ c2, 
                /* array */ local_A_pong, 
                /* fifo */ fifo_A_in, 
                /* fifo */ fifo_A_out, 
                /* enable */ inter_trans_en
              );
              A_IO_L2_in_intra_trans(
                /* module id */ idx, 
                /* host iter */ c0_prev, 
                /* host iter */ c1_prev, 
                /* host iter */ c2_prev, 
                /* array */ local_A_ping, 
                /* fifo */ fifo_A_local_out, 
                /* enable */ intra_trans_en
              );
            } else {
              A_IO_L2_in_inter_trans(
                /* module id */ idx, 
                /* host iter */ c0, 
                /* host iter */ c1, 
                /* host iter */ c2, 
                /* array */ local_A_ping, 
                /* fifo */ fifo_A_in, 
                /* fifo */ fifo_A_out, 
                /* enable */ inter_trans_en
              );
              A_IO_L2_in_intra_trans(
                /* module id */ idx, 
                /* host iter */ c0_prev, 
                /* host iter */ c1_prev, 
                /* host iter */ c2_prev, 
                /* array */ local_A_pong, 
                /* fifo */ fifo_A_local_out, 
                /* enable */ intra_trans_en
              );
            }
            intra_trans_en = 1;
            arb = !arb;
            c0_prev = c0;
            c1_prev = c1;
            c2_prev = c2;
          }
        }
    if (arb == 0) {
      A_IO_L2_in_intra_trans(
        /* module id */ idx, 
        /* host iter */ c0_prev, 
        /* host iter */ c1_prev, 
        /* host iter */ c2_prev, 
        /* array */ local_A_ping, 
        /* fifo */ fifo_A_local_out, 
        /* enable */ intra_trans_en
      );
    } else {
      A_IO_L2_in_intra_trans(
        /* module id */ idx, 
        /* host iter */ c0_prev, 
        /* host iter */ c1_prev, 
        /* host iter */ c2_prev, 
        /* array */ local_A_pong, 
        /* fifo */ fifo_A_local_out, 
        /* enable */ intra_trans_en
      );
    }
  }
}
/* Module Definition */

/* Module Definition */
void A_IO_L2_in_boundary(int idx, tapa::istream<A_t16> &fifo_A_in, tapa::ostream<A_t8> &fifo_A_local_out) {
#pragma HLS INLINE OFF
  /* Variable Declaration */
  int p0 = idx; // module id
  A_t16 local_A_ping[2][8];
  #pragma HLS RESOURCE variable=local_A_ping core=RAM_2P_BRAM
  A_t16 local_A_pong[2][8];
  #pragma HLS RESOURCE variable=local_A_pong core=RAM_2P_BRAM
  bool arb = 0;
  bool inter_trans_en = 1;
  bool intra_trans_en = 0;
  int c0, c0_prev;
  int c1, c1_prev;
  int c2, c2_prev;
  /* Variable Declaration */

  {
    for (int c0 = 0; c0 <= 15; c0 += 1)
      for (int c1 = 0; c1 <= 7; c1 += 1)
        for (int c2 = 0; c2 <= 7; c2 += 1) {
          // array
          // io_L3
          {
            if (arb == 0) {
              A_IO_L2_in_inter_trans_boundary(
                /* module id */ idx, 
                /* host iter */ c0, 
                /* host iter */ c1, 
                /* host iter */ c2, 
                /* array */ local_A_pong, 
                /* fifo */ fifo_A_in, 
                /* enable */ inter_trans_en
              );
              A_IO_L2_in_intra_trans(
                /* module id */ idx, 
                /* host iter */ c0_prev, 
                /* host iter */ c1_prev, 
                /* host iter */ c2_prev, 
                /* array */ local_A_ping, 
                /* fifo */ fifo_A_local_out, 
                /* enable */ intra_trans_en
              );
            } else {
              A_IO_L2_in_inter_trans_boundary(
                /* module id */ idx, 
                /* host iter */ c0, 
                /* host iter */ c1, 
                /* host iter */ c2, 
                /* array */ local_A_ping, 
                /* fifo */ fifo_A_in, 
                /* enable */ inter_trans_en
              );
              A_IO_L2_in_intra_trans(
                /* module id */ idx, 
                /* host iter */ c0_prev, 
                /* host iter */ c1_prev, 
                /* host iter */ c2_prev, 
                /* array */ local_A_pong, 
                /* fifo */ fifo_A_local_out, 
                /* enable */ intra_trans_en
              );
            }
            intra_trans_en = 1;
            arb = !arb;
            c0_prev = c0;
            c1_prev = c1;
            c2_prev = c2;
          }
        }
    if (arb == 0) {
      A_IO_L2_in_intra_trans(
        /* module id */ idx, 
        /* host iter */ c0_prev, 
        /* host iter */ c1_prev, 
        /* host iter */ c2_prev, 
        /* array */ local_A_ping, 
        /* fifo */ fifo_A_local_out, 
        /* enable */ intra_trans_en
      );
    } else {
      A_IO_L2_in_intra_trans(
        /* module id */ idx, 
        /* host iter */ c0_prev, 
        /* host iter */ c1_prev, 
        /* host iter */ c2_prev, 
        /* array */ local_A_pong, 
        /* fifo */ fifo_A_local_out, 
        /* enable */ intra_trans_en
      );
    }
  }
}
/* Module Definition */

/* Module Definition */
void B_IO_L3_in(tapa::istream<B_t16> &fifo_B_in, tapa::ostream<B_t16> &fifo_B_local_out) {
#pragma HLS INLINE OFF
  /* Variable Declaration */
  /* Variable Declaration */

  for (int c0 = 0; c0 <= 15; c0 += 1)
    for (int c1 = 0; c1 <= 7; c1 += 1)
      for (int c2 = 0; c2 <= 7; c2 += 1) {
        // array
        // io_L3
        for (int c3 = 0; c3 <= 3; c3 += 1) {
          // io_L2
          for (int c4 = 0; c4 <= 31; c4 += 1) {
            // access_coalesce
            // access_serialize
            for (int c5 = 0; c5 <= 7; c5 += 1) {
            #pragma HLS PIPELINE II=1
              {
                B_t16 in_data;
                B_t16 out_data;
                in_data = fifo_B_in.read();
                out_data = in_data;
                fifo_B_local_out.write(out_data);
              }
            }
          }
        }
      }
}
/* Module Definition */

/* Module Definition */
void B_IO_L3_in_serialize(B_t16_mmap B, tapa::ostream<B_t16> &fifo_B_local_out) {
#pragma HLS INLINE OFF
  /* Variable Declaration */
  /* Variable Declaration */

  for (int i = 0; i < 1048576; i++) {
  #pragma HLS PIPELINE II=1
    B_t16 fifo_data;
    fifo_data = tapa::bit_cast<B_t16>(B[i]);
    fifo_B_local_out.write(fifo_data);
  }
}
/* Module Definition */

/* Module Definition */
void B_IO_L2_in_intra_trans(int idx, int c0, int c1, int c2, B_t16 local_B[32][8], tapa::ostream<B_t8> &fifo_B_local_out, bool intra_trans_en) {
#pragma HLS INLINE OFF
  /* Variable Declaration */
  int p0 = idx; // module id
  B_t8 data_split[2];
  #pragma HLS ARRAY_PARTITION variable=data_split complete
  /* Variable Declaration */

  if (!intra_trans_en) return;

  bool done = false;
  int c5 = 0;
  int c6 = 0;
  int c7 = 0;
  while(!done){
    // simd
    {
      B_t16 in_data;
      B_t8 out_data;
      in_data = local_B[c6][8 * c5 / 16];
      for (int n = 0; n < 2; n++) {
      #pragma HLS UNROLL
        data_split[n] = tapa::truncated<8>(in_data, 8 * n);
      }
      int split_idx = (c5) % 2;
      out_data = data_split[split_idx];
      fifo_B_local_out.write(out_data);
    }
    c7++;
    if (c7 == 2) {
      c7 = 0;
      c6++;
      if (c6 == 32) {
        c6 = 0;
        c5++;
        if (c5 == 16) {
          done = true;
          break;
        }
      }
    }
  }
  // // io_L2
  // // io_L1
  // // pe
  // for (int c5 = 0; c5 <= 15; c5 += 1) {
  //   // latency
  //   for (int c6 = 0; c6 <= 31; c6 += 1) {
  //     // latency
  //     for (int c7 = 0; c7 <= 1; c7 += 1) {
  //     #pragma HLS PIPELINE II=1
  //       // simd
  //       {
  //         B_t16 in_data;
  //         B_t8 out_data;
  //         in_data = local_B[c6][8 * c5 / 16];
  //         for (int n = 0; n < 2; n++) {
  //         #pragma HLS UNROLL
  //           data_split[n] = tapa::truncated<8>(in_data, 8 * n);
  //         }
  //         int split_idx = (c5) % 2;
  //         out_data = data_split[split_idx];
  //         fifo_B_local_out.write(out_data);
  //       }
  //     }
  //   }
  // }
}
/* Module Definition */

/* Module Definition */
void B_IO_L2_in_inter_trans(int idx, int c0, int c1, int c2, B_t16 local_B[32][8], tapa::istream<B_t16> &fifo_B_in, tapa::ostream<B_t16> &fifo_B_out, bool inter_trans_en) {
#pragma HLS INLINE OFF
  /* Variable Declaration */
  int p0 = idx; // module id
  /* Variable Declaration */

  if (!inter_trans_en) return;

  for (int c3 = p0; c3 <= 3; c3 += 1) {
    // io_L2
    for (int c4 = 0; c4 <= 31; c4 += 1) {
      // access_coalesce
      for (int c5 = 0; c5 <= 7; c5 += 1) {
      #pragma HLS PIPELINE II=1
        {
          if (c3 == p0) {
            B_t16 in_data;
            B_t16 out_data;
            in_data = fifo_B_in.read();
            out_data = in_data;
            local_B[c4][c5] = out_data;
          }else{
            B_t16 in_data;
            B_t16 out_data;
            in_data = fifo_B_in.read();
            out_data = in_data;
            fifo_B_out.write(out_data);
          }
        }
      }
    } 
  }
}
/* Module Definition */

/* Module Definition */
void B_IO_L2_in_inter_trans_boundary(int idx, int c0, int c1, int c2, B_t16 local_B[32][8], tapa::istream<B_t16> &fifo_B_in, bool inter_trans_en) {
#pragma HLS INLINE OFF
  /* Variable Declaration */
  int p0 = idx; // module id
  /* Variable Declaration */

  if (!inter_trans_en) return;

  for (int c3 = p0; c3 <= 3; c3 += 1) {
    // io_L2
    for (int c4 = 0; c4 <= 31; c4 += 1) {
      // access_coalesce
      for (int c5 = 0; c5 <= 7; c5 += 1) {
      #pragma HLS PIPELINE II=1
        {
          if (c3 == p0) {
            B_t16 in_data;
            B_t16 out_data;
            in_data = fifo_B_in.read();
            out_data = in_data;
            local_B[c4][c5] = out_data;
          }
        }
      }
    }
  }
}
/* Module Definition */

/* Module Definition */
void B_IO_L2_in(int idx, tapa::istream<B_t16> &fifo_B_in, tapa::ostream<B_t16> &fifo_B_out, tapa::ostream<B_t8> &fifo_B_local_out) {
#pragma HLS INLINE OFF
  /* Variable Declaration */
  int p0 = idx; // module id
  B_t16 local_B_ping[32][8];
  #pragma HLS RESOURCE variable=local_B_ping core=RAM_2P_BRAM
  B_t16 local_B_pong[32][8];
  #pragma HLS RESOURCE variable=local_B_pong core=RAM_2P_BRAM
  bool arb = 0;
  bool inter_trans_en = 1;
  bool intra_trans_en = 0;
  int c0, c0_prev;
  int c1, c1_prev;
  int c2, c2_prev;
  /* Variable Declaration */

  {
    for (int c0 = 0; c0 <= 15; c0 += 1)
      for (int c1 = 0; c1 <= 7; c1 += 1)
        for (int c2 = 0; c2 <= 7; c2 += 1) {
          // array
          // io_L3
          {
            if (arb == 0) {
              B_IO_L2_in_inter_trans(
                /* module id */ idx, 
                /* host iter */ c0, 
                /* host iter */ c1, 
                /* host iter */ c2, 
                /* array */ local_B_pong, 
                /* fifo */ fifo_B_in, 
                /* fifo */ fifo_B_out, 
                /* enable */ inter_trans_en
              );
              B_IO_L2_in_intra_trans(
                /* module id */ idx, 
                /* host iter */ c0_prev, 
                /* host iter */ c1_prev, 
                /* host iter */ c2_prev, 
                /* array */ local_B_ping, 
                /* fifo */ fifo_B_local_out, 
                /* enable */ intra_trans_en
              );
            } else {
              B_IO_L2_in_inter_trans(
                /* module id */ idx, 
                /* host iter */ c0, 
                /* host iter */ c1, 
                /* host iter */ c2, 
                /* array */ local_B_ping, 
                /* fifo */ fifo_B_in, 
                /* fifo */ fifo_B_out, 
                /* enable */ inter_trans_en
              );
              B_IO_L2_in_intra_trans(
                /* module id */ idx, 
                /* host iter */ c0_prev, 
                /* host iter */ c1_prev, 
                /* host iter */ c2_prev, 
                /* array */ local_B_pong, 
                /* fifo */ fifo_B_local_out, 
                /* enable */ intra_trans_en
              );
            }
            intra_trans_en = 1;
            arb = !arb;
            c0_prev = c0;
            c1_prev = c1;
            c2_prev = c2;
          }
        }
    if (arb == 0) {
      B_IO_L2_in_intra_trans(
        /* module id */ idx, 
        /* host iter */ c0_prev, 
        /* host iter */ c1_prev, 
        /* host iter */ c2_prev, 
        /* array */ local_B_ping, 
        /* fifo */ fifo_B_local_out, 
        /* enable */ intra_trans_en
      );
    } else {
      B_IO_L2_in_intra_trans(
        /* module id */ idx, 
        /* host iter */ c0_prev, 
        /* host iter */ c1_prev, 
        /* host iter */ c2_prev, 
        /* array */ local_B_pong, 
        /* fifo */ fifo_B_local_out, 
        /* enable */ intra_trans_en
      );
    }
  }
}
/* Module Definition */

/* Module Definition */
void B_IO_L2_in_boundary(int idx, tapa::istream<B_t16> &fifo_B_in, tapa::ostream<B_t8> &fifo_B_local_out) {
#pragma HLS INLINE OFF
  /* Variable Declaration */
  int p0 = idx; // module id
  B_t16 local_B_ping[32][8];
  #pragma HLS RESOURCE variable=local_B_ping core=RAM_2P_BRAM
  B_t16 local_B_pong[32][8];
  #pragma HLS RESOURCE variable=local_B_pong core=RAM_2P_BRAM
  bool arb = 0;
  bool inter_trans_en = 1;
  bool intra_trans_en = 0;
  int c0, c0_prev;
  int c1, c1_prev;
  int c2, c2_prev;
  /* Variable Declaration */

  {
    for (int c0 = 0; c0 <= 15; c0 += 1)
      for (int c1 = 0; c1 <= 7; c1 += 1)
        for (int c2 = 0; c2 <= 7; c2 += 1) {
          // array
          // io_L3
          {
            if (arb == 0) {
              B_IO_L2_in_inter_trans_boundary(
                /* module id */ idx, 
                /* host iter */ c0, 
                /* host iter */ c1, 
                /* host iter */ c2, 
                /* array */ local_B_pong, 
                /* fifo */ fifo_B_in, 
                /* enable */ inter_trans_en
              );
              B_IO_L2_in_intra_trans(
                /* module id */ idx, 
                /* host iter */ c0_prev, 
                /* host iter */ c1_prev, 
                /* host iter */ c2_prev, 
                /* array */ local_B_ping, 
                /* fifo */ fifo_B_local_out, 
                /* enable */ intra_trans_en
              );
            } else {
              B_IO_L2_in_inter_trans_boundary(
                /* module id */ idx, 
                /* host iter */ c0, 
                /* host iter */ c1, 
                /* host iter */ c2, 
                /* array */ local_B_ping, 
                /* fifo */ fifo_B_in, 
                /* enable */ inter_trans_en
              );
              B_IO_L2_in_intra_trans(
                /* module id */ idx, 
                /* host iter */ c0_prev, 
                /* host iter */ c1_prev, 
                /* host iter */ c2_prev, 
                /* array */ local_B_pong, 
                /* fifo */ fifo_B_local_out, 
                /* enable */ intra_trans_en
              );
            }
            intra_trans_en = 1;
            arb = !arb;
            c0_prev = c0;
            c1_prev = c1;
            c2_prev = c2;
          }
        }
    if (arb == 0) {
      B_IO_L2_in_intra_trans(
        /* module id */ idx, 
        /* host iter */ c0_prev, 
        /* host iter */ c1_prev, 
        /* host iter */ c2_prev, 
        /* array */ local_B_ping, 
        /* fifo */ fifo_B_local_out, 
        /* enable */ intra_trans_en
      );
    } else {
      B_IO_L2_in_intra_trans(
        /* module id */ idx, 
        /* host iter */ c0_prev, 
        /* host iter */ c1_prev, 
        /* host iter */ c2_prev, 
        /* array */ local_B_pong, 
        /* fifo */ fifo_B_local_out, 
        /* enable */ intra_trans_en
      );
    }
  }
}
/* Module Definition */

/* Module Definition */
void PE(int idx, int idy, tapa::istream<A_t8> &fifo_A_in, tapa::ostream<A_t8> &fifo_A_out, tapa::istream<B_t8> &fifo_B_in, tapa::ostream<B_t8> &fifo_B_out, tapa::ostream<float> &fifo_C_drain_out) {
#pragma HLS INLINE OFF
  /* Variable Declaration */
  int p0 = idx, p1 = idy; // module id
  A_t1 local_A[1][8];
  #pragma HLS ARRAY_PARTITION variable=local_A dim=0 complete
  B_t1 local_B[1][8];
  #pragma HLS ARRAY_PARTITION variable=local_B dim=0 complete
  C_t1 local_C[2][32];
  #pragma HLS RESOURCE variable=local_C core=RAM_2P_BRAM
  /* Variable Declaration */

  for (int c0 = 0; c0 <= 15; c0 += 1)
    for (int c1 = 0; c1 <= 7; c1 += 1)
      for (int c2 = 0; c2 <= 7; c2 += 1) {
        // array
        // pe
        for (int c5 = 0; c5 <= 15; c5 += 1) {
          // latency
          for (int c6 = 0; c6 <= 31; c6 += 1) {
            // latency
            for (int c7 = 0; c7 <= 1; c7 += 1) {
            #pragma HLS PIPELINE II=1
              {
                {
                  A_t8 fifo_data;
                  fifo_data = fifo_A_in.read();
                  for (int n = 0; n < 8; n++) {
                  #pragma HLS UNROLL
                    local_A[0][n] = fifo_data[n];
                  }
                }
                {
                  B_t8 fifo_data;
                  fifo_data = fifo_B_in.read();
                  for (int n = 0; n < 8; n++) {
                  #pragma HLS UNROLL
                    local_B[0][n] = fifo_data[n];
                  }
                }
                // simd
                {
                  if (c2 == 0 && c5 == 0) {
                    // hls_unroll
                    local_C[c7][c6] = 0;
                  }
                  for (int c8 = 0; c8 <= 7; c8 += 1) {
                  #pragma HLS UNROLL
                    local_C[c7][c6] = (local_C[c7][c6] + (local_A[0][c8] * local_B[0][c8]));
                  }
                }
                if (c2 == 7 && c5 == 15)
                  fifo_C_drain_out.write(local_C[c7][c6]);
                {
                  B_t8 fifo_data;
                  float f7, f6, f5, f4, f3, f2, f1, f0;
                  f7 = local_B[0][7];
                  f6 = local_B[0][6];
                  f5 = local_B[0][5];
                  f4 = local_B[0][4];
                  f3 = local_B[0][3];
                  f2 = local_B[0][2];
                  f1 = local_B[0][1];
                  f0 = local_B[0][0];
                  fifo_data.set(7, f7);
                  fifo_data.set(6, f6);
                  fifo_data.set(5, f5);
                  fifo_data.set(4, f4);
                  fifo_data.set(3, f3);
                  fifo_data.set(2, f2);
                  fifo_data.set(1, f1);
                  fifo_data.set(0, f0);
                  fifo_B_out.write(fifo_data);
                }
                {
                  A_t8 fifo_data;
                  float f7, f6, f5, f4, f3, f2, f1, f0;
                  f7 = local_A[0][7];
                  f6 = local_A[0][6];
                  f5 = local_A[0][5];
                  f4 = local_A[0][4];
                  f3 = local_A[0][3];
                  f2 = local_A[0][2];
                  f1 = local_A[0][1];
                  f0 = local_A[0][0];
                  fifo_data.set(7, f7);
                  fifo_data.set(6, f6);
                  fifo_data.set(5, f5);
                  fifo_data.set(4, f4);
                  fifo_data.set(3, f3);
                  fifo_data.set(2, f2);
                  fifo_data.set(1, f1);
                  fifo_data.set(0, f0);
                  fifo_A_out.write(fifo_data);
                }
              }
            }
          }
        }
      }
}
/* Module Definition */

/* Module Definition */
void PE_wrapper(int idx, int idy, tapa::istream<A_t8> &fifo_A_in, tapa::ostream<A_t8> &fifo_A_out, tapa::istream<B_t8> &fifo_B_in, tapa::ostream<B_t8> &fifo_B_out, tapa::ostream<float> &fifo_C_drain_out)
 {
  PE(
    /* module id */ idx, 
    /* module id */ idy, 
    /* fifo */ fifo_A_in, 
    /* fifo */ fifo_A_out, 
    /* fifo */ fifo_B_in, 
    /* fifo */ fifo_B_out, 
    /* fifo */ fifo_C_drain_out);
}
/* Module Definition */

/* Module Definition */
void A_PE_dummy_in(int idx, int idy, tapa::istream<A_t8> &fifo_A_in) {
  /* Variable Declaration */
  int p0 = idx, p1 = idy; // module id
  /* Variable Declaration */

  for (int c0 = 0; c0 <= 15; c0 += 1)
    for (int c1 = 0; c1 <= 7; c1 += 1)
      for (int c2 = 0; c2 <= 7; c2 += 1) {
        // array
        // pe
        for (int c5 = 0; c5 <= 15; c5 += 1) {
          // latency
          for (int c6 = 0; c6 <= 31; c6 += 1) {
            // latency
            for (int c7 = 0; c7 <= 1; c7 += 1) {
            #pragma HLS PIPELINE II=1
              A_t8 fifo_data;
              fifo_data = fifo_A_in.read();
            }
          }
        }
      }
}
/* Module Definition */

/* Module Definition */
void B_PE_dummy_in(int idx, int idy, tapa::istream<B_t8> &fifo_B_in) {
  /* Variable Declaration */
  int p0 = idx, p1 = idy; // module id
  /* Variable Declaration */

  for (int c0 = 0; c0 <= 15; c0 += 1)
    for (int c1 = 0; c1 <= 7; c1 += 1)
      for (int c2 = 0; c2 <= 7; c2 += 1) {
        // array
        // pe
        for (int c5 = 0; c5 <= 15; c5 += 1) {
          // latency
          for (int c6 = 0; c6 <= 31; c6 += 1) {
            // latency
            for (int c7 = 0; c7 <= 1; c7 += 1) {
            #pragma HLS PIPELINE II=1
              B_t8 fifo_data;
              fifo_data = fifo_B_in.read();
            }
          }
        }
      }
}
/* Module Definition */

/* Module Definition */
void C_drain_IO_L1_out_intra_trans(int idx, int idy, int c0, int c1, C_t4 local_C[2][8], tapa::istream<float> &fifo_C_drain_local_in) {
#pragma HLS INLINE
  /* Variable Declaration */
  int p0 = idx, p1 = idy; // module id
  float data_split[4];
  #pragma HLS ARRAY_PARTITION variable=data_split complete
  /* Variable Declaration */


  // io_L1
  // pe
  // latency
  for (int c6 = 0; c6 <= 31; c6 += 1) {
    // latency
    for (int c7 = 0; c7 <= 1; c7 += 1) {
    #pragma HLS PIPELINE II=1
      // simd
      {
        C_t1 in_data;
        C_t4 out_data;
        in_data = fifo_C_drain_local_in.read();
        int split_idx = (c6) % 4;
        out_data = local_C[c7][c6 / 4];
        for (int n = 0; n < 4; n++) {
        #pragma HLS UNROLL
          data_split[n] = out_data[n];
        }
        data_split[split_idx] = in_data;
        out_data.set(0, data_split[0]);
        out_data.set(1, data_split[1]);
        out_data.set(2, data_split[2]);
        out_data.set(3, data_split[3]);
        local_C[c7][c6 / 4] = out_data;
      }
    }
  }
}
/* Module Definition */

/* Module Definition */
void C_drain_IO_L1_out_inter_trans(int idx, int idy, int c0, int c1, C_t4 local_C[2][8], tapa::istream<C_t4> &fifo_C_drain_in, tapa::ostream<C_t4> &fifo_C_drain_out) {
#pragma HLS INLINE
  /* Variable Declaration */
  int p0 = idx, p1 = idy; // module id
  /* Variable Declaration */

  for (int c4 = p1; c4 <= 31; c4 += 1) {
    // io_L1
    for (int c5 = 0; c5 <= 1; c5 += 1) {
      // access_coalesce
      for (int c6 = 0; c6 <= 7; c6 += 1) {
      #pragma HLS PIPELINE II=1
        {
          if (c4 == p1) {
            C_t4 in_data;
            C_t4 out_data;
            in_data = local_C[c5][c6];
            out_data = in_data;
            fifo_C_drain_out.write(out_data);
          }else{
            C_t4 in_data;
            C_t4 out_data;
            in_data = fifo_C_drain_in.read();
            out_data = in_data;
            fifo_C_drain_out.write(out_data);
          }
        }
      }
    } 
  }
}
/* Module Definition */

/* Module Definition */
void C_drain_IO_L1_out_inter_trans_boundary(int idx, int idy, int c0, int c1, C_t4 local_C[2][8], tapa::ostream<C_t4> &fifo_C_drain_out) {
#pragma HLS INLINE
  /* Variable Declaration */
  int p0 = idx, p1 = idy; // module id
  /* Variable Declaration */

  for (int c4 = p1; c4 <= 31; c4 += 1) {
    // io_L1
    for (int c5 = 0; c5 <= 1; c5 += 1) {
      // access_coalesce
      for (int c6 = 0; c6 <= 7; c6 += 1) {
        #pragma HLS PIPELINE II=1
        {
          if (c4 == p1) {
            C_t4 in_data;
            C_t4 out_data;
            in_data = local_C[c5][c6];
            out_data = in_data;
            fifo_C_drain_out.write(out_data);
          }
        }
      }
    }
  }
}
/* Module Definition */

/* Module Definition */
void C_drain_IO_L1_out(int idx, int idy, tapa::istream<C_t4> &fifo_C_drain_in, tapa::ostream<C_t4> &fifo_C_drain_out, tapa::istream<float> &fifo_C_drain_local_in) {
#pragma HLS INLINE OFF
  /* Variable Declaration */
  int p0 = idx, p1 = idy; // module id
  C_t4 local_C[2][8];
  #pragma HLS RESOURCE variable=local_C core=RAM_2P_BRAM
  /* Variable Declaration */

  for (int c0 = 0; c0 <= 15; c0 += 1)
    for (int c1 = 0; c1 <= 7; c1 += 1) {
      // array
      // io_L3
      // io_L2
      C_drain_IO_L1_out_intra_trans(
        /* module id */ idx, 
        /* module id */ idy, 
        /* host iter */ c0, 
        /* host iter */ c1, 
        /* array */ local_C, 
        /* fifo */ fifo_C_drain_local_in
      );
      C_drain_IO_L1_out_inter_trans(
        /* module id */ idx, 
        /* module id */ idy, 
        /* host iter */ c0, 
        /* host iter */ c1, 
        /* array */ local_C, 
        /* fifo */ fifo_C_drain_in, 
        /* fifo */ fifo_C_drain_out
      );
    }
}
/* Module Definition */

/* Module Definition */
void C_drain_IO_L1_out_wrapper(int idx, int idy, tapa::istream<C_t4> &fifo_C_drain_in, tapa::ostream<C_t4> &fifo_C_drain_out, tapa::istream<float> &fifo_C_drain_local_in)
 {
  C_drain_IO_L1_out(
    /* module id */ idx, 
    /* module id */ idy, 
    /* fifo */ fifo_C_drain_in, 
    /* fifo */ fifo_C_drain_out, 
    /* fifo */ fifo_C_drain_local_in);
}
/* Module Definition */

/* Module Definition */
void C_drain_IO_L1_out_boundary(int idx, int idy, tapa::ostream<C_t4> &fifo_C_drain_out, tapa::istream<float> &fifo_C_drain_local_in) {
#pragma HLS INLINE
  /* Variable Declaration */
  int p0 = idx, p1 = idy; // module id
  C_t4 local_C[2][8];
  #pragma HLS RESOURCE variable=local_C core=RAM_2P_BRAM
  /* Variable Declaration */

  for (int c0 = 0; c0 <= 15; c0 += 1)
    for (int c1 = 0; c1 <= 7; c1 += 1) {
      // array
      // io_L3
      // io_L2
      C_drain_IO_L1_out_intra_trans(
        /* module id */ idx, 
        /* module id */ idy, 
        /* host iter */ c0, 
        /* host iter */ c1, 
        /* array */ local_C, 
        /* fifo */ fifo_C_drain_local_in
      );
      C_drain_IO_L1_out_inter_trans_boundary(
        /* module id */ idx, 
        /* module id */ idy, 
        /* host iter */ c0, 
        /* host iter */ c1, 
        /* array */ local_C, 
        /* fifo */ fifo_C_drain_out
      );
    }
}
/* Module Definition */

/* Module Definition */
void C_drain_IO_L1_out_boundary_wrapper(int idx, int idy, tapa::ostream<C_t4> &fifo_C_drain_out, tapa::istream<float> &fifo_C_drain_local_in)
 {
  C_drain_IO_L1_out_boundary(
    /* module id */ idx, 
    /* module id */ idy, 
    /* fifo */ fifo_C_drain_out, 
    /* fifo */ fifo_C_drain_local_in);
}
/* Module Definition */

/* Module Definition */
void C_drain_IO_L2_out(int idx, tapa::istream<C_t4> &fifo_C_drain_in, tapa::ostream<C_t4> &fifo_C_drain_out, tapa::istream<C_t4> &fifo_C_drain_local_in) {
#pragma HLS INLINE OFF
  /* Variable Declaration */
  int p0 = idx; // module id
  /* Variable Declaration */

  for (int c0 = 0; c0 <= 15; c0 += 1) {
    for (int c1 = 0; c1 <= 7; c1 += 1) {
      // array
      // io_L3
      for (int c3 = p0; c3 <= 3; c3 += 1) {
      // io_L2
        for (int c4 = 0; c4 <= 31; c4 += 1) {
          // io_L1
          for (int c5 = 0; c5 <= 1; c5 += 1) {
            // access_coalesce
            for (int c6 = 0; c6 <= 7; c6 += 1) {
            #pragma HLS PIPELINE II=1
              {
                if (c3 == p0) {
                  C_t4 in_data;
                  C_t4 out_data;
                  in_data = fifo_C_drain_local_in.read();
                  out_data = in_data;
                  fifo_C_drain_out.write(out_data);
                }else{
                  C_t4 in_data;
                  C_t4 out_data;
                  in_data = fifo_C_drain_in.read();
                  out_data = in_data;
                  fifo_C_drain_out.write(out_data);
                }
              }
            }
          }
        }
      }
    }
  }
}
/* Module Definition */

/* Module Definition */
void C_drain_IO_L2_out_boundary(int idx, tapa::ostream<C_t4> &fifo_C_drain_out, tapa::istream<C_t4> &fifo_C_drain_local_in) {
#pragma HLS INLINE OFF
  /* Variable Declaration */
  int p0 = idx; // module id
  /* Variable Declaration */

  for (int c0 = 0; c0 <= 15; c0 += 1) {
    for (int c1 = 0; c1 <= 7; c1 += 1) {
      // array
      // io_L3
      for (int c3 = p0; c3 <= 3; c3 += 1) {
        // io_L2
        for (int c4 = 0; c4 <= 31; c4 += 1) {
          // io_L1
          for (int c5 = 0; c5 <= 1; c5 += 1) {
            // access_coalesce
            for (int c6 = 0; c6 <= 7; c6 += 1) {
            #pragma HLS PIPELINE II=1
              {
                if (c3 == p0) {
                  C_t4 in_data;
                  C_t4 out_data;
                  in_data = fifo_C_drain_local_in.read();
                  out_data = in_data;
                  fifo_C_drain_out.write(out_data);
                }
              }
            }
          }
        }
      }
    }
  }
}
/* Module Definition */

/* Module Definition */
void C_drain_IO_L3_out(tapa::ostream<C_t4> &fifo_C_drain_out, tapa::istream<C_t4> &fifo_C_drain_local_in) {
#pragma HLS INLINE OFF
  /* Variable Declaration */
  /* Variable Declaration */

  for (int c0 = 0; c0 <= 15; c0 += 1)
    for (int c1 = 0; c1 <= 7; c1 += 1) {
      // array
      // io_L3
      for (int c3 = 0; c3 <= 3; c3 += 1) {
        // io_L2
        for (int c4 = 0; c4 <= 31; c4 += 1) {
          // io_L1
          for (int c5 = 0; c5 <= 1; c5 += 1) {
            // access_coalesce
            // access_serialize
            for (int c6 = 0; c6 <= 7; c6 += 1) {
            #pragma HLS PIPELINE II=1
              {
                C_t4 in_data;
                C_t4 out_data;
                in_data = fifo_C_drain_local_in.read();
                out_data = in_data;
                fifo_C_drain_out.write(out_data);
              }
            }
          }
        }
      }
    }
}
/* Module Definition */

/* Module Definition */
void C_drain_IO_L3_out_serialize(C_t16_mmap C, tapa::istream<C_t4> &fifo_C_drain_local_in) {
#pragma HLS INLINE OFF
  /* Variable Declaration */
  /* Variable Declaration */

  for (int i = 0; i < 65536; i++) {
  #pragma HLS PIPELINE II=1
    C_t4 fifo_data;
    C_t16 mem_data;
    C_t4 mem_data_split[4];
    #pragma HLS ARRAY_PARTITION variable=mem_data_split complete
    for (int p = 0; p < 4; p++) {
      fifo_data = fifo_C_drain_local_in.read();
      mem_data_split[p] = fifo_data;
    }
    mem_data.set(0, mem_data_split[0][0]);
    mem_data.set(1, mem_data_split[0][1]);
    mem_data.set(2, mem_data_split[0][2]);
    mem_data.set(3, mem_data_split[0][3]);
    mem_data.set(4, mem_data_split[1][0]);
    mem_data.set(5, mem_data_split[1][1]);
    mem_data.set(6, mem_data_split[1][2]);
    mem_data.set(7, mem_data_split[1][3]);
    mem_data.set(8, mem_data_split[2][0]);
    mem_data.set(9, mem_data_split[2][1]);
    mem_data.set(10, mem_data_split[2][2]);
    mem_data.set(11, mem_data_split[2][3]);
    mem_data.set(12, mem_data_split[3][0]);
    mem_data.set(13, mem_data_split[3][1]);
    mem_data.set(14, mem_data_split[3][2]);
    mem_data.set(15, mem_data_split[3][3]);
    C[i] = tapa::bit_cast<bits<C_t16> >(mem_data);
  }
}
/* Module Definition */

void kernel0(A_t16_mmap A, B_t16_mmap B, C_t16_mmap C)
{
  /* FIFO Declaration */
  /* A_IO_L3_in_serialize fifo */ tapa::stream<A_t16, 2> fifo_A_A_IO_L3_in_serialize;
  /* B_IO_L3_in_serialize fifo */ tapa::stream<B_t16, 2> fifo_B_B_IO_L3_in_serialize;
  /* C_drain_IO_L3_out_serialize fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L3_out_serialize;
  /* A_IO_L2_in fifo */ tapa::stream<A_t16, 2> fifo_A_A_IO_L2_in_0("fifo_A_A_IO_L2_in_0");
  /* A_IO_L2_in fifo */ tapa::stream<A_t16, 2> fifo_A_A_IO_L2_in_1("fifo_A_A_IO_L2_in_1");
  /* A_IO_L2_in fifo */ tapa::stream<A_t16, 2> fifo_A_A_IO_L2_in_2("fifo_A_A_IO_L2_in_2");
  /* A_IO_L2_in fifo */ tapa::stream<A_t16, 2> fifo_A_A_IO_L2_in_3("fifo_A_A_IO_L2_in_3");
  /* A_IO_L2_in fifo */ tapa::stream<A_t16, 2> fifo_A_A_IO_L2_in_4("fifo_A_A_IO_L2_in_4");
  /* A_IO_L2_in fifo */ tapa::stream<A_t16, 2> fifo_A_A_IO_L2_in_5("fifo_A_A_IO_L2_in_5");
  /* A_IO_L2_in fifo */ tapa::stream<A_t16, 2> fifo_A_A_IO_L2_in_6("fifo_A_A_IO_L2_in_6");
  /* A_IO_L2_in fifo */ tapa::stream<A_t16, 2> fifo_A_A_IO_L2_in_7("fifo_A_A_IO_L2_in_7");
  /* A_IO_L2_in fifo */ tapa::stream<A_t16, 2> fifo_A_A_IO_L2_in_8("fifo_A_A_IO_L2_in_8");
  /* A_IO_L2_in fifo */ tapa::stream<A_t16, 2> fifo_A_A_IO_L2_in_9("fifo_A_A_IO_L2_in_9");
  /* A_IO_L2_in fifo */ tapa::stream<A_t16, 2> fifo_A_A_IO_L2_in_10("fifo_A_A_IO_L2_in_10");
  /* A_IO_L2_in fifo */ tapa::stream<A_t16, 2> fifo_A_A_IO_L2_in_11("fifo_A_A_IO_L2_in_11");
  /* A_IO_L2_in fifo */ tapa::stream<A_t16, 2> fifo_A_A_IO_L2_in_12("fifo_A_A_IO_L2_in_12");
  /* A_IO_L2_in fifo */ tapa::stream<A_t16, 2> fifo_A_A_IO_L2_in_13("fifo_A_A_IO_L2_in_13");
  /* A_IO_L2_in fifo */ tapa::stream<A_t16, 2> fifo_A_A_IO_L2_in_14("fifo_A_A_IO_L2_in_14");
  /* A_IO_L2_in fifo */ tapa::stream<A_t16, 2> fifo_A_A_IO_L2_in_15("fifo_A_A_IO_L2_in_15");
  /* A_IO_L2_in fifo */ tapa::stream<A_t16, 2> fifo_A_A_IO_L2_in_16("fifo_A_A_IO_L2_in_16");
  /* A_IO_L2_in fifo */ tapa::stream<A_t16, 2> fifo_A_A_IO_L2_in_17("fifo_A_A_IO_L2_in_17");
  /* A_IO_L2_in fifo */ tapa::stream<A_t16, 2> fifo_A_A_IO_L2_in_18("fifo_A_A_IO_L2_in_18");
  /* A_IO_L2_in fifo */ tapa::stream<A_t16, 2> fifo_A_A_IO_L2_in_19("fifo_A_A_IO_L2_in_19");
  /* A_IO_L2_in fifo */ tapa::stream<A_t16, 2> fifo_A_A_IO_L2_in_20("fifo_A_A_IO_L2_in_20");
  /* A_IO_L2_in fifo */ tapa::stream<A_t16, 2> fifo_A_A_IO_L2_in_21("fifo_A_A_IO_L2_in_21");
  /* A_IO_L2_in fifo */ tapa::stream<A_t16, 2> fifo_A_A_IO_L2_in_22("fifo_A_A_IO_L2_in_22");
  /* A_IO_L2_in fifo */ tapa::stream<A_t16, 2> fifo_A_A_IO_L2_in_23("fifo_A_A_IO_L2_in_23");
  /* A_IO_L2_in fifo */ tapa::stream<A_t16, 2> fifo_A_A_IO_L2_in_24("fifo_A_A_IO_L2_in_24");
  /* A_IO_L2_in fifo */ tapa::stream<A_t16, 2> fifo_A_A_IO_L2_in_25("fifo_A_A_IO_L2_in_25");
  /* A_IO_L2_in fifo */ tapa::stream<A_t16, 2> fifo_A_A_IO_L2_in_26("fifo_A_A_IO_L2_in_26");
  /* A_IO_L2_in fifo */ tapa::stream<A_t16, 2> fifo_A_A_IO_L2_in_27("fifo_A_A_IO_L2_in_27");
  /* A_IO_L2_in fifo */ tapa::stream<A_t16, 2> fifo_A_A_IO_L2_in_28("fifo_A_A_IO_L2_in_28");
  /* A_IO_L2_in fifo */ tapa::stream<A_t16, 2> fifo_A_A_IO_L2_in_29("fifo_A_A_IO_L2_in_29");
  /* A_IO_L2_in fifo */ tapa::stream<A_t16, 2> fifo_A_A_IO_L2_in_30("fifo_A_A_IO_L2_in_30");
  /* A_IO_L2_in fifo */ tapa::stream<A_t16, 2> fifo_A_A_IO_L2_in_31("fifo_A_A_IO_L2_in_31");
  /* A_IO_L2_in fifo */ tapa::stream<A_t16, 2> fifo_A_A_IO_L2_in_32("fifo_A_A_IO_L2_in_32");
  /* B_IO_L2_in fifo */ tapa::stream<B_t16, 2> fifo_B_B_IO_L2_in_0("fifo_B_B_IO_L2_in_0");
  /* B_IO_L2_in fifo */ tapa::stream<B_t16, 2> fifo_B_B_IO_L2_in_1("fifo_B_B_IO_L2_in_1");
  /* B_IO_L2_in fifo */ tapa::stream<B_t16, 2> fifo_B_B_IO_L2_in_2("fifo_B_B_IO_L2_in_2");
  /* B_IO_L2_in fifo */ tapa::stream<B_t16, 2> fifo_B_B_IO_L2_in_3("fifo_B_B_IO_L2_in_3");
  /* B_IO_L2_in fifo */ tapa::stream<B_t16, 2> fifo_B_B_IO_L2_in_4("fifo_B_B_IO_L2_in_4");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_0_0("fifo_A_PE_0_0");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_0_1("fifo_A_PE_0_1");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_0_2("fifo_A_PE_0_2");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_0_3("fifo_A_PE_0_3");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_0_4("fifo_A_PE_0_4");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_1_0("fifo_A_PE_1_0");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_1_1("fifo_A_PE_1_1");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_1_2("fifo_A_PE_1_2");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_1_3("fifo_A_PE_1_3");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_1_4("fifo_A_PE_1_4");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_2_0("fifo_A_PE_2_0");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_2_1("fifo_A_PE_2_1");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_2_2("fifo_A_PE_2_2");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_2_3("fifo_A_PE_2_3");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_2_4("fifo_A_PE_2_4");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_3_0("fifo_A_PE_3_0");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_3_1("fifo_A_PE_3_1");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_3_2("fifo_A_PE_3_2");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_3_3("fifo_A_PE_3_3");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_3_4("fifo_A_PE_3_4");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_4_0("fifo_A_PE_4_0");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_4_1("fifo_A_PE_4_1");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_4_2("fifo_A_PE_4_2");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_4_3("fifo_A_PE_4_3");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_4_4("fifo_A_PE_4_4");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_5_0("fifo_A_PE_5_0");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_5_1("fifo_A_PE_5_1");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_5_2("fifo_A_PE_5_2");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_5_3("fifo_A_PE_5_3");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_5_4("fifo_A_PE_5_4");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_6_0("fifo_A_PE_6_0");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_6_1("fifo_A_PE_6_1");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_6_2("fifo_A_PE_6_2");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_6_3("fifo_A_PE_6_3");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_6_4("fifo_A_PE_6_4");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_7_0("fifo_A_PE_7_0");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_7_1("fifo_A_PE_7_1");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_7_2("fifo_A_PE_7_2");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_7_3("fifo_A_PE_7_3");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_7_4("fifo_A_PE_7_4");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_8_0("fifo_A_PE_8_0");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_8_1("fifo_A_PE_8_1");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_8_2("fifo_A_PE_8_2");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_8_3("fifo_A_PE_8_3");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_8_4("fifo_A_PE_8_4");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_9_0("fifo_A_PE_9_0");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_9_1("fifo_A_PE_9_1");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_9_2("fifo_A_PE_9_2");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_9_3("fifo_A_PE_9_3");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_9_4("fifo_A_PE_9_4");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_10_0("fifo_A_PE_10_0");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_10_1("fifo_A_PE_10_1");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_10_2("fifo_A_PE_10_2");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_10_3("fifo_A_PE_10_3");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_10_4("fifo_A_PE_10_4");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_11_0("fifo_A_PE_11_0");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_11_1("fifo_A_PE_11_1");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_11_2("fifo_A_PE_11_2");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_11_3("fifo_A_PE_11_3");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_11_4("fifo_A_PE_11_4");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_12_0("fifo_A_PE_12_0");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_12_1("fifo_A_PE_12_1");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_12_2("fifo_A_PE_12_2");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_12_3("fifo_A_PE_12_3");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_12_4("fifo_A_PE_12_4");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_13_0("fifo_A_PE_13_0");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_13_1("fifo_A_PE_13_1");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_13_2("fifo_A_PE_13_2");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_13_3("fifo_A_PE_13_3");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_13_4("fifo_A_PE_13_4");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_14_0("fifo_A_PE_14_0");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_14_1("fifo_A_PE_14_1");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_14_2("fifo_A_PE_14_2");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_14_3("fifo_A_PE_14_3");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_14_4("fifo_A_PE_14_4");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_15_0("fifo_A_PE_15_0");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_15_1("fifo_A_PE_15_1");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_15_2("fifo_A_PE_15_2");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_15_3("fifo_A_PE_15_3");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_15_4("fifo_A_PE_15_4");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_16_0("fifo_A_PE_16_0");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_16_1("fifo_A_PE_16_1");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_16_2("fifo_A_PE_16_2");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_16_3("fifo_A_PE_16_3");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_16_4("fifo_A_PE_16_4");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_17_0("fifo_A_PE_17_0");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_17_1("fifo_A_PE_17_1");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_17_2("fifo_A_PE_17_2");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_17_3("fifo_A_PE_17_3");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_17_4("fifo_A_PE_17_4");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_18_0("fifo_A_PE_18_0");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_18_1("fifo_A_PE_18_1");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_18_2("fifo_A_PE_18_2");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_18_3("fifo_A_PE_18_3");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_18_4("fifo_A_PE_18_4");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_19_0("fifo_A_PE_19_0");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_19_1("fifo_A_PE_19_1");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_19_2("fifo_A_PE_19_2");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_19_3("fifo_A_PE_19_3");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_19_4("fifo_A_PE_19_4");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_20_0("fifo_A_PE_20_0");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_20_1("fifo_A_PE_20_1");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_20_2("fifo_A_PE_20_2");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_20_3("fifo_A_PE_20_3");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_20_4("fifo_A_PE_20_4");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_21_0("fifo_A_PE_21_0");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_21_1("fifo_A_PE_21_1");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_21_2("fifo_A_PE_21_2");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_21_3("fifo_A_PE_21_3");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_21_4("fifo_A_PE_21_4");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_22_0("fifo_A_PE_22_0");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_22_1("fifo_A_PE_22_1");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_22_2("fifo_A_PE_22_2");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_22_3("fifo_A_PE_22_3");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_22_4("fifo_A_PE_22_4");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_23_0("fifo_A_PE_23_0");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_23_1("fifo_A_PE_23_1");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_23_2("fifo_A_PE_23_2");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_23_3("fifo_A_PE_23_3");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_23_4("fifo_A_PE_23_4");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_24_0("fifo_A_PE_24_0");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_24_1("fifo_A_PE_24_1");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_24_2("fifo_A_PE_24_2");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_24_3("fifo_A_PE_24_3");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_24_4("fifo_A_PE_24_4");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_25_0("fifo_A_PE_25_0");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_25_1("fifo_A_PE_25_1");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_25_2("fifo_A_PE_25_2");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_25_3("fifo_A_PE_25_3");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_25_4("fifo_A_PE_25_4");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_26_0("fifo_A_PE_26_0");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_26_1("fifo_A_PE_26_1");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_26_2("fifo_A_PE_26_2");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_26_3("fifo_A_PE_26_3");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_26_4("fifo_A_PE_26_4");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_27_0("fifo_A_PE_27_0");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_27_1("fifo_A_PE_27_1");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_27_2("fifo_A_PE_27_2");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_27_3("fifo_A_PE_27_3");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_27_4("fifo_A_PE_27_4");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_28_0("fifo_A_PE_28_0");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_28_1("fifo_A_PE_28_1");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_28_2("fifo_A_PE_28_2");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_28_3("fifo_A_PE_28_3");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_28_4("fifo_A_PE_28_4");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_29_0("fifo_A_PE_29_0");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_29_1("fifo_A_PE_29_1");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_29_2("fifo_A_PE_29_2");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_29_3("fifo_A_PE_29_3");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_29_4("fifo_A_PE_29_4");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_30_0("fifo_A_PE_30_0");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_30_1("fifo_A_PE_30_1");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_30_2("fifo_A_PE_30_2");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_30_3("fifo_A_PE_30_3");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_30_4("fifo_A_PE_30_4");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_31_0("fifo_A_PE_31_0");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_31_1("fifo_A_PE_31_1");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_31_2("fifo_A_PE_31_2");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_31_3("fifo_A_PE_31_3");
  /* PE fifo */ tapa::stream<A_t8, 2> fifo_A_PE_31_4("fifo_A_PE_31_4");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_0_0("fifo_B_PE_0_0");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_1_0("fifo_B_PE_1_0");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_2_0("fifo_B_PE_2_0");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_3_0("fifo_B_PE_3_0");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_4_0("fifo_B_PE_4_0");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_5_0("fifo_B_PE_5_0");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_6_0("fifo_B_PE_6_0");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_7_0("fifo_B_PE_7_0");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_8_0("fifo_B_PE_8_0");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_9_0("fifo_B_PE_9_0");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_10_0("fifo_B_PE_10_0");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_11_0("fifo_B_PE_11_0");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_12_0("fifo_B_PE_12_0");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_13_0("fifo_B_PE_13_0");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_14_0("fifo_B_PE_14_0");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_15_0("fifo_B_PE_15_0");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_16_0("fifo_B_PE_16_0");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_17_0("fifo_B_PE_17_0");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_18_0("fifo_B_PE_18_0");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_19_0("fifo_B_PE_19_0");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_20_0("fifo_B_PE_20_0");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_21_0("fifo_B_PE_21_0");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_22_0("fifo_B_PE_22_0");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_23_0("fifo_B_PE_23_0");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_24_0("fifo_B_PE_24_0");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_25_0("fifo_B_PE_25_0");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_26_0("fifo_B_PE_26_0");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_27_0("fifo_B_PE_27_0");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_28_0("fifo_B_PE_28_0");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_29_0("fifo_B_PE_29_0");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_30_0("fifo_B_PE_30_0");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_31_0("fifo_B_PE_31_0");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_32_0("fifo_B_PE_32_0");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_0_1("fifo_B_PE_0_1");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_1_1("fifo_B_PE_1_1");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_2_1("fifo_B_PE_2_1");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_3_1("fifo_B_PE_3_1");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_4_1("fifo_B_PE_4_1");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_5_1("fifo_B_PE_5_1");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_6_1("fifo_B_PE_6_1");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_7_1("fifo_B_PE_7_1");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_8_1("fifo_B_PE_8_1");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_9_1("fifo_B_PE_9_1");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_10_1("fifo_B_PE_10_1");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_11_1("fifo_B_PE_11_1");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_12_1("fifo_B_PE_12_1");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_13_1("fifo_B_PE_13_1");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_14_1("fifo_B_PE_14_1");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_15_1("fifo_B_PE_15_1");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_16_1("fifo_B_PE_16_1");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_17_1("fifo_B_PE_17_1");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_18_1("fifo_B_PE_18_1");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_19_1("fifo_B_PE_19_1");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_20_1("fifo_B_PE_20_1");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_21_1("fifo_B_PE_21_1");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_22_1("fifo_B_PE_22_1");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_23_1("fifo_B_PE_23_1");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_24_1("fifo_B_PE_24_1");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_25_1("fifo_B_PE_25_1");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_26_1("fifo_B_PE_26_1");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_27_1("fifo_B_PE_27_1");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_28_1("fifo_B_PE_28_1");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_29_1("fifo_B_PE_29_1");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_30_1("fifo_B_PE_30_1");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_31_1("fifo_B_PE_31_1");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_32_1("fifo_B_PE_32_1");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_0_2("fifo_B_PE_0_2");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_1_2("fifo_B_PE_1_2");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_2_2("fifo_B_PE_2_2");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_3_2("fifo_B_PE_3_2");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_4_2("fifo_B_PE_4_2");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_5_2("fifo_B_PE_5_2");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_6_2("fifo_B_PE_6_2");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_7_2("fifo_B_PE_7_2");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_8_2("fifo_B_PE_8_2");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_9_2("fifo_B_PE_9_2");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_10_2("fifo_B_PE_10_2");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_11_2("fifo_B_PE_11_2");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_12_2("fifo_B_PE_12_2");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_13_2("fifo_B_PE_13_2");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_14_2("fifo_B_PE_14_2");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_15_2("fifo_B_PE_15_2");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_16_2("fifo_B_PE_16_2");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_17_2("fifo_B_PE_17_2");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_18_2("fifo_B_PE_18_2");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_19_2("fifo_B_PE_19_2");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_20_2("fifo_B_PE_20_2");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_21_2("fifo_B_PE_21_2");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_22_2("fifo_B_PE_22_2");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_23_2("fifo_B_PE_23_2");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_24_2("fifo_B_PE_24_2");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_25_2("fifo_B_PE_25_2");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_26_2("fifo_B_PE_26_2");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_27_2("fifo_B_PE_27_2");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_28_2("fifo_B_PE_28_2");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_29_2("fifo_B_PE_29_2");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_30_2("fifo_B_PE_30_2");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_31_2("fifo_B_PE_31_2");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_32_2("fifo_B_PE_32_2");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_0_3("fifo_B_PE_0_3");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_1_3("fifo_B_PE_1_3");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_2_3("fifo_B_PE_2_3");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_3_3("fifo_B_PE_3_3");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_4_3("fifo_B_PE_4_3");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_5_3("fifo_B_PE_5_3");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_6_3("fifo_B_PE_6_3");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_7_3("fifo_B_PE_7_3");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_8_3("fifo_B_PE_8_3");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_9_3("fifo_B_PE_9_3");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_10_3("fifo_B_PE_10_3");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_11_3("fifo_B_PE_11_3");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_12_3("fifo_B_PE_12_3");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_13_3("fifo_B_PE_13_3");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_14_3("fifo_B_PE_14_3");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_15_3("fifo_B_PE_15_3");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_16_3("fifo_B_PE_16_3");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_17_3("fifo_B_PE_17_3");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_18_3("fifo_B_PE_18_3");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_19_3("fifo_B_PE_19_3");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_20_3("fifo_B_PE_20_3");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_21_3("fifo_B_PE_21_3");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_22_3("fifo_B_PE_22_3");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_23_3("fifo_B_PE_23_3");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_24_3("fifo_B_PE_24_3");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_25_3("fifo_B_PE_25_3");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_26_3("fifo_B_PE_26_3");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_27_3("fifo_B_PE_27_3");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_28_3("fifo_B_PE_28_3");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_29_3("fifo_B_PE_29_3");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_30_3("fifo_B_PE_30_3");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_31_3("fifo_B_PE_31_3");
  /* PE fifo */ tapa::stream<B_t8, 2> fifo_B_PE_32_3("fifo_B_PE_32_3");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_0_0("fifo_C_drain_PE_0_0");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_1_0("fifo_C_drain_PE_1_0");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_2_0("fifo_C_drain_PE_2_0");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_3_0("fifo_C_drain_PE_3_0");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_4_0("fifo_C_drain_PE_4_0");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_5_0("fifo_C_drain_PE_5_0");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_6_0("fifo_C_drain_PE_6_0");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_7_0("fifo_C_drain_PE_7_0");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_8_0("fifo_C_drain_PE_8_0");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_9_0("fifo_C_drain_PE_9_0");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_10_0("fifo_C_drain_PE_10_0");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_11_0("fifo_C_drain_PE_11_0");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_12_0("fifo_C_drain_PE_12_0");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_13_0("fifo_C_drain_PE_13_0");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_14_0("fifo_C_drain_PE_14_0");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_15_0("fifo_C_drain_PE_15_0");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_16_0("fifo_C_drain_PE_16_0");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_17_0("fifo_C_drain_PE_17_0");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_18_0("fifo_C_drain_PE_18_0");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_19_0("fifo_C_drain_PE_19_0");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_20_0("fifo_C_drain_PE_20_0");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_21_0("fifo_C_drain_PE_21_0");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_22_0("fifo_C_drain_PE_22_0");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_23_0("fifo_C_drain_PE_23_0");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_24_0("fifo_C_drain_PE_24_0");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_25_0("fifo_C_drain_PE_25_0");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_26_0("fifo_C_drain_PE_26_0");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_27_0("fifo_C_drain_PE_27_0");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_28_0("fifo_C_drain_PE_28_0");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_29_0("fifo_C_drain_PE_29_0");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_30_0("fifo_C_drain_PE_30_0");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_31_0("fifo_C_drain_PE_31_0");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_0_1("fifo_C_drain_PE_0_1");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_1_1("fifo_C_drain_PE_1_1");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_2_1("fifo_C_drain_PE_2_1");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_3_1("fifo_C_drain_PE_3_1");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_4_1("fifo_C_drain_PE_4_1");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_5_1("fifo_C_drain_PE_5_1");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_6_1("fifo_C_drain_PE_6_1");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_7_1("fifo_C_drain_PE_7_1");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_8_1("fifo_C_drain_PE_8_1");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_9_1("fifo_C_drain_PE_9_1");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_10_1("fifo_C_drain_PE_10_1");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_11_1("fifo_C_drain_PE_11_1");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_12_1("fifo_C_drain_PE_12_1");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_13_1("fifo_C_drain_PE_13_1");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_14_1("fifo_C_drain_PE_14_1");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_15_1("fifo_C_drain_PE_15_1");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_16_1("fifo_C_drain_PE_16_1");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_17_1("fifo_C_drain_PE_17_1");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_18_1("fifo_C_drain_PE_18_1");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_19_1("fifo_C_drain_PE_19_1");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_20_1("fifo_C_drain_PE_20_1");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_21_1("fifo_C_drain_PE_21_1");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_22_1("fifo_C_drain_PE_22_1");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_23_1("fifo_C_drain_PE_23_1");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_24_1("fifo_C_drain_PE_24_1");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_25_1("fifo_C_drain_PE_25_1");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_26_1("fifo_C_drain_PE_26_1");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_27_1("fifo_C_drain_PE_27_1");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_28_1("fifo_C_drain_PE_28_1");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_29_1("fifo_C_drain_PE_29_1");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_30_1("fifo_C_drain_PE_30_1");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_31_1("fifo_C_drain_PE_31_1");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_0_2("fifo_C_drain_PE_0_2");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_1_2("fifo_C_drain_PE_1_2");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_2_2("fifo_C_drain_PE_2_2");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_3_2("fifo_C_drain_PE_3_2");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_4_2("fifo_C_drain_PE_4_2");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_5_2("fifo_C_drain_PE_5_2");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_6_2("fifo_C_drain_PE_6_2");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_7_2("fifo_C_drain_PE_7_2");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_8_2("fifo_C_drain_PE_8_2");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_9_2("fifo_C_drain_PE_9_2");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_10_2("fifo_C_drain_PE_10_2");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_11_2("fifo_C_drain_PE_11_2");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_12_2("fifo_C_drain_PE_12_2");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_13_2("fifo_C_drain_PE_13_2");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_14_2("fifo_C_drain_PE_14_2");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_15_2("fifo_C_drain_PE_15_2");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_16_2("fifo_C_drain_PE_16_2");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_17_2("fifo_C_drain_PE_17_2");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_18_2("fifo_C_drain_PE_18_2");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_19_2("fifo_C_drain_PE_19_2");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_20_2("fifo_C_drain_PE_20_2");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_21_2("fifo_C_drain_PE_21_2");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_22_2("fifo_C_drain_PE_22_2");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_23_2("fifo_C_drain_PE_23_2");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_24_2("fifo_C_drain_PE_24_2");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_25_2("fifo_C_drain_PE_25_2");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_26_2("fifo_C_drain_PE_26_2");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_27_2("fifo_C_drain_PE_27_2");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_28_2("fifo_C_drain_PE_28_2");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_29_2("fifo_C_drain_PE_29_2");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_30_2("fifo_C_drain_PE_30_2");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_31_2("fifo_C_drain_PE_31_2");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_0_3("fifo_C_drain_PE_0_3");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_1_3("fifo_C_drain_PE_1_3");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_2_3("fifo_C_drain_PE_2_3");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_3_3("fifo_C_drain_PE_3_3");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_4_3("fifo_C_drain_PE_4_3");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_5_3("fifo_C_drain_PE_5_3");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_6_3("fifo_C_drain_PE_6_3");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_7_3("fifo_C_drain_PE_7_3");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_8_3("fifo_C_drain_PE_8_3");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_9_3("fifo_C_drain_PE_9_3");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_10_3("fifo_C_drain_PE_10_3");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_11_3("fifo_C_drain_PE_11_3");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_12_3("fifo_C_drain_PE_12_3");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_13_3("fifo_C_drain_PE_13_3");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_14_3("fifo_C_drain_PE_14_3");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_15_3("fifo_C_drain_PE_15_3");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_16_3("fifo_C_drain_PE_16_3");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_17_3("fifo_C_drain_PE_17_3");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_18_3("fifo_C_drain_PE_18_3");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_19_3("fifo_C_drain_PE_19_3");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_20_3("fifo_C_drain_PE_20_3");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_21_3("fifo_C_drain_PE_21_3");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_22_3("fifo_C_drain_PE_22_3");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_23_3("fifo_C_drain_PE_23_3");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_24_3("fifo_C_drain_PE_24_3");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_25_3("fifo_C_drain_PE_25_3");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_26_3("fifo_C_drain_PE_26_3");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_27_3("fifo_C_drain_PE_27_3");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_28_3("fifo_C_drain_PE_28_3");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_29_3("fifo_C_drain_PE_29_3");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_30_3("fifo_C_drain_PE_30_3");
  /* PE fifo */ tapa::stream<float, 2> fifo_C_drain_PE_31_3("fifo_C_drain_PE_31_3");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_0_0("fifo_C_drain_C_drain_IO_L1_out_0_0");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_0_1("fifo_C_drain_C_drain_IO_L1_out_0_1");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_0_2("fifo_C_drain_C_drain_IO_L1_out_0_2");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_0_3("fifo_C_drain_C_drain_IO_L1_out_0_3");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_0_4("fifo_C_drain_C_drain_IO_L1_out_0_4");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_0_5("fifo_C_drain_C_drain_IO_L1_out_0_5");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_0_6("fifo_C_drain_C_drain_IO_L1_out_0_6");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_0_7("fifo_C_drain_C_drain_IO_L1_out_0_7");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_0_8("fifo_C_drain_C_drain_IO_L1_out_0_8");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_0_9("fifo_C_drain_C_drain_IO_L1_out_0_9");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_0_10("fifo_C_drain_C_drain_IO_L1_out_0_10");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_0_11("fifo_C_drain_C_drain_IO_L1_out_0_11");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_0_12("fifo_C_drain_C_drain_IO_L1_out_0_12");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_0_13("fifo_C_drain_C_drain_IO_L1_out_0_13");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_0_14("fifo_C_drain_C_drain_IO_L1_out_0_14");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_0_15("fifo_C_drain_C_drain_IO_L1_out_0_15");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_0_16("fifo_C_drain_C_drain_IO_L1_out_0_16");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_0_17("fifo_C_drain_C_drain_IO_L1_out_0_17");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_0_18("fifo_C_drain_C_drain_IO_L1_out_0_18");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_0_19("fifo_C_drain_C_drain_IO_L1_out_0_19");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_0_20("fifo_C_drain_C_drain_IO_L1_out_0_20");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_0_21("fifo_C_drain_C_drain_IO_L1_out_0_21");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_0_22("fifo_C_drain_C_drain_IO_L1_out_0_22");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_0_23("fifo_C_drain_C_drain_IO_L1_out_0_23");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_0_24("fifo_C_drain_C_drain_IO_L1_out_0_24");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_0_25("fifo_C_drain_C_drain_IO_L1_out_0_25");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_0_26("fifo_C_drain_C_drain_IO_L1_out_0_26");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_0_27("fifo_C_drain_C_drain_IO_L1_out_0_27");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_0_28("fifo_C_drain_C_drain_IO_L1_out_0_28");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_0_29("fifo_C_drain_C_drain_IO_L1_out_0_29");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_0_30("fifo_C_drain_C_drain_IO_L1_out_0_30");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_0_31("fifo_C_drain_C_drain_IO_L1_out_0_31");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_0_32("fifo_C_drain_C_drain_IO_L1_out_0_32");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_1_0("fifo_C_drain_C_drain_IO_L1_out_1_0");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_1_1("fifo_C_drain_C_drain_IO_L1_out_1_1");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_1_2("fifo_C_drain_C_drain_IO_L1_out_1_2");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_1_3("fifo_C_drain_C_drain_IO_L1_out_1_3");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_1_4("fifo_C_drain_C_drain_IO_L1_out_1_4");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_1_5("fifo_C_drain_C_drain_IO_L1_out_1_5");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_1_6("fifo_C_drain_C_drain_IO_L1_out_1_6");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_1_7("fifo_C_drain_C_drain_IO_L1_out_1_7");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_1_8("fifo_C_drain_C_drain_IO_L1_out_1_8");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_1_9("fifo_C_drain_C_drain_IO_L1_out_1_9");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_1_10("fifo_C_drain_C_drain_IO_L1_out_1_10");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_1_11("fifo_C_drain_C_drain_IO_L1_out_1_11");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_1_12("fifo_C_drain_C_drain_IO_L1_out_1_12");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_1_13("fifo_C_drain_C_drain_IO_L1_out_1_13");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_1_14("fifo_C_drain_C_drain_IO_L1_out_1_14");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_1_15("fifo_C_drain_C_drain_IO_L1_out_1_15");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_1_16("fifo_C_drain_C_drain_IO_L1_out_1_16");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_1_17("fifo_C_drain_C_drain_IO_L1_out_1_17");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_1_18("fifo_C_drain_C_drain_IO_L1_out_1_18");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_1_19("fifo_C_drain_C_drain_IO_L1_out_1_19");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_1_20("fifo_C_drain_C_drain_IO_L1_out_1_20");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_1_21("fifo_C_drain_C_drain_IO_L1_out_1_21");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_1_22("fifo_C_drain_C_drain_IO_L1_out_1_22");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_1_23("fifo_C_drain_C_drain_IO_L1_out_1_23");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_1_24("fifo_C_drain_C_drain_IO_L1_out_1_24");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_1_25("fifo_C_drain_C_drain_IO_L1_out_1_25");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_1_26("fifo_C_drain_C_drain_IO_L1_out_1_26");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_1_27("fifo_C_drain_C_drain_IO_L1_out_1_27");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_1_28("fifo_C_drain_C_drain_IO_L1_out_1_28");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_1_29("fifo_C_drain_C_drain_IO_L1_out_1_29");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_1_30("fifo_C_drain_C_drain_IO_L1_out_1_30");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_1_31("fifo_C_drain_C_drain_IO_L1_out_1_31");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_1_32("fifo_C_drain_C_drain_IO_L1_out_1_32");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_2_0("fifo_C_drain_C_drain_IO_L1_out_2_0");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_2_1("fifo_C_drain_C_drain_IO_L1_out_2_1");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_2_2("fifo_C_drain_C_drain_IO_L1_out_2_2");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_2_3("fifo_C_drain_C_drain_IO_L1_out_2_3");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_2_4("fifo_C_drain_C_drain_IO_L1_out_2_4");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_2_5("fifo_C_drain_C_drain_IO_L1_out_2_5");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_2_6("fifo_C_drain_C_drain_IO_L1_out_2_6");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_2_7("fifo_C_drain_C_drain_IO_L1_out_2_7");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_2_8("fifo_C_drain_C_drain_IO_L1_out_2_8");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_2_9("fifo_C_drain_C_drain_IO_L1_out_2_9");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_2_10("fifo_C_drain_C_drain_IO_L1_out_2_10");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_2_11("fifo_C_drain_C_drain_IO_L1_out_2_11");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_2_12("fifo_C_drain_C_drain_IO_L1_out_2_12");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_2_13("fifo_C_drain_C_drain_IO_L1_out_2_13");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_2_14("fifo_C_drain_C_drain_IO_L1_out_2_14");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_2_15("fifo_C_drain_C_drain_IO_L1_out_2_15");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_2_16("fifo_C_drain_C_drain_IO_L1_out_2_16");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_2_17("fifo_C_drain_C_drain_IO_L1_out_2_17");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_2_18("fifo_C_drain_C_drain_IO_L1_out_2_18");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_2_19("fifo_C_drain_C_drain_IO_L1_out_2_19");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_2_20("fifo_C_drain_C_drain_IO_L1_out_2_20");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_2_21("fifo_C_drain_C_drain_IO_L1_out_2_21");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_2_22("fifo_C_drain_C_drain_IO_L1_out_2_22");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_2_23("fifo_C_drain_C_drain_IO_L1_out_2_23");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_2_24("fifo_C_drain_C_drain_IO_L1_out_2_24");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_2_25("fifo_C_drain_C_drain_IO_L1_out_2_25");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_2_26("fifo_C_drain_C_drain_IO_L1_out_2_26");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_2_27("fifo_C_drain_C_drain_IO_L1_out_2_27");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_2_28("fifo_C_drain_C_drain_IO_L1_out_2_28");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_2_29("fifo_C_drain_C_drain_IO_L1_out_2_29");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_2_30("fifo_C_drain_C_drain_IO_L1_out_2_30");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_2_31("fifo_C_drain_C_drain_IO_L1_out_2_31");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_2_32("fifo_C_drain_C_drain_IO_L1_out_2_32");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_3_0("fifo_C_drain_C_drain_IO_L1_out_3_0");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_3_1("fifo_C_drain_C_drain_IO_L1_out_3_1");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_3_2("fifo_C_drain_C_drain_IO_L1_out_3_2");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_3_3("fifo_C_drain_C_drain_IO_L1_out_3_3");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_3_4("fifo_C_drain_C_drain_IO_L1_out_3_4");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_3_5("fifo_C_drain_C_drain_IO_L1_out_3_5");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_3_6("fifo_C_drain_C_drain_IO_L1_out_3_6");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_3_7("fifo_C_drain_C_drain_IO_L1_out_3_7");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_3_8("fifo_C_drain_C_drain_IO_L1_out_3_8");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_3_9("fifo_C_drain_C_drain_IO_L1_out_3_9");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_3_10("fifo_C_drain_C_drain_IO_L1_out_3_10");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_3_11("fifo_C_drain_C_drain_IO_L1_out_3_11");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_3_12("fifo_C_drain_C_drain_IO_L1_out_3_12");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_3_13("fifo_C_drain_C_drain_IO_L1_out_3_13");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_3_14("fifo_C_drain_C_drain_IO_L1_out_3_14");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_3_15("fifo_C_drain_C_drain_IO_L1_out_3_15");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_3_16("fifo_C_drain_C_drain_IO_L1_out_3_16");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_3_17("fifo_C_drain_C_drain_IO_L1_out_3_17");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_3_18("fifo_C_drain_C_drain_IO_L1_out_3_18");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_3_19("fifo_C_drain_C_drain_IO_L1_out_3_19");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_3_20("fifo_C_drain_C_drain_IO_L1_out_3_20");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_3_21("fifo_C_drain_C_drain_IO_L1_out_3_21");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_3_22("fifo_C_drain_C_drain_IO_L1_out_3_22");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_3_23("fifo_C_drain_C_drain_IO_L1_out_3_23");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_3_24("fifo_C_drain_C_drain_IO_L1_out_3_24");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_3_25("fifo_C_drain_C_drain_IO_L1_out_3_25");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_3_26("fifo_C_drain_C_drain_IO_L1_out_3_26");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_3_27("fifo_C_drain_C_drain_IO_L1_out_3_27");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_3_28("fifo_C_drain_C_drain_IO_L1_out_3_28");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_3_29("fifo_C_drain_C_drain_IO_L1_out_3_29");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_3_30("fifo_C_drain_C_drain_IO_L1_out_3_30");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_3_31("fifo_C_drain_C_drain_IO_L1_out_3_31");
  /* C_drain_IO_L1_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L1_out_3_32("fifo_C_drain_C_drain_IO_L1_out_3_32");
  /* C_drain_IO_L2_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L2_out_0("fifo_C_drain_C_drain_IO_L2_out_0");
  /* C_drain_IO_L2_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L2_out_1("fifo_C_drain_C_drain_IO_L2_out_1");
  /* C_drain_IO_L2_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L2_out_2("fifo_C_drain_C_drain_IO_L2_out_2");
  /* C_drain_IO_L2_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L2_out_3("fifo_C_drain_C_drain_IO_L2_out_3");
  /* C_drain_IO_L2_out fifo */ tapa::stream<C_t4, 2> fifo_C_drain_C_drain_IO_L2_out_4("fifo_C_drain_C_drain_IO_L2_out_4");
  /* FIFO Declaration */

  tapa::task()
  /* Module Call */
  .invoke(A_IO_L3_in_serialize,
    /* array */ A,
    /* fifo */ fifo_A_A_IO_L3_in_serialize)
  /* Module Call */

  /* Module Call */
  .invoke(A_IO_L3_in,
    /* fifo */ fifo_A_A_IO_L3_in_serialize,
    /* fifo */ fifo_A_A_IO_L2_in_0)
  /* Module Call */

  /* Module Call */
  .invoke(A_IO_L2_in,
    /* module id */ 0,
    /* fifo */ fifo_A_A_IO_L2_in_0,
    /* fifo */ fifo_A_A_IO_L2_in_1,
    /* fifo */ fifo_A_PE_0_0)
  /* Module Call */

  /* Module Call */
  .invoke(A_IO_L2_in,
    /* module id */ 1,
    /* fifo */ fifo_A_A_IO_L2_in_1,
    /* fifo */ fifo_A_A_IO_L2_in_2,
    /* fifo */ fifo_A_PE_1_0)
  /* Module Call */

  /* Module Call */
  .invoke(A_IO_L2_in,
    /* module id */ 2,
    /* fifo */ fifo_A_A_IO_L2_in_2,
    /* fifo */ fifo_A_A_IO_L2_in_3,
    /* fifo */ fifo_A_PE_2_0)
  /* Module Call */

  /* Module Call */
  .invoke(A_IO_L2_in,
    /* module id */ 3,
    /* fifo */ fifo_A_A_IO_L2_in_3,
    /* fifo */ fifo_A_A_IO_L2_in_4,
    /* fifo */ fifo_A_PE_3_0)
  /* Module Call */

  /* Module Call */
  .invoke(A_IO_L2_in,
    /* module id */ 4,
    /* fifo */ fifo_A_A_IO_L2_in_4,
    /* fifo */ fifo_A_A_IO_L2_in_5,
    /* fifo */ fifo_A_PE_4_0)
  /* Module Call */

  /* Module Call */
  .invoke(A_IO_L2_in,
    /* module id */ 5,
    /* fifo */ fifo_A_A_IO_L2_in_5,
    /* fifo */ fifo_A_A_IO_L2_in_6,
    /* fifo */ fifo_A_PE_5_0)
  /* Module Call */

  /* Module Call */
  .invoke(A_IO_L2_in,
    /* module id */ 6,
    /* fifo */ fifo_A_A_IO_L2_in_6,
    /* fifo */ fifo_A_A_IO_L2_in_7,
    /* fifo */ fifo_A_PE_6_0)
  /* Module Call */

  /* Module Call */
  .invoke(A_IO_L2_in,
    /* module id */ 7,
    /* fifo */ fifo_A_A_IO_L2_in_7,
    /* fifo */ fifo_A_A_IO_L2_in_8,
    /* fifo */ fifo_A_PE_7_0)
  /* Module Call */

  /* Module Call */
  .invoke(A_IO_L2_in,
    /* module id */ 8,
    /* fifo */ fifo_A_A_IO_L2_in_8,
    /* fifo */ fifo_A_A_IO_L2_in_9,
    /* fifo */ fifo_A_PE_8_0)
  /* Module Call */

  /* Module Call */
  .invoke(A_IO_L2_in,
    /* module id */ 9,
    /* fifo */ fifo_A_A_IO_L2_in_9,
    /* fifo */ fifo_A_A_IO_L2_in_10,
    /* fifo */ fifo_A_PE_9_0)
  /* Module Call */

  /* Module Call */
  .invoke(A_IO_L2_in,
    /* module id */ 10,
    /* fifo */ fifo_A_A_IO_L2_in_10,
    /* fifo */ fifo_A_A_IO_L2_in_11,
    /* fifo */ fifo_A_PE_10_0)
  /* Module Call */

  /* Module Call */
  .invoke(A_IO_L2_in,
    /* module id */ 11,
    /* fifo */ fifo_A_A_IO_L2_in_11,
    /* fifo */ fifo_A_A_IO_L2_in_12,
    /* fifo */ fifo_A_PE_11_0)
  /* Module Call */

  /* Module Call */
  .invoke(A_IO_L2_in,
    /* module id */ 12,
    /* fifo */ fifo_A_A_IO_L2_in_12,
    /* fifo */ fifo_A_A_IO_L2_in_13,
    /* fifo */ fifo_A_PE_12_0)
  /* Module Call */

  /* Module Call */
  .invoke(A_IO_L2_in,
    /* module id */ 13,
    /* fifo */ fifo_A_A_IO_L2_in_13,
    /* fifo */ fifo_A_A_IO_L2_in_14,
    /* fifo */ fifo_A_PE_13_0)
  /* Module Call */

  /* Module Call */
  .invoke(A_IO_L2_in,
    /* module id */ 14,
    /* fifo */ fifo_A_A_IO_L2_in_14,
    /* fifo */ fifo_A_A_IO_L2_in_15,
    /* fifo */ fifo_A_PE_14_0)
  /* Module Call */

  /* Module Call */
  .invoke(A_IO_L2_in,
    /* module id */ 15,
    /* fifo */ fifo_A_A_IO_L2_in_15,
    /* fifo */ fifo_A_A_IO_L2_in_16,
    /* fifo */ fifo_A_PE_15_0)
  /* Module Call */

  /* Module Call */
  .invoke(A_IO_L2_in,
    /* module id */ 16,
    /* fifo */ fifo_A_A_IO_L2_in_16,
    /* fifo */ fifo_A_A_IO_L2_in_17,
    /* fifo */ fifo_A_PE_16_0)
  /* Module Call */

  /* Module Call */
  .invoke(A_IO_L2_in,
    /* module id */ 17,
    /* fifo */ fifo_A_A_IO_L2_in_17,
    /* fifo */ fifo_A_A_IO_L2_in_18,
    /* fifo */ fifo_A_PE_17_0)
  /* Module Call */

  /* Module Call */
  .invoke(A_IO_L2_in,
    /* module id */ 18,
    /* fifo */ fifo_A_A_IO_L2_in_18,
    /* fifo */ fifo_A_A_IO_L2_in_19,
    /* fifo */ fifo_A_PE_18_0)
  /* Module Call */

  /* Module Call */
  .invoke(A_IO_L2_in,
    /* module id */ 19,
    /* fifo */ fifo_A_A_IO_L2_in_19,
    /* fifo */ fifo_A_A_IO_L2_in_20,
    /* fifo */ fifo_A_PE_19_0)
  /* Module Call */

  /* Module Call */
  .invoke(A_IO_L2_in,
    /* module id */ 20,
    /* fifo */ fifo_A_A_IO_L2_in_20,
    /* fifo */ fifo_A_A_IO_L2_in_21,
    /* fifo */ fifo_A_PE_20_0)
  /* Module Call */

  /* Module Call */
  .invoke(A_IO_L2_in,
    /* module id */ 21,
    /* fifo */ fifo_A_A_IO_L2_in_21,
    /* fifo */ fifo_A_A_IO_L2_in_22,
    /* fifo */ fifo_A_PE_21_0)
  /* Module Call */

  /* Module Call */
  .invoke(A_IO_L2_in,
    /* module id */ 22,
    /* fifo */ fifo_A_A_IO_L2_in_22,
    /* fifo */ fifo_A_A_IO_L2_in_23,
    /* fifo */ fifo_A_PE_22_0)
  /* Module Call */

  /* Module Call */
  .invoke(A_IO_L2_in,
    /* module id */ 23,
    /* fifo */ fifo_A_A_IO_L2_in_23,
    /* fifo */ fifo_A_A_IO_L2_in_24,
    /* fifo */ fifo_A_PE_23_0)
  /* Module Call */

  /* Module Call */
  .invoke(A_IO_L2_in,
    /* module id */ 24,
    /* fifo */ fifo_A_A_IO_L2_in_24,
    /* fifo */ fifo_A_A_IO_L2_in_25,
    /* fifo */ fifo_A_PE_24_0)
  /* Module Call */

  /* Module Call */
  .invoke(A_IO_L2_in,
    /* module id */ 25,
    /* fifo */ fifo_A_A_IO_L2_in_25,
    /* fifo */ fifo_A_A_IO_L2_in_26,
    /* fifo */ fifo_A_PE_25_0)
  /* Module Call */

  /* Module Call */
  .invoke(A_IO_L2_in,
    /* module id */ 26,
    /* fifo */ fifo_A_A_IO_L2_in_26,
    /* fifo */ fifo_A_A_IO_L2_in_27,
    /* fifo */ fifo_A_PE_26_0)
  /* Module Call */

  /* Module Call */
  .invoke(A_IO_L2_in,
    /* module id */ 27,
    /* fifo */ fifo_A_A_IO_L2_in_27,
    /* fifo */ fifo_A_A_IO_L2_in_28,
    /* fifo */ fifo_A_PE_27_0)
  /* Module Call */

  /* Module Call */
  .invoke(A_IO_L2_in,
    /* module id */ 28,
    /* fifo */ fifo_A_A_IO_L2_in_28,
    /* fifo */ fifo_A_A_IO_L2_in_29,
    /* fifo */ fifo_A_PE_28_0)
  /* Module Call */

  /* Module Call */
  .invoke(A_IO_L2_in,
    /* module id */ 29,
    /* fifo */ fifo_A_A_IO_L2_in_29,
    /* fifo */ fifo_A_A_IO_L2_in_30,
    /* fifo */ fifo_A_PE_29_0)
  /* Module Call */

  /* Module Call */
  .invoke(A_IO_L2_in,
    /* module id */ 30,
    /* fifo */ fifo_A_A_IO_L2_in_30,
    /* fifo */ fifo_A_A_IO_L2_in_31,
    /* fifo */ fifo_A_PE_30_0)
  /* Module Call */

  /* Module Call */
  .invoke(A_IO_L2_in_boundary,
    /* module id */ 31,
    /* fifo */ fifo_A_A_IO_L2_in_31,
    /* fifo */ fifo_A_PE_31_0)
  /* Module Call */

  /* Module Call */
  .invoke(B_IO_L3_in_serialize,
    /* array */ B,
    /* fifo */ fifo_B_B_IO_L3_in_serialize)
  /* Module Call */

  /* Module Call */
  .invoke(B_IO_L3_in,
    /* fifo */ fifo_B_B_IO_L3_in_serialize,
    /* fifo */ fifo_B_B_IO_L2_in_0)
  /* Module Call */

  /* Module Call */
  .invoke(B_IO_L2_in,
    /* module id */ 0,
    /* fifo */ fifo_B_B_IO_L2_in_0,
    /* fifo */ fifo_B_B_IO_L2_in_1,
    /* fifo */ fifo_B_PE_0_0)
  /* Module Call */

  /* Module Call */
  .invoke(B_IO_L2_in,
    /* module id */ 1,
    /* fifo */ fifo_B_B_IO_L2_in_1,
    /* fifo */ fifo_B_B_IO_L2_in_2,
    /* fifo */ fifo_B_PE_0_1)
  /* Module Call */

  /* Module Call */
  .invoke(B_IO_L2_in,
    /* module id */ 2,
    /* fifo */ fifo_B_B_IO_L2_in_2,
    /* fifo */ fifo_B_B_IO_L2_in_3,
    /* fifo */ fifo_B_PE_0_2)
  /* Module Call */

  /* Module Call */
  .invoke(B_IO_L2_in_boundary,
    /* module id */ 3,
    /* fifo */ fifo_B_B_IO_L2_in_3,
    /* fifo */ fifo_B_PE_0_3)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 0,
    /* module id */ 0,
    /* fifo */ fifo_A_PE_0_0,
    /* fifo */ fifo_A_PE_0_1,
    /* fifo */ fifo_B_PE_0_0,
    /* fifo */ fifo_B_PE_1_0,
    /* fifo */ fifo_C_drain_PE_0_0)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 0,
    /* module id */ 1,
    /* fifo */ fifo_A_PE_0_1,
    /* fifo */ fifo_A_PE_0_2,
    /* fifo */ fifo_B_PE_0_1,
    /* fifo */ fifo_B_PE_1_1,
    /* fifo */ fifo_C_drain_PE_0_1)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 0,
    /* module id */ 2,
    /* fifo */ fifo_A_PE_0_2,
    /* fifo */ fifo_A_PE_0_3,
    /* fifo */ fifo_B_PE_0_2,
    /* fifo */ fifo_B_PE_1_2,
    /* fifo */ fifo_C_drain_PE_0_2)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 0,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_0_3,
    /* fifo */ fifo_A_PE_0_4,
    /* fifo */ fifo_B_PE_0_3,
    /* fifo */ fifo_B_PE_1_3,
    /* fifo */ fifo_C_drain_PE_0_3)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 1,
    /* module id */ 0,
    /* fifo */ fifo_A_PE_1_0,
    /* fifo */ fifo_A_PE_1_1,
    /* fifo */ fifo_B_PE_1_0,
    /* fifo */ fifo_B_PE_2_0,
    /* fifo */ fifo_C_drain_PE_1_0)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 1,
    /* module id */ 1,
    /* fifo */ fifo_A_PE_1_1,
    /* fifo */ fifo_A_PE_1_2,
    /* fifo */ fifo_B_PE_1_1,
    /* fifo */ fifo_B_PE_2_1,
    /* fifo */ fifo_C_drain_PE_1_1)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 1,
    /* module id */ 2,
    /* fifo */ fifo_A_PE_1_2,
    /* fifo */ fifo_A_PE_1_3,
    /* fifo */ fifo_B_PE_1_2,
    /* fifo */ fifo_B_PE_2_2,
    /* fifo */ fifo_C_drain_PE_1_2)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 1,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_1_3,
    /* fifo */ fifo_A_PE_1_4,
    /* fifo */ fifo_B_PE_1_3,
    /* fifo */ fifo_B_PE_2_3,
    /* fifo */ fifo_C_drain_PE_1_3)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 2,
    /* module id */ 0,
    /* fifo */ fifo_A_PE_2_0,
    /* fifo */ fifo_A_PE_2_1,
    /* fifo */ fifo_B_PE_2_0,
    /* fifo */ fifo_B_PE_3_0,
    /* fifo */ fifo_C_drain_PE_2_0)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 2,
    /* module id */ 1,
    /* fifo */ fifo_A_PE_2_1,
    /* fifo */ fifo_A_PE_2_2,
    /* fifo */ fifo_B_PE_2_1,
    /* fifo */ fifo_B_PE_3_1,
    /* fifo */ fifo_C_drain_PE_2_1)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 2,
    /* module id */ 2,
    /* fifo */ fifo_A_PE_2_2,
    /* fifo */ fifo_A_PE_2_3,
    /* fifo */ fifo_B_PE_2_2,
    /* fifo */ fifo_B_PE_3_2,
    /* fifo */ fifo_C_drain_PE_2_2)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 2,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_2_3,
    /* fifo */ fifo_A_PE_2_4,
    /* fifo */ fifo_B_PE_2_3,
    /* fifo */ fifo_B_PE_3_3,
    /* fifo */ fifo_C_drain_PE_2_3)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 3,
    /* module id */ 0,
    /* fifo */ fifo_A_PE_3_0,
    /* fifo */ fifo_A_PE_3_1,
    /* fifo */ fifo_B_PE_3_0,
    /* fifo */ fifo_B_PE_4_0,
    /* fifo */ fifo_C_drain_PE_3_0)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 3,
    /* module id */ 1,
    /* fifo */ fifo_A_PE_3_1,
    /* fifo */ fifo_A_PE_3_2,
    /* fifo */ fifo_B_PE_3_1,
    /* fifo */ fifo_B_PE_4_1,
    /* fifo */ fifo_C_drain_PE_3_1)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 3,
    /* module id */ 2,
    /* fifo */ fifo_A_PE_3_2,
    /* fifo */ fifo_A_PE_3_3,
    /* fifo */ fifo_B_PE_3_2,
    /* fifo */ fifo_B_PE_4_2,
    /* fifo */ fifo_C_drain_PE_3_2)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 3,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_3_3,
    /* fifo */ fifo_A_PE_3_4,
    /* fifo */ fifo_B_PE_3_3,
    /* fifo */ fifo_B_PE_4_3,
    /* fifo */ fifo_C_drain_PE_3_3)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 4,
    /* module id */ 0,
    /* fifo */ fifo_A_PE_4_0,
    /* fifo */ fifo_A_PE_4_1,
    /* fifo */ fifo_B_PE_4_0,
    /* fifo */ fifo_B_PE_5_0,
    /* fifo */ fifo_C_drain_PE_4_0)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 4,
    /* module id */ 1,
    /* fifo */ fifo_A_PE_4_1,
    /* fifo */ fifo_A_PE_4_2,
    /* fifo */ fifo_B_PE_4_1,
    /* fifo */ fifo_B_PE_5_1,
    /* fifo */ fifo_C_drain_PE_4_1)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 4,
    /* module id */ 2,
    /* fifo */ fifo_A_PE_4_2,
    /* fifo */ fifo_A_PE_4_3,
    /* fifo */ fifo_B_PE_4_2,
    /* fifo */ fifo_B_PE_5_2,
    /* fifo */ fifo_C_drain_PE_4_2)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 4,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_4_3,
    /* fifo */ fifo_A_PE_4_4,
    /* fifo */ fifo_B_PE_4_3,
    /* fifo */ fifo_B_PE_5_3,
    /* fifo */ fifo_C_drain_PE_4_3)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 5,
    /* module id */ 0,
    /* fifo */ fifo_A_PE_5_0,
    /* fifo */ fifo_A_PE_5_1,
    /* fifo */ fifo_B_PE_5_0,
    /* fifo */ fifo_B_PE_6_0,
    /* fifo */ fifo_C_drain_PE_5_0)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 5,
    /* module id */ 1,
    /* fifo */ fifo_A_PE_5_1,
    /* fifo */ fifo_A_PE_5_2,
    /* fifo */ fifo_B_PE_5_1,
    /* fifo */ fifo_B_PE_6_1,
    /* fifo */ fifo_C_drain_PE_5_1)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 5,
    /* module id */ 2,
    /* fifo */ fifo_A_PE_5_2,
    /* fifo */ fifo_A_PE_5_3,
    /* fifo */ fifo_B_PE_5_2,
    /* fifo */ fifo_B_PE_6_2,
    /* fifo */ fifo_C_drain_PE_5_2)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 5,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_5_3,
    /* fifo */ fifo_A_PE_5_4,
    /* fifo */ fifo_B_PE_5_3,
    /* fifo */ fifo_B_PE_6_3,
    /* fifo */ fifo_C_drain_PE_5_3)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 6,
    /* module id */ 0,
    /* fifo */ fifo_A_PE_6_0,
    /* fifo */ fifo_A_PE_6_1,
    /* fifo */ fifo_B_PE_6_0,
    /* fifo */ fifo_B_PE_7_0,
    /* fifo */ fifo_C_drain_PE_6_0)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 6,
    /* module id */ 1,
    /* fifo */ fifo_A_PE_6_1,
    /* fifo */ fifo_A_PE_6_2,
    /* fifo */ fifo_B_PE_6_1,
    /* fifo */ fifo_B_PE_7_1,
    /* fifo */ fifo_C_drain_PE_6_1)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 6,
    /* module id */ 2,
    /* fifo */ fifo_A_PE_6_2,
    /* fifo */ fifo_A_PE_6_3,
    /* fifo */ fifo_B_PE_6_2,
    /* fifo */ fifo_B_PE_7_2,
    /* fifo */ fifo_C_drain_PE_6_2)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 6,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_6_3,
    /* fifo */ fifo_A_PE_6_4,
    /* fifo */ fifo_B_PE_6_3,
    /* fifo */ fifo_B_PE_7_3,
    /* fifo */ fifo_C_drain_PE_6_3)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 7,
    /* module id */ 0,
    /* fifo */ fifo_A_PE_7_0,
    /* fifo */ fifo_A_PE_7_1,
    /* fifo */ fifo_B_PE_7_0,
    /* fifo */ fifo_B_PE_8_0,
    /* fifo */ fifo_C_drain_PE_7_0)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 7,
    /* module id */ 1,
    /* fifo */ fifo_A_PE_7_1,
    /* fifo */ fifo_A_PE_7_2,
    /* fifo */ fifo_B_PE_7_1,
    /* fifo */ fifo_B_PE_8_1,
    /* fifo */ fifo_C_drain_PE_7_1)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 7,
    /* module id */ 2,
    /* fifo */ fifo_A_PE_7_2,
    /* fifo */ fifo_A_PE_7_3,
    /* fifo */ fifo_B_PE_7_2,
    /* fifo */ fifo_B_PE_8_2,
    /* fifo */ fifo_C_drain_PE_7_2)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 7,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_7_3,
    /* fifo */ fifo_A_PE_7_4,
    /* fifo */ fifo_B_PE_7_3,
    /* fifo */ fifo_B_PE_8_3,
    /* fifo */ fifo_C_drain_PE_7_3)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 8,
    /* module id */ 0,
    /* fifo */ fifo_A_PE_8_0,
    /* fifo */ fifo_A_PE_8_1,
    /* fifo */ fifo_B_PE_8_0,
    /* fifo */ fifo_B_PE_9_0,
    /* fifo */ fifo_C_drain_PE_8_0)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 8,
    /* module id */ 1,
    /* fifo */ fifo_A_PE_8_1,
    /* fifo */ fifo_A_PE_8_2,
    /* fifo */ fifo_B_PE_8_1,
    /* fifo */ fifo_B_PE_9_1,
    /* fifo */ fifo_C_drain_PE_8_1)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 8,
    /* module id */ 2,
    /* fifo */ fifo_A_PE_8_2,
    /* fifo */ fifo_A_PE_8_3,
    /* fifo */ fifo_B_PE_8_2,
    /* fifo */ fifo_B_PE_9_2,
    /* fifo */ fifo_C_drain_PE_8_2)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 8,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_8_3,
    /* fifo */ fifo_A_PE_8_4,
    /* fifo */ fifo_B_PE_8_3,
    /* fifo */ fifo_B_PE_9_3,
    /* fifo */ fifo_C_drain_PE_8_3)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 9,
    /* module id */ 0,
    /* fifo */ fifo_A_PE_9_0,
    /* fifo */ fifo_A_PE_9_1,
    /* fifo */ fifo_B_PE_9_0,
    /* fifo */ fifo_B_PE_10_0,
    /* fifo */ fifo_C_drain_PE_9_0)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 9,
    /* module id */ 1,
    /* fifo */ fifo_A_PE_9_1,
    /* fifo */ fifo_A_PE_9_2,
    /* fifo */ fifo_B_PE_9_1,
    /* fifo */ fifo_B_PE_10_1,
    /* fifo */ fifo_C_drain_PE_9_1)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 9,
    /* module id */ 2,
    /* fifo */ fifo_A_PE_9_2,
    /* fifo */ fifo_A_PE_9_3,
    /* fifo */ fifo_B_PE_9_2,
    /* fifo */ fifo_B_PE_10_2,
    /* fifo */ fifo_C_drain_PE_9_2)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 9,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_9_3,
    /* fifo */ fifo_A_PE_9_4,
    /* fifo */ fifo_B_PE_9_3,
    /* fifo */ fifo_B_PE_10_3,
    /* fifo */ fifo_C_drain_PE_9_3)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 10,
    /* module id */ 0,
    /* fifo */ fifo_A_PE_10_0,
    /* fifo */ fifo_A_PE_10_1,
    /* fifo */ fifo_B_PE_10_0,
    /* fifo */ fifo_B_PE_11_0,
    /* fifo */ fifo_C_drain_PE_10_0)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 10,
    /* module id */ 1,
    /* fifo */ fifo_A_PE_10_1,
    /* fifo */ fifo_A_PE_10_2,
    /* fifo */ fifo_B_PE_10_1,
    /* fifo */ fifo_B_PE_11_1,
    /* fifo */ fifo_C_drain_PE_10_1)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 10,
    /* module id */ 2,
    /* fifo */ fifo_A_PE_10_2,
    /* fifo */ fifo_A_PE_10_3,
    /* fifo */ fifo_B_PE_10_2,
    /* fifo */ fifo_B_PE_11_2,
    /* fifo */ fifo_C_drain_PE_10_2)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 10,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_10_3,
    /* fifo */ fifo_A_PE_10_4,
    /* fifo */ fifo_B_PE_10_3,
    /* fifo */ fifo_B_PE_11_3,
    /* fifo */ fifo_C_drain_PE_10_3)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 11,
    /* module id */ 0,
    /* fifo */ fifo_A_PE_11_0,
    /* fifo */ fifo_A_PE_11_1,
    /* fifo */ fifo_B_PE_11_0,
    /* fifo */ fifo_B_PE_12_0,
    /* fifo */ fifo_C_drain_PE_11_0)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 11,
    /* module id */ 1,
    /* fifo */ fifo_A_PE_11_1,
    /* fifo */ fifo_A_PE_11_2,
    /* fifo */ fifo_B_PE_11_1,
    /* fifo */ fifo_B_PE_12_1,
    /* fifo */ fifo_C_drain_PE_11_1)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 11,
    /* module id */ 2,
    /* fifo */ fifo_A_PE_11_2,
    /* fifo */ fifo_A_PE_11_3,
    /* fifo */ fifo_B_PE_11_2,
    /* fifo */ fifo_B_PE_12_2,
    /* fifo */ fifo_C_drain_PE_11_2)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 11,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_11_3,
    /* fifo */ fifo_A_PE_11_4,
    /* fifo */ fifo_B_PE_11_3,
    /* fifo */ fifo_B_PE_12_3,
    /* fifo */ fifo_C_drain_PE_11_3)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 12,
    /* module id */ 0,
    /* fifo */ fifo_A_PE_12_0,
    /* fifo */ fifo_A_PE_12_1,
    /* fifo */ fifo_B_PE_12_0,
    /* fifo */ fifo_B_PE_13_0,
    /* fifo */ fifo_C_drain_PE_12_0)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 12,
    /* module id */ 1,
    /* fifo */ fifo_A_PE_12_1,
    /* fifo */ fifo_A_PE_12_2,
    /* fifo */ fifo_B_PE_12_1,
    /* fifo */ fifo_B_PE_13_1,
    /* fifo */ fifo_C_drain_PE_12_1)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 12,
    /* module id */ 2,
    /* fifo */ fifo_A_PE_12_2,
    /* fifo */ fifo_A_PE_12_3,
    /* fifo */ fifo_B_PE_12_2,
    /* fifo */ fifo_B_PE_13_2,
    /* fifo */ fifo_C_drain_PE_12_2)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 12,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_12_3,
    /* fifo */ fifo_A_PE_12_4,
    /* fifo */ fifo_B_PE_12_3,
    /* fifo */ fifo_B_PE_13_3,
    /* fifo */ fifo_C_drain_PE_12_3)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 13,
    /* module id */ 0,
    /* fifo */ fifo_A_PE_13_0,
    /* fifo */ fifo_A_PE_13_1,
    /* fifo */ fifo_B_PE_13_0,
    /* fifo */ fifo_B_PE_14_0,
    /* fifo */ fifo_C_drain_PE_13_0)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 13,
    /* module id */ 1,
    /* fifo */ fifo_A_PE_13_1,
    /* fifo */ fifo_A_PE_13_2,
    /* fifo */ fifo_B_PE_13_1,
    /* fifo */ fifo_B_PE_14_1,
    /* fifo */ fifo_C_drain_PE_13_1)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 13,
    /* module id */ 2,
    /* fifo */ fifo_A_PE_13_2,
    /* fifo */ fifo_A_PE_13_3,
    /* fifo */ fifo_B_PE_13_2,
    /* fifo */ fifo_B_PE_14_2,
    /* fifo */ fifo_C_drain_PE_13_2)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 13,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_13_3,
    /* fifo */ fifo_A_PE_13_4,
    /* fifo */ fifo_B_PE_13_3,
    /* fifo */ fifo_B_PE_14_3,
    /* fifo */ fifo_C_drain_PE_13_3)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 14,
    /* module id */ 0,
    /* fifo */ fifo_A_PE_14_0,
    /* fifo */ fifo_A_PE_14_1,
    /* fifo */ fifo_B_PE_14_0,
    /* fifo */ fifo_B_PE_15_0,
    /* fifo */ fifo_C_drain_PE_14_0)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 14,
    /* module id */ 1,
    /* fifo */ fifo_A_PE_14_1,
    /* fifo */ fifo_A_PE_14_2,
    /* fifo */ fifo_B_PE_14_1,
    /* fifo */ fifo_B_PE_15_1,
    /* fifo */ fifo_C_drain_PE_14_1)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 14,
    /* module id */ 2,
    /* fifo */ fifo_A_PE_14_2,
    /* fifo */ fifo_A_PE_14_3,
    /* fifo */ fifo_B_PE_14_2,
    /* fifo */ fifo_B_PE_15_2,
    /* fifo */ fifo_C_drain_PE_14_2)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 14,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_14_3,
    /* fifo */ fifo_A_PE_14_4,
    /* fifo */ fifo_B_PE_14_3,
    /* fifo */ fifo_B_PE_15_3,
    /* fifo */ fifo_C_drain_PE_14_3)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 15,
    /* module id */ 0,
    /* fifo */ fifo_A_PE_15_0,
    /* fifo */ fifo_A_PE_15_1,
    /* fifo */ fifo_B_PE_15_0,
    /* fifo */ fifo_B_PE_16_0,
    /* fifo */ fifo_C_drain_PE_15_0)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 15,
    /* module id */ 1,
    /* fifo */ fifo_A_PE_15_1,
    /* fifo */ fifo_A_PE_15_2,
    /* fifo */ fifo_B_PE_15_1,
    /* fifo */ fifo_B_PE_16_1,
    /* fifo */ fifo_C_drain_PE_15_1)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 15,
    /* module id */ 2,
    /* fifo */ fifo_A_PE_15_2,
    /* fifo */ fifo_A_PE_15_3,
    /* fifo */ fifo_B_PE_15_2,
    /* fifo */ fifo_B_PE_16_2,
    /* fifo */ fifo_C_drain_PE_15_2)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 15,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_15_3,
    /* fifo */ fifo_A_PE_15_4,
    /* fifo */ fifo_B_PE_15_3,
    /* fifo */ fifo_B_PE_16_3,
    /* fifo */ fifo_C_drain_PE_15_3)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 16,
    /* module id */ 0,
    /* fifo */ fifo_A_PE_16_0,
    /* fifo */ fifo_A_PE_16_1,
    /* fifo */ fifo_B_PE_16_0,
    /* fifo */ fifo_B_PE_17_0,
    /* fifo */ fifo_C_drain_PE_16_0)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 16,
    /* module id */ 1,
    /* fifo */ fifo_A_PE_16_1,
    /* fifo */ fifo_A_PE_16_2,
    /* fifo */ fifo_B_PE_16_1,
    /* fifo */ fifo_B_PE_17_1,
    /* fifo */ fifo_C_drain_PE_16_1)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 16,
    /* module id */ 2,
    /* fifo */ fifo_A_PE_16_2,
    /* fifo */ fifo_A_PE_16_3,
    /* fifo */ fifo_B_PE_16_2,
    /* fifo */ fifo_B_PE_17_2,
    /* fifo */ fifo_C_drain_PE_16_2)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 16,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_16_3,
    /* fifo */ fifo_A_PE_16_4,
    /* fifo */ fifo_B_PE_16_3,
    /* fifo */ fifo_B_PE_17_3,
    /* fifo */ fifo_C_drain_PE_16_3)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 17,
    /* module id */ 0,
    /* fifo */ fifo_A_PE_17_0,
    /* fifo */ fifo_A_PE_17_1,
    /* fifo */ fifo_B_PE_17_0,
    /* fifo */ fifo_B_PE_18_0,
    /* fifo */ fifo_C_drain_PE_17_0)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 17,
    /* module id */ 1,
    /* fifo */ fifo_A_PE_17_1,
    /* fifo */ fifo_A_PE_17_2,
    /* fifo */ fifo_B_PE_17_1,
    /* fifo */ fifo_B_PE_18_1,
    /* fifo */ fifo_C_drain_PE_17_1)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 17,
    /* module id */ 2,
    /* fifo */ fifo_A_PE_17_2,
    /* fifo */ fifo_A_PE_17_3,
    /* fifo */ fifo_B_PE_17_2,
    /* fifo */ fifo_B_PE_18_2,
    /* fifo */ fifo_C_drain_PE_17_2)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 17,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_17_3,
    /* fifo */ fifo_A_PE_17_4,
    /* fifo */ fifo_B_PE_17_3,
    /* fifo */ fifo_B_PE_18_3,
    /* fifo */ fifo_C_drain_PE_17_3)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 18,
    /* module id */ 0,
    /* fifo */ fifo_A_PE_18_0,
    /* fifo */ fifo_A_PE_18_1,
    /* fifo */ fifo_B_PE_18_0,
    /* fifo */ fifo_B_PE_19_0,
    /* fifo */ fifo_C_drain_PE_18_0)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 18,
    /* module id */ 1,
    /* fifo */ fifo_A_PE_18_1,
    /* fifo */ fifo_A_PE_18_2,
    /* fifo */ fifo_B_PE_18_1,
    /* fifo */ fifo_B_PE_19_1,
    /* fifo */ fifo_C_drain_PE_18_1)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 18,
    /* module id */ 2,
    /* fifo */ fifo_A_PE_18_2,
    /* fifo */ fifo_A_PE_18_3,
    /* fifo */ fifo_B_PE_18_2,
    /* fifo */ fifo_B_PE_19_2,
    /* fifo */ fifo_C_drain_PE_18_2)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 18,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_18_3,
    /* fifo */ fifo_A_PE_18_4,
    /* fifo */ fifo_B_PE_18_3,
    /* fifo */ fifo_B_PE_19_3,
    /* fifo */ fifo_C_drain_PE_18_3)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 19,
    /* module id */ 0,
    /* fifo */ fifo_A_PE_19_0,
    /* fifo */ fifo_A_PE_19_1,
    /* fifo */ fifo_B_PE_19_0,
    /* fifo */ fifo_B_PE_20_0,
    /* fifo */ fifo_C_drain_PE_19_0)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 19,
    /* module id */ 1,
    /* fifo */ fifo_A_PE_19_1,
    /* fifo */ fifo_A_PE_19_2,
    /* fifo */ fifo_B_PE_19_1,
    /* fifo */ fifo_B_PE_20_1,
    /* fifo */ fifo_C_drain_PE_19_1)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 19,
    /* module id */ 2,
    /* fifo */ fifo_A_PE_19_2,
    /* fifo */ fifo_A_PE_19_3,
    /* fifo */ fifo_B_PE_19_2,
    /* fifo */ fifo_B_PE_20_2,
    /* fifo */ fifo_C_drain_PE_19_2)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 19,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_19_3,
    /* fifo */ fifo_A_PE_19_4,
    /* fifo */ fifo_B_PE_19_3,
    /* fifo */ fifo_B_PE_20_3,
    /* fifo */ fifo_C_drain_PE_19_3)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 20,
    /* module id */ 0,
    /* fifo */ fifo_A_PE_20_0,
    /* fifo */ fifo_A_PE_20_1,
    /* fifo */ fifo_B_PE_20_0,
    /* fifo */ fifo_B_PE_21_0,
    /* fifo */ fifo_C_drain_PE_20_0)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 20,
    /* module id */ 1,
    /* fifo */ fifo_A_PE_20_1,
    /* fifo */ fifo_A_PE_20_2,
    /* fifo */ fifo_B_PE_20_1,
    /* fifo */ fifo_B_PE_21_1,
    /* fifo */ fifo_C_drain_PE_20_1)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 20,
    /* module id */ 2,
    /* fifo */ fifo_A_PE_20_2,
    /* fifo */ fifo_A_PE_20_3,
    /* fifo */ fifo_B_PE_20_2,
    /* fifo */ fifo_B_PE_21_2,
    /* fifo */ fifo_C_drain_PE_20_2)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 20,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_20_3,
    /* fifo */ fifo_A_PE_20_4,
    /* fifo */ fifo_B_PE_20_3,
    /* fifo */ fifo_B_PE_21_3,
    /* fifo */ fifo_C_drain_PE_20_3)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 21,
    /* module id */ 0,
    /* fifo */ fifo_A_PE_21_0,
    /* fifo */ fifo_A_PE_21_1,
    /* fifo */ fifo_B_PE_21_0,
    /* fifo */ fifo_B_PE_22_0,
    /* fifo */ fifo_C_drain_PE_21_0)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 21,
    /* module id */ 1,
    /* fifo */ fifo_A_PE_21_1,
    /* fifo */ fifo_A_PE_21_2,
    /* fifo */ fifo_B_PE_21_1,
    /* fifo */ fifo_B_PE_22_1,
    /* fifo */ fifo_C_drain_PE_21_1)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 21,
    /* module id */ 2,
    /* fifo */ fifo_A_PE_21_2,
    /* fifo */ fifo_A_PE_21_3,
    /* fifo */ fifo_B_PE_21_2,
    /* fifo */ fifo_B_PE_22_2,
    /* fifo */ fifo_C_drain_PE_21_2)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 21,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_21_3,
    /* fifo */ fifo_A_PE_21_4,
    /* fifo */ fifo_B_PE_21_3,
    /* fifo */ fifo_B_PE_22_3,
    /* fifo */ fifo_C_drain_PE_21_3)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 22,
    /* module id */ 0,
    /* fifo */ fifo_A_PE_22_0,
    /* fifo */ fifo_A_PE_22_1,
    /* fifo */ fifo_B_PE_22_0,
    /* fifo */ fifo_B_PE_23_0,
    /* fifo */ fifo_C_drain_PE_22_0)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 22,
    /* module id */ 1,
    /* fifo */ fifo_A_PE_22_1,
    /* fifo */ fifo_A_PE_22_2,
    /* fifo */ fifo_B_PE_22_1,
    /* fifo */ fifo_B_PE_23_1,
    /* fifo */ fifo_C_drain_PE_22_1)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 22,
    /* module id */ 2,
    /* fifo */ fifo_A_PE_22_2,
    /* fifo */ fifo_A_PE_22_3,
    /* fifo */ fifo_B_PE_22_2,
    /* fifo */ fifo_B_PE_23_2,
    /* fifo */ fifo_C_drain_PE_22_2)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 22,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_22_3,
    /* fifo */ fifo_A_PE_22_4,
    /* fifo */ fifo_B_PE_22_3,
    /* fifo */ fifo_B_PE_23_3,
    /* fifo */ fifo_C_drain_PE_22_3)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 23,
    /* module id */ 0,
    /* fifo */ fifo_A_PE_23_0,
    /* fifo */ fifo_A_PE_23_1,
    /* fifo */ fifo_B_PE_23_0,
    /* fifo */ fifo_B_PE_24_0,
    /* fifo */ fifo_C_drain_PE_23_0)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 23,
    /* module id */ 1,
    /* fifo */ fifo_A_PE_23_1,
    /* fifo */ fifo_A_PE_23_2,
    /* fifo */ fifo_B_PE_23_1,
    /* fifo */ fifo_B_PE_24_1,
    /* fifo */ fifo_C_drain_PE_23_1)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 23,
    /* module id */ 2,
    /* fifo */ fifo_A_PE_23_2,
    /* fifo */ fifo_A_PE_23_3,
    /* fifo */ fifo_B_PE_23_2,
    /* fifo */ fifo_B_PE_24_2,
    /* fifo */ fifo_C_drain_PE_23_2)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 23,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_23_3,
    /* fifo */ fifo_A_PE_23_4,
    /* fifo */ fifo_B_PE_23_3,
    /* fifo */ fifo_B_PE_24_3,
    /* fifo */ fifo_C_drain_PE_23_3)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 24,
    /* module id */ 0,
    /* fifo */ fifo_A_PE_24_0,
    /* fifo */ fifo_A_PE_24_1,
    /* fifo */ fifo_B_PE_24_0,
    /* fifo */ fifo_B_PE_25_0,
    /* fifo */ fifo_C_drain_PE_24_0)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 24,
    /* module id */ 1,
    /* fifo */ fifo_A_PE_24_1,
    /* fifo */ fifo_A_PE_24_2,
    /* fifo */ fifo_B_PE_24_1,
    /* fifo */ fifo_B_PE_25_1,
    /* fifo */ fifo_C_drain_PE_24_1)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 24,
    /* module id */ 2,
    /* fifo */ fifo_A_PE_24_2,
    /* fifo */ fifo_A_PE_24_3,
    /* fifo */ fifo_B_PE_24_2,
    /* fifo */ fifo_B_PE_25_2,
    /* fifo */ fifo_C_drain_PE_24_2)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 24,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_24_3,
    /* fifo */ fifo_A_PE_24_4,
    /* fifo */ fifo_B_PE_24_3,
    /* fifo */ fifo_B_PE_25_3,
    /* fifo */ fifo_C_drain_PE_24_3)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 25,
    /* module id */ 0,
    /* fifo */ fifo_A_PE_25_0,
    /* fifo */ fifo_A_PE_25_1,
    /* fifo */ fifo_B_PE_25_0,
    /* fifo */ fifo_B_PE_26_0,
    /* fifo */ fifo_C_drain_PE_25_0)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 25,
    /* module id */ 1,
    /* fifo */ fifo_A_PE_25_1,
    /* fifo */ fifo_A_PE_25_2,
    /* fifo */ fifo_B_PE_25_1,
    /* fifo */ fifo_B_PE_26_1,
    /* fifo */ fifo_C_drain_PE_25_1)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 25,
    /* module id */ 2,
    /* fifo */ fifo_A_PE_25_2,
    /* fifo */ fifo_A_PE_25_3,
    /* fifo */ fifo_B_PE_25_2,
    /* fifo */ fifo_B_PE_26_2,
    /* fifo */ fifo_C_drain_PE_25_2)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 25,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_25_3,
    /* fifo */ fifo_A_PE_25_4,
    /* fifo */ fifo_B_PE_25_3,
    /* fifo */ fifo_B_PE_26_3,
    /* fifo */ fifo_C_drain_PE_25_3)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 26,
    /* module id */ 0,
    /* fifo */ fifo_A_PE_26_0,
    /* fifo */ fifo_A_PE_26_1,
    /* fifo */ fifo_B_PE_26_0,
    /* fifo */ fifo_B_PE_27_0,
    /* fifo */ fifo_C_drain_PE_26_0)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 26,
    /* module id */ 1,
    /* fifo */ fifo_A_PE_26_1,
    /* fifo */ fifo_A_PE_26_2,
    /* fifo */ fifo_B_PE_26_1,
    /* fifo */ fifo_B_PE_27_1,
    /* fifo */ fifo_C_drain_PE_26_1)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 26,
    /* module id */ 2,
    /* fifo */ fifo_A_PE_26_2,
    /* fifo */ fifo_A_PE_26_3,
    /* fifo */ fifo_B_PE_26_2,
    /* fifo */ fifo_B_PE_27_2,
    /* fifo */ fifo_C_drain_PE_26_2)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 26,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_26_3,
    /* fifo */ fifo_A_PE_26_4,
    /* fifo */ fifo_B_PE_26_3,
    /* fifo */ fifo_B_PE_27_3,
    /* fifo */ fifo_C_drain_PE_26_3)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 27,
    /* module id */ 0,
    /* fifo */ fifo_A_PE_27_0,
    /* fifo */ fifo_A_PE_27_1,
    /* fifo */ fifo_B_PE_27_0,
    /* fifo */ fifo_B_PE_28_0,
    /* fifo */ fifo_C_drain_PE_27_0)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 27,
    /* module id */ 1,
    /* fifo */ fifo_A_PE_27_1,
    /* fifo */ fifo_A_PE_27_2,
    /* fifo */ fifo_B_PE_27_1,
    /* fifo */ fifo_B_PE_28_1,
    /* fifo */ fifo_C_drain_PE_27_1)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 27,
    /* module id */ 2,
    /* fifo */ fifo_A_PE_27_2,
    /* fifo */ fifo_A_PE_27_3,
    /* fifo */ fifo_B_PE_27_2,
    /* fifo */ fifo_B_PE_28_2,
    /* fifo */ fifo_C_drain_PE_27_2)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 27,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_27_3,
    /* fifo */ fifo_A_PE_27_4,
    /* fifo */ fifo_B_PE_27_3,
    /* fifo */ fifo_B_PE_28_3,
    /* fifo */ fifo_C_drain_PE_27_3)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 28,
    /* module id */ 0,
    /* fifo */ fifo_A_PE_28_0,
    /* fifo */ fifo_A_PE_28_1,
    /* fifo */ fifo_B_PE_28_0,
    /* fifo */ fifo_B_PE_29_0,
    /* fifo */ fifo_C_drain_PE_28_0)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 28,
    /* module id */ 1,
    /* fifo */ fifo_A_PE_28_1,
    /* fifo */ fifo_A_PE_28_2,
    /* fifo */ fifo_B_PE_28_1,
    /* fifo */ fifo_B_PE_29_1,
    /* fifo */ fifo_C_drain_PE_28_1)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 28,
    /* module id */ 2,
    /* fifo */ fifo_A_PE_28_2,
    /* fifo */ fifo_A_PE_28_3,
    /* fifo */ fifo_B_PE_28_2,
    /* fifo */ fifo_B_PE_29_2,
    /* fifo */ fifo_C_drain_PE_28_2)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 28,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_28_3,
    /* fifo */ fifo_A_PE_28_4,
    /* fifo */ fifo_B_PE_28_3,
    /* fifo */ fifo_B_PE_29_3,
    /* fifo */ fifo_C_drain_PE_28_3)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 29,
    /* module id */ 0,
    /* fifo */ fifo_A_PE_29_0,
    /* fifo */ fifo_A_PE_29_1,
    /* fifo */ fifo_B_PE_29_0,
    /* fifo */ fifo_B_PE_30_0,
    /* fifo */ fifo_C_drain_PE_29_0)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 29,
    /* module id */ 1,
    /* fifo */ fifo_A_PE_29_1,
    /* fifo */ fifo_A_PE_29_2,
    /* fifo */ fifo_B_PE_29_1,
    /* fifo */ fifo_B_PE_30_1,
    /* fifo */ fifo_C_drain_PE_29_1)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 29,
    /* module id */ 2,
    /* fifo */ fifo_A_PE_29_2,
    /* fifo */ fifo_A_PE_29_3,
    /* fifo */ fifo_B_PE_29_2,
    /* fifo */ fifo_B_PE_30_2,
    /* fifo */ fifo_C_drain_PE_29_2)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 29,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_29_3,
    /* fifo */ fifo_A_PE_29_4,
    /* fifo */ fifo_B_PE_29_3,
    /* fifo */ fifo_B_PE_30_3,
    /* fifo */ fifo_C_drain_PE_29_3)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 30,
    /* module id */ 0,
    /* fifo */ fifo_A_PE_30_0,
    /* fifo */ fifo_A_PE_30_1,
    /* fifo */ fifo_B_PE_30_0,
    /* fifo */ fifo_B_PE_31_0,
    /* fifo */ fifo_C_drain_PE_30_0)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 30,
    /* module id */ 1,
    /* fifo */ fifo_A_PE_30_1,
    /* fifo */ fifo_A_PE_30_2,
    /* fifo */ fifo_B_PE_30_1,
    /* fifo */ fifo_B_PE_31_1,
    /* fifo */ fifo_C_drain_PE_30_1)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 30,
    /* module id */ 2,
    /* fifo */ fifo_A_PE_30_2,
    /* fifo */ fifo_A_PE_30_3,
    /* fifo */ fifo_B_PE_30_2,
    /* fifo */ fifo_B_PE_31_2,
    /* fifo */ fifo_C_drain_PE_30_2)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 30,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_30_3,
    /* fifo */ fifo_A_PE_30_4,
    /* fifo */ fifo_B_PE_30_3,
    /* fifo */ fifo_B_PE_31_3,
    /* fifo */ fifo_C_drain_PE_30_3)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 31,
    /* module id */ 0,
    /* fifo */ fifo_A_PE_31_0,
    /* fifo */ fifo_A_PE_31_1,
    /* fifo */ fifo_B_PE_31_0,
    /* fifo */ fifo_B_PE_32_0,
    /* fifo */ fifo_C_drain_PE_31_0)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 31,
    /* module id */ 1,
    /* fifo */ fifo_A_PE_31_1,
    /* fifo */ fifo_A_PE_31_2,
    /* fifo */ fifo_B_PE_31_1,
    /* fifo */ fifo_B_PE_32_1,
    /* fifo */ fifo_C_drain_PE_31_1)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 31,
    /* module id */ 2,
    /* fifo */ fifo_A_PE_31_2,
    /* fifo */ fifo_A_PE_31_3,
    /* fifo */ fifo_B_PE_31_2,
    /* fifo */ fifo_B_PE_32_2,
    /* fifo */ fifo_C_drain_PE_31_2)
  /* Module Call */

  /* Module Call */
  .invoke(PE_wrapper,
    /* module id */ 31,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_31_3,
    /* fifo */ fifo_A_PE_31_4,
    /* fifo */ fifo_B_PE_31_3,
    /* fifo */ fifo_B_PE_32_3,
    /* fifo */ fifo_C_drain_PE_31_3)
  /* Module Call */

  /* Module Call */
  .invoke(A_PE_dummy_in,
    /* module id */ 0,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_0_4)
  /* Module Call */

  /* Module Call */
  .invoke(A_PE_dummy_in,
    /* module id */ 1,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_1_4)
  /* Module Call */

  /* Module Call */
  .invoke(A_PE_dummy_in,
    /* module id */ 2,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_2_4)
  /* Module Call */

  /* Module Call */
  .invoke(A_PE_dummy_in,
    /* module id */ 3,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_3_4)
  /* Module Call */

  /* Module Call */
  .invoke(A_PE_dummy_in,
    /* module id */ 4,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_4_4)
  /* Module Call */

  /* Module Call */
  .invoke(A_PE_dummy_in,
    /* module id */ 5,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_5_4)
  /* Module Call */

  /* Module Call */
  .invoke(A_PE_dummy_in,
    /* module id */ 6,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_6_4)
  /* Module Call */

  /* Module Call */
  .invoke(A_PE_dummy_in,
    /* module id */ 7,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_7_4)
  /* Module Call */

  /* Module Call */
  .invoke(A_PE_dummy_in,
    /* module id */ 8,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_8_4)
  /* Module Call */

  /* Module Call */
  .invoke(A_PE_dummy_in,
    /* module id */ 9,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_9_4)
  /* Module Call */

  /* Module Call */
  .invoke(A_PE_dummy_in,
    /* module id */ 10,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_10_4)
  /* Module Call */

  /* Module Call */
  .invoke(A_PE_dummy_in,
    /* module id */ 11,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_11_4)
  /* Module Call */

  /* Module Call */
  .invoke(A_PE_dummy_in,
    /* module id */ 12,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_12_4)
  /* Module Call */

  /* Module Call */
  .invoke(A_PE_dummy_in,
    /* module id */ 13,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_13_4)
  /* Module Call */

  /* Module Call */
  .invoke(A_PE_dummy_in,
    /* module id */ 14,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_14_4)
  /* Module Call */

  /* Module Call */
  .invoke(A_PE_dummy_in,
    /* module id */ 15,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_15_4)
  /* Module Call */

  /* Module Call */
  .invoke(A_PE_dummy_in,
    /* module id */ 16,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_16_4)
  /* Module Call */

  /* Module Call */
  .invoke(A_PE_dummy_in,
    /* module id */ 17,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_17_4)
  /* Module Call */

  /* Module Call */
  .invoke(A_PE_dummy_in,
    /* module id */ 18,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_18_4)
  /* Module Call */

  /* Module Call */
  .invoke(A_PE_dummy_in,
    /* module id */ 19,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_19_4)
  /* Module Call */

  /* Module Call */
  .invoke(A_PE_dummy_in,
    /* module id */ 20,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_20_4)
  /* Module Call */

  /* Module Call */
  .invoke(A_PE_dummy_in,
    /* module id */ 21,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_21_4)
  /* Module Call */

  /* Module Call */
  .invoke(A_PE_dummy_in,
    /* module id */ 22,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_22_4)
  /* Module Call */

  /* Module Call */
  .invoke(A_PE_dummy_in,
    /* module id */ 23,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_23_4)
  /* Module Call */

  /* Module Call */
  .invoke(A_PE_dummy_in,
    /* module id */ 24,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_24_4)
  /* Module Call */

  /* Module Call */
  .invoke(A_PE_dummy_in,
    /* module id */ 25,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_25_4)
  /* Module Call */

  /* Module Call */
  .invoke(A_PE_dummy_in,
    /* module id */ 26,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_26_4)
  /* Module Call */

  /* Module Call */
  .invoke(A_PE_dummy_in,
    /* module id */ 27,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_27_4)
  /* Module Call */

  /* Module Call */
  .invoke(A_PE_dummy_in,
    /* module id */ 28,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_28_4)
  /* Module Call */

  /* Module Call */
  .invoke(A_PE_dummy_in,
    /* module id */ 29,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_29_4)
  /* Module Call */

  /* Module Call */
  .invoke(A_PE_dummy_in,
    /* module id */ 30,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_30_4)
  /* Module Call */

  /* Module Call */
  .invoke(A_PE_dummy_in,
    /* module id */ 31,
    /* module id */ 3,
    /* fifo */ fifo_A_PE_31_4)
  /* Module Call */

  /* Module Call */
  .invoke(B_PE_dummy_in,
    /* module id */ 31,
    /* module id */ 0,
    /* fifo */ fifo_B_PE_32_0)
  /* Module Call */

  /* Module Call */
  .invoke(B_PE_dummy_in,
    /* module id */ 31,
    /* module id */ 1,
    /* fifo */ fifo_B_PE_32_1)
  /* Module Call */

  /* Module Call */
  .invoke(B_PE_dummy_in,
    /* module id */ 31,
    /* module id */ 2,
    /* fifo */ fifo_B_PE_32_2)
  /* Module Call */

  /* Module Call */
  .invoke(B_PE_dummy_in,
    /* module id */ 31,
    /* module id */ 3,
    /* fifo */ fifo_B_PE_32_3)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 0,
    /* module id */ 0,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_1,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_0,
    /* fifo */ fifo_C_drain_PE_0_0)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 0,
    /* module id */ 1,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_2,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_1,
    /* fifo */ fifo_C_drain_PE_1_0)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 0,
    /* module id */ 2,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_3,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_2,
    /* fifo */ fifo_C_drain_PE_2_0)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 0,
    /* module id */ 3,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_4,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_3,
    /* fifo */ fifo_C_drain_PE_3_0)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 0,
    /* module id */ 4,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_5,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_4,
    /* fifo */ fifo_C_drain_PE_4_0)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 0,
    /* module id */ 5,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_6,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_5,
    /* fifo */ fifo_C_drain_PE_5_0)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 0,
    /* module id */ 6,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_7,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_6,
    /* fifo */ fifo_C_drain_PE_6_0)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 0,
    /* module id */ 7,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_8,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_7,
    /* fifo */ fifo_C_drain_PE_7_0)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 0,
    /* module id */ 8,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_9,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_8,
    /* fifo */ fifo_C_drain_PE_8_0)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 0,
    /* module id */ 9,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_10,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_9,
    /* fifo */ fifo_C_drain_PE_9_0)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 0,
    /* module id */ 10,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_11,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_10,
    /* fifo */ fifo_C_drain_PE_10_0)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 0,
    /* module id */ 11,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_12,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_11,
    /* fifo */ fifo_C_drain_PE_11_0)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 0,
    /* module id */ 12,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_13,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_12,
    /* fifo */ fifo_C_drain_PE_12_0)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 0,
    /* module id */ 13,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_14,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_13,
    /* fifo */ fifo_C_drain_PE_13_0)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 0,
    /* module id */ 14,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_15,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_14,
    /* fifo */ fifo_C_drain_PE_14_0)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 0,
    /* module id */ 15,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_16,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_15,
    /* fifo */ fifo_C_drain_PE_15_0)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 0,
    /* module id */ 16,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_17,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_16,
    /* fifo */ fifo_C_drain_PE_16_0)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 0,
    /* module id */ 17,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_18,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_17,
    /* fifo */ fifo_C_drain_PE_17_0)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 0,
    /* module id */ 18,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_19,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_18,
    /* fifo */ fifo_C_drain_PE_18_0)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 0,
    /* module id */ 19,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_20,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_19,
    /* fifo */ fifo_C_drain_PE_19_0)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 0,
    /* module id */ 20,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_21,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_20,
    /* fifo */ fifo_C_drain_PE_20_0)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 0,
    /* module id */ 21,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_22,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_21,
    /* fifo */ fifo_C_drain_PE_21_0)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 0,
    /* module id */ 22,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_23,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_22,
    /* fifo */ fifo_C_drain_PE_22_0)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 0,
    /* module id */ 23,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_24,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_23,
    /* fifo */ fifo_C_drain_PE_23_0)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 0,
    /* module id */ 24,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_25,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_24,
    /* fifo */ fifo_C_drain_PE_24_0)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 0,
    /* module id */ 25,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_26,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_25,
    /* fifo */ fifo_C_drain_PE_25_0)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 0,
    /* module id */ 26,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_27,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_26,
    /* fifo */ fifo_C_drain_PE_26_0)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 0,
    /* module id */ 27,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_28,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_27,
    /* fifo */ fifo_C_drain_PE_27_0)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 0,
    /* module id */ 28,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_29,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_28,
    /* fifo */ fifo_C_drain_PE_28_0)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 0,
    /* module id */ 29,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_30,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_29,
    /* fifo */ fifo_C_drain_PE_29_0)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 0,
    /* module id */ 30,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_31,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_30,
    /* fifo */ fifo_C_drain_PE_30_0)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_boundary_wrapper,
    /* module id */ 0,
    /* module id */ 31,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_31,
    /* fifo */ fifo_C_drain_PE_31_0)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 1,
    /* module id */ 0,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_1,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_0,
    /* fifo */ fifo_C_drain_PE_0_1)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 1,
    /* module id */ 1,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_2,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_1,
    /* fifo */ fifo_C_drain_PE_1_1)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 1,
    /* module id */ 2,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_3,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_2,
    /* fifo */ fifo_C_drain_PE_2_1)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 1,
    /* module id */ 3,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_4,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_3,
    /* fifo */ fifo_C_drain_PE_3_1)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 1,
    /* module id */ 4,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_5,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_4,
    /* fifo */ fifo_C_drain_PE_4_1)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 1,
    /* module id */ 5,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_6,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_5,
    /* fifo */ fifo_C_drain_PE_5_1)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 1,
    /* module id */ 6,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_7,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_6,
    /* fifo */ fifo_C_drain_PE_6_1)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 1,
    /* module id */ 7,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_8,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_7,
    /* fifo */ fifo_C_drain_PE_7_1)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 1,
    /* module id */ 8,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_9,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_8,
    /* fifo */ fifo_C_drain_PE_8_1)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 1,
    /* module id */ 9,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_10,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_9,
    /* fifo */ fifo_C_drain_PE_9_1)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 1,
    /* module id */ 10,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_11,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_10,
    /* fifo */ fifo_C_drain_PE_10_1)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 1,
    /* module id */ 11,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_12,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_11,
    /* fifo */ fifo_C_drain_PE_11_1)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 1,
    /* module id */ 12,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_13,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_12,
    /* fifo */ fifo_C_drain_PE_12_1)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 1,
    /* module id */ 13,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_14,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_13,
    /* fifo */ fifo_C_drain_PE_13_1)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 1,
    /* module id */ 14,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_15,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_14,
    /* fifo */ fifo_C_drain_PE_14_1)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 1,
    /* module id */ 15,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_16,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_15,
    /* fifo */ fifo_C_drain_PE_15_1)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 1,
    /* module id */ 16,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_17,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_16,
    /* fifo */ fifo_C_drain_PE_16_1)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 1,
    /* module id */ 17,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_18,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_17,
    /* fifo */ fifo_C_drain_PE_17_1)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 1,
    /* module id */ 18,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_19,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_18,
    /* fifo */ fifo_C_drain_PE_18_1)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 1,
    /* module id */ 19,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_20,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_19,
    /* fifo */ fifo_C_drain_PE_19_1)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 1,
    /* module id */ 20,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_21,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_20,
    /* fifo */ fifo_C_drain_PE_20_1)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 1,
    /* module id */ 21,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_22,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_21,
    /* fifo */ fifo_C_drain_PE_21_1)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 1,
    /* module id */ 22,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_23,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_22,
    /* fifo */ fifo_C_drain_PE_22_1)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 1,
    /* module id */ 23,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_24,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_23,
    /* fifo */ fifo_C_drain_PE_23_1)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 1,
    /* module id */ 24,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_25,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_24,
    /* fifo */ fifo_C_drain_PE_24_1)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 1,
    /* module id */ 25,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_26,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_25,
    /* fifo */ fifo_C_drain_PE_25_1)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 1,
    /* module id */ 26,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_27,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_26,
    /* fifo */ fifo_C_drain_PE_26_1)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 1,
    /* module id */ 27,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_28,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_27,
    /* fifo */ fifo_C_drain_PE_27_1)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 1,
    /* module id */ 28,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_29,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_28,
    /* fifo */ fifo_C_drain_PE_28_1)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 1,
    /* module id */ 29,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_30,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_29,
    /* fifo */ fifo_C_drain_PE_29_1)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 1,
    /* module id */ 30,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_31,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_30,
    /* fifo */ fifo_C_drain_PE_30_1)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_boundary_wrapper,
    /* module id */ 1,
    /* module id */ 31,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_31,
    /* fifo */ fifo_C_drain_PE_31_1)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 2,
    /* module id */ 0,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_1,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_0,
    /* fifo */ fifo_C_drain_PE_0_2)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 2,
    /* module id */ 1,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_2,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_1,
    /* fifo */ fifo_C_drain_PE_1_2)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 2,
    /* module id */ 2,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_3,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_2,
    /* fifo */ fifo_C_drain_PE_2_2)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 2,
    /* module id */ 3,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_4,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_3,
    /* fifo */ fifo_C_drain_PE_3_2)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 2,
    /* module id */ 4,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_5,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_4,
    /* fifo */ fifo_C_drain_PE_4_2)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 2,
    /* module id */ 5,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_6,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_5,
    /* fifo */ fifo_C_drain_PE_5_2)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 2,
    /* module id */ 6,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_7,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_6,
    /* fifo */ fifo_C_drain_PE_6_2)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 2,
    /* module id */ 7,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_8,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_7,
    /* fifo */ fifo_C_drain_PE_7_2)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 2,
    /* module id */ 8,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_9,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_8,
    /* fifo */ fifo_C_drain_PE_8_2)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 2,
    /* module id */ 9,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_10,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_9,
    /* fifo */ fifo_C_drain_PE_9_2)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 2,
    /* module id */ 10,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_11,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_10,
    /* fifo */ fifo_C_drain_PE_10_2)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 2,
    /* module id */ 11,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_12,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_11,
    /* fifo */ fifo_C_drain_PE_11_2)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 2,
    /* module id */ 12,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_13,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_12,
    /* fifo */ fifo_C_drain_PE_12_2)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 2,
    /* module id */ 13,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_14,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_13,
    /* fifo */ fifo_C_drain_PE_13_2)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 2,
    /* module id */ 14,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_15,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_14,
    /* fifo */ fifo_C_drain_PE_14_2)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 2,
    /* module id */ 15,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_16,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_15,
    /* fifo */ fifo_C_drain_PE_15_2)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 2,
    /* module id */ 16,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_17,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_16,
    /* fifo */ fifo_C_drain_PE_16_2)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 2,
    /* module id */ 17,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_18,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_17,
    /* fifo */ fifo_C_drain_PE_17_2)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 2,
    /* module id */ 18,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_19,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_18,
    /* fifo */ fifo_C_drain_PE_18_2)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 2,
    /* module id */ 19,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_20,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_19,
    /* fifo */ fifo_C_drain_PE_19_2)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 2,
    /* module id */ 20,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_21,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_20,
    /* fifo */ fifo_C_drain_PE_20_2)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 2,
    /* module id */ 21,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_22,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_21,
    /* fifo */ fifo_C_drain_PE_21_2)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 2,
    /* module id */ 22,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_23,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_22,
    /* fifo */ fifo_C_drain_PE_22_2)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 2,
    /* module id */ 23,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_24,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_23,
    /* fifo */ fifo_C_drain_PE_23_2)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 2,
    /* module id */ 24,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_25,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_24,
    /* fifo */ fifo_C_drain_PE_24_2)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 2,
    /* module id */ 25,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_26,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_25,
    /* fifo */ fifo_C_drain_PE_25_2)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 2,
    /* module id */ 26,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_27,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_26,
    /* fifo */ fifo_C_drain_PE_26_2)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 2,
    /* module id */ 27,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_28,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_27,
    /* fifo */ fifo_C_drain_PE_27_2)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 2,
    /* module id */ 28,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_29,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_28,
    /* fifo */ fifo_C_drain_PE_28_2)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 2,
    /* module id */ 29,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_30,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_29,
    /* fifo */ fifo_C_drain_PE_29_2)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 2,
    /* module id */ 30,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_31,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_30,
    /* fifo */ fifo_C_drain_PE_30_2)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_boundary_wrapper,
    /* module id */ 2,
    /* module id */ 31,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_31,
    /* fifo */ fifo_C_drain_PE_31_2)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 3,
    /* module id */ 0,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_1,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_0,
    /* fifo */ fifo_C_drain_PE_0_3)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 3,
    /* module id */ 1,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_2,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_1,
    /* fifo */ fifo_C_drain_PE_1_3)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 3,
    /* module id */ 2,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_3,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_2,
    /* fifo */ fifo_C_drain_PE_2_3)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 3,
    /* module id */ 3,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_4,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_3,
    /* fifo */ fifo_C_drain_PE_3_3)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 3,
    /* module id */ 4,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_5,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_4,
    /* fifo */ fifo_C_drain_PE_4_3)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 3,
    /* module id */ 5,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_6,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_5,
    /* fifo */ fifo_C_drain_PE_5_3)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 3,
    /* module id */ 6,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_7,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_6,
    /* fifo */ fifo_C_drain_PE_6_3)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 3,
    /* module id */ 7,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_8,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_7,
    /* fifo */ fifo_C_drain_PE_7_3)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 3,
    /* module id */ 8,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_9,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_8,
    /* fifo */ fifo_C_drain_PE_8_3)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 3,
    /* module id */ 9,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_10,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_9,
    /* fifo */ fifo_C_drain_PE_9_3)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 3,
    /* module id */ 10,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_11,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_10,
    /* fifo */ fifo_C_drain_PE_10_3)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 3,
    /* module id */ 11,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_12,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_11,
    /* fifo */ fifo_C_drain_PE_11_3)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 3,
    /* module id */ 12,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_13,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_12,
    /* fifo */ fifo_C_drain_PE_12_3)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 3,
    /* module id */ 13,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_14,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_13,
    /* fifo */ fifo_C_drain_PE_13_3)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 3,
    /* module id */ 14,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_15,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_14,
    /* fifo */ fifo_C_drain_PE_14_3)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 3,
    /* module id */ 15,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_16,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_15,
    /* fifo */ fifo_C_drain_PE_15_3)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 3,
    /* module id */ 16,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_17,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_16,
    /* fifo */ fifo_C_drain_PE_16_3)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 3,
    /* module id */ 17,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_18,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_17,
    /* fifo */ fifo_C_drain_PE_17_3)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 3,
    /* module id */ 18,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_19,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_18,
    /* fifo */ fifo_C_drain_PE_18_3)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 3,
    /* module id */ 19,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_20,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_19,
    /* fifo */ fifo_C_drain_PE_19_3)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 3,
    /* module id */ 20,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_21,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_20,
    /* fifo */ fifo_C_drain_PE_20_3)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 3,
    /* module id */ 21,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_22,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_21,
    /* fifo */ fifo_C_drain_PE_21_3)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 3,
    /* module id */ 22,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_23,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_22,
    /* fifo */ fifo_C_drain_PE_22_3)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 3,
    /* module id */ 23,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_24,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_23,
    /* fifo */ fifo_C_drain_PE_23_3)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 3,
    /* module id */ 24,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_25,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_24,
    /* fifo */ fifo_C_drain_PE_24_3)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 3,
    /* module id */ 25,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_26,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_25,
    /* fifo */ fifo_C_drain_PE_25_3)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 3,
    /* module id */ 26,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_27,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_26,
    /* fifo */ fifo_C_drain_PE_26_3)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 3,
    /* module id */ 27,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_28,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_27,
    /* fifo */ fifo_C_drain_PE_27_3)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 3,
    /* module id */ 28,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_29,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_28,
    /* fifo */ fifo_C_drain_PE_28_3)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 3,
    /* module id */ 29,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_30,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_29,
    /* fifo */ fifo_C_drain_PE_29_3)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_wrapper,
    /* module id */ 3,
    /* module id */ 30,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_31,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_30,
    /* fifo */ fifo_C_drain_PE_30_3)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L1_out_boundary_wrapper,
    /* module id */ 3,
    /* module id */ 31,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_31,
    /* fifo */ fifo_C_drain_PE_31_3)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L2_out,
    /* module id */ 0,
    /* fifo */ fifo_C_drain_C_drain_IO_L2_out_1,
    /* fifo */ fifo_C_drain_C_drain_IO_L2_out_0,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_0_0)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L2_out,
    /* module id */ 1,
    /* fifo */ fifo_C_drain_C_drain_IO_L2_out_2,
    /* fifo */ fifo_C_drain_C_drain_IO_L2_out_1,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_1_0)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L2_out,
    /* module id */ 2,
    /* fifo */ fifo_C_drain_C_drain_IO_L2_out_3,
    /* fifo */ fifo_C_drain_C_drain_IO_L2_out_2,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_2_0)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L2_out_boundary,
    /* module id */ 3,
    /* fifo */ fifo_C_drain_C_drain_IO_L2_out_3,
    /* fifo */ fifo_C_drain_C_drain_IO_L1_out_3_0)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L3_out,
    /* fifo */ fifo_C_drain_C_drain_IO_L3_out_serialize,
    /* fifo */ fifo_C_drain_C_drain_IO_L2_out_0)
  /* Module Call */

  /* Module Call */
  .invoke(C_drain_IO_L3_out_serialize,
    /* array */ C,
    /* fifo */ fifo_C_drain_C_drain_IO_L3_out_serialize)
  /* Module Call */

  ;
}
