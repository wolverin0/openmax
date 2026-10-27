# Real pinned binary smoke test on loopback only. No elevation or network configuration.
param([string]$BundleRoot, [string]$OutputRoot, [ValidateSet('x86','x64')][string]$Architecture)
$ErrorActionPreference = 'Stop'
if (-not $BundleRoot) { $BundleRoot = $PSScriptRoot }
if (-not $OutputRoot) { $OutputRoot = Join-Path $PSScriptRoot '..\..\artifacts' }
. (Join-Path $PSScriptRoot 'notebook_core.ps1')
if (-not $Architecture) { $Architecture = Get-FmxRuntimeArchitecture }
$resultDir = [IO.Path]::GetFullPath((Join-Path $OutputRoot ('notebook-loopback-' + [guid]::NewGuid().ToString('N'))))
[IO.Directory]::CreateDirectory($resultDir) | Out-Null
$serverIdentity = $null
$clientIdentity = $null
try {
    $exe = Copy-FmxRuntime $BundleRoot (Join-Path $resultDir 'runtime') -Architecture $Architecture
    Write-Host "Testing $Architecture runtime; PowerShell process is64bit=$([Environment]::Is64BitProcess)."
    $reservation = [Net.Sockets.TcpListener]::new([Net.IPAddress]::Loopback, 0)
    $reservation.Start()
    $port = $reservation.LocalEndpoint.Port
    $reservation.Stop()
    $server = Start-Process -FilePath $exe -ArgumentList "-s -B 127.0.0.1 -p $port --forceflush" -WindowStyle Hidden -PassThru -WorkingDirectory (Split-Path $exe) -RedirectStandardOutput (Join-Path $resultDir 'server.out.log') -RedirectStandardError (Join-Path $resultDir 'server.err.log')
    $serverIdentity = Get-FmxIdentity $server.Id
    $ready = $false
    for ($i = 0; $i -lt 25; $i++) {
        if (@(Get-NetTCPConnection -LocalAddress '127.0.0.1' -LocalPort $port -State Listen -ErrorAction SilentlyContinue | Where-Object { $_.OwningProcess -eq $server.Id }).Count) { $ready = $true; break }
        Start-Sleep -Milliseconds 200
    }
    if (-not $ready) { throw 'Loopback server did not listen.' }
    foreach ($direction in @('forward','reverse')) {
        $jsonPath = Join-Path $resultDir "$direction.json"
        $arguments = "-c 127.0.0.1 -p $port -t 1 -J"
        if ($direction -eq 'reverse') { $arguments += ' -R' }
        $client = Start-Process -FilePath $exe -ArgumentList $arguments -WindowStyle Hidden -PassThru -WorkingDirectory (Split-Path $exe) -RedirectStandardOutput $jsonPath -RedirectStandardError (Join-Path $resultDir "$direction.err.log")
        $null = $client.Handle
        $clientIdentity = Get-FmxIdentity $client.Id
        if (-not $client.WaitForExit(15000)) { throw 'Loopback client timeout.' }
        $result = Get-Content -LiteralPath $jsonPath -Raw | ConvertFrom-Json
        if ($client.ExitCode -ne 0 -or $result.error -or $result.end.sum_received.bytes -le 0) { throw "Loopback $direction failed." }
        Write-Host "PASS: actual pinned iperf3 loopback $direction transferred $($result.end.sum_received.bytes) bytes."
    }
} finally {
    foreach ($id in @($clientIdentity,$serverIdentity)) { if (Test-FmxProcess $id) { Stop-Process -Id $id.Id -Force } }
    Write-Host "Evidence retained: $resultDir"
}
if (Test-FmxProcess $serverIdentity) { throw 'Owned loopback server remained alive.' }
Write-Host 'PASS: owned loopback server stopped. This is not notebook or RF acceptance.'
