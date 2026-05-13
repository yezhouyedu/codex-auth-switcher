# Codex Auth Switcher

A small local tool for switching between multiple saved Codex `auth.json` files.

It supports both:

- a simple Tkinter GUI
- a CLI for scripting

The tool never prints token values. It only validates that files are JSON,
copies whole files, and stores SHA-256 fingerprints so it can tell which saved
profile matches the active `auth.json`.

## Why

Codex currently reads one active auth file, usually:

```text
C:\Users\<you>\.codex\auth.json
```

If you have multiple accounts, you can save each account's `auth.json` as a
profile and switch the active file when needed.

## Install

Requires Python 3.10+.

Clone or download this folder, then run:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

On Windows, you can also double-click `setup-venv.bat`.

If the Qt UI reports a `QtCore` DLL loading error on Windows, install or repair
Microsoft Visual C++ Redistributable:

```powershell
winget install Microsoft.VCRedist.2015+.x64
```

Then open the GUI:

```powershell
.\.venv\Scripts\python.exe .\codex_auth_switcher.py
```

By default this opens the GUI.

On Windows, you can also double-click:

```text
run-gui.bat
```

## CLI Usage

The GUI has a language selector in the top-right corner. English mode uses
English labels throughout; Chinese mode uses Chinese labels throughout.

The GUI also detects whether the npm Codex CLI is installed. If only the
Microsoft Store / WindowsApps Codex command is found, `Login & Save` is
disabled and the app shows install buttons:

- `Install / Repair CLI`: installs `@openai/codex` globally with npm and shows diagnostics.
- `Install CLI & Login`: installs the CLI, then runs `codex login --device-auth`.

Save the current Codex auth as a profile:

```powershell
python .\codex_auth_switcher.py save main --note "primary account"
```

Import an auth file you copied elsewhere:

```powershell
python .\codex_auth_switcher.py save alt --from C:\path\to\auth.json
```

Run Codex login and save the resulting auth file:

```powershell
python .\codex_auth_switcher.py login-save alt --note "secondary account"
```

If your Codex login command is different:

```powershell
python .\codex_auth_switcher.py login-save alt --command "codex login"
```

The default login command is:

```powershell
codex login --device-auth
```

On Windows, the tool opens a separate PowerShell terminal for the login command
so Codex can show device-code or browser-auth prompts. Finish the login there,
then press Enter to return to the app.

List profiles:

```powershell
python .\codex_auth_switcher.py list
```

Switch active Codex auth:

```powershell
python .\codex_auth_switcher.py switch alt
```

Show which saved profile matches the active auth:

```powershell
python .\codex_auth_switcher.py current
```

Open the GUI:

```powershell
python .\codex_auth_switcher.py gui
```

## Where Profiles Are Stored

By default:

```text
C:\Users\<you>\.codex\auth_profiles\
```

Each profile is stored as:

```text
<profile-name>.auth.json
```

The active file is still:

```text
C:\Users\<you>\.codex\auth.json
```

Before switching, the current active file is backed up next to it as:

```text
auth.json.backup-YYYYMMDD-HHMMSS
```

## Security Notes

Do not commit real profile files. This repository's `.gitignore` excludes:

- `*.auth.json`
- `auth.json`
- `auth_profiles/`
- backup auth files

Treat saved profiles like passwords. Keep the profile directory local and
private.

`Login & Save` and `login-save` run the configured Codex login command, then
save the active `auth.json` as a profile. When testing, point `--auth-path` and
`--profile-dir` at temporary files first.

The login-save flow is transactional. The tool copies the previous `auth.json`
before running login. If login fails, exits early, or profile saving fails, the
previous active file is restored. The new auth remains active only after the
profile is saved successfully.

## Custom Paths

For testing or unusual setups:

```powershell
python .\codex_auth_switcher.py --auth-path C:\tmp\auth.json --profile-dir C:\tmp\profiles list
```
