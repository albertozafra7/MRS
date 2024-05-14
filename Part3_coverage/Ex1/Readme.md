# Robot Formation Simulation

This project simulates the formation of robots in various shapes. The robots can be arranged in line, circle, grid, square, star, and hexagon shapes. The formation dynamically updates, and the robots' positions are visualized using Matplotlib.

## Features

- Generates robot positions in various shapes: line, circle, grid, square, star, and hexagon.
- Handles more robots than the basic vertices of the shapes by distributing them along the edges.
- Dynamically updates and visualizes the robot positions.
- Supports pausing the simulation using a keyboard interrupt.

## Requirements

- Python 3.6+
- `numpy` library
- `matplotlib` library

## Usage

Run the simulation with the following command:

    ```sh
    python enclosing.py --n_robots NUM_ROBOTS --shape SHAPE
    ```

Where `NUM_ROBOTS` is the number of robots (including the enclosed), and `SHAPE` is one of "line", "circle", "grid", "square", "star", or "hexagon".

### Examples

#### Line formation

    ```sh
    python enclosing.py --n_robots=7 --shape=line
    ```

This command runs the simulation with 7 robots in a line formation.

#### Circular formation

    ```sh
    python enclosing.py --n_robots=15 --shape=circle
    ```

This command runs the simulation with 15 robots in a circular formation.


#### Grid formation

    ```sh
    python enclosing.py --n_robots=10 --shape=grid
    ```

This command runs the simulation with 10 robots in a grid formation.

#### Square formation

    ```sh
    python enclosing.py --n_robots=13 --shapesquare
    ```

This command runs the simulation with 13 robots in a square formation.

#### Star formation

    ```sh
    python enclosing.py --n_robots=11 --shape=star
    ```

This command runs the simulation with 11 robots in a star formation.

#### Hexagon formation

    ```sh
    python enclosing.py --n_robots=20 --shape=hexagon
    ```

This command runs the simulation with 20 robots in a hexagon formation.

#### Orbiting control

    ```sh
    python enclosing.py --n_robots=20 --shape=hexagon --rotate=T
    ```

This command runs the simulation with 20 robots in a hexagon formation while orbiting around the target. Keep in mind that this only works on closed shapes and that the generated shape might be deformed


## Code Overview

### `generate_robot_positions(shape, num_robots)`

Generates the initial positions for the robots based on the specified shape. Handles more robots than the vertices by distributing them along the edges of the shape.

### `class Formation`

This class handles the simulation of the robot formation.

- `__init__(self, q, c)`: Initializes the formation with the starting positions `q` and the desired positions `c`.
- `run(self)`: Runs the simulation for a specified number of iterations.
- `compute_inter_positions(self, positions)`: Computes inter-robot relative positions.
- `plot_robots(self)`: Plots the current positions of the robots.

### Example Main Function

The main function parses command-line arguments, generates initial and desired positions, and runs the formation simulation.

    ```python
    if __name__ == "__main__":
        parser = argparse.ArgumentParser()
        parser.add_argument('--n_robots', dest='n', type=int, help='Number of Robots')
        parser.add_argument('--shape', dest='shape', type=str, help='You can select between "circle", "grid", "line", "square", "star", "hexagon"')
        args = parser.parse_args()

        q = np.random.rand(args.n, 2) * 10
        q[-1] = np.array([0, 0])

        c = generate_robot_positions(args.shape, args.n)
        enc = Formation(q, c)
    ```
