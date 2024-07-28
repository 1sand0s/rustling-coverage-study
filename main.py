import seutil as su
import logging
import os
import argparse

from datetime import datetime
from pathlib import Path
from seutil.bash import BashError

WORKLOAD=[100, 1000, 10000]

## Directories.
_DIR = Path(os.path.dirname(os.path.realpath(__file__)))
LOG_DIR = _DIR / ".logs"
RUST_SRC_DIR = _DIR / "rust/todo_app/src"

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

def gen_rust_tests(
    num_tests: int
)->None:
    """
    Generates tests for Rust in module tests.rs with num_tests number of tests.
    """
    with open(RUST_SRC_DIR / "tests.rs", 'w') as f:
        f.write("#[cfg(test)]\n")
        f.write("mod tests {\n\n")
        f.write("\tuse crate::tasks::{Task, TaskManager};\n")

        for i in range(1, num_tests + 1):
            f.write("\t#[test]\n")
            f.write(f"\tfn test{i}Tasks() {{\n")
            f.write('\t\tlet mut task = Task::new("Test Task".to_string());\n')
            if i % 3 == 0:
                f.write('\t\tassert_eq!(task.description, "Test Task");\n')
            elif i % 2 == 0:
                f.write(f"\t\tassert!(!task.completed);\n")
            else:
                f.write(f"\t\ttask.completed = true;\n")
                f.write(f"\t\tassert!(task.completed);\n")
            #fi
            f.write("\t}\n")
        #rof
        f.write("}\n")
    #htiw
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
#fi
