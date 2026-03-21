$env:PATH += ";C:\Users\Alexis\AppData\Local\Programs\railway"
Set-Location "C:\Users\Alexis\Documents\swarm-main"

Write-Host "=== Deployment logs (redacted-website) ==="
& railway logs --service "redacted-website" --lines 30 2>&1

Write-Host "`n=== Add redacted.meme domain to redacted-website ==="
& railway domain --service "redacted-website" 2>&1

Write-Host "`n=== Add terminal.redacted.meme domain to REDACTED-AI ==="
& railway domain --service "REDACTED-AI" 2>&1
