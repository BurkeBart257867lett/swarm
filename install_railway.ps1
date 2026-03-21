$resp = Invoke-WebRequest -Uri 'https://api.github.com/repos/railwayapp/cli/releases/latest' -UseBasicParsing
$json = $resp.Content | ConvertFrom-Json
$asset = $json.assets | Where-Object { $_.name -like '*x86_64-pc-windows-msvc.zip' } | Select-Object -First 1
Write-Host "Downloading: $($asset.name)"
$zip = "$env:TEMP\railway_x64.zip"
Invoke-WebRequest -Uri $asset.browser_download_url -OutFile $zip -UseBasicParsing
$dest = "C:\Users\Alexis\AppData\Local\Programs\railway"
New-Item -ItemType Directory -Force -Path $dest | Out-Null
Expand-Archive -Path $zip -DestinationPath $dest -Force
Write-Host "Installed to $dest"
& "$dest\railway.exe" --version
