$env:PATH += ";C:\Users\Alexis\AppData\Local\Programs\railway"
Set-Location "C:\Users\Alexis\Documents\swarm-main"
Write-Host "=== whoami ==="
& railway whoami --json 2>&1
Write-Host "`n=== project list ==="
& railway project list --json 2>&1
Write-Host "`n=== status ==="
& railway status --json 2>&1
