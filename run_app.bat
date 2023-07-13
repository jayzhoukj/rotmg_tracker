@echo off
:: Set path to Miniconda
set ana_path=C:\Users\%USERNAME%\miniconda3
:: Activate Anaconda Prompt (Miniconda) in Windows
call %ana_path%\Scripts\activate.bat
:: Activate Miniconda virtual environment
call conda activate rotmg_server_tracker
:: Launch Streamlit app
echo Start Time: %Time%
echo Starting Streamlit app...
call streamlit run app.py
echo Streamlit app terminated!
echo Finish Time: %Time
pause