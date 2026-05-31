# TRoyAI E-Otomation Agency — Cloudflare Deploy Script
# Usage: .\scripts\deploy.ps1 -ApiEmail "troyaiagent@gmail.com" -ApiKey "cfk_..." -AgentApiKey "TRoy-..."

param(
    [string]$ApiEmail = "troyaiagent@gmail.com",
    [string]$ApiKey,
    [string]$AgentApiKey
)

$ACCOUNT_ID = "7f9d6ab3d14d37e9fc6f4cec7527a94a"
$D1_DB_ID   = "877c18a3-dedb-4299-9207-f999b5a0626f"
$WORKER     = "eotomation-api"
$SITE       = "troyaiagent-site"
$DASHBOARD  = "troyaiagent-dashboard"

$AuthHeaders = @("X-Auth-Email: $ApiEmail", "X-Auth-Key: $ApiKey")

Write-Host "`n=== TRoyAI Deploy ===" -ForegroundColor Yellow

# --- D1 Schema ---
Write-Host "`n[1/4] Applying D1 schema..." -ForegroundColor Cyan
$schemaContent = Get-Content "$PSScriptRoot\..\worker\schema.sql" -Raw
$schemaB64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($schemaContent))
$body = @{ sql = $schemaContent } | ConvertTo-Json
$result = curl.exe -s -X POST `
    -H "X-Auth-Email: $ApiEmail" -H "X-Auth-Key: $ApiKey" `
    -H "Content-Type: application/json" `
    -d $body `
    "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/d1/database/$D1_DB_ID/query"
Write-Host $result

# --- Worker ---
Write-Host "`n[2/4] Deploying Worker..." -ForegroundColor Cyan
$scriptFile = Resolve-Path "$PSScriptRoot\..\worker\index.js"
$metaJson = '{"main_module":"index.js"}'
$metaFile = [System.IO.Path]::GetTempFileName() + ".json"
Set-Content -Path $metaFile -Value $metaJson -Encoding UTF8

curl.exe -s -X PUT `
    -H "X-Auth-Email: $ApiEmail" -H "X-Auth-Key: $ApiKey" `
    -F "index.js=@$scriptFile;filename=index.js;type=application/javascript+module" `
    -F "metadata=$metaJson;type=application/json" `
    "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/workers/scripts/$WORKER"

# Set secret
$secretBody = @{ name = "AGENT_API_KEY"; text = $AgentApiKey; type = "secret_text" } | ConvertTo-Json
curl.exe -s -X PUT `
    -H "X-Auth-Email: $ApiEmail" -H "X-Auth-Key: $ApiKey" `
    -H "Content-Type: application/json" -d $secretBody `
    "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/workers/scripts/$WORKER/secrets"

Write-Host "Worker deployed."

# --- Site (Pages) ---
Write-Host "`n[3/4] Deploying marketing site..." -ForegroundColor Cyan
$siteFile = Resolve-Path "$PSScriptRoot\..\site\index.html"
$siteHash = (Get-FileHash $siteFile -Algorithm SHA256).Hash.ToLower().Substring(0,32)
$manifest = "{`"index.html`":`"$siteHash`"}"
$manifestFile = [System.IO.Path]::GetTempFileName() + ".json"
Set-Content -Path $manifestFile -Value $manifest -Encoding UTF8

curl.exe -s --http1.1 --no-keepalive -X POST `
    -H "X-Auth-Email: $ApiEmail" -H "X-Auth-Key: $ApiKey" `
    -F "manifest=<$manifestFile;type=application/json" `
    -F "index.html=@$siteFile;filename=index.html;type=text/html" `
    "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/pages/projects/$SITE/deployments"

Write-Host "Site deployed."

# --- Dashboard (Pages) ---
Write-Host "`n[4/4] Deploying dashboard..." -ForegroundColor Cyan
$dashFiles = @("index.html", "style.css", "app.js")
$manifestObj = @{}
$formArgs = @()

foreach ($f in $dashFiles) {
    $fp = Resolve-Path "$PSScriptRoot\..\dashboard\$f"
    $hash = (Get-FileHash $fp -Algorithm SHA256).Hash.ToLower().Substring(0,32)
    $manifestObj[$f] = $hash
    $mime = if ($f -like "*.css") { "text/css" } elseif ($f -like "*.js") { "application/javascript" } else { "text/html" }
    $formArgs += "-F"
    $formArgs += "$f=@$fp;filename=$f;type=$mime"
}

$dashManifest = ($manifestObj | ConvertTo-Json -Compress)
$dashManifestFile = [System.IO.Path]::GetTempFileName() + ".json"
Set-Content -Path $dashManifestFile -Value $dashManifest -Encoding UTF8

curl.exe -s --http1.1 --no-keepalive -X POST `
    -H "X-Auth-Email: $ApiEmail" -H "X-Auth-Key: $ApiKey" `
    -F "manifest=<$dashManifestFile;type=application/json" `
    @formArgs `
    "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/pages/projects/$DASHBOARD/deployments"

Write-Host "Dashboard deployed."
Write-Host "`n=== Deploy complete ===" -ForegroundColor Green
Write-Host "  Site:      https://troyaiagent.com"
Write-Host "  Dashboard: https://dashboard.troyaiagent.com"
Write-Host "  API:       https://api.troyaiagent.com/api/health"
