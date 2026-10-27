# One-copy offline notebook endpoint. No downloads or persistent policy changes.
[CmdletBinding()]
param([string]$BundleRoot, [switch]$ValidatePackageOnly, [ValidateSet('x86','x64')][string]$ValidateArchitecture)
$ErrorActionPreference = 'Stop'
if (-not $BundleRoot) { $BundleRoot = $PSScriptRoot }
. (Join-Path $PSScriptRoot 'notebook_core.ps1')
$failed = $false
$state = $null
$statusListener = $null
$mutex = $null
$locked = $false
$guardian = $null
$runDir = $null
try {
    if ($PSVersionTable.PSVersion.Major -lt 5) { throw 'Windows PowerShell 5 or later is required.' }
    if ($ValidateArchitecture -and -not $ValidatePackageOnly) { throw 'Architecture override is only allowed for offline package validation.' }
    $runtimeArchitecture = Get-FmxRuntimeArchitecture
    $BundleRoot = [IO.Path]::GetFullPath($BundleRoot)
    if ($ValidatePackageOnly) {
        $validationDir = Join-Path $env:TEMP ('FuturaMAX-validation-' + [guid]::NewGuid().ToString('N'))
        if ($ValidateArchitecture) { $runtimeArchitecture = $ValidateArchitecture }
        $validated = Copy-FmxRuntime $BundleRoot $validationDir -Architecture $runtimeArchitecture
        Write-Host "Offline runtime hashes: PASS. No network changes. Validated copy: $validated"
        return
    }
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = [Security.Principal.WindowsPrincipal]::new($identity)
    if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        Write-Host 'Windows will ask once for administrator permission to add temporary test rules.'
        $psExe = Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\powershell.exe'
        $argsText = '-NoProfile -ExecutionPolicy RemoteSigned -File "' + (Join-Path $PSScriptRoot 'start_notebook_server.ps1') + '" -BundleRoot "' + (Join-Path $BundleRoot '.') + '"'
        $elevated = Start-Process -FilePath $psExe -ArgumentList $argsText -Verb RunAs -Wait -PassThru
        exit $elevated.ExitCode
    }
    $mutex = [Threading.Mutex]::new($false, 'Global\FuturaMAX-NotebookBench-88ae1d73e1c3')
    try { $locked = $mutex.WaitOne(0) } catch [Threading.AbandonedMutexException] { $locked = $true }
    if (-not $locked) { throw 'Notebook helper already running; use its existing window.' }
    $runRoot = Initialize-FmxRunRoot
    Repair-FmxStaleRuns $runRoot
    $runId = [guid]::NewGuid().ToString('N')
    $runDir = Join-Path $runRoot $runId
    [IO.Directory]::CreateDirectory($runDir) | Out-Null
    foreach ($file in @('notebook_core.ps1','notebook_watchdog.ps1')) { Copy-Item -LiteralPath (Join-Path $PSScriptRoot $file) -Destination $runDir }
    Start-Transcript -LiteralPath (Join-Path $runDir 'console.log') -Force | Out-Null
    Write-Host "Diagnostics: $runDir"
    Write-Host "Selected Windows runtime: $runtimeArchitecture (automatic OS detection)."
    $exe = Copy-FmxRuntime $BundleRoot (Join-Path $runDir 'runtime') -Architecture $runtimeArchitecture
    $version = Start-Process -FilePath $exe -ArgumentList '--version' -WorkingDirectory (Split-Path $exe) -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $runDir 'version.txt') -RedirectStandardError (Join-Path $runDir 'version-error.txt')
    $null = $version.Handle
    if (-not $version.WaitForExit(10000)) { $version.Kill(); throw 'Bundled runtime did not respond within 10 seconds.' }
    if ($version.ExitCode -ne 0 -or (Get-Content -LiteralPath (Join-Path $runDir 'version.txt') -Raw) -notmatch 'iperf 3\.22') { throw 'Verified runtime cannot execute on this Windows installation. See version-error.txt.' }
    Write-Host 'Waiting up to 30 seconds for notebook Ethernet link/address...'
    $nic = $null
    for ($attempt = 0; $attempt -lt 15; $attempt++) {
        try { $nic = Select-FmxAdapter @(Get-NetAdapter) @(Get-NetIPAddress -AddressFamily IPv4); break }
        catch { if ($attempt -eq 14) { throw }; Start-Sleep -Seconds 2 }
    }
    $existing = @(Get-NetRoute -DestinationPrefix '192.168.1.155/32' -PolicyStore ActiveStore -ErrorAction SilentlyContinue)
    $reuse = $false
    if ($existing.Count) {
        if ($existing.Count -eq 1 -and $existing[0].InterfaceIndex -eq $nic.InterfaceIndex -and $existing[0].NextHop -eq '192.168.1.3') { $reuse = $true }
        else { throw 'Conflicting existing host route preserved. No network changes made.' }
    }
    foreach ($port in @(5201,5202)) {
        if (@(Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue).Count -or @(Get-NetUDPEndpoint -LocalPort $port -ErrorAction SilentlyContinue).Count) { throw "Port $port is already occupied. Existing service preserved." }
    }
    $psPath = (Get-FmxIdentity $PID).Path
    $state = [pscustomobject]@{
        Schema = 1; RunId = $runId; RunDirectory = $runDir; Owner = (Get-FmxIdentity $PID)
        DeadlineUtc = [DateTime]::UtcNow.AddHours(2).ToString('o'); Status = 'PREPARED'
        InterfaceIndex = $nic.InterfaceIndex; Alias = $nic.Alias; IPv4 = $nic.IPv4
        RuntimeArchitecture = $runtimeArchitecture
        Route = [pscustomobject]@{ CreatePlanned = (-not $reuse); Metric = (Get-Random -Minimum 43000 -Maximum 60000) }
        RuleNames = @("FMX-$runId-TCP", "FMX-$runId-UDP", "FMX-$runId-STATUS")
        Server = $null; Error = $null; Restarts = 0
    }
    $journal = Join-Path $runDir 'state.json'
    Write-FmxState $journal $state
    $guardianArgs = '-NoProfile -ExecutionPolicy RemoteSigned -File "' + (Join-Path $runDir 'notebook_watchdog.ps1') + '" -RunDirectory "' + $runDir + '"'
    $guardian = Start-Process -FilePath $psPath -ArgumentList $guardianArgs -WindowStyle Hidden -PassThru
    for ($i = 0; $i -lt 50 -and -not (Test-Path -LiteralPath (Join-Path $runDir 'guardian.json')); $i++) { Start-Sleep -Milliseconds 100 }
    if (-not (Test-Path -LiteralPath (Join-Path $runDir 'guardian.json'))) { throw 'Cleanup guardian failed to start; network unchanged.' }
    $guardianIdentity = Get-Content -LiteralPath (Join-Path $runDir 'guardian.json') -Raw | ConvertFrom-Json
    if ($guardianIdentity.Id -ne $guardian.Id -or -not (Test-FmxProcess $guardianIdentity)) { throw 'Cleanup guardian identity not valid; network unchanged.' }
    # Durable intent plus a live guardian precede all networking writes.
    if ($state.Route.CreatePlanned) { New-NetRoute -DestinationPrefix '192.168.1.155/32' -InterfaceIndex $nic.InterfaceIndex -NextHop '192.168.1.3' -RouteMetric $state.Route.Metric -PolicyStore ActiveStore | Out-Null }
    foreach ($protocol in @('TCP','UDP')) {
        New-NetFirewallRule -Name "FMX-$runId-$protocol" -DisplayName "FuturaMAX notebook $protocol" -Group $runId -Description $runDir -Direction Inbound -Action Allow -Protocol $protocol -LocalPort 5201 -LocalAddress $nic.IPv4 -RemoteAddress '192.168.1.155','192.168.1.3' -InterfaceAlias $nic.Alias -Program $exe -Profile Any | Out-Null
    }
    New-NetFirewallRule -Name "FMX-$runId-STATUS" -DisplayName 'FuturaMAX notebook status' -Group $runId -Description $runDir -Direction Inbound -Action Allow -Protocol TCP -LocalPort 5202 -LocalAddress $nic.IPv4 -RemoteAddress '192.168.1.155','192.168.1.3' -InterfaceAlias $nic.Alias -Program $psPath -Profile Any | Out-Null
    $statusListener = [Net.Sockets.TcpListener]::new([Net.IPAddress]::Parse($nic.IPv4), 5202)
    $statusListener.Start()
    $startNeeded = $true
    $printedReady = $false
    while ([DateTime]::UtcNow -lt [DateTime]::Parse($state.DeadlineUtc).ToUniversalTime()) {
        if (-not (Test-FmxProcess $guardianIdentity)) { throw 'Cleanup guardian exited; stopping safely.' }
        $nowNic = Select-FmxAdapter @(Get-NetAdapter) @(Get-NetIPAddress -AddressFamily IPv4)
        if ($nowNic.IPv4 -ne $nic.IPv4 -or $nowNic.InterfaceIndex -ne $nic.InterfaceIndex) { throw 'Ethernet address changed during test; stopping to avoid invalid measurements.' }
        if ($startNeeded) {
            $logStem = Join-Path $runDir ("iperf-$($state.Restarts)")
            $server = Start-Process -FilePath $exe -ArgumentList "-s -B $($nic.IPv4) -p 5201 --forceflush" -WorkingDirectory (Split-Path $exe) -WindowStyle Hidden -PassThru -RedirectStandardOutput "$logStem.out.log" -RedirectStandardError "$logStem.err.log"
            $null = $server.Handle
            try { $state.Server = Get-FmxIdentity $server.Id } catch { $state.Server = $null }
            Write-FmxState $journal $state
            $listening = $false
            for ($i = 0; $i -lt 25; $i++) {
                if (@(Get-NetTCPConnection -LocalAddress $nic.IPv4 -LocalPort 5201 -State Listen -ErrorAction SilentlyContinue | Where-Object { $_.OwningProcess -eq $server.Id }).Count) { $listening = $true; break }
                if ($server.HasExited) { break }
                Start-Sleep -Milliseconds 200
            }
            if (-not $listening) {
                if (Test-FmxProcess $state.Server) { Stop-Process -Id $state.Server.Id -Force }
                if ($state.Restarts -ge 2) { throw 'iperf failed three starts; all attempt logs retained.' }
                $state.Restarts++
                $state.Status = 'RETRYING'
                Write-FmxState $journal $state
                Write-Host "Server did not listen; automatic repair $($state.Restarts)/2."
                Start-Sleep -Seconds 1
                continue
            }
            $startNeeded = $false
            $state.Status = 'READY'
            Write-FmxState $journal $state
            if (-not $printedReady) {
                Write-Host "READY - notebook $($nic.IPv4):5201. Keep this window open." -ForegroundColor Green
                Write-Host 'No Internet needed. Press Q to stop and clean up. Maximum session: 2 hours.'
                Write-Host 'READY confirms a local listener, not yet a completed radio throughput test.'
                $printedReady = $true
            }
        }
        if (-not (Test-FmxProcess $state.Server)) {
            if ($state.Restarts -ge 2) { throw 'Server restart budget exhausted; logs retained.' }
            $state.Restarts++
            $state.Status = 'RETRYING'
            Write-FmxState $journal $state
            Write-Host "Server exited; automatic restart $($state.Restarts)/2."
            $startNeeded = $true
            continue
        }
        if ($statusListener.Pending()) {
            $client = $statusListener.AcceptTcpClient()
            try {
                $remote = $client.Client.RemoteEndPoint.Address.ToString()
                if ($remote -in @('192.168.1.155','192.168.1.3')) {
                    Send-FmxStatusResponse $client $state
                }
            } catch { Write-Warning 'Status reader disconnected.' } finally { $client.Close() }
        }
        if ([Console]::KeyAvailable -and [Console]::ReadKey($true).Key -eq 'Q') { break }
        Start-Sleep -Milliseconds 500
    }
} catch {
    $failed = $true
    Write-Host "STOPPED: $($_.Exception.Message)" -ForegroundColor Red
    if ($state) { $state.Error = $_.Exception.Message; $state.Status = 'FAILED'; Write-FmxState $journal $state }
    if ($runDir) { [IO.File]::WriteAllText((Join-Path $runDir 'failure.txt'), $_.ToString()); Write-Host "Diagnostics retained: $runDir" }
} finally {
    if ($statusListener) { $statusListener.Stop() }
    if ($state) {
        try {
            Stop-FmxResources $state
            $state.Status = 'CLEANED'
            Write-FmxState $journal $state
            Write-Host 'Owned server, firewall rules and temporary route cleaned up.'
        } catch { $failed = $true; Write-Warning "Cleanup incomplete: $($_.Exception.Message). Guardian/startup recovery will retry." }
        [IO.File]::WriteAllText((Join-Path $runDir 'stop'), 'stop')
    }
    if ($guardian) { $null = $guardian.WaitForExit(5000) }
    if ($locked) { $mutex.ReleaseMutex() }
    if ($mutex) { $mutex.Dispose() }
    if ($runDir) { try { Stop-Transcript | Out-Null } catch {} }
}
if ($failed) {
    Write-Host 'Setup could not finish safely. No security protections were disabled.'
    $null = Read-Host 'Press Enter to close (diagnostics remain saved)'
    exit 1
}
exit 0
