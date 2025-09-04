@echo off
echo Activating AI Object Counting System Virtual Environment...
cd backend
call venv\Scripts\activate
echo.
echo SUCCESS: Virtual environment activated!
echo You can now run:
echo    - python app.py (to start backend)
echo    - python test_mysql_connection_fixed.py (to test MySQL)
echo    - python setup_mysql.py (to setup databases)
echo.
cmd /k
