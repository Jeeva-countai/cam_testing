#!/bin/bash

# Run cam1.py in the background and log output
python3 /home/kniti/Documents/test/cam1.py &

# Run cam2.py in the background and log output
python3 /home/kniti/Documents/test/cam2.py &

# Wait for both to finish
wait
