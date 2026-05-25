#!/usr/bin/env bash
set -e
echo "------ START SCRIPT ------"
echo "Date: $(date)"
echo "PWD: $(pwd)"
echo "Listing files:"
ls -la
echo "Python executable: $(which python || which python3 || true)"
python -V || python3 -V || true
echo "Pip freeze:" 
pip freeze || true
echo "Uvicorn version:"
python -c "import uvicorn, sys; print(uvicorn.__version__)" || python3 -c "import uvicorn, sys; print(uvicorn.__version__)" || true
echo "Environment variables (filtered):"
env | egrep -i 'PORT|PATH|PYTHON|N8N|LLM' || true
echo "Starting uvicorn..."
exec python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
