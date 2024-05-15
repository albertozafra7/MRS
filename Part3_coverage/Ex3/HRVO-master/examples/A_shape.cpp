/*
 * Circle.cpp
 * HRVO Library
 *
 * Copyright 2009 University of North Carolina at Chapel Hill
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 * Please send all bug reports to <geom@cs.unc.edu>.
 *
 * The authors may be contacted via:
 *
 * Jamie Snape, Jur van den Berg, Stephen J. Guy, and Dinesh Manocha
 * Dept. of Computer Science
 * 201 S. Columbia St.
 * Frederick P. Brooks, Jr. Computer Science Bldg.
 * Chapel Hill, N.C. 27599-3175
 * United States of America
 *
 * <https://gamma.cs.unc.edu/HRVO/>
 */

/**
 * \file   Circle.cpp
 * \brief  Example with 250 agents navigating through a circular environment.
 */

#ifndef HRVO_OUTPUT_TIME_AND_POSITIONS
#define HRVO_OUTPUT_TIME_AND_POSITIONS 1
#endif

#include <cmath>

#if HRVO_OUTPUT_TIME_AND_POSITIONS
#include <iostream>
#endif

#include <HRVO.h>

using namespace hrvo;

const float HRVO_TWO_PI = 6.283185307179586f;
const double side_length = 30.f;
const std::size_t n_robots = 30;
const double time_step = 0.75f;

std::vector <Vector2> generate_square(const double robot_rel_dist);
std::vector <Vector2> generate_A_letter(const double robot_rel_dist);

int main()
{
	Simulator simulator;

	simulator.setTimeStep(time_step);
	simulator.setAgentDefaults(15.0f, 10, 1.2f, 1.5f, 1.0f, 2.0f);

	// double inter_robot_dist = 1/((double) n_robots);
	double inter_robot_dist = 5;

    const std::vector<Vector2> initial_positions = generate_square(inter_robot_dist);
	// std::cout << "Initial Positons" <<std::endl;
	// for (std::size_t i = 0; i < n_robots; ++i) {
	// 	std::cout << initial_positions[i] << " ";
	// }

	// std::cout << std::endl << "Final Positions" << std::endl;

    const std::vector<Vector2> final_positions = generate_A_letter(inter_robot_dist*5);
	// for (std::size_t i = 0; i < n_robots; ++i) {
	// 	std::cout << final_positions[i] << " ";
	// }
	// std::cout << std::endl;
	for (std::size_t i = 0; i < n_robots; ++i) {
		simulator.addAgent(initial_positions[i], simulator.addGoal(final_positions[i]));
	}

	do {
#if HRVO_OUTPUT_TIME_AND_POSITIONS
		std::cout << simulator.getGlobalTime();

		for (std::size_t i = 0; i < simulator.getNumAgents(); ++i) {
			std::cout << " " << simulator.getAgentPosition(i);
		}

		std::cout << std::endl;
#endif /* HRVO_OUTPUT_TIME_AND_POSITIONS */

		simulator.doStep();
	}
	while (!simulator.haveReachedGoals());

	return 0;
}

std::vector <Vector2> generate_square(const double robot_rel_dist){
	std::vector <Vector2> positions;
	Vector2 currPos = Vector2(side_length/2, side_length/2);
	positions.push_back(currPos);
	double step = side_length * 4 / ((float) n_robots);
	
	std::vector <Vector2> directions;
	directions.push_back(Vector2( 0,-1)*robot_rel_dist); // 1st go down
	directions.push_back(Vector2(-1, 0)*robot_rel_dist); // 2nd go left
	directions.push_back(Vector2( 0, 1)*robot_rel_dist); // 3rd go up
	directions.push_back(Vector2( 1, 0)*robot_rel_dist); // 4rd go right

	std::vector <double> lenghts;
	lenghts.push_back(side_length); 			
	lenghts.push_back(side_length);
	lenghts.push_back(side_length);
	lenghts.push_back(side_length);
	uint j = 0; // keeps track of the direction
	double already_advanced = 0;

	for (size_t i = 0; i < n_robots-1; i++){
		currPos += directions[j]; // move in the current direction
		already_advanced += step;
		if (already_advanced > lenghts[j]){
			currPos -= directions[j]; // go back
			currPos += directions[j]/step * (step - (already_advanced-lenghts[j])); // advance untill the end of the side
			j += 1; // change directions
			currPos += directions[j]/step * (already_advanced-lenghts[j-1]); // advance the rest of the step in the new direction
			already_advanced -= lenghts[j-1]; // restart the counter of the advancement on the new side
		}
		positions.push_back(currPos);
	}
	return positions;
}

std::vector<Vector2> generate_A_letter(const double robot_rel_dist) {
    std::vector<Vector2> positions;
    Vector2 currPos = Vector2(0,side_length);
    positions.push_back(currPos);

    double step = side_length * 7 / (double)n_robots;

    std::vector<Vector2> directions;
	directions.push_back(Vector2(0.25,-0.5)*robot_rel_dist);  // 1st go down right
	directions.push_back(Vector2(0.25,-0.5)*robot_rel_dist);  // 2nd go down right
	directions.push_back(Vector2(-0.25,0.5)*robot_rel_dist);  // 3rd go up left
	directions.push_back(Vector2(-0.25,0)*robot_rel_dist);	  // 4th go left
	directions.push_back(Vector2(-0.25,-0.5)*robot_rel_dist); // 5th go down left
	directions.push_back(Vector2(0.25,0.5)*robot_rel_dist);	  // 6th go up right
	directions.push_back(Vector2(0.2,0.5)*robot_rel_dist);	  // 7th go up right
    

    std::vector<double> lengths;
	lengths.push_back(side_length/2); 			
	lengths.push_back(side_length);
	lengths.push_back(side_length);
	lengths.push_back(side_length);			
	lengths.push_back(side_length);
	lengths.push_back(side_length);
	lengths.push_back(side_length/2);

	/*
	directions.push_back(Vector2(0.25,0.5)*robot_rel_dist);	  // 6th go up right
	directions.push_back(Vector2(0.25,-0.5)*robot_rel_dist);  // 1st go down right
	directions.push_back(Vector2(0.25,-0.5)*robot_rel_dist);  // 2nd go down right
	directions.push_back(Vector2(-0.25,0.45)*robot_rel_dist);  // 3rd go up left
	directions.push_back(Vector2(-0.25,0)*robot_rel_dist);	  // 4th go left
	directions.push_back(Vector2(-0.25,-0.5)*robot_rel_dist); // 5th go down left
	directions.push_back(Vector2(0.2,0.45)*robot_rel_dist);	  // 7th go up right
	*/

    uint j = 0; // keeps track of the direction
    double already_advanced = 0;

    for (size_t i = 0; i < n_robots - 1; i++) {
        currPos = currPos + directions[j]; // move in the current direction
        already_advanced += step;
        if (already_advanced > lengths[j]) {
            currPos = currPos - directions[j]; // go back
            currPos = currPos + (directions[j] / step) * (step - (already_advanced - lengths[j])); // advance until the end of the side
            j++; // change directions
            currPos = currPos + (directions[j] / step) * (already_advanced - lengths[j - 1]); // advance the rest of the step in the new direction
            already_advanced -= lengths[j - 1]; // restart the counter of the advancement on the new side
        }
        positions.push_back(currPos);
    }
    return positions;
}

