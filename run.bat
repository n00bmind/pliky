@echo off
pushd %~dp0
call activate.bat
python main.py D:\!2K_Games\volt_dev
deactivate
popd
