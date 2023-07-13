# Odyssey

## Publication

+ Suhail Basalama, Jie Wang, Jason Cong. [A Comprehensive Automated Exploration Framework for Systolic Array Designs]. In DAC, 2023.

## About
This repo contains the source code of Odyssey, an automated framework incorporating a hyprid genetic-mathematical programming search method, a padding-based search algorithm, and other randomized search methods. It can be used to explore the huge design space of systolic arrays. The framework is tested using the open-source [AutoSA framework](https://github.com/UCLA-VAST/AutoSA), but the methodology of our paper is applicable for other systolic array designs.


## Content
1. [Requirements and Dependencies](#requirements-and-dependencies)
<!-- 2. [Project File Tree](#project-file-tree) -->
3. [Running the Project](#running-the-project)


## Requirements and Dependencies
The hybrid genetic/mathematical-programming method requires the installation of the [ampl solver](https://ampl.com/products/solvers/all-solvers-for-ampl/).

All other dependencies are python packages found in the requirement.txt

<!-- ### Requirements -->

<!-- 

## Project File Tree
The project file structure is as below:

````
.
+-- dse_database          # database, graphs, codes to generate/analyze them
    +-- [machsuite/poly]  # the source code, ds config, and database for each of the benchmarks
    +-- programl          # the generated graphs for each of the kernels
    +-- merlin_prj        # the Merlin project to run each of the kernels
+-- models                # the final trained models along with the initial one-hot encoder
+-- src                   # the source codes for defining and training the model and running the DSE
```` -->


## Running the Project

To perform the tests, run the python 'run_tests.py' script under the 'tests' directory. For example:
````bash
source env.sh
cd tests
python run_tests.py --workload=mm
````
To test other problem sizes, please add your tests to a json file similar to 'tests/mm.json', and rerun the previous commands.

## Citation
If you find any of the ideas/codes useful for your research, please cite our paper:

	@inproceedings{basalamadac2023,
        title={A Comprehensive Automated Exploration Framework for Systolic Array Designs},
        author={Basalama, Suhail and Wang, Jia and Cong, Jason},
        booktitle={2023 60th ACM/IEEE Design Automation Conference (DAC)},
        year={2023}
    }