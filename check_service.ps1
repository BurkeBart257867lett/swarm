$env:PATH += ";C:\Users\Alexis\AppData\Local\Programs\railway"
Set-Location "C:\Users\Alexis\Documents\swarm-main"

$config = Get-Content "$env:USERPROFILE\.railway\config.json" | ConvertFrom-Json
$token = $config.user.token
$serviceId = "4f55d261-2235-4f89-9d6e-03f5da6b3eca"
$environmentId = "b07b0204-16f5-4063-9a24-f3b6dfe45e53"

# Get service source info
$q = @"
{
  "query": "{ serviceInstance(serviceId: \"$serviceId\", environmentId: \"$environmentId\") { source { repo image } startCommand } }"
}
"@

$resp = Invoke-WebRequest -Uri "https://backboard.railway.com/graphql/v2" `
  -Method POST `
  -Headers @{ "Authorization" = "Bearer $token"; "Content-Type" = "application/json" } `
  -Body $q -UseBasicParsing
Write-Host "Service instance:"
$resp.Content

# Get latest deployment
$q2 = @"
{
  "query": "{ deployments(input: { serviceId: \"$serviceId\", environmentId: \"$environmentId\" }, first: 1) { edges { node { id status createdAt meta } } } }"
}
"@
$resp2 = Invoke-WebRequest -Uri "https://backboard.railway.com/graphql/v2" `
  -Method POST `
  -Headers @{ "Authorization" = "Bearer $token"; "Content-Type" = "application/json" } `
  -Body $q2 -UseBasicParsing
Write-Host "`nLatest deployment meta:"
$resp2.Content | ConvertFrom-Json | ConvertTo-Json -Depth 6
