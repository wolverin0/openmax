param([Parameter(Mandatory=$true)][string]$RunDirectory)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'notebook_core.ps1')
$journal = Join-Path $RunDirectory 'state.json'
try {
    $state = Get-Content -LiteralPath $journal -Raw | ConvertFrom-Json
    Write-FmxState (Join-Path $RunDirectory 'guardian.json') (Get-FmxIdentity $PID)
    while ((Test-FmxProcess $state.Owner) -and [DateTime]::UtcNow -lt [DateTime]::Parse($state.DeadlineUtc).ToUniversalTime() -and -not (Test-Path -LiteralPath (Join-Path $RunDirectory 'stop'))) { Start-Sleep -Seconds 1 }
    $state = Get-Content -LiteralPath $journal -Raw | ConvertFrom-Json
    Stop-FmxResources $state
    [IO.File]::WriteAllText((Join-Path $RunDirectory 'guardian-cleaned.txt'), [DateTime]::UtcNow.ToString('o'))
} catch {
    [IO.File]::WriteAllText((Join-Path $RunDirectory 'guardian-error.txt'), $_.ToString())
    exit 1
}
