$ErrorActionPreference = "Stop"

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $here

# Install into a repo-local folder so we don't depend on system/user site-packages.
python -m pip install --upgrade -r requirements.txt -t .packages

Write-Host "Installed dependencies into .packages"
