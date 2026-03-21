$resp = Invoke-WebRequest -Uri "https://redacted-website-production.up.railway.app/" -UseBasicParsing
Write-Host "Status: $($resp.StatusCode)"
if ($resp.Content -match "Pattern Blue MemeFi") {
    Write-Host "PASS: Website title found"
} else {
    Write-Host "FAIL: Expected website not found"
}
if ($resp.Content -match "terminal.redacted.meme") {
    Write-Host "PASS: Terminal URL present"
} else {
    Write-Host "FAIL: Terminal URL not found"
}
if ($resp.Content -match "localhost") {
    Write-Host "FAIL: localhost links still present!"
} else {
    Write-Host "PASS: No localhost links"
}
