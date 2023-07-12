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
              // hls_pipeline
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
        // simd
        // hls_pipeline
        {
          A_t16 in_data;
          A_t8 out_data;
          A_t8 data_split[2];
          #pragma HLS ARRAY_PARTITION variable=data_split complete
          in_data = local_A[c7][8 * c5 / 16];
          for (int n = 0; n < 2; n++) {
          #pragma HLS UNROLL
            data_split[n] = tapa::truncated<8>(in_data, 8 * n);
          }
          int split_idx = (8 * c5 / 8) % 2;
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
    if (c3 == p0) {
      for (int c4 = 0; c4 <= 1; c4 += 1) {
        // access_coalesce
        for (int c5 = 0; c5 <= 7; c5 += 1) {
          // hls_pipeline
          {
            A_t16 in_data;
            A_t16 out_data;
            in_data = fifo_A_in.read();
            out_data = in_data;
            local_A[c4][16 * c5 / 16] = out_data;
          }
        }
      }
    } else {
      for (int c4 = 0; c4 <= 1; c4 += 1) {
        // access_coalesce
        for (int c5 = 0; c5 <= 7; c5 += 1) {
          // hls_pipeline
          {
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

  for (int c3 = p0; c3 <= 31; c3 += 1)
    if (c3 == p0) {
      // io_L2
      for (int c4 = 0; c4 <= 1; c4 += 1) {
        // access_coalesce
        for (int c5 = 0; c5 <= 7; c5 += 1) {
          // hls_pipeline
          {
            A_t16 in_data;
            A_t16 out_data;
            in_data = fifo_A_in.read();
            out_data = in_data;
            local_A[c4][16 * c5 / 16] = out_data;
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
              // hls_pipeline
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
        // simd
        // hls_pipeline
        {
          B_t16 in_data;
          B_t8 out_data;
          B_t8 data_split[2];
          #pragma HLS ARRAY_PARTITION variable=data_split complete
          in_data = local_B[c6][8 * c5 / 16];
          for (int n = 0; n < 2; n++) {
          #pragma HLS UNROLL
            data_split[n] = tapa::truncated<8>(in_data, 8 * n);
          }
          int split_idx = (8 * c5 / 8) % 2;
          out_data = data_split[split_idx];
          fifo_B_local_out.write(out_data);
        }
      }
    }
  }
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
    if (c3 == p0) {
      for (int c4 = 0; c4 <= 31; c4 += 1) {
        // access_coalesce
        for (int c5 = 0; c5 <= 7; c5 += 1) {
          // hls_pipeline
          {
            B_t16 in_data;
            B_t16 out_data;
            in_data = fifo_B_in.read();
            out_data = in_data;
            local_B[c4][16 * c5 / 16] = out_data;
          }
        }
      }
    } else {
      for (int c4 = 0; c4 <= 31; c4 += 1) {
        // access_coalesce
        for (int c5 = 0; c5 <= 7; c5 += 1) {
          // hls_pipeline
          {
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

  for (int c3 = p0; c3 <= 3; c3 += 1)
    if (c3 == p0) {
      // io_L2
      for (int c4 = 0; c4 <= 31; c4 += 1) {
        // access_coalesce
        for (int c5 = 0; c5 <= 7; c5 += 1) {
          // hls_pipeline
          {
            B_t16 in_data;
            B_t16 out_data;
            in_data = fifo_B_in.read();
            out_data = in_data;
            local_B[c4][16 * c5 / 16] = out_data;
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
              // hls_pipeline
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
                    // hls_unroll
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
              // hls_pipeline
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
              // hls_pipeline
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
  /* Variable Declaration */


  // io_L1
  // pe
  // latency
  for (int c6 = 0; c6 <= 31; c6 += 1) {
    // latency
    for (int c7 = 0; c7 <= 1; c7 += 1) {
      // simd
      // hls_pipeline
      {
        C_t1 in_data;
        C_t4 out_data;
        float data_split[4];
        #pragma HLS ARRAY_PARTITION variable=data_split complete
        in_data = fifo_C_drain_local_in.read();
        int split_idx = (c6 / 1) % 4;
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
    if (c4 == p1) {
      for (int c5 = 0; c5 <= 1; c5 += 1) {
        // access_coalesce
        for (int c6 = 0; c6 <= 7; c6 += 1) {
          // hls_pipeline
          {
            C_t4 in_data;
            C_t4 out_data;
            in_data = local_C[c5][4 * c6 / 4];
            out_data = in_data;
            fifo_C_drain_out.write(out_data);
          }
        }
      }
    } else {
      for (int c5 = 0; c5 <= 1; c5 += 1) {
        // access_coalesce
        for (int c6 = 0; c6 <= 7; c6 += 1) {
          // hls_pipeline
          {
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

  for (int c4 = p1; c4 <= 31; c4 += 1)
    if (c4 == p1) {
      // io_L1
      for (int c5 = 0; c5 <= 1; c5 += 1) {
        // access_coalesce
        for (int c6 = 0; c6 <= 7; c6 += 1) {
          // hls_pipeline
          {
            C_t4 in_data;
            C_t4 out_data;
            in_data = local_C[c5][4 * c6 / 4];
            out_data = in_data;
            fifo_C_drain_out.write(out_data);
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

  for (int c0 = 0; c0 <= 15; c0 += 1)
    for (int c1 = 0; c1 <= 7; c1 += 1) {
      // array
      // io_L3
      for (int c3 = p0; c3 <= 3; c3 += 1) {
        // io_L2
        if (c3 == p0) {
          for (int c4 = 0; c4 <= 31; c4 += 1) {
            // io_L1
            for (int c5 = 0; c5 <= 1; c5 += 1) {
              // access_coalesce
              for (int c6 = 0; c6 <= 7; c6 += 1) {
                // hls_pipeline
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
        } else {
          for (int c4 = 0; c4 <= 31; c4 += 1) {
            // io_L1
            for (int c5 = 0; c5 <= 1; c5 += 1) {
              // access_coalesce
              for (int c6 = 0; c6 <= 7; c6 += 1) {
                // hls_pipeline
                {
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
/* Module Definition */

/* Module Definition */
void C_drain_IO_L2_out_boundary(int idx, tapa::ostream<C_t4> &fifo_C_drain_out, tapa::istream<C_t4> &fifo_C_drain_local_in) {
#pragma HLS INLINE OFF
  /* Variable Declaration */
  int p0 = idx; // module id
  /* Variable Declaration */

  for (int c0 = 0; c0 <= 15; c0 += 1)
    for (int c1 = 0; c1 <= 7; c1 += 1) {
      // array
      // io_L3
      for (int c3 = p0; c3 <= 3; c3 += 1)
        if (c3 == p0) {
          // io_L2
          for (int c4 = 0; c4 <= 31; c4 += 1) {
            // io_L1
            for (int c5 = 0; c5 <= 1; c5 += 1) {
              // access_coalesce
              for (int c6 = 0; c6 <= 7; c6 += 1) {
                // hls_pipeline
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
              // hls_pipeline
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

