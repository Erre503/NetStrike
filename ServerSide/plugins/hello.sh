#!/bin/bash

# Declare a variable to hold the parameter
message="Custom message"

# Function to set the parameter
set_param() {
    message="$1"
}

# Function to get the parameter
get_param() {
    echo "$message"
}

# Function to execute the main action
execute() {
    echo "Hello, World! $msg"
}

execute
