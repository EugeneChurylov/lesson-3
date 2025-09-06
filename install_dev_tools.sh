#!/bin/bash

LOG_FILE="install.log"
echo "==== Installation started at $(date) ====" >> $LOG_FILE

check_command() {
    command -v $1 >/dev/null 2>&1
}

log() {
    echo "$1"
    echo "$1" >> $LOG_FILE
}

# Python
if check_command python3; then
    PY_VER=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    log "Python version: $PY_VER"
else
    log "Python not found, installing..."
    sudo apt update
    sudo apt install -y python3 python3-venv python3-pip
fi

# pip
if check_command pip3; then
    log "pip is installed"
else
    log "Installing pip..."
    sudo apt install -y python3-pip
fi

# Docker
if check_command docker; then
    log "Docker is installed"
else
    log "Installing Docker..."
    sudo apt update
    sudo apt install -y docker.io
    sudo systemctl enable docker
    sudo systemctl start docker
fi

# Docker Compose
if check_command docker-compose; then
    log "Docker Compose is installed"
else
    log "Installing Docker Compose..."
    sudo apt install -y docker-compose
fi

# Python ML libraries
PY_LIBS=(torch torchvision pillow)
for lib in "${PY_LIBS[@]}"; do
    if python3 -c "import $lib" &>/dev/null; then
        log "$lib already installed"
    else
        log "Installing $lib..."
        pip3 install $lib
    fi
done

log "==== Installation finished at $(date) ===="
