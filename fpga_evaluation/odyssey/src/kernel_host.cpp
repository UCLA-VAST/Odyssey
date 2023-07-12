#include "kernel_host.h"
#include <assert.h>
#include <stdio.h>
#include "kernel_kernel.h"
#include <sys/time.h>
#include <gflags/gflags.h>
DEFINE_string(bitstream, "", "path to bitstream file, run csim if empty");
using namespace std;
#include "kernel.h"

// #define LAYOUT1
#define LAYOUT2
// #define LAYOUT3

int main(int argc, char **argv) {
  gflags::ParseCommandLineFlags(&argc, &argv, /*remove_flags=*/true);

//  data_t A[I][K], B[K][J], C[I][J], C_golden[I][J]; 
#ifdef LAYOUT2  
  static data_t A[I][K], B[J][K], C[I][J], C_golden[I][J]; // gemm0,3
#endif  
#ifdef LAYOUT3  
  static data_t A[K][I], B[K][J], C[I][J], C_golden[I][J]; // gemm4
#endif  

  for (int i = 0; i < I; i++) 
    for (int k = 0; k < K; k++) {
#ifdef LAYOUT2      
      A[i][k] = (data_t)rand() / RAND_MAX;
#endif
#ifdef LAYOUT3      
      A[k][i] = (data_t)rand() / RAND_MAX;
#endif      
    }

  for (int j = 0; j < J; j++)
    for (int k = 0; k < K; k++) {
#ifdef LAYOUT2      
      B[j][k] = (data_t)rand() / RAND_MAX;
#endif
#ifdef LAYOUT3      
      B[k][j] = (data_t)rand() / RAND_MAX;
#endif      
    }

  {
    // Allocate memory in host memory
    std::vector<float, tapa::aligned_allocator<float>> dev_A_unserialized((1032) * (1024));
    std::vector<float, tapa::aligned_allocator<float>> dev_A(8454144);
    std::vector<float, tapa::aligned_allocator<float>> dev_B_unserialized((1040) * (1024));
    std::vector<float, tapa::aligned_allocator<float>> dev_B(8519680);
    std::vector<float, tapa::aligned_allocator<float>> dev_C_unserialized((1032) * (1040));
    std::vector<float, tapa::aligned_allocator<float>> dev_C(1073280);

    // Initialize host buffers
    std::copy(reinterpret_cast<float *>(A), reinterpret_cast<float *>(A) + (1032) * (1024), dev_A_unserialized.begin());
    std::copy(reinterpret_cast<float *>(B), reinterpret_cast<float *>(B) + (1040) * (1024), dev_B_unserialized.begin());
    host_serialize_A(dev_A, dev_A_unserialized);
    host_serialize_B(dev_B, dev_B_unserialized);


    cout<<FLAGS_bitstream<<endl;
    int trials = 5;
    FILE *fp = fopen("result.csv", "w");
    fprintf(fp, "fre, throughput, cycles, latency (ms), dsp_count, dsp_eff\n");
    for(int i=0; i<trials; i++){
      // Launch the kernel
      int64_t kernel_time_ns = tapa::invoke(kernel0, FLAGS_bitstream, 
        tapa::read_only_mmap<float>(dev_A).reinterpret<bits<A_t16> >(),
        tapa::read_only_mmap<float>(dev_B).reinterpret<bits<B_t16> >(),
        tapa::write_only_mmap<float>(dev_C).reinterpret<bits<C_t16> >());
        // kernel_time_ns -= 100000;
        float GOPS =  2.147483648;
        int dsp_count = 8600;
        float frequency = 279; //MHz

        float peak_throughput = (2*dsp_count/5)*(frequency/1e3); //GOP/s
        float kernel_time_s =  (float) kernel_time_ns /  1e9;
        float achieved_throughput = GOPS / kernel_time_s; //GOP/s
        float cycles = kernel_time_ns*(frequency/1e3);
        float dsp_eff = (achieved_throughput/peak_throughput)*100;
        fprintf(fp, "%f, %f, %0.f, %f, %d, %f%\n", frequency, achieved_throughput, cycles, kernel_time_s*1e3, dsp_count, dsp_eff);
    }
    host_deserialize_C(dev_C_unserialized, dev_C);
    // Restore data from host buffers
    std::copy(dev_C_unserialized.begin(), dev_C_unserialized.end(), reinterpret_cast<float *>(C));
  }

  for (int i = 0; i < I; i++)
    for (int j = 0; j < J; j++) {
      C_golden[i][j] = 0;
      for (int k = 0; k < K; k++) {
#ifdef LAYOUT2        
        C_golden[i][j] = C_golden[i][j] + A[i][k] * B[j][k];
#endif
#ifdef LAYOUT3        
        C_golden[i][j] = C_golden[i][j] + A[k][i] * B[k][j];
#endif        
      }
    }

  int err = 0;
  for (int i = 0; i < I; i++)
    for (int j = 0; j < J; j++) {
      if (fabs((float)C_golden[i][j] - (float)C[i][j]) > 0.001)
        err++;
    }

  if (err)
    printf("Failed with %d errors!\n", err);
  else
    printf("Passed!\n");

  return 0;
}
