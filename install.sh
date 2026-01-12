#!/bin/bash

echo "Installing Imajin dependencies..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "Installation completed successfully!"
    echo "To run the application, use: python src/main.py"
else
    echo "Installation failed. Please check the error messages above."
    exit 1
fi
