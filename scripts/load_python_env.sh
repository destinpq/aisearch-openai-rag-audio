 #!/bin/bash

# Check if virtual environment exists, create if it doesn't
if [ ! -d ".venv" ]; then
    echo 'Creating Python virtual environment ".venv"...'
    python3 -m venv .venv
fi

echo 'Activating virtual environment...'
source .venv/bin/activate

echo 'Installing dependencies from "requirements.txt" into virtual environment (in quiet mode)...'
python -m pip --quiet --disable-pip-version-check install -r app/backend/requirements.txt