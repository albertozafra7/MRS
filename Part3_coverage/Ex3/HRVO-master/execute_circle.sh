# Program to execute the circle problem in a virtual window
# echo "Building everything"
# cmake .
# cmake --build .


# echo "Executing the Circle example to save the agent positions through time"
# ./examples/Circle > ./examples/circle_output.txt

echo "Visualizing the output"
python3 visualize_sim.py --file_path=./examples/circle_output.txt

# echo "Removing the trace of the program"
# rm ./examples/circle_output.txt