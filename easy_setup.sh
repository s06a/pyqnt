#!/bin/bash

# Function to check if Docker is running
check_docker() {
    if ! systemctl is-active --quiet docker; then
        echo "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Function to check if the Docker image is built
check_image() {
    if ! sudo docker images | grep -q "piquant"; then
        echo "Docker image 'piquant' not found. Building the image..."
        sudo docker-compose up --build -d
    else
        echo "Docker image 'piquant' is already built."
    fi
}

# Function to check if the Docker container is running
check_container() {
    if ! sudo docker ps | grep -q "piquant"; then
        echo "Starting the Docker container..."
        sudo docker-compose up -d
    else
        echo "Docker container 'piquant' is already running."
    fi
}

# Function to check if PiQuant is installed
check_piquant() {
    if command -v piquant &> /dev/null; then
        echo "PiQuant is already installed."
        return 1  # Indicate that PiQuant is installed
    else
        return 0  # Indicate that PiQuant is not installed
    fi
}

# Function to install PiQuant
install_piquant() {
    echo "How would you like to install PiQuant?"
    echo "1. Install globally (may break existing packages)"
    echo "2. Install for the current user"
    echo "3. Install in a virtual environment"
    read -p "Choose an option [1-3]: " install_option

    case $install_option in
        1)
            echo "Installing PiQuant globally..."
            if ! pip install --break-system-packages .; then
                echo "Failed to install PiQuant globally."
                exit 1
            fi
            ;;
        2)
            echo "Installing PiQuant for the current user..."
            if ! pip install --user .; then
                echo "Failed to install PiQuant for the current user."
                exit 1
            fi
            ;;
        3)
            echo "Installing PiQuant in a virtual environment..."
            if [ -d "piquant_env" ]; then
                echo "Virtual environment 'piquant_env' already exists. Activating..."
                source piquant_env/bin/activate
            else
                echo "Creating virtual environment 'piquant_env'..."
                python3 -m venv piquant_env
                source piquant_env/bin/activate
            fi
            if ! pip install .; then
                echo "Failed to install PiQuant in the virtual environment."
                exit 1
            fi
            deactivate
            echo "PiQuant installed in the virtual environment 'piquant_env'."
            ;;
        *)
            echo "Invalid option. Please try again."
            install_piquant
            ;;
    esac
}

# Function to rebuild the Docker image
rebuild_image() {
    echo "Rebuilding the Docker image..."
    # Check if the image exists and get its ID using grep and awk
    image_id=$(sudo docker images | grep "piquant" | awk '{print $3}')

    if [ -n "$image_id" ]; then
        echo "Removing the existing Docker image with ID: $image_id..."
        if ! sudo docker rmi "$image_id"; then
            echo "Failed to remove the existing Docker image."
            exit 1
        fi
    else
        echo "No existing Docker image found to remove."
    fi

    echo "Building the new Docker image..."
    if ! sudo docker-compose up --build -d; then
        echo "Failed to build the Docker image."
        exit 1
    fi
    echo "Docker image rebuilt successfully."
}

# Function to prompt user for action
prompt_user() {
    echo "What would you like to do?"
    echo "1. Check Docker status and run container (Backend)"
    echo "2. Check and install PiQuant (Just CLI app)"
    echo "3. Rebuild and reinstall PiQuant (Backend and CLI app)"
    echo "4. Rebuild Docker image (Backend)"
    echo "5. Exit"
    read -p "Choose an option [1-5]: " option

    case $option in
        1)
            check_docker
            check_image
            check_container
            ;;
        2)
            if check_piquant; then
                install_piquant
            fi
            ;;
        3)
            echo "Rebuilding and reinstalling PiQuant..."
            sudo docker-compose down
            sudo docker-compose up --build -d
            install_piquant
            ;;
        4)
            rebuild_image
 ;;
        5)
            echo "Exiting the script."
            exit 0
            ;;
        *)
            echo "Invalid option. Please try again."
            prompt_user
            ;;
    esac
}

# Main script execution
check_docker
prompt_user