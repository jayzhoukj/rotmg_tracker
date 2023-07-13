@echo off
:: Set path to Miniconda
set ana_path=C:\Users\%USERNAME%\miniconda3
:: Activate Anaconda Prompt (Miniconda) in Windows
call %ana_path%\Scripts\activate.bat
:: Activate Miniconda virtual environment
call conda activate rotmg_server_tracker
:: Generate requirements.txt
echo Start Time: %Time%
call pip freeze > requirements.txt
echo Finish Time: %Time
pause