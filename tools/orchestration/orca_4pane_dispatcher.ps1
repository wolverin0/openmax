param(
    [ValidateSet("status", "send")]
    [string]$Action = "status",
    [ValidateSet("claude", "codex2", "opencode", "codex1")]
    [string]$Lane = "claude",
    [string]$Prompt = ""
)

$Panes = @{
    "claude"   = @{ Id = "term_9705e0e5-6469-4bd0-94dd-7637b28ba94c"; Role = "Claude Opus 5.5 high (Live PtP/WA/LTU Precision & Orchestration)"; Type = "claude" }
    "codex2"   = @{ Id = "term_49371596-a24b-4db6-a139-06e704b50b8d"; Role = "Codex GPT-6.1-Sol high #2 (Firmware Kits, SimPy/pymoo, Git & Gates)"; Type = "codex" }
    "opencode" = @{ Id = "term_1441998e-6a73-4160-9819-7c7b1a2a1d68"; Role = "OpenCode DeepSeek V4.1 Flash max (Binary Reverse Engineering .ko/SGMT)"; Type = "opencode" }
    "codex1"   = @{ Id = "term_017af6bd-9773-4889-9717-f89e11bc9c40"; Role = "Codex GPT-6.1-Sol high #1 (Guarida 34-Endpoint & Multi-Radio Autoresearch)"; Type = "codex" }
}

function Get-PaneStatus($key) {
    $p = $Panes[$key]
    $raw = orca terminal read --terminal $p.Id --screen
    $lines = $raw -split "`n" | Where-Object { $_.Trim() -ne '' }
    $tail = ($lines | Select-Object -Last 8) -join "`n"
    $state = "UNKNOWN"
    if ($p.Type -eq "claude") {
        if ($tail -match "Brooding|Thinking|Running|esc to interrupt|✻|✢|✳|✶|·\s+\d+s") { $state = "RUNNING" }
        elseif ($tail -match "paste again to expand") { $state = "NEEDS_ENTER" }
        else { $state = "IDLE" }
    } elseif ($p.Type -eq "codex") {
        if ($tail -match "Working \(") { $state = "RUNNING" }
        elseif ($tail -match "· Ready ·") { $state = "IDLE" }
        else { $state = "IDLE" }
    } elseif ($p.Type -eq "opencode") {
        if ($tail -match "esc interrupt") { $state = "RUNNING" }
        else { $state = "IDLE" }
    }
    return [PSCustomObject]@{
        Lane  = $key
        Id    = $p.Id
        Role  = $p.Role
        State = $state
        Tail  = ($lines | Select-Object -Last 5) -join "`n"
    }
}

if ($Action -eq "status") {
    foreach ($k in @("claude", "codex2", "opencode", "codex1")) {
        $st = Get-PaneStatus $k
        Write-Host "=== [$($st.Lane.ToUpper())] $($st.State) | $($st.Role) ==="
        Write-Host $st.Tail
    }
    exit 0
}

if ($Action -eq "send") {
    $p = $Panes[$Lane]
    $cleanPrompt = $Prompt
    if ($p.Type -eq "opencode") {
        # Never allow '!' in OpenCode TUI (triggers '$' shell mode)
        $cleanPrompt = $cleanPrompt.Replace("!", "").Replace("<!--", "doc-head:")
    }
    orca terminal send --terminal $p.Id --text $cleanPrompt | Out-Null
    Start-Sleep -Milliseconds 4000
    orca terminal send --terminal $p.Id --enter | Out-Null
    if ($p.Type -eq "claude") {
        # Claude Code folds long pastes ('paste again to expand') + runs jev-model-router (~1.8s)
        Start-Sleep -Milliseconds 2200
        $check = Get-PaneStatus $Lane
        if ($check.State -eq "NEEDS_ENTER" -or $check.State -eq "IDLE") {
            orca terminal send --terminal $p.Id --enter | Out-Null
            Start-Sleep -Milliseconds 1500
        }
    } else {
        Start-Sleep -Milliseconds 1500
    }
    $final = Get-PaneStatus $Lane
    Write-Host "Dispatched to [$Lane] -> State: $($final.State)"
    Write-Host $final.Tail
}
