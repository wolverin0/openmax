param(
    [Parameter(Mandatory=$true)][string]$SourceRoot,
    [Parameter(Mandatory=$true)][string]$GhidraHome,
    [Parameter(Mandatory=$true)][string]$JavaExe,
    [string]$PythonExe = 'python',
    [string]$RuntimeRoot = 'firmware/build/re1-20261010'
)
$ErrorActionPreference = 'Stop'
$re1Checkout = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '../../..')).Path
$re1Runtime = [IO.Path]::GetFullPath((Join-Path $re1Checkout $RuntimeRoot))
$re1Allowed = [IO.Path]::GetFullPath((Join-Path $re1Checkout 'firmware/build/'))
if (-not $re1Runtime.StartsWith($re1Allowed, [StringComparison]::OrdinalIgnoreCase)) {
    throw 'Runtime must remain under this checkout firmware/build'
}
$re1RunId = (Get-Date -Format 'yyyyMMdd-HHmmss-fff') + '-' + [Guid]::NewGuid().ToString('N').Substring(0, 8)
$re1Runtime = Join-Path $re1Runtime ('run-' + $re1RunId)
if (Test-Path -LiteralPath $re1Runtime) { throw 'Refusing to reuse an evidence directory' }
$re1Modules = Join-Path (Resolve-Path -LiteralPath $SourceRoot).Path 'firmware/build/codex-analysis-20261006/rootfs/lib/modules/2.6.32.68'
$re1Pinned = @{
    'ubnt_poll_host.ko' = '19f379b1a776603634e367d547eaabed20f705865cacaaef06193ac04bb70e14'
    'umac.ko' = '46525dc6f8b789bf820f0713841a2a9ecdcba833300ddb1ab1ef06fc4ab6a9c5'
}
function Assert-Re1Inputs {
    foreach ($re1Name in $re1Pinned.Keys) {
        if ((Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $re1Modules $re1Name)).Hash.ToLowerInvariant() -ne $re1Pinned[$re1Name]) {
            throw "Pinned input mismatch: $re1Name"
        }
    }
}
Assert-Re1Inputs
$re1Watch = [Diagnostics.Stopwatch]::StartNew()
New-Item -ItemType Directory -Force -Path $re1Runtime,(Join-Path $re1Runtime 'projects'),(Join-Path $re1Runtime 'profile/temp') | Out-Null
$re1GhidraResolved = (Resolve-Path -LiteralPath $GhidraHome).Path
$re1JavaResolved = (Resolve-Path -LiteralPath $JavaExe).Path
$re1Common = @(
    '-Djava.system.class.loader=ghidra.GhidraClassLoader', '-Djava.awt.headless=true', '-Xshare:off',
    ('-Dapplication.settingsdir=' + (Join-Path $re1Runtime 'profile/settings')),
    ('-Dapplication.cachedir=' + (Join-Path $re1Runtime 'profile/cache')),
    ('-Dapplication.tempdir=' + (Join-Path $re1Runtime 'profile/temp')),
    ('-Djava.io.tmpdir=' + (Join-Path $re1Runtime 'profile/temp')),
    '-Xmx2G', '-XX:ParallelGCThreads=2', '-XX:CICompilerCount=2', '-cp',
    (Join-Path $re1GhidraResolved 'Ghidra/Framework/Utility/lib/Utility.jar'),
    'ghidra.Ghidra', 'ghidra.app.util.headless.AnalyzeHeadless', (Join-Path $re1Runtime 'projects')
)
try {
    $re1HostArgs = @(('re1-host-' + $re1RunId), '-import', (Join-Path $re1Modules 'ubnt_poll_host.ko'),
        '-scriptPath', $PSScriptRoot, '-postScript', 'RE1Inspect.java', (Join-Path $re1Runtime 'host-ghidra.json'),
        '-analysisTimeoutPerFile', '180', '-max-cpu', '2')
    $re1Invocation = @{java=$re1JavaResolved;host_arguments=($re1Common + $re1HostArgs);java_sha256=(Get-FileHash -Algorithm SHA256 -LiteralPath $re1JavaResolved).Hash;ghidra_utility_sha256=(Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $re1GhidraResolved 'Ghidra/Framework/Utility/lib/Utility.jar')).Hash}
    $re1Invocation | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $re1Runtime 'invocation.json') -Encoding UTF8
    & $re1JavaResolved @re1Common @re1HostArgs *> (Join-Path $re1Runtime ('host-' + $re1RunId + '.log'))
    if ($LASTEXITCODE -ne 0) { throw "Host headless failed: $LASTEXITCODE" }
    if (-not (Test-Path -LiteralPath (Join-Path $re1Runtime 'host-ghidra.json'))) { throw 'Fresh host evidence missing' }
    & $PythonExe (Join-Path $PSScriptRoot 're1_pilot.py') --source-root $SourceRoot --runtime $re1Runtime --prepare-only
    if ($LASTEXITCODE -ne 0) { throw 'Host byte qualification failed' }
    $re1ApArgs = @(('re1-ap-' + $re1RunId), '-import', (Join-Path $re1Runtime 'ap-segment-00.bin'),
        '-loader', 'BinaryLoader', '-processor', 'Xtensa:LE:32:default', '-loader-baseAddr', '0x40b000',
        '-scriptPath', $PSScriptRoot, '-postScript', 'RE1Xtensa.java',
        (Join-Path $re1Runtime 'ap-import-manifest.json'), (Join-Path $re1Runtime 'ap-ghidra.json'),
        '-noanalysis', '-max-cpu', '2')
    $re1Invocation.ap_arguments = $re1Common + $re1ApArgs
    $re1Invocation.script_sha256 = @{}
    foreach ($re1Script in @('re1_pilot.py','RE1Inspect.java','RE1Xtensa.java','run_re1.ps1')) {
        $re1Invocation.script_sha256[$re1Script] = (Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $PSScriptRoot $re1Script)).Hash
    }
    $re1Invocation | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $re1Runtime 'invocation.json') -Encoding UTF8
    & $re1JavaResolved @re1Common @re1ApArgs *> (Join-Path $re1Runtime ('ap-' + $re1RunId + '.log'))
    if ($LASTEXITCODE -ne 0) { throw "AP headless failed: $LASTEXITCODE" }
    if (-not (Test-Path -LiteralPath (Join-Path $re1Runtime 'ap-ghidra.json'))) { throw 'Fresh AP evidence missing' }
    & $PythonExe (Join-Path $PSScriptRoot 're1_pilot.py') --source-root $SourceRoot --runtime $re1Runtime
    if ($LASTEXITCODE -ne 0) { throw 'Final byte/syntax qualification failed' }
    $re1Watch.Stop()
    $re1Invocation.elapsed_seconds = $re1Watch.Elapsed.TotalSeconds
    $re1Invocation | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $re1Runtime 'invocation.json') -Encoding UTF8
    Write-Output ('RE1 evidence: ' + $re1Runtime)
} finally { Assert-Re1Inputs }
