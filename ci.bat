@echo off
set "PROYECT_PATH=%~dp0"
set "PYTHONPATH=%PROYECT_PATH%;%PYTHONPATH%"

echo ******   EXECUTING BLACK   ******
black . --exclude virtual_environment
echo ******   EXECUTING ISORT   ******
isort . --skip-glob virtual_environment
echo ******   EXECUTING PYLINT   ******
pylint src --ignore=virtual_environment
pylint tests --ignore=virtual_environment  
pylint main.py --ignore=virtual_environment
echo ******   EXECUTING MYPY   ******
mypy . --exclude virtual_environment
echo ******   EXECUTING PYTEST   ******
pytest --cov tests/
REM --cov-report html