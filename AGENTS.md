# GAMER PAT Repository Guide

## Non-Negotiable Rules
- Always keep `AGENT_INSTALL.md` and `README.md` consistent.
- Do not modify the core instruction content (Main / Literature / Writing / Reviewers / Gaming) unless explicitly requested.
- When updating `loglm`-related behavior, align documentation with the latest public source: `https://github.com/ks91/loglm`.
- Keep text files in UTF-8 (no BOM).

## Scope
- This file defines repository maintenance rules for GAMER PAT development.
- End-user runtime prerequisites (TeX, PDF viewers, etc.) belong in `AGENT_INSTALL.md`, not here.

## Source Files
- Prompt package for installation: `AGENT_INSTALL.md`
- Installation and usage documentation: `README.md`
- Research guidance logic: instruction texts (Main / Literature / Writing / Reviewers / Gaming)

## Update Policy
- For prompt behavior changes:
  1. Clarify intent.
  2. Update `AGENT_INSTALL.md`.
  3. Update related `README.md` sections when behavior or setup guidance changes.
- For `loglm` specification changes:
  - Update the install section in `README.md` without leaving stale resolution/output descriptions.

## Log Reference (When Running via loglm)
- `loglm` creates `logs/` under the directory where it is launched.
- Typical filename pattern: `logs/loglm-<agent>-log-YYYYMMDD-HHMMSS-pid<PID>.txt`.
- Prefer decoding raw logs before reading: `loglm-decode <raw-log-path>`.
- If decoding succeeds, inspect the decoded output first; if `loglm-decode` is unavailable, fall back to raw logs.
- Use these logs when you need cross-context continuity for prior user interactions or operation history.

## Validation Checklist
- `AGENT_INSTALL.md` and `README.md` are consistent.
- `loglm` behavior descriptions match `https://github.com/ks91/loglm`.
- Files remain UTF-8 encoded.
- Diffs are scoped to intended files only.
