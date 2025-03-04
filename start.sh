#!/bin/bash
pip install -r requirements.txt
waitress-serve --port=5000 app:app