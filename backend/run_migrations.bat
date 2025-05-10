@echo off
echo Running database migrations...

REM Activate virtual environment if it exists
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

REM Run migrations
alembic upgrade head

REM Check if migrations were successful
if %ERRORLEVEL% EQU 0 (
    echo Migrations completed successfully
) else (
    echo Error running migrations
    exit /b 1
) 