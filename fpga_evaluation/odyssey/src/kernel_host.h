template <typename T1, typename T2> inline T1 min(T1 x, T2 y) { return (x < T1(y)) ? x : T1(y); }
template <typename T1, typename T2> inline T1 max(T1 x, T2 y) { return (x > T1(y)) ? x : T1(y); }

#include <tapa.h>
using tapa::aligned_allocator;/* Helper Function */
void host_serialize_A(std::vector<float, aligned_allocator<float>> &A_to, std::vector<float, aligned_allocator<float>> &A_from){
  /* Variable Declaration */
  unsigned int cnt = 0;
  /* Variable Declaration */

  for (int c0 = 0; c0 <= 7; c0 += 1)
    for (int c1 = 0; c1 <= 7; c1 += 1)
      for (int c2 = 0; c2 <= 15; c2 += 1) {
        // array
        // io_L3
        for (int c3 = 0; c3 <= 42; c3 += 1) {
          // io_L2
          for (int c4 = 0; c4 <= 2; c4 += 1)
            for (int c5 = 0; c5 <= 63; c5 += 1)
              A_to[cnt++] = A_from[(129 * c0 + 3 * c3 + c4) * 1024 + (64 * c2 + c5)];
        }
      }
}
/* Helper Function */

/* Helper Function */
void host_serialize_B(std::vector<float, aligned_allocator<float>> &B_to, std::vector<float, aligned_allocator<float>> &B_from){
  /* Variable Declaration */
  unsigned int cnt = 0;
  /* Variable Declaration */

  for (int c0 = 0; c0 <= 7; c0 += 1)
    for (int c1 = 0; c1 <= 7; c1 += 1)
      for (int c2 = 0; c2 <= 15; c2 += 1) {
        // array
        // io_L3
        for (int c3 = 0; c3 <= 4; c3 += 1) {
          // io_L2
          for (int c4 = 0; c4 <= 25; c4 += 1)
            for (int c5 = 0; c5 <= 63; c5 += 1)
              B_to[cnt++] = B_from[(130 * c1 + 26 * c3 + c4) * 1024 + (64 * c2 + c5)];
        }
      }
}
/* Helper Function */

/* Helper Function */
void host_deserialize_C(std::vector<float, aligned_allocator<float>> &C_to, std::vector<float, aligned_allocator<float>> &C_from){
  /* Variable Declaration */
  unsigned int cnt = 0;
  /* Variable Declaration */

  for (int c0 = 0; c0 <= 7; c0 += 1)
    for (int c1 = 0; c1 <= 7; c1 += 1) {
      // array
      // io_L3
      for (int c3 = 0; c3 <= 4; c3 += 1) {
        // io_L2
        for (int c4 = 0; c4 <= 42; c4 += 1) {
          // io_L1
          // pe
          for (int c5 = 0; c5 <= 2; c5 += 1)
            for (int c6 = 0; c6 <= 25; c6 += 1)
              C_to[(129 * c0 + 3 * c4 + c5) * 1040 + (130 * c1 + 26 * c3 + c6)] = C_from[cnt++];
        }
      }
    }
}
/* Helper Function */

