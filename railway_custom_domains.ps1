$env:PATH += ";C:\Users\Alexis\AppData\Local\Programs\railway"
Set-Location "C:\Users\Alexis\Documents\swarm-main"

Write-Host "=== Adding redacted.meme to redacted-website ==="
& railway domain --service "redacted-website" --json "redacted.meme" 2>&1

Write-Host "`n=== Adding terminal.redacted.meme to REDACTED-AI ==="
& railway domain --service "REDACTED-AI" --json "terminal.redacted.meme" 2>&1
