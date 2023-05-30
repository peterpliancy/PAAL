#!/bin/bash

# Enable immediate exit on error
set -e

# Check if .pyenv directory exists, if so remove it
if [ -d "$HOME/.pyenv" ]; then
    echo "Removing existing .pyenv directory..."
    rm -rf "$HOME/.pyenv"
fi

# Check if pyenv is installed, if not install it
if ! command -v pyenv &> /dev/null; then
    echo "Installing pyenv..."
    curl -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash
fi

# Add pyenv to the PATH
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init -)"

# Define Python dependencies
PYTHON_DEPS=(
    'flask'
    'jinja2'
    'pandas'
    'requests'
    'pathlib'
    'blinker'
    'certifi'
    'charset-normalizer'
    'click'
    'itsdangerous'
    'MarkupSafe'
    'numpy'
    'python-dateutil'
    'pytz'
    'six'
    'urllib3==1.26.7'
    'PyQt5'
    'pyside2'
)

# Function to prompt the user to press Return/Enter
prompt_return() {
    read -p "Press Return/Enter to proceed to the next step..."
}

# Function to display instructions for enabling Rosetta mode
display_instructions() {
    echo "It looks like you are running an Apple Silicon based Mac, and in order for us to continue the installation, you need to perform the following steps:"
    echo ""
    echo "1. Open the Utilities folder in the Applications folder."
    prompt_return
    echo "2. Click/Highlight the Terminal application and press Command + I."
    prompt_return
    echo "3. In the Terminal Info window, check the box that says 'Open using Rosetta'."
    prompt_return
    echo "4. Quit Terminal, open it back up, and run the PAAL_Install.sh file one more time!"
    prompt_return
    echo ""
}

# Check if running on an Apple Silicon based Mac and Rosetta is not already installed
if [[ "$(uname -p)" == "arm" && ! "$(/usr/bin/pgrep -q oahd && echo Yes || echo No)" == "Yes" ]]; then
    echo "Rosetta is not installed."
    echo "Installing Rosetta..."
    softwareupdate --install-rosetta --agree-to-license
    echo "Rosetta installation complete."
    display_instructions
    exit 0
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install "${PYTHON_DEPS[@]}"

# Download PAAL ZIP file
echo "Downloading PAAL ZIP file..."
curl -L -o /tmp/PAAL1.0-main.zip "https://github.com/peterpliancy/PAAL1.0/archive/refs/heads/main.zip"
echo "PAAL ZIP file downloaded successfully."

# Unpack PAAL ZIP file
echo "Unpacking PAAL ZIP file..."
unzip -q "/tmp/PAAL1.0TK-main.zip" -d /tmp/
echo "PAAL ZIP file unpacked successfully."

# Rename and move PAAL to Applications folder
echo "Renaming and moving PAAL to Applications folder..."
mv -f "/tmp/PAAL1.0TK-main" "/tmp/PAAL 1.0"
mv -f "/tmp/PAAL 1.0" "/Applications/PAAL 1.0"
echo "PAAL has been renamed and moved to the Applications folder."

# Run PAAL.py
echo "Launching PAAL.py..."
python3 "/Applications/PAAL 1.0/PAAL.py"

echo "Installation and launch complete."
