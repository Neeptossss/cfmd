# Check if python is installed
python --version
if [ $? -ne 0 ]; then
    echo "Python is not installed. Please install it."
    exit 1
fi

# Check if python version is 3.6 or higher
python_version=$(python --version | cut -d " " -f 2)
if [ $(echo $python_version | cut -d "." -f 1) -lt 3 ] || [ $(echo $python_version | cut -d "." -f 2) -lt 6 ]; then
    echo "Python version 3.6 or higher is required. Please upgrade your python version."
    exit 1
fi

# Check if pip is installed
pip --version
if [ $? -ne 0 ]; then
    echo "Pip is not installed. Please install it."
    exit 1
fi

# Install pyinstaller
pip install pyinstaller

# Build the executable
pyinstaller --onefile --noconsole main.py

# Move the executable to the dist folder
mv dist/main dist/$(basename $(pwd))
