# GAMER PAT Repository Guide

## Non-Negotiable Rules
- Always keep `AGENT_INSTALL.md`, `README.md`, and `gamer-pat-claude-agent.md` consistent where they overlap.
- Do not modify the core instruction content (Main / Literature / Writing / Reviewers / Gaming) unless explicitly requested.
- When updating `loglm`-related behavior, align documentation with the latest public source: `https://github.com/ks91/loglm`.
- Keep text files in UTF-8 (no BOM).

## Scope
- This file defines repository maintenance rules for GAMER PAT development.
- End-user runtime prerequisites (TeX, PDF viewers, etc.) belong in `AGENT_INSTALL.md`, not here.

## Source Files
- Prompt package for installation: `AGENT_INSTALL.md`
- Installation and usage documentation: `README.md`
- Discord agent import source: `gamer-pat-claude-agent.md`
- Research guidance logic: instruction texts (Main / Literature / Writing / Reviewers / Gaming)

## Update Policy
- For prompt behavior changes:
  1. Clarify intent.
  2. Update `AGENT_INSTALL.md`.
  3. Update `gamer-pat-claude-agent.md` when the Claude/Discord import version contains duplicated prompt sections affected by the change.
  4. Update related `README.md` sections when behavior or setup guidance changes.
- For `loglm` specification changes:
  - Update the install section in `README.md` without leaving stale resolution/output descriptions.
- For Discord agent import changes:
  - Keep `gamer-pat-claude-agent.md` aligned with the current import format used by `discord-agent-hub`:
    `https://github.com/ks91/discord-agent-hub`

## Log Reference (When Running via loglm)
- `loglm` creates `logs/` under the directory where it is launched.
- Typical filename pattern: `logs/loglm-<agent>-log-YYYYMMDD-HHMMSS-pid<PID>.txt`.
- Prefer decoding raw logs before reading: `loglm-decode <raw-log-path>`.
- If decoding succeeds, inspect the decoded output first; if `loglm-decode` is unavailable, fall back to raw logs.
- Use these logs when you need cross-context continuity for prior user interactions or operation history.

## Validation Checklist
- `AGENT_INSTALL.md`, `README.md`, and `gamer-pat-claude-agent.md` are consistent where they intentionally overlap.
- `loglm` behavior descriptions match `https://github.com/ks91/loglm`.
- Discord import metadata and structure match `https://github.com/ks91/discord-agent-hub` expectations when that file is touched.
- Files remain UTF-8 encoded.
- Diffs are scoped to intended files only.
