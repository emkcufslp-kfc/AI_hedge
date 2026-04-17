$ErrorActionPreference = "Stop"

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $here

$env:PYTHONPATH = (Join-Path $here ".packages")

python -m streamlit run streamlit_app.py
