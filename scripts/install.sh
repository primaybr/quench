#!/usr/bin/env sh
# quench - Remote bootstrap installer for POSIX environments
# Installs Quench AI agent rules and behavioral disciplines into any project.

set -eu

# Print usage information
show_usage() {
    cat << 'EOF'
quench - Remote Bootstrap Installer

Usage:
  install.sh [options]
  curl -fsSL https://raw.githubusercontent.com/primaybr/quench/master/scripts/install.sh | bash -s -- [options]

Options:
  -t, --tool <name>    Adapter to install (e.g. cursor, copilot, kilo, cline,
                       windsurf, claude, generic, aider, zed, junie,
                       antigravity, rules, all). Default: rules
  -d, --target <dir>   Target project directory (default: .)
  -h, --hooks          Install git pre-commit and commit-msg validation hooks
  -f, --force          Overwrite existing files in target directory
  -s, --source <dir>   Local Quench source path (offline/dev override)
      --help           Show this help message and exit
EOF
}

# Defaults
TOOL=""
TARGET="."
HOOKS=0
FORCE=0
SOURCE=""

# Parse arguments
while [ $# -gt 0 ]; do
    case "$1" in
        -t|--tool)
            if [ $# -lt 2 ]; then
                printf 'Error: --tool requires an argument\n' >&2
                exit 1
            fi
            TOOL="$2"
            shift 2
            ;;
        -d|--target)
            if [ $# -lt 2 ]; then
                printf 'Error: --target requires an argument\n' >&2
                exit 1
            fi
            TARGET="$2"
            shift 2
            ;;
        -h|--hooks)
            HOOKS=1
            shift
            ;;
        -f|--force)
            FORCE=1
            shift
            ;;
        -s|--source)
            if [ $# -lt 2 ]; then
                printf 'Error: --source requires an argument\n' >&2
                exit 1
            fi
            SOURCE="$2"
            shift 2
            ;;
        --help)
            show_usage
            exit 0
            ;;
        *)
            printf 'Error: Unknown option: %s\n' "$1" >&2
            show_usage >&2
            exit 1
            ;;
    esac
done

# Environment variable fallbacks
if [ -z "$TOOL" ]; then
    if [ -n "${QUENCH_TOOL:-}" ]; then
        TOOL="$QUENCH_TOOL"
    else
        TOOL="rules"
    fi
fi

if [ "$TARGET" = "." ] && [ -n "${QUENCH_TARGET:-}" ]; then
    TARGET="$QUENCH_TARGET"
fi

if [ "$HOOKS" -eq 0 ] && [ "${QUENCH_HOOKS:-}" = "1" ]; then
    HOOKS=1
fi

if [ "$FORCE" -eq 0 ] && [ "${QUENCH_FORCE:-}" = "1" ]; then
    FORCE=1
fi

if [ -z "$SOURCE" ] && [ -n "${QUENCH_SOURCE:-}" ]; then
    SOURCE="$QUENCH_SOURCE"
fi

# Validate tool selection
case "$TOOL" in
    cursor|copilot|kilo|cline|windsurf|claude|generic|aider|zed|junie|antigravity|rules|all)
        ;;
    *)
        printf 'Error: Unknown tool "%s".\n' "$TOOL" >&2
        printf 'Supported options: cursor, copilot, kilo, cline, windsurf, claude, generic, aider, zed, junie, antigravity, rules, all\n' >&2
        exit 1
        ;;
esac

QUENCH_SRC=""
TMP_DIR=""

cleanup() {
    if [ -n "$TMP_DIR" ] && [ -d "$TMP_DIR" ]; then
        rm -rf "$TMP_DIR"
    fi
}
trap cleanup EXIT INT TERM

# 1. Explicit source argument or env
if [ -n "$SOURCE" ]; then
    if [ -d "$SOURCE/adapters" ] || [ -f "$SOURCE/quench.py" ] || [ -f "$SOURCE/scripts/quench.py" ]; then
        QUENCH_SRC="$SOURCE"
    else
        printf 'Error: Provided --source directory is not a valid Quench repository: %s\n' "$SOURCE" >&2
        exit 1
    fi
fi

# 2. Local directory detection relative to script
if [ -z "$QUENCH_SRC" ]; then
    SCRIPT_PATH="$0"
    if [ "$SCRIPT_PATH" != "sh" ] && [ "$SCRIPT_PATH" != "bash" ] && [ -f "$SCRIPT_PATH" ]; then
        SCRIPT_DIR=$(cd "$(dirname "$SCRIPT_PATH")" 2>/dev/null && pwd)
        if [ -d "$SCRIPT_DIR/../adapters" ] && [ -f "$SCRIPT_DIR/quench.py" ]; then
            QUENCH_SRC=$(cd "$SCRIPT_DIR/.." && pwd)
        elif [ -d "$SCRIPT_DIR/adapters" ] && [ -f "$SCRIPT_DIR/rules/AGENTS.md" ]; then
            QUENCH_SRC="$SCRIPT_DIR"
        fi
    fi
fi

# 3. Current working directory check
if [ -z "$QUENCH_SRC" ]; then
    if [ -d "./adapters" ] && [ -f "./rules/AGENTS.md" ]; then
        QUENCH_SRC="$PWD"
    fi
fi

# 4. Remote download / clone if not found locally
if [ -z "$QUENCH_SRC" ]; then
    TMP_DIR=$(mktemp -d 2>/dev/null || mktemp -d -t 'quench_bootstrap')
    REPO_URL="https://github.com/primaybr/quench.git"
    ARCHIVE_URL="https://github.com/primaybr/quench/archive/refs/heads/master.tar.gz"

    if command -v git >/dev/null 2>&1; then
        printf 'Cloning Quench repository from GitHub...\n'
        if ! git clone --depth 1 "$REPO_URL" "$TMP_DIR" >/dev/null 2>&1; then
            printf 'Error: Failed to clone Quench from %s\n' "$REPO_URL" >&2
            exit 1
        fi
        QUENCH_SRC="$TMP_DIR"
    elif command -v curl >/dev/null 2>&1; then
        printf 'Downloading Quench archive via curl...\n'
        if ! curl -fsSL "$ARCHIVE_URL" | tar -xz -C "$TMP_DIR" --strip-components=1 >/dev/null 2>&1; then
            printf 'Error: Failed to download Quench archive from %s\n' "$ARCHIVE_URL" >&2
            exit 1
        fi
        QUENCH_SRC="$TMP_DIR"
    elif command -v wget >/dev/null 2>&1; then
        printf 'Downloading Quench archive via wget...\n'
        if ! wget -qO- "$ARCHIVE_URL" | tar -xz -C "$TMP_DIR" --strip-components=1 >/dev/null 2>&1; then
            printf 'Error: Failed to download Quench archive from %s\n' "$ARCHIVE_URL" >&2
            exit 1
        fi
        QUENCH_SRC="$TMP_DIR"
    else
        printf 'Error: Neither git, curl, nor wget was found in PATH.\n' >&2
        exit 1
    fi
fi

# Ensure target directory exists
mkdir -p "$TARGET"
RESOLVED_TARGET=$(cd "$TARGET" 2>/dev/null && pwd || printf '%s' "$TARGET")

printf 'Initializing Quench (%s) in: %s\n' "$TOOL" "$RESOLVED_TARGET"

COPIED_COUNT=0

copy_item() {
    src_rel="$1"
    dst_rel="$2"
    src_full="$QUENCH_SRC/$src_rel"
    dst_full="$TARGET/$dst_rel"

    if [ ! -f "$src_full" ]; then
        printf 'Warning: Source template missing: %s\n' "$src_rel"
        return
    fi

    if [ -f "$dst_full" ] && [ "$FORCE" -eq 0 ]; then
        printf '  Skipped (already exists): %s (use --force to overwrite)\n' "$dst_rel"
        return
    fi

    dst_dir=$(dirname "$dst_full")
    mkdir -p "$dst_dir"

    is_overwrite=0
    if [ -f "$dst_full" ]; then
        is_overwrite=1
    fi

    cp "$src_full" "$dst_full"
    COPIED_COUNT=$((COPIED_COUNT + 1))

    if [ "$is_overwrite" -eq 1 ]; then
        printf '  Overwritten: %s\n' "$dst_rel"
    else
        printf '  Installed: %s\n' "$dst_rel"
    fi
}

install_tool() {
    case "$1" in
        cursor)
            copy_item "adapters/cursor/.cursorrules" ".cursorrules"
            copy_item "adapters/cursor/.cursor/rules/steel-mind.mdc" ".cursor/rules/steel-mind.mdc"
            copy_item "adapters/cursor/.cursor/rules/plaincast.mdc" ".cursor/rules/plaincast.mdc"
            copy_item "adapters/cursor/.cursor/rules/leakguard.mdc" ".cursor/rules/leakguard.mdc"
            copy_item "adapters/cursor/.cursor/rules/precision-output.mdc" ".cursor/rules/precision-output.mdc"
            ;;
        copilot)
            copy_item "adapters/copilot/copilot-instructions.md" ".github/copilot-instructions.md"
            ;;
        kilo)
            copy_item "adapters/kilo/kilo.jsonc" "kilo.jsonc"
            copy_item "adapters/kilo/.kilo/rules/steel-mind.md" ".kilo/rules/steel-mind.md"
            copy_item "adapters/kilo/.kilo/rules/plaincast.md" ".kilo/rules/plaincast.md"
            copy_item "adapters/kilo/.kilo/rules/leakguard.md" ".kilo/rules/leakguard.md"
            copy_item "adapters/kilo/.kilo/rules/precision-output.md" ".kilo/rules/precision-output.md"
            ;;
        cline)
            copy_item "adapters/cline/.clinerules/steel-mind.md" ".clinerules/steel-mind.md"
            copy_item "adapters/cline/.clinerules/plaincast.md" ".clinerules/plaincast.md"
            copy_item "adapters/cline/.clinerules/leakguard.md" ".clinerules/leakguard.md"
            copy_item "adapters/cline/.clinerules/precision-output.md" ".clinerules/precision-output.md"
            ;;
        windsurf)
            copy_item "adapters/windsurf/.windsurfrules" ".windsurfrules"
            ;;
        claude)
            copy_item "adapters/claude/CLAUDE.md" "CLAUDE.md"
            ;;
        generic)
            copy_item "adapters/generic/system-prompt.md" "system-prompt.md"
            ;;
        aider)
            copy_item "adapters/aider/CONVENTIONS.md" "CONVENTIONS.md"
            ;;
        zed)
            copy_item "adapters/zed/.zedprompts/steel-mind.md" ".zedprompts/steel-mind.md"
            copy_item "adapters/zed/.zedprompts/plaincast.md" ".zedprompts/plaincast.md"
            copy_item "adapters/zed/.zedprompts/leakguard.md" ".zedprompts/leakguard.md"
            copy_item "adapters/zed/.zedprompts/precision-output.md" ".zedprompts/precision-output.md"
            ;;
        junie)
            copy_item "adapters/junie/.junie/rules/steel-mind.md" ".junie/rules/steel-mind.md"
            copy_item "adapters/junie/.junie/rules/plaincast.md" ".junie/rules/plaincast.md"
            copy_item "adapters/junie/.junie/rules/leakguard.md" ".junie/rules/leakguard.md"
            copy_item "adapters/junie/.junie/rules/precision-output.md" ".junie/rules/precision-output.md"
            ;;
        antigravity)
            copy_item "adapters/antigravity/.agents/rules/AGENTS.md" ".agents/rules/AGENTS.md"
            ;;
        rules)
            copy_item "rules/AGENTS.md" "AGENTS.md"
            ;;
    esac
}

if [ "$TOOL" = "all" ]; then
    install_tool "cursor"
    install_tool "copilot"
    install_tool "kilo"
    install_tool "cline"
    install_tool "windsurf"
    install_tool "claude"
    install_tool "generic"
    install_tool "aider"
    install_tool "zed"
    install_tool "junie"
    install_tool "antigravity"
    install_tool "rules"
else
    install_tool "$TOOL"
fi

if [ "$HOOKS" -eq 1 ]; then
    printf 'Installing Git validation hooks...\n'
    mkdir -p "$TARGET/.githooks"

    for hook in pre-commit commit-msg; do
        src_hook="$QUENCH_SRC/.githooks/$hook"
        if [ -f "$src_hook" ]; then
            dst_hook="$TARGET/.githooks/$hook"
            cp "$src_hook" "$dst_hook"
            chmod 755 "$dst_hook" 2>/dev/null || true
            printf '  Configured hook: .githooks/%s\n' "$hook"

            if [ -d "$TARGET/.git" ]; then
                mkdir -p "$TARGET/.git/hooks"
                dst_git_hook="$TARGET/.git/hooks/$hook"
                cp "$src_hook" "$dst_git_hook"
                chmod 755 "$dst_git_hook" 2>/dev/null || true
                printf '  Configured hook: .git/hooks/%s\n' "$hook"
            fi
        fi
    done

    if [ -d "$TARGET/.git" ] && command -v git >/dev/null 2>&1; then
        (cd "$TARGET" && git config core.hooksPath .githooks 2>/dev/null) || true
    fi
fi

printf '\nQuench initialization complete. %d file(s) configured.\n' "$COPIED_COUNT"
