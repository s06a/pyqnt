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
                echo " Failed to install PiQuant in the virtual environment."
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

# Function to remove a Docker image by name
remove_docker_image() {
    local image_name="$1"
    
    # Check if any containers are using the image and get the first one
    container_id=$(sudo docker ps | grep "$image_name" | awk '{print $1}' | head -n 1)

    if [ -n "$container_id" ]; then
        echo "Stopping running container using the image '$image_name' with ID: $container_id..."
        sudo docker stop "$container_id"
    fi

    # Now remove the image
    image_id=$(sudo docker images | grep "$image_name" | awk '{print $3}' | head -n 1)

    if [ -n "$image_id" ]; then
        echo "Removing the Docker image with ID: $image_id..."
        if ! sudo docker rmi "$image_id"; then
            echo "Failed to remove the Docker image."
            exit 1
        fi
        echo "Docker image removed successfully."
    else
        echo "No Docker image found with the name '$image_name' to remove."
    fi
}

# Function to rebuild the Docker image and reinstall PiQuant
rebuild_and_reinstall() {
    echo "Rebuilding the Docker image and reinstalling PiQuant..."
    
    # Remove the existing Docker image
    remove_docker_image "piquant"

    echo "Building the new Docker image..."
    if ! sudo docker-compose up --build -d; then
        echo "Failed to build the Docker image."
        exit 1
    fi
    echo "Docker image rebuilt successfully."

    # Now install PiQuant
    install_piquant
}

# Function to remove PiQuant and its Docker image
remove_piquant() {
    echo "Removing PiQuant and its Docker image..."

    # Check if PiQuant is installed and remove it
    if command -v piquant &> /dev/null; then
        echo "PiQuant is installed. Removing..."
        if pip show piquant &> /dev/null; then
            # Check if installed globally
            pip uninstall -y piquant
        elif pip show --user piquant &> /dev/null; then
            # Check if installed for the current user
            pip uninstall --user -y piquant
        elif [ -d "piquant_env" ]; then
            # Check if installed in a virtual environment
            echo "Activating virtual environment 'piquant_env' to remove PiQuant..."
            source piquant_env/bin/activate
            pip uninstall -y piquant
            deactivate
            echo "Virtual environment 'piquant_env' will not be removed."
        fi
        echo "PiQuant removed successfully."
    else
        echo "PiQuant is not installed."
    fi

    # Remove the Docker image
    remove_docker_image "piquant"
}

# Function to prompt user for action
prompt_user() {
    echo "What would you like to do?"
    echo "1. Check Docker status and run container"
    echo "2. Check and install PiQuant"
    echo "3. Rebuild Docker image and reinstall PiQuant"
    echo "4. Remove PiQuant and its Docker image completely"
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
            rebuild_and_reinstall
            ;;
        4)
            remove_piquant
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