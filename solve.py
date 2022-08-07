#!/usr/bin/env python3

import argparse

import solver


def show_about():
    print("""Killer Sudoku Solver

Script to solve Killer Sudoku puzzles, where the classic Sudoku puzzles are extended with cages. 
that can span multiple nonets.

Developed by: Tommy Andersen <andersentommy@gmail.com>

License: MIT License
""")


def main():
    parser = argparse.ArgumentParser(description="Solve a Killer Sudoku from file")
    parser.add_argument("--stats",
                        action="store_true",
                        help=("If set the solver will output information on how many combinations "
                              "were attempted"))
    parser.add_argument("--show-initial-board",
                        action="store_true",
                        help="Show the board and regions before trying to solve it.")
    parser.add_argument("--benchmark",
                        action="store_true",
                        help=("Benchmark against the specified files, by attempting to solve the "
                              "puzzles and show the time taken to do so"))
    parser.add_argument("--about",
                        action="store_true",
                        help="Show text describing this script, and exits")
    parser.add_argument("filename",
                        nargs='+',
                        help="The name of the JSON-file to load board and regions from")
    parsed_args = parser.parse_args()

    if parsed_args.about:
        return show_about()

    solver.run_solver(filenames=parsed_args.filename,
                      show_stats=parsed_args.stats,
                      benchmark=parsed_args.benchmark,
                      show_initial_board=parsed_args.show_initial_board)


if __name__ == '__main__':
    main()
