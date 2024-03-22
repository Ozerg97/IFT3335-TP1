## Solve Every Sudoku Puzzle

## See http://norvig.com/sudoku.html

## Throughout this program we have:
##   r is a row,    e.g. 'A'
##   c is a column, e.g. '3'
##   s is a square, e.g. 'A3'
##   d is a digit,  e.g. '9'
##   u is a unit,   e.g. ['A1','B1','C1','D1','E1','F1','G1','H1','I1']
##   grid is a grid,e.g. 81 non-blank chars, e.g. starting with '.18...7...
##   values is a dict of possible values, e.g. {'A1':'12349', 'A2':'8', ...}

import time, numpy

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [a + b for a in A for b in B]


digits = '123456789'
rows = 'ABCDEFGHI'
cols = digits
squares = cross(rows, cols)
unitlist = ([cross(rows, c) for c in cols] +
            [cross(r, cols) for r in rows] +
            [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')])
units = dict((s, [u for u in unitlist if s in u])
             for s in squares)
peers = dict((s, set(sum(units[s], [])) - set([s]))
             for s in squares)


################ Unit Tests ################

def test():
    "A set of tests that must pass."
    assert len(squares) == 81
    assert len(unitlist) == 27
    assert all(len(units[s]) == 3 for s in squares)
    assert all(len(peers[s]) == 20 for s in squares)
    assert units['C2'] == [['A2', 'B2', 'C2', 'D2', 'E2', 'F2', 'G2', 'H2', 'I2'],
                           ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9'],
                           ['A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'C1', 'C2', 'C3']]
    assert peers['C2'] == set(['A2', 'B2', 'D2', 'E2', 'F2', 'G2', 'H2', 'I2',
                               'C1', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9',
                               'A1', 'A3', 'B1', 'B3'])
    print('All tests pass.')


################ Parse a Grid ################

def initialize_values(grid):
    """initialize the values dictionary based on the provided grid"""
    values = dict(zip(squares, grid))
    return values


def parse_grid(grid):
    """Convert grid to a dict of possible values, {square: digits}, or
    return False if a contradiction is detected."""
    ## To start, every square can be any digit; then assign values from the grid.
    values = dict((s, digits) for s in squares)
    for s, d in grid_values(grid).items():
        if d in digits and not assign(values, s, d):
            return False  ## (Fail if we can't assign d to square s.)
    return values


def grid_values(grid):
    "Convert grid into a dict of {square: char} with '0' or '.' for empties."
    chars = [c for c in grid if c in digits or c in '0.']
    assert len(chars) == 81
    return dict(zip(squares, chars))


################ Constraint Propagation ################

def assign(values, s, d):
    """Eliminate all the other values (except d) from values[s] and propagate.
    Return values, except return False if a contradiction is detected."""
    other_values = values[s].replace(d, '')
    if all(eliminate(values, s, d2) for d2 in other_values):
        return values
    else:
        return False


def eliminate(values, s, d):
    """Eliminate d from values[s]; propagate when values or places <= 2.
    Return values, except return False if a contradiction is detected."""
    if d not in values[s]:
        return values  ## Already eliminated
    values[s] = values[s].replace(d, '')
    ## (1) If a square s is reduced to one value d2, then eliminate d2 from the peers.
    if len(values[s]) == 0:
        return False  ## Contradiction: removed last value
    elif len(values[s]) == 1:
        d2 = values[s]
        if not all(eliminate(values, s2, d2) for s2 in peers[s]):
            return False
    ## (2) If a unit u is reduced to only one place for a value d, then put it there.
    for u in units[s]:
        dplaces = [s for s in u if d in values[s]]
        if len(dplaces) == 0:
            return False  ## Contradiction: no place for this value
        elif len(dplaces) == 1:
            # d can only be in one place in unit; assign it there
            if not assign(values, dplaces[0], d):
                return False
    return values


################ Display as 2-D grid ################
# this function as been modified from what we've received
def display(values):
    "Display these values as a 2-D grid."
    width = 1 + max(len(str(values[s])) for s in squares)
    line = '+'.join(['-' * (width * 3)] * 3)
    for r in rows:
        row_str = ''.join(str(values[r + c]).center(width) + ('|' if c in '36' else '') for c in cols)
        print(row_str)
        if r in 'CF':
            print(line)


################ Search ################

def solve(grid): return search(parse_grid(grid))


def search(values):
    "Using depth-first search and propagation, try all possible values."
    if values is False:
        return False  ## Failed earlier
    if all(len(values[s]) == 1 for s in squares):
        return values  ## Solved!
    ## Chose the unfilled square s with the fewest possibilities
    n, s = min((len(values[s]), s) for s in squares if len(values[s]) > 1)
    return some(search(assign(values.copy(), s, d))
                for d in values[s])


################ Utilities ################

def some(seq):
    "Return some element of seq that is true."
    for e in seq:
        if e: return e
    return False


def from_file(filename, sep='\n'):
    "Parse a file into a list of strings, separated by sep."
    return open(filename).read().strip().split(sep)


def shuffled(seq):
    "Return a randomly shuffled copy of the input sequence."
    seq = list(seq)
    random.shuffle(seq)
    return seq


################ System test ################

import time, numpy

def solve_all(grids, name='', showif=0.0):
    """Attempt to solve a sequence of grids. Report results.
    When showif is a number of seconds, display puzzles that take longer.
    When showif is None, don't display any puzzles."""

    def time_solve(grid):
        start = time.perf_counter()
        values = apply_hill_climbing_annealing(initialize_values(grid))
        t = time.perf_counter() - start
        ## Display puzzles that take long enough
        if showif is not None and t > showif:
            display(grid_values(grid))
            if values: display(values)
            print('(%.2f seconds)\n' % t)
        return (t, solved(values))

    times, results = zip(*[time_solve(grid) for grid in grids])
    N = len(grids)
    if N >1:
        print("Solved %d of %d %s puzzles (avg %.2f secs (%d Hz), max %.2f secs)." % (
            sum(results), N, name, sum(times) / N, N / sum(times), max(times)))

def solved(values):
    "A puzzle is solved if each unit is a permutation of the digits 1 to 9."

    def unitsolved(unit): return set(values[s] for s in unit) == set(digits)

    return values is not False and all(unitsolved(unit) for unit in unitlist)


def random_puzzle(N=17):
    """Make a random puzzle with N or more assignments. Restart on contradictions.
    Note the resulting puzzle is not guaranteed to be solvable, but empirically
    about 99.8% of them are solvable. Some have multiple solutions."""
    values = dict((s, digits) for s in squares)
    for s in shuffled(squares):
        if not assign(values, s, random.choice(values[s])):
            break
        ds = [values[s] for s in squares if len(values[s]) == 1]
        if len(ds) >= N and len(set(ds)) >= 8:
            return ''.join(values[s] if len(values[s]) == 1 else '.' for s in squares)
    return random_puzzle(N)  ## Give up and make a new puzzle


#=========Implementation question 4 & 5
def fill_randomly(square):
    '''fill the square randomly respecting the constraints'''
    values = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
    random.shuffle(values)
    #values = ['5', '2', '1', '4', '3', '6', '9', '8', '7']  # to remove just for test
    for i in range(len(square)):
        if square[i] == '0':
            if not values:
                break  # No more values available, break the loop

            for j in range(len(values)):
                if values[j] not in square:
                    square[i] = values[j]
                    break
    return square

def fill(current_configuration, boxes):
    '''fill the squares randomly'''
    for i in range(81):
        # extract the square from the current configuration based on the boxes
        if i == 0 or i == 3 or i == 6 \
                or i == 29 or i == 32 or i == 35 \
                or i == 54 or i == 57 or i == 60:
            square_keys = boxes[i][2]
            square = [current_configuration[key] for key in square_keys]
            j = i + 3
            # crreate a copy of the current configuration
            new_configuration = current_configuration.copy()

            # apply a swap within the selected square
            filled_square = fill_randomly(square)

            # update the new configuration with the filled square
            for key, value in zip(square_keys, filled_square):
                new_configuration[key] = value

            # count conflicts in the new configuration
            current_configuration = new_configuration.copy()

    return current_configuration

def count_general_conflicts(configuration):
    '''check conflicts in all the square'''
    conflicts = 0

    # Check conflicts in rows
    for row in rows:
        row_values = [configuration[row + str(i)] for i in range(1, 10)]
        for i in range(9):
            for j in range(i + 1, 9):
                if row_values[i] != '0' and row_values[i] == row_values[j]:
                    conflicts += 1
    # Check conflicts in columns
    for col in cols:
        col_values = [configuration[row + col] for row in rows]
        for i in range(9):
            for j in range(i + 1, 9):
                if col_values[i] != '0' and col_values[i] == col_values[j]:
                    conflicts += 1
    return conflicts

#=============Hill climbing===============
from itertools import combinations

def apply_hill_climbing(puzzle):
    max_iterations = 150
    current_configuration = puzzle.copy()
    boxes = list(units.values())

    # generate initial solution
    current_configuration = fill(current_configuration, boxes)
    for _ in range(max_iterations):
        best_conflict = count_general_conflicts(current_configuration)
        if best_conflict == 0:
            print("solved!")
            break

        next_configuration = find_best_neighbor(current_configuration, boxes)
        next_conflict = count_general_conflicts(next_configuration)

        if next_conflict < best_conflict:
            current_configuration = next_configuration.copy()
        else:
            return current_configuration

    return current_configuration

def find_best_neighbor(current_configuration, boxes):
    '''generate all possible neighbors by swapping digits
    in the same box'''
    neighbors = []
    square_index = random.choice(range(len(boxes)))
    square_keys = boxes[square_index][2]
    for combo in combinations(range(9), 2):
        new_configuration = current_configuration.copy()
        square = [current_configuration[key] for key in square_keys]
        square[combo[0]], square[combo[1]] = square[combo[1]], square[combo[0]]
        for key, value in zip(square_keys, square):
            new_configuration[key] = value
        neighbors.append(new_configuration)

    # find the neighbor with the lowest conflict count
    best_neighbor = min(neighbors, key=count_general_conflicts)
    return best_neighbor

#============Simulated Annealing===========================
import random
import math
def apply_hill_climbing_annealing(puzzle, initial_temperature=1.15, alpha=0.99):
    iterations = 500
    initial_configuration = puzzle.copy()
    current_configuration = initial_configuration.copy()
    temperature = initial_temperature
    boxes = list(units.values())

    # fill the squares randomly
    current_configuration = fill(current_configuration, boxes)
    best_configuration = current_configuration.copy()

    for step in range(1, iterations + 1):
        best_conflict = count_general_conflicts(current_configuration)

        # Update temperature
        temperature = alpha * temperature
        if temperature == 0:
            return best_configuration

        # find the best neighboring state
        neighbouring_state = find_best_neighbor(current_configuration, boxes)


        # determine the energy of the current and neighbouring state
        neighbouring_energy = count_general_conflicts(neighbouring_state)
        current_energy = count_general_conflicts(current_configuration)

        # calculate deltaE
        deltaE = neighbouring_energy - current_energy

        # if the neighbouring state has a lower energy than the current or if the acceptance probability is fulfilled
        if deltaE < 0 or random.random() < math.exp(deltaE / temperature):
            current_configuration = neighbouring_state.copy()
            best_conflict = neighbouring_energy
            best_configuration = current_configuration.copy()

        if best_conflict == 0:
            print("Solved")
            break

    print("Best conflict:", best_conflict)
    return best_configuration

#============ END Simulated Annealing===========================



grid1 = '003020600900305001001806400008102900700000008006708200002609500800203009005010300'
grid2 = '4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......'
hard1 = '.....6....59.....82....8....45........3........6..3.54...325..6..................'


### Custom tests ###

# test apply_hill_climbing function
def test_apply_hill_climbing():
    #initial_grid = '003020600900305001001806400008102900700000008006708200002609500800203009005010300'
    with open('100sudoku.txt', 'r') as file:
        grids = file.readlines()
    for idx, grid in enumerate(grids):
        initial_values = initialize_values(grid.strip())

        print(f"Grid {idx + 1} - Initial Configuration:")
        display(initial_values)

        updated_values = apply_hill_climbing(initial_values)

        print(f"Grid {idx + 1} - After Applying Hill-Climbing:")
        display(updated_values)
        print("\n" + "="*50)  # Separator between grids

def test_apply_simulated_annealing():
    with open('100sudoku.txt', 'r') as file:
        grids = file.readlines()
    for idx, grid in enumerate(grids):
        initial_values = initialize_values(grid.strip())

        print(f"Grid {idx + 1} - Initial Configuration:")
        display(initial_values)

        updated_values = apply_hill_climbing_annealing(initial_values)

        print(f"Grid {idx + 1} - After Applying Simulated Annealing:")
        display(updated_values)
        print("\n" + "="*50)  # separator between grids

def test_one():
    initial_values = initialize_values(grid1)
    print("initial configuration")
    display(initial_values)

    updated_values = apply_hill_climbing_annealing(initial_values)

    print("After Applying Hill-Climbing:")
    display(updated_values)

# test count_conflicts function

if __name__ == '__main__':
    test()
    # Run the custom tests
    solve_all(from_file("100sudoku.txt"), '', None)
    #test_one()
    #test_apply_hill_climbing()
    #test_apply_simulated_annealing()
    #test_count_conflicts()
    # solve_all(from_file("100sudoku.txt"), "100sudoku", 0.005)
    # solve_all(from_file("easy50.txt", '========'), "easy", None)
    # solve_all(from_file("easy50.txt", '========'), "easy", None)
    # solve_all(from_file("top95.txt"), "hard", None)
    # solve_all(from_file("hardest.txt"), "hardest", None)
    # solve_all([random_puzzle() for _ in range(99)], "random", 100.0)

## References used:
## http://www.scanraid.com/BasicStrategies.htm
## http://www.sudokudragon.com/sudokustrategy.htm
## http://www.krazydad.com/blog/2005/09/29/an-index-of-sudoku-strategies/
## http://www2.warwick.ac.uk/fac/sci/moac/currentstudents/peter_cock/python/sudoku/
