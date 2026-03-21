$env:PATH += ";C:\Users\Alexis\AppData\Local\Programs\railway"
Set-Location "C:\Users\Alexis\Documents\swarm-main"

$config = Get-Content "$env:USERPROFILE\.railway\config.json" | ConvertFrom-Json
$token = $config.user.token
$serviceId = "4f55d261-2235-4f89-9d6e-03f5da6b3eca"
$environmentId = "b07b0204-16f5-4063-9a24-f3b6dfe45e53"

# Get latest deployment details including startCommand
$q = @"
{
  "query": "{ deployments(input: { serviceId: \"$serviceId\", environmentId: \"$environmentId\" }, first: 1) { edges { node { id status createdAt meta canRedeploy } } } }"
}
"@

$resp = Invoke-WebRequest -Uri "https://backboard.railway.com/graphql/v2" `
  -Method POST `
  -Headers @{ "Authorization" = "Bearer $token"; "Content-Type" = "application/json" } `
  -Body $q -UseBasicParsing
Write-Host "Latest deployment:"
$resp.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
