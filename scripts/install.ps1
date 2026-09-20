<#
quench - Remote bootstrap installer for PowerShell (Windows)
Installs Quench AI agent rules and behavioral disciplines into any project.

Usage:
  powershell -ExecutionPolicy Bypass -File install.ps1 [-Tool <name>] [-Target <dir>] [-Hooks] [-Force]
  irm https://raw.githubusercontent.com/primaybr/quench/master/scripts/install.ps1 | iex
#>

[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [string]$Tool,

    [Parameter(Position = 1)]
    [string]$Target,

    [switch]$Hooks,
    [switch]$Force,
    [string]$Source,
    [switch]$Help
)

$ErrorActionPreference = 'Stop'

function Show-Usage {
    Write-Host @"
quench - Remote Bootstrap Installer (PowerShell)

Usage:
  .\install.ps1 [parameters]
  irm https://raw.githubusercontent.com/primaybr/quench/master/scripts/install.ps1 | iex

Parameters:
  -Tool <name>    Adapter to install (e.g. cursor, copilot, kilo, cline,
                  windsurf, claude, generic, aider, zed, junie,
                  antigravity, rules, all). Default: rules
  -Target <dir>   Target project directory (default: .)
  -Hooks          Install git pre-commit and commit-msg validation hooks
  -Force          Overwrite existing files in target directory
  -Source <dir>   Local Quench source path (offline/dev override)
  -Help           Show this help message and exit
"@
}

if ($Help) {
    Show-Usage
    exit 0
}

# Handle remaining arguments or positional args passed via $args
if ($args -and $args.Count -gt 0) {
    for ($i = 0; $i -lt $args.Count; $i++) {
        $arg = [string]$args[$i]
        switch -Regex ($arg) {
            '^(-t|--tool|-Tool)$' {
                $i++; if ($i -lt $args.Count) { $Tool = [string]$args[$i] }
            }
            '^(-d|--target|-Target)$' {
                $i++; if ($i -lt $args.Count) { $Target = [string]$args[$i] }
            }
            '^(-hooks|--hooks|-Hooks)$' {
                $Hooks = $true
            }
            '^(-f|--force|-Force)$' {
                $Force = $true
            }
            '^(-s|--source|-Source)$' {
                $i++; if ($i -lt $args.Count) { $Source = [string]$args[$i] }
            }
            '^(-h|--help|-Help|\/\?)$' {
                Show-Usage
                exit 0
            }
        }
    }
}

# Variable fallbacks from global/scope or environment
if ([string]::IsNullOrWhiteSpace($Tool)) {
    if ((Test-Path variable:global:Tool) -and -not [string]::IsNullOrWhiteSpace($global:Tool)) {
        $Tool = [string]$global:Tool
    } elseif (-not [string]::IsNullOrWhiteSpace($env:QUENCH_TOOL)) {
        $Tool = $env:QUENCH_TOOL
    } else {
        $Tool = "rules"
    }
}
$Tool = $Tool.ToLower()

if ([string]::IsNullOrWhiteSpace($Target)) {
    if ((Test-Path variable:global:Target) -and -not [string]::IsNullOrWhiteSpace($global:Target)) {
        $Target = [string]$global:Target
    } elseif (-not [string]::IsNullOrWhiteSpace($env:QUENCH_TARGET)) {
        $Target = $env:QUENCH_TARGET
    } else {
        $Target = "."
    }
}

if (-not $Hooks) {
    if ((Test-Path variable:global:Hooks) -and $global:Hooks) {
        $Hooks = [bool]$global:Hooks
    } elseif ($env:QUENCH_HOOKS -eq "1" -or $env:QUENCH_HOOKS -eq "true") {
        $Hooks = $true
    }
}

if (-not $Force) {
    if ((Test-Path variable:global:Force) -and $global:Force) {
        $Force = [bool]$global:Force
    } elseif ($env:QUENCH_FORCE -eq "1" -or $env:QUENCH_FORCE -eq "true") {
        $Force = $true
    }
}

if ([string]::IsNullOrWhiteSpace($Source)) {
    if ((Test-Path variable:global:Source) -and -not [string]::IsNullOrWhiteSpace($global:Source)) {
        $Source = [string]$global:Source
    } elseif (-not [string]::IsNullOrWhiteSpace($env:QUENCH_SOURCE)) {
        $Source = $env:QUENCH_SOURCE
    }
}

$SupportedTools = @(
    'cursor', 'copilot', 'kilo', 'cline', 'windsurf',
    'claude', 'generic', 'aider', 'zed', 'junie',
    'antigravity', 'rules', 'all'
)

if ($SupportedTools -notcontains $Tool) {
    Write-Host "Error: Unknown tool '$Tool'."
    Write-Host "Supported options: $($SupportedTools -join ', ')"
    exit 1
}

$quenchSrc = $null
$tempDir = $null

try {
    # 1. Explicit source
    if ($Source -and (Test-Path $Source)) {
        $quenchSrc = (Resolve-Path $Source).Path
    }

    # 2. Local directory check relative to script
    if (-not $quenchSrc -and $PSScriptRoot) {
        $parentDir = Split-Path -Parent $PSScriptRoot
        if ((Test-Path (Join-Path $parentDir "adapters")) -and (Test-Path (Join-Path $parentDir "rules"))) {
            $quenchSrc = (Resolve-Path $parentDir).Path
        }
    }

    # 3. Current directory check
    if (-not $quenchSrc) {
        if ((Test-Path "adapters") -and (Test-Path "rules/AGENTS.md")) {
            $quenchSrc = (Resolve-Path ".").Path
        }
    }

    # 4. Remote clone or download
    if (-not $quenchSrc) {
        $tempDir = Join-Path ([System.IO.Path]::GetTempPath()) ("quench_" + [System.Guid]::NewGuid().ToString("N"))
        $null = New-Item -ItemType Directory -Path $tempDir -Force

        $repoUrl = "https://github.com/primaybr/quench.git"
        $zipUrl = "https://github.com/primaybr/quench/archive/refs/heads/master.zip"

        $gitCmd = Get-Command git -ErrorAction SilentlyContinue
        if ($gitCmd) {
            Write-Host "Cloning Quench repository from GitHub..."
            & git clone --depth 1 $repoUrl $tempDir 2>$null
            if ($LASTEXITCODE -eq 0 -and (Test-Path (Join-Path $tempDir "adapters"))) {
                $quenchSrc = $tempDir
            }
        }

        if (-not $quenchSrc) {
            Write-Host "Downloading Quench archive via web..."
            $zipFile = Join-Path $tempDir "quench.zip"
            $curlCmd = Get-Command curl.exe -ErrorAction SilentlyContinue
            if ($curlCmd) {
                & curl.exe -fsSL $zipUrl -o $zipFile
            } else {
                Invoke-WebRequest -Uri $zipUrl -OutFile $zipFile -UseBasicParsing
            }

            Add-Type -AssemblyName System.IO.Compression.FileSystem
            [System.IO.Compression.ZipFile]::ExtractToDirectory($zipFile, $tempDir)

            $extractedMaster = Join-Path $tempDir "quench-master"
            if (Test-Path $extractedMaster) {
                $quenchSrc = $extractedMaster
            } else {
                $quenchSrc = $tempDir
            }
        }
    }

    if (-not $quenchSrc -or -not (Test-Path (Join-Path $quenchSrc "adapters"))) {
        Write-Host "Error: Could not locate or download Quench repository files."
        exit 1
    }

    # Prepare target directory
    $targetPath = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($Target)
    if (-not (Test-Path $targetPath)) {
        $null = New-Item -ItemType Directory -Path $targetPath -Force
    }
    $resolvedTarget = (Resolve-Path $targetPath).Path

    Write-Host "Initializing Quench ($Tool) in: $resolvedTarget"

    $AdapterMap = @{
        'cursor' = @(
            @{ Src = 'adapters/cursor/.cursorrules'; Dst = '.cursorrules' },
            @{ Src = 'adapters/cursor/.cursor/rules/steel-mind.mdc'; Dst = '.cursor/rules/steel-mind.mdc' },
            @{ Src = 'adapters/cursor/.cursor/rules/plaincast.mdc'; Dst = '.cursor/rules/plaincast.mdc' },
            @{ Src = 'adapters/cursor/.cursor/rules/leakguard.mdc'; Dst = '.cursor/rules/leakguard.mdc' },
            @{ Src = 'adapters/cursor/.cursor/rules/precision-output.mdc'; Dst = '.cursor/rules/precision-output.mdc' }
        );
        'copilot' = @(
            @{ Src = 'adapters/copilot/copilot-instructions.md'; Dst = '.github/copilot-instructions.md' }
        );
        'kilo' = @(
            @{ Src = 'adapters/kilo/kilo.jsonc'; Dst = 'kilo.jsonc' },
            @{ Src = 'adapters/kilo/.kilo/rules/steel-mind.md'; Dst = '.kilo/rules/steel-mind.md' },
            @{ Src = 'adapters/kilo/.kilo/rules/plaincast.md'; Dst = '.kilo/rules/plaincast.md' },
            @{ Src = 'adapters/kilo/.kilo/rules/leakguard.md'; Dst = '.kilo/rules/leakguard.md' },
            @{ Src = 'adapters/kilo/.kilo/rules/precision-output.md'; Dst = '.kilo/rules/precision-output.md' }
        );
        'cline' = @(
            @{ Src = 'adapters/cline/.clinerules/steel-mind.md'; Dst = '.clinerules/steel-mind.md' },
            @{ Src = 'adapters/cline/.clinerules/plaincast.md'; Dst = '.clinerules/plaincast.md' },
            @{ Src = 'adapters/cline/.clinerules/leakguard.md'; Dst = '.clinerules/leakguard.md' },
            @{ Src = 'adapters/cline/.clinerules/precision-output.md'; Dst = '.clinerules/precision-output.md' }
        );
        'windsurf' = @(
            @{ Src = 'adapters/windsurf/.windsurfrules'; Dst = '.windsurfrules' }
        );
        'claude' = @(
            @{ Src = 'adapters/claude/CLAUDE.md'; Dst = 'CLAUDE.md' }
        );
        'generic' = @(
            @{ Src = 'adapters/generic/system-prompt.md'; Dst = 'system-prompt.md' }
        );
        'aider' = @(
            @{ Src = 'adapters/aider/CONVENTIONS.md'; Dst = 'CONVENTIONS.md' }
        );
        'zed' = @(
            @{ Src = 'adapters/zed/.zedprompts/steel-mind.md'; Dst = '.zedprompts/steel-mind.md' },
            @{ Src = 'adapters/zed/.zedprompts/plaincast.md'; Dst = '.zedprompts/plaincast.md' },
            @{ Src = 'adapters/zed/.zedprompts/leakguard.md'; Dst = '.zedprompts/leakguard.md' },
            @{ Src = 'adapters/zed/.zedprompts/precision-output.md'; Dst = '.zedprompts/precision-output.md' }
        );
        'junie' = @(
            @{ Src = 'adapters/junie/.junie/rules/steel-mind.md'; Dst = '.junie/rules/steel-mind.md' },
            @{ Src = 'adapters/junie/.junie/rules/plaincast.md'; Dst = '.junie/rules/plaincast.md' },
            @{ Src = 'adapters/junie/.junie/rules/leakguard.md'; Dst = '.junie/rules/leakguard.md' },
            @{ Src = 'adapters/junie/.junie/rules/precision-output.md'; Dst = '.junie/rules/precision-output.md' }
        );
        'antigravity' = @(
            @{ Src = 'adapters/antigravity/.agents/rules/AGENTS.md'; Dst = '.agents/rules/AGENTS.md' }
        );
        'rules' = @(
            @{ Src = 'rules/AGENTS.md'; Dst = 'AGENTS.md' }
        )
    }

    $toolsToInstall = if ($Tool -eq 'all') {
        @('cursor', 'copilot', 'kilo', 'cline', 'windsurf', 'claude', 'generic', 'aider', 'zed', 'junie', 'antigravity', 'rules')
    } else {
        @($Tool)
    }

    $copiedCount = 0

    foreach ($t in $toolsToInstall) {
        $fileList = $AdapterMap[$t]
        foreach ($item in $fileList) {
            $srcRel = $item.Src -replace '/', [System.IO.Path]::DirectorySeparatorChar
            $dstRel = $item.Dst -replace '/', [System.IO.Path]::DirectorySeparatorChar
            $srcFull = Join-Path $quenchSrc $srcRel
            $dstFull = Join-Path $resolvedTarget $dstRel

            if (-not (Test-Path $srcFull)) {
                Write-Host "Warning: Source template missing: $($item.Src)"
                continue
            }

            $alreadyExists = Test-Path $dstFull
            if ($alreadyExists -and -not $Force) {
                Write-Host "  Skipped (already exists): $($item.Dst) (use -Force to overwrite)"
                continue
            }

            $parentFolder = Split-Path -Parent $dstFull
            if (-not (Test-Path $parentFolder)) {
                $null = New-Item -ItemType Directory -Path $parentFolder -Force
            }

            Copy-Item -Path $srcFull -Destination $dstFull -Force
            $copiedCount++

            if ($alreadyExists -and $Force) {
                Write-Host "  Overwritten: $($item.Dst)"
            } else {
                Write-Host "  Installed: $($item.Dst)"
            }
        }
    }

    if ($Hooks) {
        Write-Host "Installing Git validation hooks..."
        $targetGithooks = Join-Path $resolvedTarget ".githooks"
        if (-not (Test-Path $targetGithooks)) {
            $null = New-Item -ItemType Directory -Path $targetGithooks -Force
        }

        $targetGit = Join-Path $resolvedTarget ".git"
        $hasGit = Test-Path $targetGit

        $hookFiles = @('pre-commit', 'commit-msg')
        foreach ($h in $hookFiles) {
            $srcHook = Join-Path $quenchSrc (Join-Path ".githooks" $h)
            if (Test-Path $srcHook) {
                $dstGithooks = Join-Path $targetGithooks $h
                Copy-Item -Path $srcHook -Destination $dstGithooks -Force
                Write-Host "  Configured hook: .githooks/$h"

                if ($hasGit) {
                    $dotGitHooks = Join-Path $targetGit "hooks"
                    if (-not (Test-Path $dotGitHooks)) {
                        $null = New-Item -ItemType Directory -Path $dotGitHooks -Force
                    }
                    $dstDotGitHook = Join-Path $dotGitHooks $h
                    Copy-Item -Path $srcHook -Destination $dstDotGitHook -Force
                    Write-Host "  Configured hook: .git/hooks/$h"
                }
            }
        }

        if ($hasGit) {
            try {
                & git -C $resolvedTarget config core.hooksPath .githooks 2>$null
            } catch {
                # Ignore if git command fails
            }
        }
    }

    Write-Host ""
    Write-Host "Quench initialization complete. $copiedCount file(s) configured."
} finally {
    if ($tempDir -and (Test-Path $tempDir)) {
        Remove-Item -Path $tempDir -Recurse -Force -ErrorAction SilentlyContinue
    }
}
