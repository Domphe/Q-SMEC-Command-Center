# Q-SMEC Command Center — Windows Startup Script
# Run as Administrator via Task Scheduler at logon
#
# 1. Gets current WSL2 IP address
# 2. Updates the port proxy rule (port 8000)
# 3. Starts the uvicorn server inside WSL

$ErrorActionPreference = "Continue"
$LogFile = "E:\Data1\Q-SMEC-Command-Center\startup.log"

function Write-Log($msg) {
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$ts  $msg" | Out-File -Append -FilePath $LogFile
}

Write-Log "=== Q-SMEC Command Center startup ==="

# Step 1: Get current WSL2 IP
$wslIp = (wsl -d Ubuntu-22.04 -- hostname -I).Trim().Split(" ")[0]
if (-not $wslIp) {
    Write-Log "ERROR: Could not get WSL IP"
    exit 1
}
Write-Log "WSL IP: $wslIp"

# Step 2: Remove old port proxy and add new one
netsh interface portproxy delete v4tov4 listenport=8000 listenaddress=0.0.0.0 2>$null
netsh interface portproxy add v4tov4 listenport=8000 listenaddress=0.0.0.0 connectport=8000 connectaddress=$wslIp
Write-Log "Port proxy updated: 0.0.0.0:8000 -> ${wslIp}:8000"

# Step 3: Start the server inside WSL
wsl -d Ubuntu-22.04 -- bash /mnt/e/Data1/Q-SMEC-Command-Center/scripts/start-server.sh
Write-Log "Server start triggered"

# Step 4: Wait and verify
Start-Sleep -Seconds 5
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/api/health" -TimeoutSec 5
    Write-Log "Health check: $($health.status) (v$($health.version))"
} catch {
    Write-Log "WARNING: Health check failed — server may still be starting"
}

Write-Log "=== Startup complete ==="
