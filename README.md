# Amaranth HDL LSFR
This respository is a re-write of Alexforencich's [verilog-lfsr](https://github.com/alexforencich/verilog-lfsr), with Amaranth HDL.

# Develop Notes:
This is a re-implementation of Alexforencich’s verilog-lfsr project using Amaranth HDL. The purpose of this project is to test the power and efficiency of Amaranth/Python for degital design and simulation.

Using Amaranth HDL, we have created a more concise and elegant code structure than Verilog. Additionally, Python provides a convenient and flexible environment for debugging and verifying the design.

However, it should be noted that as Python "int" is 64-bit, caution should be taken when dealing with >64 bits wide IOs and signals. This may require additional logic to ensure correct operation.

To use this project, simply clone the repository and run the provided Python script. Contributions are welcome, and we encourage you to submit pull requests with any improvements or bug fixes.

Thank you for your interest in our project! We hope that you find it helpful and informative.

# Pre-requirement
Reference to [Amaranth_Prj_Template](https://github.com/weshu/Amaranth_Prj_Template)

# Test this project
Reference to [Amaranth_Prj_Template](https://github.com/weshu/Amaranth_Prj_Template)

## Usage

This repository contains a `Makefile` that automates various tasks related to developing the LFSR module. 
To use the `Makefile`, simply run one of the following commands in your terminal or command prompt, depending on what you want to achieve:

- `make target`: Replace `target` with one of the available targets described below.

### `init`
Initializes the project by creating some empty folders and files that will be used during development.

### `unittest`
Runs the unit tests for your Verilog designs using a testbench. It checks the functionality of individual modules and ensures they meet their specifications.

### `verilog`
Generates a Verilog file for the top module of your design. This can be useful when you want to simulate or synthesize your circuit using an external tool like iSim, Quartus, or Xilinx Vivado.

### `verilog-dbg`
Similar to the `verilog` target but generates a Verilog file with source information included. This can be helpful when debugging simulations or analyzing waveforms in a waveform viewer.

### `docs`
Generates documentation for your project using Sphinx. The generated HTML files will be placed in the `docs` folder and can be opened in a web browser to explore the design's structure, functionality, and API.

### `clean`

This target cleans the generated Verilog files and docs to free up some space and start with a clean slate.

### `clean-docs`

This target cleans only the generated docs to save some disk space without affecting your design or Verilog files.
