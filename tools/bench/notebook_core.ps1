# Importing these offline helpers does not change the machine.
function Select-FmxAdapter {
    param($Adapters, $Addresses)
    $matched = @($Adapters | Where-Object { ($_.MacAddress -replace '[:-]', '').ToLowerInvariant() -eq '88ae1d73e1c3' -and $_.Status -eq 'Up' })
    if ($matched.Count -ne 1) { throw 'Expected notebook Ethernet 88-AE-1D-73-E1-C3 linked and enabled.' }
    $nic = $matched[0]
    $ips = @($Addresses | Where-Object { $_.InterfaceIndex -eq $nic.ifIndex -and $_.IPAddress -match '^192\.168\.1\.(\d+)$' -and [int]$Matches[1] -gt 0 -and [int]$Matches[1] -lt 255 -and [int]$Matches[1] -notin @(2,3,155) -and $_.AddressState -eq 'Preferred' -and $_.PrefixLength -eq 24 })
    if ($ips.Count -ne 1) { throw 'Expected one preferred 192.168.1.x/24 address on notebook Ethernet; refusing ambiguous/wrong network.' }
    [pscustomobject]@{ InterfaceIndex = [int]$nic.ifIndex; Alias = [string]$nic.Name; IPv4 = [string]$ips[0].IPAddress }
}

function Get-FmxRuntimeArchitecture {
    param([bool]$Is64BitOperatingSystem = [Environment]::Is64BitOperatingSystem)
    if ($Is64BitOperatingSystem) { return 'x64' }
    return 'x86'
}
function Get-FmxRuntimeSpec {
    param([ValidateSet('x86','x64')][string]$Architecture)
    if (-not $Architecture) { $Architecture = Get-FmxRuntimeArchitecture }
    if ($Architecture -eq 'x86') {
        return [pscustomobject]@{
            Architecture = 'x86'; Machine = 0x014c
            ArchiveName = 'iperf-3.22-win32.zip'; ArchivePrefix = 'iperf3/'
            ArchiveHash = 'cedbca03a029ec35081b0466ab5d9aade099105bdabcf3c413204e9efa3b8a7c'
            Members = [ordered]@{
                'iperf3.exe' = '5ed5046041a53dad4e25945c0703739b95f68bf5477045c9beb5c7cd20288445'
                'cygwin1.dll' = 'f1f04586da69854a6e00f978dca5edb8318bd585f51aa88c5fd6ba9b0e3fbb65'
            }
        }
    }
    [pscustomobject]@{
        Architecture = 'x64'; Machine = 0x8664
        ArchiveName = 'iperf-3.22-win64.zip'; ArchivePrefix = ''
        ArchiveHash = 'c9feabb3d721039508ccb81f74c2ada3ae11b9e75d33d24510573c2aa21da420'
        Members = [ordered]@{
            'iperf3.exe' = 'bcafba4aff825fa94685b6b3d049f8b1338c69e6dc1d06e6a00ac046191e4999'
            'cygwin1.dll' = 'd66788fce4ef1ce787fc1a83f2dd1e063e58bbf0d48ad93164ee195a983c035e'
        }
    }
}
function Test-FmxPEMachine {
    param([string]$Path, [int]$Machine)
    try {
        $bytes = [IO.File]::ReadAllBytes($Path)
        if ($bytes.Length -lt 64 -or $bytes[0] -ne 0x4d -or $bytes[1] -ne 0x5a) { return $false }
        $offset = [BitConverter]::ToInt32($bytes,60)
        if ($offset -lt 64 -or $offset -gt ($bytes.Length - 26)) { return $false }
        if ([BitConverter]::ToUInt32($bytes,$offset) -ne 0x4550 -or [BitConverter]::ToUInt16($bytes,$offset+4) -ne $Machine) { return $false }
        $expectedMagic = 0x010b
        if ($Machine -eq 0x8664) { $expectedMagic = 0x020b }
        return [BitConverter]::ToUInt16($bytes,$offset+24) -eq $expectedMagic
    } catch { return $false }
}
function Copy-FmxRuntime {
    param([string]$BundleRoot, [string]$Destination, [ValidateSet('x86','x64')][string]$Architecture)
    if (-not $Architecture) { $Architecture = Get-FmxRuntimeArchitecture }
    $spec = Get-FmxRuntimeSpec -Architecture $Architecture
    $hashes = $spec.Members
    [IO.Directory]::CreateDirectory($Destination) | Out-Null
    $usable = $true
    $runtimeSource = Join-Path $BundleRoot ('runtime\' + $spec.Architecture)
    foreach ($name in $hashes.Keys) {
        $source = Join-Path $runtimeSource $name
        if (-not (Test-Path -LiteralPath $source -PathType Leaf) -or (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash -ne $hashes[$name]) { $usable = $false; break }
    }
    if ($usable) {
        foreach ($name in $hashes.Keys) { [IO.File]::Copy((Join-Path $runtimeSource $name), (Join-Path $Destination $name), $true) }
    } else {
        Write-Host "Using verified $($spec.Architecture) backup archive (offline)."
        $zip = Join-Path $BundleRoot ('packages\' + $spec.ArchiveName)
        if (-not (Test-Path -LiteralPath $zip -PathType Leaf)) { throw 'Offline package missing and extracted runtime unavailable.' }
        if ((Get-FileHash -LiteralPath $zip -Algorithm SHA256).Hash -ne $spec.ArchiveHash) { throw 'Package checksum mismatch; nothing will be run.' }
        $staging = Join-Path $Destination ('archive-' + [guid]::NewGuid().ToString('N'))
        try { Expand-Archive -LiteralPath $zip -DestinationPath $staging -Force -ErrorAction Stop }
        catch {
            Write-Host 'Archive helper failed; using built-in ZIP reader.'
            Add-Type -AssemblyName System.IO.Compression.FileSystem
            $archive = [IO.Compression.ZipFile]::OpenRead($zip)
            try {
                [IO.Directory]::CreateDirectory((Join-Path $staging $spec.ArchivePrefix)) | Out-Null
                foreach ($entry in $archive.Entries) {
                    if ($spec.ArchivePrefix -and $entry.FullName -eq $spec.ArchivePrefix -and $entry.Length -eq 0) { continue }
                    $expectedNames = @($hashes.Keys | ForEach-Object { $spec.ArchivePrefix + $_ })
                    if ($entry.FullName -notin $expectedNames) { throw 'Unexpected archive member.' }
                    [IO.Compression.ZipFileExtensions]::ExtractToFile($entry, (Join-Path $staging $entry.FullName), $true)
                }
            } finally { $archive.Dispose() }
        }
        foreach ($name in $hashes.Keys) { [IO.File]::Copy((Join-Path $staging ($spec.ArchivePrefix + $name)), (Join-Path $Destination $name), $true) }
    }
    foreach ($name in $hashes.Keys) {
        if ((Get-FileHash -LiteralPath (Join-Path $Destination $name) -Algorithm SHA256).Hash -ne $hashes[$name]) { throw "Runtime checksum failed: $name" }
        if (-not (Test-FmxPEMachine (Join-Path $Destination $name) $spec.Machine)) { throw "Runtime architecture mismatch: $name must be $($spec.Architecture)." }
    }
    Join-Path $Destination 'iperf3.exe'
}

function Get-FmxIdentity {
    param([int]$ProcessId)
    $p = Get-Process -Id $ProcessId -ErrorAction Stop
    [pscustomobject]@{ Id = $p.Id; StartTicks = $p.StartTime.ToUniversalTime().Ticks.ToString(); Path = $p.Path }
}
function Test-FmxProcess {
    param($Identity)
    if ($null -eq $Identity) { return $false }
    try {
        $p = Get-FmxIdentity -ProcessId $Identity.Id
        return ($p.StartTicks -eq $Identity.StartTicks -and $p.Path -eq $Identity.Path)
    } catch { return $false }
}
function Write-FmxState {
    param([string]$Path, $State)
    $tmp = $Path + '.' + [guid]::NewGuid().ToString('N') + '.tmp'
    [IO.File]::WriteAllText($tmp, ($State | ConvertTo-Json -Depth 8), [Text.UTF8Encoding]::new($false))
    if ([IO.File]::Exists($Path)) { [IO.File]::Replace($tmp, $Path, [NullString]::Value) }
    else { [IO.File]::Move($tmp, $Path) }
}
function Send-FmxStatusResponse {
    param($Client, $State)
    # Consume bounded request headers before closing, avoiding TCP reset on unread data.
    $Client.ReceiveTimeout = 1000
    $Client.SendTimeout = 1000
    $stream = $Client.GetStream()
    $header = [Text.StringBuilder]::new()
    $timer = [Diagnostics.Stopwatch]::StartNew()
    while ($header.Length -lt 8192 -and $timer.ElapsedMilliseconds -lt 2000) {
        $byte = $stream.ReadByte()
        if ($byte -lt 0) { return }
        $null = $header.Append([char]$byte)
        if ($header.ToString().EndsWith("`r`n`r`n")) { break }
    }
    $request = $header.ToString()
    if (-not $request.EndsWith("`r`n`r`n") -or $request -notmatch '^GET /(status)? HTTP/1\.[01]\r\n' -or $request -match '(?im)^(Content-Length:|Transfer-Encoding:)') { return }
    $body = [Text.Encoding]::UTF8.GetBytes(($State | ConvertTo-Json -Depth 6 -Compress))
    $response = [Text.Encoding]::ASCII.GetBytes("HTTP/1.1 200 OK`r`nContent-Type: application/json`r`nContent-Length: $($body.Length)`r`nConnection: close`r`n`r`n")
    $stream.Write($response,0,$response.Length)
    $stream.Write($body,0,$body.Length)
}
function Stop-FmxResources {
    param($State)
    $problems = [Collections.Generic.List[string]]::new()
    $expectedExe = Join-Path $State.RunDirectory 'runtime\iperf3.exe'
    if ($State.Server -and $State.Server.Path -eq $expectedExe -and (Test-FmxProcess $State.Server)) {
        try { Stop-Process -Id $State.Server.Id -Force -ErrorAction Stop } catch { $problems.Add($_.Exception.Message) }
    }
    # Protected unique runtime path covers a crash between process spawn and journal update.
    foreach ($p in @(Get-Process -Name iperf3 -ErrorAction SilentlyContinue)) {
        try { if ($p.Path -eq $expectedExe) { Stop-Process -Id $p.Id -Force -ErrorAction Stop } } catch { $problems.Add($_.Exception.Message) }
    }
    foreach ($name in $State.RuleNames) {
        try {
            foreach ($rule in @(Get-NetFirewallRule -Name $name -ErrorAction SilentlyContinue)) {
                if ($rule.Group -eq $State.RunId -and $rule.Description -eq $State.RunDirectory) { $rule | Remove-NetFirewallRule -ErrorAction Stop }
                else { $problems.Add("Foreign/changed rule preserved: $name") }
            }
        } catch { $problems.Add($_.Exception.Message) }
    }
    if ($State.Route.CreatePlanned) {
        try {
            Get-NetRoute -DestinationPrefix '192.168.1.155/32' -PolicyStore ActiveStore -ErrorAction SilentlyContinue |
                Where-Object { $_.InterfaceIndex -eq $State.InterfaceIndex -and $_.NextHop -eq '192.168.1.3' -and $_.RouteMetric -eq $State.Route.Metric } |
                Remove-NetRoute -Confirm:$false -ErrorAction Stop
        } catch { $problems.Add($_.Exception.Message) }
    }
    if ($problems.Count) { throw ($problems -join '; ') }
}
function Initialize-FmxRunRoot {
    $root = Join-Path $env:ProgramData 'FuturaMAX-NotebookRuns'
    if (-not (Test-Path -LiteralPath $root)) {
        [IO.Directory]::CreateDirectory($root) | Out-Null
        $acl = [Security.AccessControl.DirectorySecurity]::new()
        $acl.SetAccessRuleProtection($true, $false)
        foreach ($sidText in @('S-1-5-18', 'S-1-5-32-544')) {
            $sid = [Security.Principal.SecurityIdentifier]::new($sidText)
            $rule = [Security.AccessControl.FileSystemAccessRule]::new($sid, 'FullControl', 'ContainerInherit,ObjectInherit', 'None', 'Allow')
            $acl.AddAccessRule($rule)
        }
        $acl.SetOwner([Security.Principal.SecurityIdentifier]::new('S-1-5-32-544'))
        Set-Acl -LiteralPath $root -AclObject $acl
    }
    if ((Get-Item -LiteralPath $root -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Run root must not be a link.' }
    $acl = Get-Acl -LiteralPath $root
    if ($acl.GetOwner([Security.Principal.SecurityIdentifier]).Value -notin @('S-1-5-18','S-1-5-32-544')) { throw 'Unexpected run root owner; refusing privileged recovery.' }
    foreach ($rule in $acl.Access) {
        $sid = $rule.IdentityReference.Translate([Security.Principal.SecurityIdentifier]).Value
        if ($rule.AccessControlType -eq 'Allow' -and $sid -notin @('S-1-5-18','S-1-5-32-544') -and ([int]$rule.FileSystemRights -band 0xD0156)) { throw 'Run root allows non-administrator writes; refusing recovery.' }
    }
    $root
}
function Repair-FmxStaleRuns {
    param([string]$Root)
    foreach ($dir in @(Get-ChildItem -LiteralPath $Root -Directory)) {
        if ($dir.Name -notmatch '^[a-f0-9]{32}$' -or ($dir.Attributes -band [IO.FileAttributes]::ReparsePoint)) { continue }
        $path = Join-Path $dir.FullName 'state.json'
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { continue }
        $s = Get-Content -LiteralPath $path -Raw | ConvertFrom-Json
        if ($s.Schema -ne 1 -or $s.RunId -ne $dir.Name -or $s.RunDirectory -ne $dir.FullName) { throw 'Invalid previous run journal; no cleanup attempted.' }
        if (Test-FmxProcess $s.Owner) { throw 'Another notebook helper is active; keep its existing window open.' }
        if ($s.Status -ne 'CLEANED') {
            Write-Host "Recovering interrupted run $($s.RunId)..."
            Stop-FmxResources $s
            $s.Status = 'CLEANED'
            Write-FmxState $path $s
        }
    }
}
