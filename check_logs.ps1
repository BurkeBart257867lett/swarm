$env:PATH += ";C:\Users\Alexis\AppData\Local\Programs\railway"
Set-Location "C:\Users\Alexis\Documents\swarm-main"
Start-Sleep -Seconds 35
Write-Host "=== Logs for redacted-website ==="
& railway logs --service "redacted-website" --lines 20 2>&1
