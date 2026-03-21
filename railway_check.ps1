$env:PATH += ";C:\Users\Alexis\AppData\Local\Programs\railway"
Set-Location "C:\Users\Alexis\Documents\swarm-main"

Write-Host "=== Linking to distinguished-wonder ==="
& railway link --project "1afabeef-fb14-47ec-974f-26b92158fc28" --environment "b07b0204-16f5-4063-9a24-f3b6dfe45e53" 2>&1

Write-Host "`n=== Status ==="
& railway status --json 2>&1

Write-Host "`n=== Service status all ==="
& railway service status --all --json 2>&1
