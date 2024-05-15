# Program to execute the circle problem in a virtual window
echo "Building everything"
cmake .
cmake --build .


echo "Executing the A letter code to save the agent positions through time"
./examples/A_shape > ./examples/A_output.txt

echo "Visualizing the output"
python3 visualize_sim.py --file_path=./examples/A_output.txt --quarter_colors=T

echo "Removing the trace of the program"
rm ./examples/A_output.txt