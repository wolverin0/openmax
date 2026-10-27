# Conventional HTTP clients against the real response helper on loopback only.
# Never imports/runs the main helper, elevates, or changes routes/firewall rules.
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$fixtureRoot = Join-Path ([IO.Path]::GetTempPath()) ('FuturaMAX-status-fixture-' + [guid]::NewGuid().ToString('N'))
[IO.Directory]::CreateDirectory($fixtureRoot) | Out-Null
$readyFile = Join-Path $fixtureRoot 'ready.json'
$corePath = Join-Path $PSScriptRoot 'notebook_core.ps1'
$job = $null
try {
    $job = Start-Job -ArgumentList $corePath, $readyFile -ScriptBlock {
        param($CorePath, $ReadyFile)
        $ErrorActionPreference = 'Stop'
        . $CorePath
        $listener = [Net.Sockets.TcpListener]::new([Net.IPAddress]::Loopback, 0)
        try {
            $listener.Start()
            [IO.File]::WriteAllText($ReadyFile, (@{ Port=$listener.LocalEndpoint.Port } | ConvertTo-Json))
            $state = [pscustomobject]@{ Schema=1; Status='READY'; IPv4='192.168.1.171'; RunId='loopback-fixture-only' }
            for ($requestIndex = 0; $requestIndex -lt 2; $requestIndex++) {
                $pending = $listener.AcceptTcpClientAsync()
                if (-not $pending.Wait(8000)) { throw 'Loopback HTTP fixture accept timeout.' }
                $client = $pending.Result
                try { Send-FmxStatusResponse $client $state }
                finally { $client.Close() }
            }
            'Loopback HTTP requests served: 2'
        } finally { $listener.Stop() }
    }
    $readyDeadline = [DateTime]::UtcNow.AddSeconds(10)
    while (-not (Test-Path -LiteralPath $readyFile) -and [DateTime]::UtcNow -lt $readyDeadline -and $job.State -eq 'Running') {
        Start-Sleep -Milliseconds 100
    }
    if (-not (Test-Path -LiteralPath $readyFile)) { throw 'Loopback HTTP fixture did not become ready.' }
    $port = (Get-Content -LiteralPath $readyFile -Raw | ConvertFrom-Json).Port
    $uri = 'http://127.0.0.1:' + $port + '/status'
    $web = Invoke-WebRequest -UseBasicParsing -Uri $uri -Method Get -TimeoutSec 5
    if ($web.StatusCode -ne 200) { throw 'Invoke-WebRequest HTTP status is not 200.' }
    if ($web.Headers['Content-Type'] -notlike 'application/json*') { throw 'Invoke-WebRequest response is not JSON.' }
    $first = $web.Content | ConvertFrom-Json
    if ($first.Status -ne 'READY' -or $first.IPv4 -ne '192.168.1.171') { throw 'Invoke-WebRequest returned wrong status/address.' }
    Write-Output 'PASS: conventional Invoke-WebRequest GET /status returns 200 JSON READY and expected IPv4'
    $second = Invoke-RestMethod -Uri $uri -Method Get -TimeoutSec 5
    if ($second.Status -ne 'READY' -or $second.IPv4 -ne '192.168.1.171') { throw 'Invoke-RestMethod returned wrong status/address.' }
    Write-Output 'PASS: conventional Invoke-RestMethod GET /status parses READY and expected IPv4'
    $completed = Wait-Job -Job $job -Timeout 10
    if ($null -eq $completed -or $job.State -ne 'Completed') {
        Receive-Job -Job $job -ErrorAction Continue
        throw 'Loopback HTTP fixture did not complete successfully.'
    }
    Receive-Job -Job $job
    Write-Output 'Conventional loopback status cases passed: 2'
} finally {
    # Stop/remove this one owned background job only; never select by name.
    if ($null -ne $job) {
        if ($job.State -eq 'Running') { Stop-Job -Job $job }
        Remove-Job -Job $job -Force
    }
    $resolvedFixture = [IO.Path]::GetFullPath($fixtureRoot)
    $resolvedTemp = [IO.Path]::GetFullPath([IO.Path]::GetTempPath())
    if (-not $resolvedFixture.StartsWith($resolvedTemp, [StringComparison]::OrdinalIgnoreCase) -or (Split-Path $resolvedFixture -Leaf) -notlike 'FuturaMAX-status-fixture-*') {
        throw 'Status fixture cleanup target validation failed.'
    }
    [IO.Directory]::Delete($resolvedFixture, $true)
}
