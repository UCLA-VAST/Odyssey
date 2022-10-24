#include "kernel.h"

int main(int argc, char **argv){
  // declarations
  static data_t cin[R + P - 1][C + Q - 1][I];
  static data_t w[O][P][Q][I];
  static data_t cout[R][C][O];
  static data_t cout_golden[R][C][O];

  // data initialization
  for (int i = 0 ; i < I; i++)
    for (int r = 0; r < R + P - 1; r++)
      for (int c = 0; c < C + Q - 1; c++) {
        cin[r][c][i] = (data_t)rand() / RAND_MAX; 
      }

  for (int o = 0; o < O; o++)
    for (int i = 0; i < I; i++) 
      for (int p = 0; p < P; p++)
        for (int q = 0; q < Q; q++) {
          w[o][p][q][i] = (data_t)rand() / RAND_MAX; 
        }
 
#pragma scop
  for (int o = 0; o < O; o++)
    for (int r = 0; r < R; r++)
      for (int c = 0; c < C; c++) {
        cout[r][c][o] = 0;
        for (int i = 0; i < I; i++)
          for (int p = 0; p < P; p++)
            for (int q = 0; q < Q; q++) {
              cout[r][c][o] = cout[r][c][o] + cin[r + p][c + q][i] * w[o][p][q][i];
            }
      }
#pragma endscop  
 
  for (int o = 0; o < O; o++)
    for (int r = 0; r < R; r++)
      for (int c = 0; c < C; c++) {
        cout_golden[r][c][o] = 0;
        for (int i = 0; i < I; i++)
          for (int p = 0; p < P; p++)
            for (int q = 0; q < Q; q++) {
              cout_golden[r][c][o] = cout_golden[r][c][o] + cin[r + p][c + q][i] * w[o][p][q][i];
            }
      }

  int err = 0;
  float thres = 0.001;
  for (int o = 0; o < O; o++)
    for (int r = 0; r < R; r++)
      for (int c = 0; c < C; c++) {
        if (fabs((float)cout_golden[r][c][o] - (float)cout[r][c][o]) > thres) {
          err++;
        }
      }

  if (err)
    printf("Failed with %d errors!\n", err);
  else
    printf("Passed!\n");
}
