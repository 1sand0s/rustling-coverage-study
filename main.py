import seutil as su
import logging
import os
import argparse
import re
import math
import json

from datetime import datetime
from pathlib import Path
from seutil.bash import BashError
from statistics import mean, stdev
from tabulate import tabulate

WORKLOAD=[100, 1000, 10000]

## Directories.
_DIR = Path(os.path.dirname(os.path.realpath(__file__)))
LOG_DIR = _DIR / ".logs"
RUST_DIR = _DIR / "rust/todo_app"
RUST_SRC_DIR = RUST_DIR / "src"
CPP_SRC_DIR = _DIR / "cpp"
GTEST_DIR = _DIR / ".gtest"
GTEST_INCLUDE_DIR = GTEST_DIR / "googletest/include"
GTEST_LIB_DIR = GTEST_DIR / "build/lib"

## Set up logging
su.io.mkdir(LOG_DIR)
log_file = Path(LOG_DIR / f"{datetime.now().isoformat()}.log")
su.log.setup(
    log_file=log_file,
    level_stderr=logging.WARNING,
    level_file=logging.DEBUG,
    maxBytes=1_000_000_000, # 1G per log file
    backupCount=10) # 10 log files
logger = su.log.get_logger(__name__, level=logging.DEBUG)
logger.warning(f"See log file: {log_file}")


#Rust coverage tools
RUST_COVERAGE_TOOLS = ['llvm-cov', 'tarpaulin']
CPP_COVERAGE_TOOLS = ['gcov']

def install_rust()->None:
    """
    Installs Rust lang.
    """
    logger.info("Checking is Rust is already installed...")
    try:
        su.bash.run(
            "cargo --help",
            check_returncode=0
        )
        logger.info(f"Rust already installed. Skipping installation.")
    except BashError as e:
        logger.info("Installing Rust...")
        su.bash.run("curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh")
    #yrt

    logger.info("Verifying Rust installation...")
    try:
        su.bash.run(
            "cargo --help",
            check_returncode=0
        )
        logger.info(f"Rust installation successful.")
    except BashError as e:
        logger.warning(f"Rust installation failed due to:"
                       f"{e}"
        )
    #yrt
#fed

def install_rust_coverage_tools()->None:
    """
    Installs coverage tools for Rust.
    """
    logger.info("Checking if Rust is installed...")
    try:
        su.bash.run(
            "cargo --help",
            check_returncode=0
        )
    except BashError as e:
        logger.error("Install Rust first!")
        return
    #yrt
    
    logger.info(f"Installing {RUST_COVERAGE_TOOLS}...")
    for tool in RUST_COVERAGE_TOOLS:
        try:
            su.bash.run(
                f"cargo install cargo-{tool}",
                check_returncode=0
            )
        except BashError as e:
            logger.error(f"Could not install coverage tool {tool}.")
            continue
        #yrt
    #rof
#fed

def install_cpp_coverage_tools()->None:
    """
    Installs coverage tools for C++.
    """
    logger.info(f"Install gcov manually from terminal with apt-get")
#fed

def _process_time_stdout(
    time_stdout: str,
)->float:
    pattern = r"real\s+(\d+)m([\d.]+)s"
    match = re.search(pattern, time_stdout)

    if match:
        minutes = int(match.group(1))
        seconds = float(match.group(2))
        total_seconds = minutes * 60 + seconds
        return total_seconds
    else:
        return -1
    #fi
#fed

def gen_rust_tests(
    num_tests: int
)->None:
    """
    Generates tests for Rust in module tests.rs with num_tests number of tests.
    """
    logger.info(f"Generating tests for Rust for workload {num_tests}...")
    with open(RUST_SRC_DIR / "tests.rs", 'w') as f:
        f.write("#[cfg(test)]\n")
        f.write("mod tests {\n\n")
        f.write("\tuse crate::tasks::{Task};\n")

        for i in range(1, num_tests + 1):
            f.write("\t#[test]\n")
            f.write(f"\tfn test{i}_tasks() {{\n")
            if i % 3 == 0:
                f.write('\t\tlet task = Task::new("Test Task".to_string());\n')
                f.write('\t\tassert_eq!(task.description, "Test Task");\n')
            elif i % 2 == 0:
                f.write('\t\tlet task = Task::new("Test Task".to_string());\n')
                f.write(f"\t\tassert!(!task.completed);\n")
            else:
                f.write('\t\tlet mut task = Task::new("Test Task".to_string());\n')
                f.write(f"\t\ttask.completed = true;\n")
                f.write(f"\t\tassert!(task.completed);\n")
            #fi
            f.write("\t}\n")
        #rof
        f.write("}\n")
    #htiw
    logger.info(f"Test generation for Rust finished.")
#fed

def gen_cpp_tests(
    num_tests: int
)->None:
    """
    Generates tests for Cpp with num_tests number of tests.
    """
    logger.info(f"Generating tests for Cpp for workload {num_tests}...")
    with open(CPP_SRC_DIR / "tests.cpp", 'w') as f:
        f.write("#include <gtest/gtest.h>\n")
        f.write("#include \"Task.h\"\n\n")

        for i in range(1, num_tests + 1):
            f.write(f"TEST(TaskTest, Test_{i}_Tasks) {{\n")
            f.write('\tTask task("Test Task");\n')
            if i % 3 == 0:
                f.write('\tEXPECT_EQ(task.getDescription(), "Test Task");\n')
            elif i % 2 == 0:
                f.write(f"\tEXPECT_FALSE(task.isCompleted());\n")
            else:
                f.write(f"\ttask.setCompleted(true);\n")
                f.write(f"\tEXPECT_FALSE(task.isCompleted());\n")
            #fi
            f.write("}\n")
        #rof

        f.write("int main(int argc, char **argv) {\n")
        f.write("\t::testing::InitGoogleTest(&argc, argv);\n")
        f.write("\treturn RUN_ALL_TESTS();\n}")

    #htiw
    logger.info(f"Test generation for Cpp finished.")
#fed

def _install_gtest()->None:
    logger.info("Checking if GoogleTest is installed...")
    if Path(f'{GTEST_LIB_DIR}/libgtest.a').is_file() and Path(f'{GTEST_LIB_DIR}/libgtest_main.a').is_file() and Path(GTEST_INCLUDE_DIR).is_dir():
        logger.info("GoogleTest is already installed!")
        return
    #fi
    try:
        su.bash.run(
            "git clone https://github.com/google/googletest .gtest",
            check_returncode=0
        )
        su.io.mkdir(f'{GTEST_DIR}/build')
        os.chdir(f'{GTEST_DIR}/build')
        su.bash.run(
            "cmake ..",
            check_returncode=0
        )
        su.bash.run(
            "make",
            check_returncode=0
        )
        os.chdir(_DIR)
    except BashError as e:
        logger.error("GoogleTest installation failed due to"
                     f"{e}")
        return
    #yrt
    logger.info("GoogleTest installation successful!")
#fed

def _run_test_without_coverage_cpp(
    workload: int
)->None:
    logger.info(f"Running test without coverage for cpp workload {workload}...")
    if not Path(f'{CPP_SRC_DIR}/tests.cpp').is_file():
        logger.error(f"Generate test for workload {workload} for Cpp first!")
        return
    #fi
    try:
        os.chdir(CPP_SRC_DIR)
        su.bash.run(
            "rm -f *.gcno *.gcda tests",
            check_returncode=0
        )
        su.bash.run(
            f"g++ -isystem {GTEST_INCLUDE_DIR} -pthread tests.cpp Task.cpp TaskManager.cpp {GTEST_LIB_DIR}/libgtest.a  {GTEST_LIB_DIR}/libgtest_main.a -o tests",
            check_returncode=0
        )
        output = su.bash.run(
            "time ./tests",
        ).stderr
        logger.info(f'Cpp_Without_Coverage_{workload}_exec_time: {_process_time_stdout(output)}s')
        os.chdir(_DIR)
    except BashError as e:
        os.chdir(_DIR)
        logger.error(f"Running tests for workload {workload} for Cpp failed!"
                     f"{e}")
        return
    #yrt
    logger.info(f"Finished running tests without coverage for workload {workload} for Cpp.")
#fed

def _run_test_with_coverage_cpp(
    workload: int
)->None:
    logger.info(f"Running test with coverage for cpp workload {workload}...")
    if not Path(f'{CPP_SRC_DIR}/tests.cpp').is_file():
        logger.error(f"Generate test for workload {workload} for Cpp first!")
        return
    #fi
    try:
        os.chdir(CPP_SRC_DIR)
        su.bash.run(
            "rm -f *.gcno *.gcda tests",
            check_returncode=0
        )
        su.bash.run(
            f"g++ -isystem {GTEST_INCLUDE_DIR} -pthread --coverage tests.cpp Task.cpp TaskManager.cpp {GTEST_LIB_DIR}/libgtest.a  {GTEST_LIB_DIR}/libgtest_main.a -o tests",
            check_returncode=0
        )
        output = su.bash.run(
            "time (./tests && gcov -n *.gcno)",
        ).stderr
        logger.info(f'Cpp_With_Coverage_{workload}_exec_time: {_process_time_stdout(output)}s')
        os.chdir(_DIR)
    except BashError as e:
        os.chdir(_DIR)
        logger.error(f"Running tests for workload {workload} for Cpp failed!"
                     f"{e}")
        return
    #yrt
    logger.info(f"Finished running tests with coverage for workload {workload} for Cpp.")
#fed

def _run_test_without_coverage_rust(
    workload: int
)->None:
    logger.info(f"Running test without coverage for rust workload {workload}...")
    if not Path(f'{RUST_SRC_DIR}/tests.rs').is_file():
        logger.error(f"Generate test for workload {workload} for Rust first!")
        return
    #fi
    try:
        os.chdir(RUST_DIR)
        su.bash.run(
            "cargo clean",
            check_returncode=0
        )
        output = su.bash.run(
            "time cargo test 2>/dev/null",
        ).stderr
        logger.info(f'Rust_Without_Coverage_{workload}_exec_time: {_process_time_stdout(output)}s')
        os.chdir(_DIR)
    except BashError as e:
        os.chdir(_DIR)
        logger.error(f"Running tests for workload {workload} for Rust failed!"
                     f"{e}")
        return
    #yrt
    logger.info(f"Finished running tests without coverage for workload {workload} for Rust.")
#fed

def _run_test_with_coverage_rust(
    workload: int,
    rust_coverage_tool: str,    
)->None:
    logger.info(f"Running test with coverage for rust coverage tool {rust_coverage_tool} with workload {workload}...")
    if not Path(f'{RUST_SRC_DIR}/tests.rs').is_file():
        logger.error(f"Generate test for workload {workload} for Rust first!")
        return
    #fi
    try:
        os.chdir(RUST_DIR)
        su.bash.run(
            "cargo clean",
            check_returncode=0
        )
        output = su.bash.run(
            f"time cargo {rust_coverage_tool} --tests 2>/dev/null",
        ).stderr
        logger.info(f'Rust_With_Coverage_{rust_coverage_tool}_{workload}_exec_time: {_process_time_stdout(output)}s')
        os.chdir(_DIR)
    except BashError as e:
        os.chdir(_DIR)
        logger.error(f"Running tests for workload {workload} for Rust failed!"
                     f"{e}")
        return
    #yrt
    logger.info(f"Finished running tests with coverage for rust coverage tool {rust_coverage_tool} with workload {workload}.")
#fed

def collect_coverage_overhead_rust(
    workloads: list[int],
    average: int,
    should_process_log_file: bool,
)->None:
    logger.info(f"Collecting coverage for {workloads} for rust over {average} runs...")
    for workload in workloads:
        for i in range(1, average + 1):
            logger.info(f"Collecting coverage for rust workload {workload} for run {i}")
            gen_rust_tests(workload)
            _run_test_without_coverage_rust(workload=workload)
            for tool in RUST_COVERAGE_TOOLS:
                _run_test_with_coverage_rust(workload=workload, rust_coverage_tool=tool)
            #rof
            logger.info(f"Finished collecting coverage for rust workload {workload} for run {i}!")
        #rof
    #rof
    logger.info(f"Finished collecting coverage for {workloads} for rust over {average} runs")

    if should_process_log_file:
        logger.info("Processing log file...")
        process_log_file(log_file=log_file, workloads=workloads)
        logger.info("Finishing...")
    #fi
#fed

def collect_coverage_overhead_cpp(
    workloads: list[int],
    average: int,
    should_process_log_file: bool,
)->None:
    logger.info(f"Collecting coverage for {workloads} for cpp over {average} runs...")
    _install_gtest()
    for workload in workloads:
        for i in range(1, average + 1):
            logger.info(f"Collecting coverage for cpp workload {workload} for run {i}")
            gen_cpp_tests(workload)
            _run_test_without_coverage_cpp(workload=workload)
            _run_test_with_coverage_cpp(workload=workload)
            logger.info(f"Finished collecting coverage for cpp workload {workload} for run {i}!")
        #rof
    #rof
    logger.info(f"Finished collecting coverage for {workloads} for cpp over {average} runs")

    if should_process_log_file:
        logger.info("Processing log file...")
        process_log_file(log_file=log_file, workloads=workloads)
        logger.info("Finishing...")
    #fi
#fed

def collect_coverage_overhead(
    workloads: list[int],
    average: int,
)->None:
    collect_coverage_overhead_rust(
        workloads=workloads,
        average=average,
        should_process_log_file=False,
    )
    collect_coverage_overhead_cpp(
        workloads=workloads,
        average=average,
        should_process_log_file=False,
    )

    logger.info("Processing log file...")
    process_log_file(log_file=log_file, workloads=workloads)
    logger.info("Finishing...")
#fed

def process_log_file(
    log_file: Path,
    workloads: list[int],
)->None:
    data: dict = {}
    with open(log_file, "r+") as file:
        file_contents = file.read()
        for workload in workloads:
            data[workload] = {}
            data[workload]['Rust'] = {}
            data[workload]['Rust']['avg'] = math.nan
            data[workload]['Rust']['stdev'] = math.nan
            data[workload]['Cpp'] = {}
            data[workload]['Cpp']['avg'] = math.nan
            data[workload]['Cpp']['stdev'] = math.nan
            data[workload]['Cpp']['gcov'] = {}
            data[workload]['Cpp']['gcov']['avg'] = math.nan
            data[workload]['Cpp']['gcov']['stdev'] = math.nan
            for tool in RUST_COVERAGE_TOOLS:
                data[workload]['Rust'][tool] = {}
                data[workload]['Rust'][tool]['avg'] = math.nan
                data[workload]['Rust'][tool]['stdev'] = math.nan 
                match = re.findall(f'Rust_With_Coverage_{tool}_{workload}_exec_time:\s+([\d.]+)s', file_contents)
                if match:
                    exec_times: list[float] = [float(i) for i in match]
                    data[workload]['Rust'][tool]['avg'] = mean(exec_times)
                    data[workload]['Rust'][tool]['stdev'] = stdev(exec_times)
                #fi
            #rof
            match = re.findall(f'Rust_Without_Coverage_{workload}_exec_time:\s+([\d.]+)s', file_contents)
            if match:
                exec_times: list[float] = [float(i) for i in match]
                data[workload]['Rust']['avg'] = mean(exec_times)
                data[workload]['Rust']['stdev'] = stdev(exec_times)
            #fi
            match = re.findall(f'Cpp_Without_Coverage_{workload}_exec_time:\s+([\d.]+)s', file_contents)
            if match:
                exec_times: list[float] = [float(i) for i in match]
                data[workload]['Cpp']['avg'] = mean(exec_times)
                data[workload]['Cpp']['stdev'] = stdev(exec_times)
            #fi
            match = re.findall(f'Cpp_With_Coverage_{workload}_exec_time:\s+([\d.]+)s', file_contents)
            if match:
                exec_times: list[float] = [float(i) for i in match]
                data[workload]['Cpp']['gcov']['avg'] = mean(exec_times)
                data[workload]['Cpp']['gcov']['stdev'] = stdev(exec_times)
            #fi
        #rof
    #htiw

    headers: list[str] = [str(i) for i in workloads]
    headers.insert(0, '#Tests')
    coverage_overhead: list[list] = [None] * (len(RUST_COVERAGE_TOOLS) + 1)
    test_times_no_coverage: list[list] = [None] * 2 
    test_times_with_coverage: list[list] = [None] * (len(RUST_COVERAGE_TOOLS) + 1)

    for idx,tool in enumerate(RUST_COVERAGE_TOOLS):
        coverage_overhead[idx] = []
        test_times_with_coverage[idx] = []

        coverage_overhead[idx].append(f'Rust ({tool})')
        test_times_with_coverage[idx].append(f'Rust ({tool})')

        for workload in workloads:
            coverage_overhead[idx].append(round(data[workload]['Rust'][tool]['avg'] / data[workload]['Rust']['avg'], 2))
            test_times_with_coverage[idx].append(f"{round(data[workload]['Rust'][tool]['avg'], 4)} \u00B1 {round(data[workload]['Rust'][tool]['stdev'], 4)}")
        #rof
    #rof

    coverage_overhead[idx+1] = []
    test_times_with_coverage[idx+1] = []
    coverage_overhead[idx+1].append('Cpp (gcov)')    
    test_times_with_coverage[idx+1].append('Cpp (gcov)')
    for workload in workloads:
        coverage_overhead[idx+1].append(round(data[workload]['Cpp']['gcov']['avg'] / data[workload]['Cpp']['avg'], 2))
        test_times_with_coverage[idx+1].append(f"{round(data[workload]['Cpp']['gcov']['avg'], 4)} \u00B1 {round(data[workload]['Cpp']['gcov']['stdev'], 4)}")
    #rof
    
    test_times_no_coverage[0] = []
    test_times_no_coverage[0].append('Rust')
    for workload in workloads:
        test_times_no_coverage[0].append(f"{round(data[workload]['Rust']['avg'], 4)} \u00B1 {round(data[workload]['Rust']['stdev'], 4)}")
    #rof
    test_times_no_coverage[1] = []
    test_times_no_coverage[1].append('Cpp')
    for workload in workloads:
        test_times_no_coverage[1].append(f"{round(data[workload]['Cpp']['avg'], 4)} \u00B1 {round(data[workload]['Cpp']['stdev'], 4)}")
    #rof
    
    print("Execution times in seconds for tests with coverage")
    print(tabulate(test_times_with_coverage, headers=headers, tablefmt="simple_outline"))

    print("\n\nExecution times in seconds for tests without coverage")
    print(tabulate(test_times_no_coverage, headers=headers, tablefmt="simple_outline"))

    
    print("\n\nCoverage overhead as a ratio of execution time with and without coverage")
    print(tabulate(coverage_overhead, headers=headers, tablefmt="simple_outline"))
    #print(json.dumps(data, indent = 4))
#fed

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script for comparing performance of coverage tools for Rust and C++.")
    parser.add_argument("--install-rust",
                         help="Installs Rust lang.",
                        action='store_true')
    parser.add_argument("--install-rust-coverage-tools",
                         help="Installs coverage tools for Rust.",
                        action='store_true')
    parser.add_argument("--install-cpp-coverage-tools",
                         help="Installs coverage tools for C++.",
                        action='store_true')
    parser.add_argument("--gen-rust-tests",
                        help=f"Generates tests.rs in {RUST_SRC_DIR}/todo_app/rust/src containing workload number of tests.",
                        choices=WORKLOAD,
                        type=int,
                        nargs=1)
    parser.add_argument("--gen-cpp-tests",
                        help=f"Generates tests.cpp in {CPP_SRC_DIR} containing workload number of tests.",
                        choices=WORKLOAD,
                        type=int,
                        nargs=1)
    parser.add_argument("--collect-coverage-overhead-rust",
                        help=f"Collects coverage overheads for Rust coverage tools.",
                        choices=WORKLOAD,
                        type=int,
                        nargs='*')
    parser.add_argument("--collect-coverage-overhead-cpp",
                        help=f"Collects coverage overheads for Cpp coverage tools.",
                        choices=WORKLOAD,
                        type=int,
                        nargs='*')
    parser.add_argument("--collect-coverage-overhead",
                        help=f"Collects coverage overheads for Cpp and Rust coverage tools.",
                        choices=WORKLOAD,
                        type=int,
                        nargs='*')
    parser.add_argument("--average",
                        help=f"Averages test runs over specified number while collecting coverage",
                        type=int,
                        nargs=1)
    args = parser.parse_args()
    if args.install_rust:
       install_rust()
    #fi
    if args.install_rust_coverage_tools:
       install_rust_coverage_tools()
    #fi
    if args.install_cpp_coverage_tools:
       install_cpp_coverage_tools()
    #fi
    if args.gen_rust_tests is not None:
       gen_rust_tests(args.gen_rust_tests[0])
    #fi
    if args.gen_cpp_tests is not None:
       gen_cpp_tests(args.gen_cpp_tests[0])
    #fi
    if args.collect_coverage_overhead_rust is not None:
       collect_coverage_overhead_rust(workloads=args.collect_coverage_overhead_rust,
                                      average=args.average[0] if args.average is not None else 5,
                                      should_process_log_file=True)
    #fi
    if args.collect_coverage_overhead_cpp is not None:
       collect_coverage_overhead_cpp(workloads=args.collect_coverage_overhead_cpp,
                                     average=args.average[0] if args.average is not None else 5,
                                     should_process_log_file=True)
    #fi
    if args.collect_coverage_overhead is not None:
       collect_coverage_overhead(workloads=args.collect_coverage_overhead,
                                 average=args.average[0] if args.average is not None else 5)
    #fi
#fi
