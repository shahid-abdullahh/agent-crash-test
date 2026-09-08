# ==============================================================================
# Agent Crash Test — Demo State Reset Script (Windows PowerShell)
# ==============================================================================
Write-Host ">>> Resetting Agent Crash Test Demo State..." -ForegroundColor Cyan

$baseUrl = "http://127.0.0.1:8000"
try {
    $res = Invoke-RestMethod -Uri "$baseUrl/admin/demo/reset" -Method Post
    Write-Host "Sandbox state and demo runs reset successfully!" -ForegroundColor Green
    Write-Host ($res | ConvertTo-Json) -ForegroundColor Gray
} catch {
    Write-Host "Failed to reset demo state. Ensure backend server is running on $baseUrl" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor DarkRed
}
