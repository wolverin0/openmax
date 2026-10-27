# Build a portable offline helper. No network, elevation or machine changes.
[CmdletBinding()]
param([string]$OutputRoot)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
Add-Type -AssemblyName System.IO.Compression.FileSystem
$projectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
if (-not $OutputRoot) { $OutputRoot = Join-Path $projectRoot 'artifacts' }
$OutputRoot = [IO.Path]::GetFullPath($OutputRoot)
$helperNames = @('START_FUTURAMAX.cmd', 'start_notebook_server.ps1', 'notebook_watchdog.ps1',
    'notebook_core.ps1', 'RUN_ON_NOTEBOOK.md', 'RUNTIME_PROVENANCE.md')
foreach ($name in $helperNames) {
    if (-not (Test-Path -LiteralPath (Join-Path $PSScriptRoot $name) -PathType Leaf)) {
        throw "Required notebook helper missing: $name"
    }
    if (Get-Item -LiteralPath (Join-Path $PSScriptRoot $name) -Stream Zone.Identifier -ErrorAction SilentlyContinue) {
        throw "Internet-zone marker on local helper $name; refusing to distribute a policy-blocked bundle."
    }
}
. (Join-Path $PSScriptRoot 'notebook_core.ps1')
$packages = [Collections.Generic.List[object]]::new()
try {
    # Validate BOTH architectures before creating an output directory.
    foreach ($architecture in @('x86', 'x64')) {
        $spec = Get-FmxRuntimeSpec -Architecture $architecture
        $archivePath = Join-Path $PSScriptRoot ('packages\' + $spec.ArchiveName)
        if (-not (Test-Path -LiteralPath $archivePath -PathType Leaf)) { throw "Offline package missing: $($spec.ArchiveName)" }
        if ((Get-FileHash -LiteralPath $archivePath -Algorithm SHA256).Hash -ne $spec.ArchiveHash) {
            throw 'Package checksum mismatch; no bundle will be created.'
        }
        $archive = [IO.Compression.ZipFile]::OpenRead($archivePath)
        $packages.Add([pscustomobject]@{ Spec=$spec; Archive=$archive; Path=$archivePath })
        $seen = @{}
        $directoryCount = 0
        foreach ($entry in $archive.Entries) {
            if ($spec.ArchivePrefix -and $entry.FullName -ceq $spec.ArchivePrefix -and $entry.Length -eq 0) {
                $directoryCount++
                if ($directoryCount -gt 1) { throw 'Duplicate archive directory entry.' }
                continue
            }
            # Exact known prefix+filename only; flatten after validation.
            $name = @($spec.Members.Keys | Where-Object { ($spec.ArchivePrefix + $_) -ceq $entry.FullName })
            if ($name.Count -ne 1 -or $seen.ContainsKey($entry.FullName)) {
                throw "Unexpected package member path: $($entry.FullName)"
            }
            $seen[$entry.FullName] = $true
            $stream = $entry.Open()
            $sha = [Security.Cryptography.SHA256]::Create()
            try {
                $hash = [BitConverter]::ToString($sha.ComputeHash($stream)).Replace('-', '').ToLowerInvariant()
                if ($hash -ne $spec.Members[$name[0]]) { throw "Package member checksum mismatch: $($entry.FullName)" }
            } finally { $stream.Dispose(); $sha.Dispose() }
        }
        if ($seen.Count -ne $spec.Members.Count) { throw 'Unexpected package member count.' }
    }

    $buildRoot = Join-Path $OutputRoot ('notebook-bundle-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '-' + [guid]::NewGuid().ToString('N'))
    if (Test-Path -LiteralPath $buildRoot) { throw 'Unique build directory already exists; refusing overwrite.' }
    $bundleRoot = Join-Path $buildRoot 'FuturaMAX-Notebook'
    [IO.Directory]::CreateDirectory((Join-Path $bundleRoot 'packages')) | Out-Null
    [IO.Directory]::CreateDirectory((Join-Path $bundleRoot 'runtime')) | Out-Null
    foreach ($name in $helperNames) {
        [IO.File]::Copy((Join-Path $PSScriptRoot $name), (Join-Path $bundleRoot $name), $false)
        if (Get-Item -LiteralPath (Join-Path $bundleRoot $name) -Stream Zone.Identifier -ErrorAction SilentlyContinue) {
            throw "Copied helper $name has an Internet-zone marker; bundle rejected."
        }
    }
    foreach ($package in $packages) {
        $spec = $package.Spec
        [IO.File]::Copy($package.Path, (Join-Path $bundleRoot ('packages\' + $spec.ArchiveName)), $false)
        $runtimeDir = Join-Path $bundleRoot ('runtime\' + $spec.Architecture)
        [IO.Directory]::CreateDirectory($runtimeDir) | Out-Null
        foreach ($name in $spec.Members.Keys) {
            $entry = $package.Archive.GetEntry($spec.ArchivePrefix + $name)
            $destination = Join-Path $runtimeDir $name
            [IO.Compression.ZipFileExtensions]::ExtractToFile($entry, $destination, $false)
            if (-not (Test-FmxPEMachine -Path $destination -Machine $spec.Machine)) { throw "Runtime PE architecture mismatch: $($spec.Architecture)/$name" }
        }
    }
} finally { foreach ($package in $packages) { $package.Archive.Dispose() } }

$records = @(Get-ChildItem -LiteralPath $bundleRoot -File -Recurse | Sort-Object FullName | ForEach-Object {
    [ordered]@{
        path = $_.FullName.Substring($bundleRoot.Length + 1).Replace('\', '/')
        size_bytes = $_.Length
        sha256 = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    }
})
$manifest = [ordered]@{
    schema_version = 2
    created_utc = [DateTime]::UtcNow.ToString('o')
    offline = $true
    packages = @($packages | ForEach-Object { [ordered]@{ architecture=$_.Spec.Architecture; archive=$_.Spec.ArchiveName; sha256=$_.Spec.ArchiveHash } })
    files = $records
}
$manifestPath = Join-Path $bundleRoot 'manifest.json'
[IO.File]::WriteAllText($manifestPath, ($manifest | ConvertTo-Json -Depth 6), [Text.UTF8Encoding]::new($false))
$bundleZip = Join-Path $buildRoot 'FuturaMAX-Notebook.zip'
[IO.Compression.ZipFile]::CreateFromDirectory($bundleRoot, $bundleZip, [IO.Compression.CompressionLevel]::Optimal, $true)
$zipHash = (Get-FileHash -LiteralPath $bundleZip -Algorithm SHA256).Hash.ToLowerInvariant()
[IO.File]::WriteAllText((Join-Path $buildRoot 'FuturaMAX-Notebook.zip.sha256'), "$zipHash  FuturaMAX-Notebook.zip`r`n", [Text.UTF8Encoding]::new($false))
Write-Host "Offline notebook folder: $bundleRoot"
Write-Host "Offline notebook ZIP: $bundleZip"
Write-Host "ZIP SHA256: $zipHash"
# A receipt only: the notebook operator must still extract and launch it.
