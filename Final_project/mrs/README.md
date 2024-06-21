# Swarm Robotics Simulator

This repository contains the implementation of a simulator for controlling a multi-agent robotic swarm. The system is developed using Python and leverages various libraries and tools for communication, computation, and coordination among the agents.

## Table of Contents

- [Introduction](#introduction)
- [Setup](#setup)
- [Usage](#usage)
- [Code Structure](#code-structure)
- [Configuration](#configuration)
- [License](#license)

## Introduction

The simulator is designed to control a group of robotic agents, allowing them to organize into predefined geometrical patterns and maintain these formations while navigating through dynamic environments. The control system consists of a global control algorithm and a local control algorithm, which work together to ensure the coherence and alignment of the swarm.

## Setup

### Prerequisites

- Python 3.x
- Required Python libraries: `numpy`, `scipy`, `paramiko`, `xmlrpc`, `matplotlib`, `multiprocessing`

### Installation

1. Clone this repository:
    ```bash
    git clone https://github.com/albertozafra7/MRS.git
    cd Final_project/mrs
    ```

2. Install the required libraries:
    ```bash
    pip install numpy scipy paramiko matplotlib multiprocessing
    ```

3. Move the /mrs directory to the /home directory of the remote server

## Usage

To run the simulator, execute the main script with the required configuration files, an example of the configuration files can be found under the /params directory:

```bash
python main.py --conn_file path/to/conn_file.txt --dir_file path/to/dir_file.txt --pos_file path/to/pos_file.txt --shape_file path/to/shape_file.txt --logs_file path/to/logs_file.txt
```


## Code Structure

- **main.py**: The main script to initialize and run the simulator.
- **simulator.py**: Contains the Simulator class responsible for managing the simulation, including control algorithms and communication with other agents.
- **utils.py**: Utility functions used by the simulator for reading configurations and other helper tasks.
- **print_colors.py**: Defines color formatting for console outputs.
- **bot_initializer.py**: This script initializes and runs an agent.
- **agent.py**: Defines the agent class that represents an individual agent with formation control and communication functionalities.
- **formation_control_class.py**: Defines the formation_control class responsible for handling the control and positioning of agents in specified formations.
- **Communication.py**: Handles communication between agents using RPC (Remote Procedure Call).

### Detailed Description
#### main.py

The entry point of the system. It parses the command-line arguments to get the paths of the configuration files and initializes the Simulator object with these files.

#### simulator.py

Defines the Simulator class which handles the control logic and communication with other agents. The class is initialized with the paths to the configuration files:

```python
class Simulator:
    def __init__(self, conn_file, dir_file, pos_file, shape_file, logs_file, max_iters=1000, height=60, width=60, bot_size=5, group_cols=True, random_cols=False):
```

Additional Methods in Simulator

- execute_simulation(): Runs the main simulation loop.
- initialize_robots(dirsF): Initializes robots and starts them using remote SSH calls.
- start_robot(): Starts individual robots using specified configurations.
- start_connections(): Establishes connections between robots.
- kill_agents(): Terminates all agent processes.
- update_pose(uid): Updates the position of a specific robot.
- update_group_poses(idG): Updates the positions of all robots in a group.
- update_poses(): Updates the positions of all robots.
- log_evolution(): Logs the evolution of the robots' positions.

#### bot_initializer.py

Imports:
    Import necessary modules: argparse, utils, Communication, numpy, and agent.

Main Execution Block:
    Parse command-line arguments for agent and simulation parameters.
    Load connections and directions from specified files with error handling.
    Instantiate an agent object with the parsed parameters and loaded files.
    Print a message indicating the program is exiting.

#### agent.py

Imports:
    Import necessary modules: numpy, time, datetime, formation_control, utils, and Communication.

agent Class:
    init(): Initialize the agent with parameters for the number of robots, groups, unique ID, initial poses, shapes, etc.
        Initialize global and local properties.
        Initialize the communication system.
        Start communication servers.
        Start the simulation.
    simulate(): Main simulation loop for the agent.
        Update global and local positions.
        Update and execute formation controls.
        Update computed positions to the communication system.
    get_agent_pos(): Return the current position of the agent.

#### formation_control_class.py

Imports:
    Import necessary modules: multiprocessing, numpy.

formation_control Class:
    init(): Initialize formation control with parameters for the number of agents, IDs, initial poses, shapes, control gains, etc.
    get_agent_pose(): Return the current pose of the agent.
    update_poses(): Update stored poses.
    update_center(): Update the center of the formation.
    get_desired_agent_pose(): Return the desired pose of the agent.
    execute_control(): Execute the control algorithm to adjust agent positions.
    compute_inter_robot_positions(): Compute relative positions between robots.
    generate_robot_positions(): Generate desired positions for different shapes (line, circle, grid, square, star, hexagon).

#### Communication.py

Imports:
    Import necessary modules: xmlrpc.server, xmlrpc.client, json, time, numpy, multiprocessing.

MyServer Class:
    Inherits from SimpleXMLRPCServer and overrides serve_forever to allow stopping the server.

Communication Class:
    init(): Initialize communication with parameters for the number of local and global agents, IDs, IP address, port, and directions.
        Initialize shared arrays for storing positions.
        Start communication servers and connections.
    start_servers(): Set up and start RPC server and client processes.
    service(): Handle RPC requests in a loop.
    RPC_get_positions(): RPC method to get positions.
    RPC_get_position(): RPC method to get a single position.
    RPC_finish(): RPC method to finish the communication.
    RPC_get_poses(): RPC method to get and update poses.
    start_connections(): Start connections to other agents.
    talker(): Main loop for sending and receiving data between agents.

## Configuration

Configuration files specify the setup of the swarm, including agent positions, IP addresses, and communication graphs. Examples include:

    conn_file.txt: Specifies the connection graph between agents.
    dir_file.txt: IP addresses and ports for each agent.
    pos_file.txt: Initial positions of the agents.
    shape_file.txt: Definitions of the desired shapes and formations.
    logs_file.txt: Path to the file where logs will be stored.

## License 
This project is licensed under the MIT License. See the LICENSE file for details.