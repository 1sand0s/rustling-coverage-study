This repository contains a simple benchmark to compare the performance of
coverage analysis tools for Rust and C++.

## Table of contents

1. [Requirements](#Requirements)
2. [Usage](#Usage)

## Requirements

The packaged python script installs all the requirements except `gcov`, `poetry` and `python 3.12.x` which 
must be installed manually and must be available on `Path`. The requirements are listed for
reference.

1. Rust language framework and tools.

2. [GoogleTest](https://github.com/google/googletest). Test framework for C++

3. [llvm-cov](https://github.com/taiki-e/cargo-llvm-cov) and [Tarpaulin](https://github.com/xd009642/tarpaulin). Coverage tools for Rust.

4. [Gcov](https://gcc.gnu.org/onlinedocs/gcc/Gcov.html). Coverage tool for C++.

5. [Poetry](https://python-poetry.org). Dependency management for Python.

6. Python 3.12.x. Handles scripting.

## Usage

1. Use `poetry` to install script (`main.py`) dependencies within a virtual environment.
   ```
   poetry shell
   poetry install
   ```
   
2. Run script within virtual environment setup by poetry to collect coverage for C++ or Rust or both.
   In the example below, we collect coverage for workloads with 100, 1000 and 10000 tests with each 
   test-suite execution time being averaged over `2` runs for C++ and Rust. 
   ```
   python main.py --collect-coverage-overhead 100 1000 10000  --average 2
   ```
   
3. Output for example given in `Step 2`
   ```
   Execution times in seconds for tests with coverage
   ┌──────────────────┬─────────────────┬─────────────────┬─────────────────┐
   │ #Tests           │ 100             │ 1000            │ 10000           │
   ├──────────────────┼─────────────────┼─────────────────┼─────────────────┤
   │ Rust (llvm-cov)  │ 0.4845 ± 0.0021 │ 1.2965 ± 0.0516 │ 10.611 ± 0.0608 │
   │ Rust (tarpaulin) │ 0.689 ± 0.0198  │ 1.9045 ± 0.0078 │ 15.587 ± 0.0099 │
   │ Cpp (gcov)       │ 0.002 ± 0.0     │ 0.008 ± 0.0     │ 0.0695 ± 0.0007 │
   └──────────────────┴─────────────────┴─────────────────┴─────────────────┘
   
   
   Execution times in seconds for tests without coverage
   ┌──────────┬─────────────────┬─────────────────┬─────────────────┐
   │ #Tests   │ 100             │ 1000            │ 10000           │
   ├──────────┼─────────────────┼─────────────────┼─────────────────┤
   │ Rust     │ 0.2625 ± 0.0191 │ 1.0335 ± 0.0035 │ 9.3525 ± 0.1025 │
   │ Cpp      │ 0.001 ± 0.0     │ 0.006 ± 0.0     │ 0.055 ± 0.0     │
   └──────────┴─────────────────┴─────────────────┴─────────────────┘
   
   
   Coverage overhead as a ratio of execution time with and without coverage
   ┌──────────────────┬───────┬────────┬─────────┐
   │ #Tests           │   100 │   1000 │   10000 │
   ├──────────────────┼───────┼────────┼─────────┤
   │ Rust (llvm-cov)  │  1.85 │   1.25 │    1.13 │
   │ Rust (tarpaulin) │  2.62 │   1.84 │    1.67 │
   │ Cpp (gcov)       │  2    │   1.33 │    1.26 │
   └──────────────────┴───────┴────────┴─────────┘ 
   ```

4. For more script options
   ```
   python main.py --help
   ```
