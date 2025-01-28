#!/bin/bash

# Run all graphs in the graphs/tests directory. There is no auto-
# checking to see if they fail 

# Directory to process
DIRECTORY="graphs/tests"

# Check if the directory exists
if [ ! -d "$DIRECTORY" ]; then
    echo "Error: Directory $DIRECTORY does not exist."
    exit 1
fi

# Iterate through each file in the directory
for FILE in "$DIRECTORY"/*; do
    # Check if it's a file (not a directory or other type)
    if [ -f "$FILE" ]; then
        # Extract the filename without the path
        FILENAME=$(basename "$FILE")

        # Use the filename in a command (replace 'echo' with your desired command)
        echo "Processing file: $FILENAME"

        # Example command using the filename
        # Replace the following line with the command you want to execute
        ana --graph "$FILE"  # Replace 'some_command' with your actual command
    fi
done
