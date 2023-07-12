#include <tapa.h>
#include <ap_int.h>

template <typename T>
using bits = ap_uint<tapa::widthof<T>()>;

/* Data Type */
typedef float A_t1;
typedef float B_t1;
typedef float C_t1;
typedef tapa::vec_t<float, 16> A_t16;
typedef tapa::mmap<bits<A_t16> > A_t16_mmap;
typedef tapa::vec_t<float, 8> A_t8;
typedef tapa::mmap<bits<A_t8> > A_t8_mmap;
typedef tapa::vec_t<float, 16> B_t16;
typedef tapa::mmap<bits<B_t16> > B_t16_mmap;
typedef tapa::vec_t<float, 8> B_t8;
typedef tapa::mmap<bits<B_t8> > B_t8_mmap;
typedef tapa::vec_t<float, 16> C_t16;
typedef tapa::mmap<bits<C_t16> > C_t16_mmap;
typedef tapa::vec_t<float, 4> C_t4;
typedef tapa::mmap<bits<C_t4> > C_t4_mmap;
/* Data Type */

void kernel0(A_t16_mmap A, B_t16_mmap B, C_t16_mmap C);
void A_IO_L2_in_intra_trans(int idx, int c0, int c1, int c2, A_t16 local_A[2][8], tapa::ostream<A_t8> &fifo_A_local_out, bool intra_trans_en);
void A_IO_L2_in_inter_trans(int idx, int c0, int c1, int c2, A_t16 local_A[2][8], tapa::istream<A_t16> &fifo_A_in, tapa::ostream<A_t16> &fifo_A_out, bool inter_trans_en);
void A_IO_L2_in_inter_trans_boundary(int idx, int c0, int c1, int c2, A_t16 local_A[2][8], tapa::istream<A_t16> &fifo_A_in, bool inter_trans_en);
void B_IO_L2_in_intra_trans(int idx, int c0, int c1, int c2, B_t16 local_B[32][8], tapa::ostream<B_t8> &fifo_B_local_out, bool intra_trans_en);
void B_IO_L2_in_inter_trans(int idx, int c0, int c1, int c2, B_t16 local_B[32][8], tapa::istream<B_t16> &fifo_B_in, tapa::ostream<B_t16> &fifo_B_out, bool inter_trans_en);
void B_IO_L2_in_inter_trans_boundary(int idx, int c0, int c1, int c2, B_t16 local_B[32][8], tapa::istream<B_t16> &fifo_B_in, bool inter_trans_en);
void PE_wrapper(int idx, int idy, tapa::istream<A_t8> &fifo_A_in, tapa::ostream<A_t8> &fifo_A_out, tapa::istream<B_t8> &fifo_B_in, tapa::ostream<B_t8> &fifo_B_out, tapa::ostream<float> &fifo_C_drain_out);
void C_drain_IO_L1_out_intra_trans(int idx, int idy, int c0, int c1, C_t4 local_C[2][8], tapa::istream<float> &fifo_C_drain_local_in);
void C_drain_IO_L1_out_inter_trans(int idx, int idy, int c0, int c1, C_t4 local_C[2][8], tapa::istream<C_t4> &fifo_C_drain_in, tapa::ostream<C_t4> &fifo_C_drain_out);
void C_drain_IO_L1_out_inter_trans_boundary(int idx, int idy, int c0, int c1, C_t4 local_C[2][8], tapa::ostream<C_t4> &fifo_C_drain_out);
void C_drain_IO_L1_out_wrapper(int idx, int idy, tapa::istream<C_t4> &fifo_C_drain_in, tapa::ostream<C_t4> &fifo_C_drain_out, tapa::istream<float> &fifo_C_drain_local_in);
void C_drain_IO_L1_out_boundary_wrapper(int idx, int idy, tapa::ostream<C_t4> &fifo_C_drain_out, tapa::istream<float> &fifo_C_drain_local_in);
