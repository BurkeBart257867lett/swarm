$env:PATH += ";C:\Users\Alexis\AppData\Local\Programs\railway"
Set-Location "C:\Users\Alexis\Documents\swarm-main\website"

Write-Host "=== Fresh build deploy from website/ ==="
& railway up --detach --service "redacted-website" -m "Fix start command: use serve:app" 2>&1
