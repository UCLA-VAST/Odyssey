# Odyssey

## Publication

+ Suhail Basalama, Jie Wang, Jason Cong. [A Comprehensive Automated Exploration Framework for Systolic Array Designs]. In DAC, 2023.

## About
This repo contains the source code of Odyssey, an automated framework incorporating a hypbrid genetic-mathematical programming search method, a padding-based search algorithm, and other randomized search methods. It can be used to explore the huge design space of systolic arrays. The framework is tested using the open-source [AutoSA framework](https://github.com/UCLA-VAST/AutoSA), but the methodology of our paper is applicable for other systolic array designs.


## Content
1. [Requirements and Dependencies](#requirements-and-dependencies)
<!-- 2. [Project File Tree](#project-file-tree) -->
3. [Running the Project](#running-the-project)


## Requirements and Dependencies

### Requirements

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

<!-- The `src/config.py` contains all the tunable parameters of the project. The current configuration runs the trainer in regression mode with some pre-defined hyper parameters. If you want to change the modes of running, please edit this file.

After setting the configurations, run the following command to execute the project:

````bash
cd src
python3 -W ignore main.py
````

You can run the `src/main.py` for training, inference, and design space exploration based on the parameters in `src/config.py`. For generating the graph, run the following command: 

````bash
cd dse_database
python3 -W ignore graph-gen.py ## modify inside of __main__ with your desired kernels
````


## Citation
If you find any of the ideas/codes useful for your research, please cite our paper:

	@inproceedings{sohrabizadeh2021gnn,
        title={Automated Accelerator Optimization Aided by Graph Neural Networks},
        author={Sohrabizadeh, Atefeh and Bai, Yunsheng and Sun, Yizhou and Cong, Jason},
        booktitle={2022 59th ACM/IEEE Design Automation Conference (DAC)},
        year={2022}
    } -->