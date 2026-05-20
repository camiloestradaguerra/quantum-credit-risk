@echo off
REM =========================================================================
REM SETUP SCRIPT - Quantum + Classical ML Environment
REM =========================================================================
REM This script sets up the Python virtual environment for the project
REM
REM Usage: setup.bat
REM
REM Prerequisites:
REM   - Python 3.10+ installed and in PATH
REM   - Windows environment
REM =========================================================================

echo ========================================================================
echo ENVIRONMENT SETUP - Quantum + Classical ML Project
echo ========================================================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://www.python.org/
    exit /b 1
)

echo.
echo [1/5] Creating virtual environment...
python -m venv venv_quantum_ml

if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    exit /b 1
)

echo SUCCESS: Virtual environment created

echo.
echo [2/5] Activating virtual environment...
call venv_quantum_ml\Scripts\activate.bat

if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    exit /b 1
)

echo SUCCESS: Virtual environment activated

echo.
echo [3/5] Upgrading pip, setuptools, wheel...
python -m pip install --upgrade pip setuptools wheel

if errorlevel 1 (
    echo ERROR: Failed to upgrade pip
    exit /b 1
)

echo SUCCESS: pip upgraded

echo.
echo [4/5] Installing dependencies from requirements.txt...
pip install -r .copilot_agentic_workspace\requirements.txt

if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    echo Check .copilot_agentic_workspace\requirements.txt for any issues
    exit /b 1
)

echo SUCCESS: All dependencies installed

echo.
echo [5/5] Verifying installation...

REM Verify key packages
python -c "import numpy; print(f'numpy {numpy.__version__}')" >nul 2>&1
if errorlevel 1 (
    echo ERROR: numpy verification failed
    exit /b 1
)

python -c "import pandas; print(f'pandas {pandas.__version__}')" >nul 2>&1
if errorlevel 1 (
    echo ERROR: pandas verification failed
    exit /b 1
)

python -c "import sklearn; print(f'scikit-learn {sklearn.__version__}')" >nul 2>&1
if errorlevel 1 (
    echo ERROR: scikit-learn verification failed
    exit /b 1
)

python -c "import xgboost; print(f'xgboost {xgboost.__version__}')" >nul 2>&1
if errorlevel 1 (
    echo ERROR: xgboost verification failed
    exit /b 1
)

python -c "import qiskit; print(f'qiskit {qiskit.__version__}')" >nul 2>&1
if errorlevel 1 (
    echo WARNING: qiskit verification failed - Quantum support may be limited
) else (
    echo SUCCESS: qiskit verified
)

echo SUCCESS: All verifications passed

echo.
echo ========================================================================
echo ENVIRONMENT SETUP COMPLETE
echo ========================================================================
echo.
echo To activate the environment in future sessions, run:
echo   venv_quantum_ml\Scripts\activate.bat
echo.
echo To deactivate, run:
echo   deactivate
echo.
echo Next steps:
echo   1. Run outlier analysis: python .copilot_agentic_workspace\scripts\outlier_analysis.py
echo   2. Run classical ML pipeline: python .copilot_agentic_workspace\scripts\1_classical_ml_pipeline.py
echo   3. Run quantum ML pipeline: python .copilot_agentic_workspace\scripts\2_quantum_ml_pipeline.py
echo.
echo ========================================================================

pause
