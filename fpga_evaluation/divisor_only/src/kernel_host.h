template <typename T1, typename T2> inline T1 min(T1 x, T2 y) { return (x < T1(y)) ? x : T1(y); }
template <typename T1, typename T2> inline T1 max(T1 x, T2 y) { return (x > T1(y)) ? x : T1(y); }

#include <tapa.h>
using tapa::aligned_allocator;/* Helper Function */
void host_serialize_A(std::vector<float, aligned_allocator<float>> &A_to, std::vector<float, aligned_allocator<float>> &A_from){
  /* Variable Declaration */
  unsigned int cnt = 0;
  /* Variable Declaration */

  for (int c0 = 0; c0 <= 15; c0 += 1)
    for (int c1 = 0; c1 <= 7; c1 += 1)
      for (int c2 = 0; c2 <= 7; c2 += 1) {
        // array
        // io_L3
        for (int c3 = 0; c3 <= 31; c3 += 1) {
          // io_L2
          for (int c4 = 0; c4 <= 1; c4 += 1)
            for (int c5 = 0; c5 <= 127; c5 += 1)
              A_to[cnt++] = A_from[(64 * c0 + 2 * c3 + c4) * 1024 + (128 * c2 + c5)];
        }
      }
}
/* Helper Function */

/* Helper Function */
void host_serialize_B(std::vector<float, aligned_allocator<float>> &B_to, std::vector<float, aligned_allocator<float>> &B_from){
  /* Variable Declaration */
  unsigned int cnt = 0;
  /* Variable Declaration */

  for (int c0 = 0; c0 <= 15; c0 += 1)
    for (int c1 = 0; c1 <= 7; c1 += 1)
      for (int c2 = 0; c2 <= 7; c2 += 1) {
        // array
        // io_L3
        for (int c3 = 0; c3 <= 3; c3 += 1) {
          // io_L2
          for (int c4 = 0; c4 <= 31; c4 += 1)
            for (int c5 = 0; c5 <= 127; c5 += 1)
              B_to[cnt++] = B_from[(128 * c1 + 32 * c3 + c4) * 1024 + (128 * c2 + c5)];
        }
      }
}
/* Helper Function */

/* Helper Function */
void host_deserialize_C(std::vector<float, aligned_allocator<float>> &C_to, std::vector<float, aligned_allocator<float>> &C_from){
  /* Variable Declaration */
  unsigned int cnt = 0;
  /* Variable Declaration */

  for (int c0 = 0; c0 <= 15; c0 += 1)
    for (int c1 = 0; c1 <= 7; c1 += 1) {
      // array
      // io_L3
      for (int c3 = 0; c3 <= 3; c3 += 1) {
        // io_L2
        for (int c4 = 0; c4 <= 31; c4 += 1) {
          // io_L1
          // pe
          for (int c5 = 0; c5 <= 1; c5 += 1)
            for (int c6 = 0; c6 <= 31; c6 += 1)
              C_to[(64 * c0 + 2 * c4 + c5) * 1024 + (128 * c1 + 32 * c3 + c6)] = C_from[cnt++];
        }
      }
    }
}
/* Helper Function */

