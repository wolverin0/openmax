# Behavioral fixture checks: no live adapters, routes, rules, processes or UAC.
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
. (Join-Path $PSScriptRoot 'notebook_core.ps1')
$script:Passed = 0
function Assert-Fmx([bool]$Condition, [string]$Message) {
    if (-not $Condition) { throw "ASSERTION FAILED: $Message" }
}
function Test-FmxCase([string]$Name, [scriptblock]$Body) {
    & $Body
    $script:Passed++
    Write-Output "PASS: $Name"
}
function Assert-FmxThrows([scriptblock]$Body, [string]$Message) {
    $caught = $false
    try { & $Body | Out-Null } catch { $caught = $true }
    Assert-Fmx $caught $Message
}
function New-FmxAddress([string]$IP) {
    [pscustomobject]@{ InterfaceIndex = 7; IPAddress = $IP; AddressState = 'Preferred'; PrefixLength = 24 }
}
$adapter = [pscustomobject]@{ InterfaceIndex = 7; ifIndex = 7; Name = 'Lab Ethernet'; MacAddress = '88-AE-1D-73-E1-C3'; Status = 'Up' }
Test-FmxCase 'adapter allows changed DHCP address' {
    $selected = Select-FmxAdapter @($adapter) @(New-FmxAddress '192.168.1.171')
    Assert-Fmx ($selected.InterfaceIndex -eq 7 -and $selected.IPv4 -eq '192.168.1.171') 'Must select unique Ethernet MAC with current DHCP IP.'
}
Test-FmxCase 'adapter refuses wrong MAC' {
    $wrong = [pscustomobject]@{ InterfaceIndex = 7; ifIndex = 7; Name = 'Lab'; MacAddress = '00-00-00-00-00-01'; Status = 'Up' }
    Assert-FmxThrows { Select-FmxAdapter @($wrong) @(New-FmxAddress '192.168.1.171') } 'Wrong adapter MAC must fail closed.'
}
Test-FmxCase 'adapter refuses ambiguous usable addresses' {
    Assert-FmxThrows { Select-FmxAdapter @($adapter) @((New-FmxAddress '192.168.1.171'), (New-FmxAddress '192.168.1.172')) } 'Two usable IPv4 addresses must fail closed.'
}
Test-FmxCase 'adapter refuses down interface' {
    $down = [pscustomobject]@{ InterfaceIndex = 7; ifIndex = 7; Name = 'Lab'; MacAddress = $adapter.MacAddress; Status = 'Down' }
    Assert-FmxThrows { Select-FmxAdapter @($down) @(New-FmxAddress '192.168.1.171') } 'Down adapter must fail closed.'
}
Test-FmxCase 'adapter refuses reserved and nonbench addresses' {
    foreach ($ip in @('192.168.1.2', '192.168.1.3', '192.168.1.155', '192.168.1.0', '192.168.1.255', '10.0.0.171')) {
        Assert-FmxThrows { Select-FmxAdapter @($adapter) @(New-FmxAddress $ip) } "Reserved/nonbench IP $ip must fail closed."
    }
}

# Process cmdlets are mocked before any process-identity or cleanup tests.
$script:FakeProcesses = @{}
$script:StoppedProcesses = @()
function Get-Process {
    param([int]$Id, [string]$Name, [string]$ErrorAction)
    if ($Name) { return @($script:FakeProcesses.Values | Where-Object { $_.Path -like '*\iperf3.exe' }) }
    if ($script:FakeProcesses.ContainsKey($Id)) { return $script:FakeProcesses[$Id] }
    return $null
}
function Stop-Process {
    param([int]$Id, $InputObject, [switch]$Force, [string]$ErrorAction)
    if ($InputObject) { $Id = $InputObject.Id }
    $script:StoppedProcesses += $Id
    $script:FakeProcesses.Remove($Id)
}
$fakeStart = [DateTime]::new(2026, 10, 6, 12, 0, 0)
$identity = [pscustomobject]@{ Id = 901; StartTicks = $fakeStart.ToUniversalTime().Ticks.ToString(); Path = 'C:\Fixture only\iperf3.exe' }
$script:FakeProcesses[901] = [pscustomobject]@{ Id = 901; StartTime = $fakeStart; Path = $identity.Path }
Test-FmxCase 'process identity accepts exact ID birth and path' {
    Assert-Fmx (Test-FmxProcess $identity) 'Exact process identity should match.'
}
Test-FmxCase 'process identity refuses reused PID' {
    $reused = [pscustomobject]@{ Id = 901; StartTicks = ($fakeStart.ToUniversalTime().Ticks + 1).ToString(); Path = $identity.Path }
    Assert-Fmx (-not (Test-FmxProcess $reused)) 'Same PID with different creation ticks must not match.'
}
Test-FmxCase 'process identity refuses wrong executable path' {
    $wrong = [pscustomobject]@{ Id = 901; StartTicks = $identity.StartTicks; Path = 'C:\Another process\iperf3.exe' }
    Assert-Fmx (-not (Test-FmxProcess $wrong)) 'Same PID and creation time with different path must not match.'
}
Test-FmxCase 'process identity refuses missing PID' {
    $missing = [pscustomobject]@{ Id = 902; StartTicks = $identity.StartTicks; Path = $identity.Path }
    Assert-Fmx (-not (Test-FmxProcess $missing)) 'Missing PID must not match.'
}

$script:FakeRules = @{}
$script:FakeRoutes = @()
$script:RemovedRules = @()
$script:RemovedRoutes = @()
function Get-NetFirewallRule {
    param([string]$Name, [string]$ErrorAction)
    if ($script:FakeRules.ContainsKey($Name)) { $script:FakeRules[$Name] }
}
function Remove-NetFirewallRule {
    [CmdletBinding()]
    param([Parameter(ValueFromPipeline)]$InputObject)
    process { $script:RemovedRules += $InputObject.Name; $script:FakeRules.Remove($InputObject.Name) }
}
function Get-NetRoute {
    param([string]$DestinationPrefix, [string]$PolicyStore, [string]$ErrorAction)
    $script:FakeRoutes
}
function Remove-NetRoute {
    [CmdletBinding(SupportsShouldProcess)]
    param([Parameter(ValueFromPipeline)]$InputObject)
    process {
        $script:RemovedRoutes += $InputObject.Id
        $script:FakeRoutes = @($script:FakeRoutes | Where-Object { $_.Id -ne $InputObject.Id })
    }
}
$runDir = 'C:\Fixture only\owned unique run'
$ownedExe = Join-Path $runDir 'runtime\iperf3.exe'
$state = [pscustomobject]@{
    RunId = 'fixture-run'; RunDirectory = $runDir; InterfaceIndex = 7
    Server = [pscustomobject]@{ Id = 903; StartTicks = $identity.StartTicks; Path = $ownedExe }
    RuleNames = @('fixture-TCP', 'fixture-UDP')
    Route = [pscustomobject]@{ CreatePlanned = $true; Metric = 32123 }
}
$script:FakeProcesses[903] = [pscustomobject]@{ Id = 903; StartTime = $fakeStart; Path = $ownedExe }
$script:FakeProcesses[904] = [pscustomobject]@{ Id = 904; StartTime = $fakeStart; Path = $ownedExe }
$script:FakeProcesses[905] = [pscustomobject]@{ Id = 905; StartTime = $fakeStart; Path = 'C:\Foreign\iperf3.exe' }
foreach ($name in $state.RuleNames) {
    $script:FakeRules[$name] = [pscustomobject]@{ Name = $name; Group = $state.RunId; Description = $state.RunDirectory }
}
$script:FakeRules['foreign-rule'] = [pscustomobject]@{ Name = 'foreign-rule'; Group = 'other'; Description = 'other' }
$script:FakeRoutes = @(
    [pscustomobject]@{ Id = 'owned'; InterfaceIndex = 7; NextHop = '192.168.1.3'; RouteMetric = 32123 },
    [pscustomobject]@{ Id = 'foreign-metric'; InterfaceIndex = 7; NextHop = '192.168.1.3'; RouteMetric = 1 },
    [pscustomobject]@{ Id = 'foreign-interface'; InterfaceIndex = 8; NextHop = '192.168.1.3'; RouteMetric = 32123 },
    [pscustomobject]@{ Id = 'foreign-hop'; InterfaceIndex = 7; NextHop = '192.168.1.1'; RouteMetric = 32123 }
)
Test-FmxCase 'cleanup removes only exact owned resources including spawn-journal gap' {
    Stop-FmxResources $state
    Assert-Fmx (($script:StoppedProcesses | Sort-Object) -join ',' -eq '903,904') 'Only own executable paths may stop.'
    Assert-Fmx ($script:FakeProcesses.ContainsKey(905) -and $script:FakeProcesses.ContainsKey(901)) 'Foreign processes must remain.'
    Assert-Fmx ($script:RemovedRules.Count -eq 2 -and $script:FakeRules.ContainsKey('foreign-rule')) 'Only owned named firewall rules may remove.'
    Assert-Fmx ($script:RemovedRoutes.Count -eq 1 -and $script:RemovedRoutes[0] -eq 'owned') 'Only exact route tuple may remove.'
}
Test-FmxCase 'cleanup is idempotent' {
    Stop-FmxResources $state
    Assert-Fmx ($script:StoppedProcesses.Count -eq 2 -and $script:RemovedRules.Count -eq 2 -and $script:RemovedRoutes.Count -eq 1) 'Second cleanup must not remove more resources.'
}
Test-FmxCase 'cleanup preserves changed ownership rule and reports it' {
    $script:FakeRules['fixture-TCP'] = [pscustomobject]@{ Name = 'fixture-TCP'; Group = 'foreign'; Description = $runDir }
    Assert-FmxThrows { Stop-FmxResources $state } 'Changed rule ownership must be reported.'
    Assert-Fmx ($script:FakeRules.ContainsKey('fixture-TCP')) 'Changed rule must remain.'
    $script:FakeRules.Remove('fixture-TCP')
}
Test-FmxCase 'cleanup refuses foreign server journal path' {
    $state.Server = [pscustomobject]@{ Id = 905; StartTicks = $identity.StartTicks; Path = 'C:\Foreign\iperf3.exe' }
    Stop-FmxResources $state
    Assert-Fmx ($script:FakeProcesses.ContainsKey(905)) 'Foreign executable in server journal must remain.'
}

# Runtime fixtures are disposable local files. Never launch the packaged executable.
$fixtureRoot = Join-Path ([IO.Path]::GetTempPath()) ('FuturaMAX fixture & ! ' + [guid]::NewGuid().ToString('N'))
[IO.Directory]::CreateDirectory($fixtureRoot) | Out-Null
Add-Type -AssemblyName System.IO.Compression.FileSystem
$bundle = Join-Path $fixtureRoot 'bundle with spaces'
[IO.Directory]::CreateDirectory((Join-Path $bundle 'packages')) | Out-Null
foreach ($architecture in @('x86','x64')) {
    $spec = Get-FmxRuntimeSpec -Architecture $architecture
    $runtimeDir = Join-Path $bundle ('runtime\' + $architecture)
    [IO.Directory]::CreateDirectory($runtimeDir) | Out-Null
    $sourceZip = Join-Path $PSScriptRoot ('packages\' + $spec.ArchiveName)
    $fixtureZip = Join-Path $bundle ('packages\' + $spec.ArchiveName)
    [IO.File]::Copy($sourceZip, $fixtureZip)
    $archive = [IO.Compression.ZipFile]::OpenRead($fixtureZip)
    try {
        foreach ($name in $spec.Members.Keys) {
            [IO.Compression.ZipFileExtensions]::ExtractToFile($archive.GetEntry($spec.ArchivePrefix + $name), (Join-Path $runtimeDir $name), $false)
        }
    } finally { $archive.Dispose() }
}
$script:ArchiveHelperCalls = 0
function Expand-Archive {
    param([string]$LiteralPath, [string]$DestinationPath, [switch]$Force, [string]$ErrorAction)
    $script:ArchiveHelperCalls++
    throw 'Fixture: PowerShell archive helper unavailable.'
}
try {
    Test-FmxCase '32-bit OS deterministically selects x86 runtime' {
        Assert-Fmx ((Get-FmxRuntimeArchitecture -Is64BitOperatingSystem $false) -eq 'x86') '32-bit OS must choose x86 independent of test host.'
    }
    Test-FmxCase '64-bit OS deterministically selects x64 runtime' {
        Assert-Fmx ((Get-FmxRuntimeArchitecture -Is64BitOperatingSystem $true) -eq 'x64') '64-bit OS must choose x64 independent of PowerShell process architecture.'
    }
    Test-FmxCase 'runtime optional architecture uses actual OS default' {
        $actualSpec = Get-FmxRuntimeSpec -Architecture (Get-FmxRuntimeArchitecture)
        $exe = Copy-FmxRuntime $bundle (Join-Path $fixtureRoot 'destination default architecture')
        Assert-Fmx ((Get-FileHash -LiteralPath $exe -Algorithm SHA256).Hash -eq $actualSpec.Members['iperf3.exe']) 'Omitted architecture must select actual OS runtime.'
    }
    foreach ($architecture in @('x86','x64')) {
        $spec = Get-FmxRuntimeSpec -Architecture $architecture
        $runtimeDir = Join-Path $bundle ('runtime\' + $architecture)
        $fixtureZip = Join-Path $bundle ('packages\' + $spec.ArchiveName)
        Test-FmxCase "$architecture source archive matches authoritative pin" {
            Assert-Fmx ((Get-FileHash -LiteralPath $fixtureZip -Algorithm SHA256).Hash -eq $spec.ArchiveHash) 'Actual offline source archive must match pinned spec.'
        }
        Test-FmxCase "$architecture actual EXE and DLL have matching PE machine and member hashes" {
            foreach ($name in $spec.Members.Keys) {
                $member = Join-Path $runtimeDir $name
                Assert-Fmx ((Get-FileHash -LiteralPath $member -Algorithm SHA256).Hash -eq $spec.Members[$name]) 'Actual member bytes must match pinned spec.'
                Assert-Fmx (Test-FmxPEMachine -Path $member -Machine $spec.Machine) "Actual $architecture $name must have correct PE architecture."
            }
        }
        Test-FmxCase "$architecture EXE and DLL reject swapped architecture" {
            $opposite = 0x014c
            if ($architecture -eq 'x86') { $opposite = 0x8664 }
            foreach ($name in $spec.Members.Keys) {
                Assert-Fmx (-not (Test-FmxPEMachine -Path (Join-Path $runtimeDir $name) -Machine $opposite)) "Actual $architecture $name must reject swapped PE architecture."
            }
        }
        Test-FmxCase "$architecture runtime uses verified preextracted fallback without archive helper" {
            $callsBefore = $script:ArchiveHelperCalls
            $exe = Copy-FmxRuntime $bundle (Join-Path $fixtureRoot ("destination & ! $architecture preextracted")) -Architecture $architecture
            Assert-Fmx (Test-Path -LiteralPath $exe -PathType Leaf) 'Verified executable should copy with special-character paths.'
            Assert-Fmx ($script:ArchiveHelperCalls -eq $callsBefore) 'Preextracted runtime must not depend on archive helper.'
        }
        Test-FmxCase "$architecture runtime falls back to pinned ZIP and built-in reader" {
            $callsBefore = $script:ArchiveHelperCalls
            [IO.File]::WriteAllText((Join-Path $runtimeDir 'iperf3.exe'), 'corrupt fixture')
            $exe = Copy-FmxRuntime $bundle (Join-Path $fixtureRoot ("destination $architecture ZIP fallback")) -Architecture $architecture
            Assert-Fmx ((Get-FileHash -LiteralPath $exe -Algorithm SHA256).Hash -eq $spec.Members['iperf3.exe']) 'Pinned ZIP fallback must restore correct bytes.'
            Assert-Fmx ($script:ArchiveHelperCalls -eq ($callsBefore + 1)) 'Archive helper failure should invoke built-in fallback once.'
        }
        Test-FmxCase "$architecture runtime refuses corrupt archive and invalid extracted runtime" {
            $callsBefore = $script:ArchiveHelperCalls
            [IO.File]::WriteAllText($fixtureZip, 'corrupt fixture archive')
            Assert-FmxThrows { Copy-FmxRuntime $bundle (Join-Path $fixtureRoot ("destination $architecture corrupt")) -Architecture $architecture } 'Corrupt archive must fail closed.'
            Assert-Fmx ($script:ArchiveHelperCalls -eq $callsBefore) 'Bad hash must be rejected before archive helper.'
        }
        Test-FmxCase "$architecture runtime refuses missing bundle payload" {
            Assert-FmxThrows { Copy-FmxRuntime (Join-Path $fixtureRoot 'missing bundle') (Join-Path $fixtureRoot ("destination $architecture missing")) -Architecture $architecture } 'No runtime and no archive must fail closed.'
        }
    }
    Test-FmxCase 'PE validator refuses malformed and missing files' {
        $malformed = Join-Path $fixtureRoot 'invalid PE.exe'
        [IO.File]::WriteAllText($malformed, 'not an executable')
        Assert-Fmx (-not (Test-FmxPEMachine $malformed 0x014c)) 'Malformed PE must fail closed.'
        Assert-Fmx (-not (Test-FmxPEMachine (Join-Path $fixtureRoot 'missing.exe') 0x8664)) 'Missing PE must fail closed.'
    }
    Test-FmxCase 'journal JSON writes and atomically replaces without leftover staging file' {
        $journal = Join-Path $fixtureRoot 'state.json'
        Write-FmxState $journal ([pscustomobject]@{ Status = 'FIRST'; RunId = 'fixture' })
        Write-FmxState $journal ([pscustomobject]@{ Status = 'SECOND'; RunId = 'fixture' })
        $saved = Get-Content -LiteralPath $journal -Raw | ConvertFrom-Json
        Assert-Fmx ($saved.Status -eq 'SECOND') 'Atomic replacement must preserve second complete JSON.'
        Assert-Fmx (@(Get-ChildItem -LiteralPath $fixtureRoot -Filter '*.tmp' -File).Count -eq 0) 'Successful atomic replace must consume staging file.'
    }

    # Execute the real guardian loop in hidden child PowerShell, importing only a
    # fixture mock core. The child has no route/firewall/process cleanup cmdlets.
    $mockGuardianCore = @'
function Get-FmxIdentity { param([int]$ProcessId); [pscustomobject]@{ Id=$ProcessId; StartTicks='guardian-fixture'; Path='fixture' } }
function Test-FmxProcess {
    param($Identity)
    return ($Identity.Id -eq 1001 -and $Identity.StartTicks -eq '111' -and $Identity.Path -eq 'fixture-owner' -and (Test-Path -LiteralPath (Join-Path $PSScriptRoot 'owner-alive')))
}
function Write-FmxState { param([string]$Path,$State); [IO.File]::WriteAllText($Path,($State | ConvertTo-Json -Depth 8)) }
function Stop-FmxResources {
    param($State)
    if ($State.RunId -ne 'guardian-fixture-owned' -or $State.RuleNames.Count -ne 2) { throw 'Unexpected fixture cleanup identity.' }
    [IO.File]::WriteAllText((Join-Path $PSScriptRoot 'mock-cleanup.json'),($State | ConvertTo-Json -Depth 8))
}
'@
    function Invoke-FmxGuardianFixture([string]$Case, [bool]$Alive, [string]$Birth, [bool]$SendStop) {
        $guardianDir = Join-Path $fixtureRoot ('guardian ' + $Case)
        [IO.Directory]::CreateDirectory($guardianDir) | Out-Null
        [IO.File]::Copy((Join-Path $PSScriptRoot 'notebook_watchdog.ps1'), (Join-Path $guardianDir 'notebook_watchdog.ps1'))
        [IO.File]::WriteAllText((Join-Path $guardianDir 'notebook_core.ps1'), $mockGuardianCore)
        if ($Alive) { [IO.File]::WriteAllText((Join-Path $guardianDir 'owner-alive'), 'fixture') }
        $guardianState = [pscustomobject]@{
            RunId = 'guardian-fixture-owned'; RunDirectory = $guardianDir
            Owner = [pscustomobject]@{ Id=1001; StartTicks=$Birth; Path='fixture-owner' }
            DeadlineUtc = [DateTime]::UtcNow.AddSeconds(30).ToString('o')
            RuleNames = @('fixture-owned-TCP','fixture-owned-UDP')
            Route = [pscustomobject]@{ CreatePlanned=$true; Metric=32123 }
        }
        [IO.File]::WriteAllText((Join-Path $guardianDir 'state.json'), ($guardianState | ConvertTo-Json -Depth 8))
        $psExe = Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\powershell.exe'
        $argsText = '-NoProfile -ExecutionPolicy RemoteSigned -File "' + (Join-Path $guardianDir 'notebook_watchdog.ps1') + '" -RunDirectory "' + $guardianDir + '"'
        $child = Start-Process -FilePath $psExe -ArgumentList $argsText -WindowStyle Hidden -PassThru
        try {
            # Separate bounded child startup from bounded cleanup; missing-owner
            # cases need readiness evidence too, not a silent startup timeout.
            $readyDeadline = [DateTime]::UtcNow.AddSeconds(10)
            while (-not (Test-Path -LiteralPath (Join-Path $guardianDir 'guardian.json')) -and [DateTime]::UtcNow -lt $readyDeadline -and -not $child.HasExited) {
                Start-Sleep -Milliseconds 100
            }
            if (-not (Test-Path -LiteralPath (Join-Path $guardianDir 'guardian.json'))) {
                $errorMarker = Join-Path $guardianDir 'guardian-error.txt'
                if (Test-Path -LiteralPath $errorMarker) { Write-Output (Get-Content -LiteralPath $errorMarker -Raw) }
                throw "Guardian readiness not observed within ten seconds: case=$Case childExited=$($child.HasExited)"
            }
            if ($SendStop) {
                Assert-Fmx (-not $child.HasExited) 'Matching live owner must keep guardian running.'
                Assert-Fmx (-not (Test-Path -LiteralPath (Join-Path $guardianDir 'mock-cleanup.json'))) 'Live owner must not trigger cleanup before stop flag.'
                [IO.File]::WriteAllText((Join-Path $guardianDir 'stop'), 'fixture stop')
            }
            Assert-Fmx ($child.WaitForExit(10000)) 'Guardian child must terminate within bounded ten seconds.'
            Assert-Fmx ($child.ExitCode -eq 0) "Guardian child exit code must be zero: $Case"
            Assert-Fmx (Test-Path -LiteralPath (Join-Path $guardianDir 'guardian-cleaned.txt')) 'Actual guardian must record cleaned marker.'
            $cleaned = Get-Content -LiteralPath (Join-Path $guardianDir 'mock-cleanup.json') -Raw | ConvertFrom-Json
            Assert-Fmx ($cleaned.RunId -eq $guardianState.RunId -and $cleaned.RunDirectory -eq $guardianDir -and $cleaned.Route.Metric -eq 32123) 'Guardian must pass exact owned fixture state to cleanup.'
            Assert-Fmx (-not (Test-Path -LiteralPath (Join-Path $guardianDir 'guardian-error.txt'))) 'No guardian error marker expected.'
        } finally {
            # Stop only this fixture child if a check fails; never target by name.
            if (-not $child.HasExited) { $child.Kill(); $child.WaitForExit(5000) | Out-Null }
            $child.Dispose()
        }
    }
    Test-FmxCase 'actual guardian cleans exact fixture after owner disappears' {
        Invoke-FmxGuardianFixture 'owner absent' $false '111' $false
    }
    Test-FmxCase 'actual guardian preserves live owner then cleans on stop flag' {
        Invoke-FmxGuardianFixture 'live owner stop' $true '111' $true
    }
    Test-FmxCase 'actual guardian treats wrong owner birth as dead' {
        Invoke-FmxGuardianFixture 'wrong birth' $true '112' $false
    }
} finally {
    $resolvedFixture = [IO.Path]::GetFullPath($fixtureRoot)
    $resolvedTemp = [IO.Path]::GetFullPath([IO.Path]::GetTempPath())
    if (-not $resolvedFixture.StartsWith($resolvedTemp, [StringComparison]::OrdinalIgnoreCase) -or (Split-Path $resolvedFixture -Leaf) -notlike 'FuturaMAX fixture & ! *') {
        throw 'Fixture cleanup target validation failed.'
    }
    [IO.Directory]::Delete($resolvedFixture, $true)
}
Write-Output "Behavioral offline cases passed: $script:Passed"
