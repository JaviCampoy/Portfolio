@echo off
echo ******   EXECUTING BLACK   ******
black . --exclude virtual_environment
echo ******   EXECUTING ISORT   ******
isort . --skip-glob virtual_environment
echo ******   EXECUTING PYLINT   ******
pylint . --ignore=virtual_environment
pylint backend
echo ******   EXECUTING MYPY   ******
mypy . --exclude virtual_environment
echo ******   EXECUTING PYTEST   ******
pytest --cov . tests/
REM --cov-report html