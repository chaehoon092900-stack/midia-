@echo off
title Broadcast Console Server
echo Starting Broadcast Console Server...
python -m pip install flask requests --quiet
start http://localhost:5000
python server.py
pause
