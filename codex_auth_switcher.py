#!/usr/bin/env python3
"""Switch between saved Codex auth.json profiles.

The tool never prints token values. It copies whole auth.json files between a
private profile directory and the active Codex config path.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import shutil
import sys
import tempfile
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


APP_NAME = "Codex Auth Switcher"
DEFAULT_CODEX_DIR = Path.home() / ".codex"
DEFAULT_AUTH_PATH = DEFAULT_CODEX_DIR / "auth.json"
DEFAULT_PROFILE_DIR = DEFAULT_CODEX_DIR / "auth_profiles"
META_NAME = "profiles.json"
DEFAULT_LOGIN_COMMAND = "codex login --device-auth"


UI_TEXT = {
    "zh": {
        "window_title": "Codex 账号切换器",
        "app_title": "Codex 账号切换器",
        "subtitle": "本地保存、登录、切换 Codex 账号；不会显示 token 内容。",
        "language_label": "界面语言 / Language",
        "language_values": {"zh": "中文", "en": "英文"},
        "active_kicker": "当前账号",
        "profile_count": "{count} 个账号",
        "selected_kicker": "选中账号",
        "selected_empty": "尚未选中账号",
        "selected_name_label": "账号",
        "selected_fingerprint_label": "指纹",
        "selected_note_label": "备注",
        "selected_last_used_label": "上次使用",
        "active_unknown": "未识别或未保存",
        "auth_path": "认证文件",
        "refresh": "刷新",
        "profile": "账号备注",
        "fingerprint": "指纹",
        "note": "备注",
        "last_used": "上次使用",
        "actions": "操作",
        "login_save": "登录并保存",
        "save_current": "保存当前认证",
        "import_file": "导入认证文件",
        "switch_selected": "切换选中账号",
        "delete_selected": "删除选中账号",
        "storage": "保存位置",
        "storage_hint": "账号文件只保存在本机 .codex 目录，请不要提交到 GitHub。",
        "safety": "安全提示",
        "safety_hint": "切换前会自动备份当前 auth.json；登录功能会执行你填写的命令。",
        "ready": "就绪。找到 {count} 个账号。",
        "select_first": "请先选中一个账号。",
        "save_dialog": "保存当前认证",
        "save_action": "保存",
        "import_dialog": "导入认证文件",
        "import_action": "导入",
        "login_dialog": "登录并保存新账号",
        "login_action": "开始登录",
        "profile_name": "账号备注",
        "profile_name_hint": "例如 main、backup、work",
        "note_field": "备注",
        "note_hint": "可选，例如主账号或备用账号",
        "login_command": "登录命令",
        "overwrite": "如果同名账号已存在，则覆盖",
        "cancel": "取消",
        "json_files": "JSON 文件",
        "all_files": "所有文件",
        "confirm_login": "现在会运行登录命令。登录成功后，新的 auth.json 会保存为账号 profile。",
        "confirm_switch": "确认切换当前 Codex 认证到“{name}”？",
        "confirm_delete": "确认删除保存的账号“{name}”？这不会删除当前 active auth.json。",
        "switched": "已切换到 {name}。",
        "backup": "备份文件：{path}",
        "saved_after_login": "登录完成，已保存账号“{name}”。",
        "login_busy": "正在运行登录命令。完成浏览器或终端登录后，请回到这里等待。",
        "login_failed": "登录失败，账号没有保存。",
        "error_title": "出错了",
        "info_title": "提示",
        "confirm_title": "确认操作",
    },
    "en": {
        "window_title": "Codex Auth Switcher",
        "app_title": "Codex Auth Switcher",
        "subtitle": "Save, log in, and switch Codex accounts locally without exposing tokens.",
        "language_label": "Language / 界面语言",
        "language_values": {"zh": "Chinese", "en": "English"},
        "active_kicker": "Active Profile",
        "profile_count": "{count} profile(s)",
        "selected_kicker": "Selected Profile",
        "selected_empty": "No profile selected",
        "selected_name_label": "Profile",
        "selected_fingerprint_label": "Fingerprint",
        "selected_note_label": "Note",
        "selected_last_used_label": "Last used",
        "active_unknown": "None or unknown",
        "auth_path": "Auth file",
        "refresh": "Refresh",
        "profile": "Profile",
        "fingerprint": "Fingerprint",
        "note": "Note",
        "last_used": "Last used",
        "actions": "Actions",
        "login_save": "Login & Save",
        "save_current": "Save Current",
        "import_file": "Import File",
        "switch_selected": "Switch Selected",
        "delete_selected": "Delete Selected",
        "storage": "Storage",
        "storage_hint": "Profiles stay under your local .codex folder. Do not commit them to GitHub.",
        "safety": "Safety",
        "safety_hint": "The current auth.json is backed up before switching. Login runs the command you enter.",
        "ready": "Ready. {count} profile(s) found.",
        "select_first": "Select a profile first.",
        "save_dialog": "Save Current Auth",
        "save_action": "Save",
        "import_dialog": "Import Auth File",
        "import_action": "Import",
        "login_dialog": "Login and Save New Auth",
        "login_action": "Start Login",
        "profile_name": "Profile name",
        "profile_name_hint": "For example main, backup, or work",
        "note_field": "Note",
        "note_hint": "Optional, such as primary or secondary account",
        "login_command": "Login command",
        "overwrite": "Overwrite profile if it already exists",
        "cancel": "Cancel",
        "json_files": "JSON files",
        "all_files": "All files",
        "confirm_login": "The login command will run now. When it succeeds, the new auth.json will be saved as a profile.",
        "confirm_switch": "Switch active Codex auth.json to '{name}'?",
        "confirm_delete": "Delete saved profile '{name}'? This does not delete active auth.json.",
        "switched": "Switched to {name}.",
        "backup": "Backup: {path}",
        "saved_after_login": "Saved profile '{name}' after login.",
        "login_busy": "Running login command. Complete the browser or terminal login flow, then wait here.",
        "login_failed": "Login failed or profile was not saved.",
        "error_title": "Error",
        "info_title": "Info",
        "confirm_title": "Confirm",
    },
}


class SwitcherError(Exception):
    """A user-facing error."""


@dataclass(frozen=True)
class Profile:
    name: str
    path: Path
    created_at: str | None = None
    last_used_at: str | None = None
    sha256: str | None = None
    note: str | None = None


@dataclass(frozen=True)
class LoginResult:
    profile: Profile
    backup: Path | None
    returncode: int


@dataclass(frozen=True)
class CodexCliStatus:
    available: bool
    usable_for_login: bool
    path: str | None
    version: str | None
    message: str


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def safe_profile_name(name: str) -> str:
    cleaned = name.strip()
    if not cleaned:
        raise SwitcherError("Profile name cannot be empty.")
    if cleaned in {".", ".."}:
        raise SwitcherError("Profile name is not allowed.")
    bad_chars = set('/\\:*?"<>|')
    if any(ch in bad_chars or ord(ch) < 32 for ch in cleaned):
        raise SwitcherError('Profile name cannot contain / \\ : * ? " < > | or control characters.')
    return cleaned


def profile_file(profile_dir: Path, name: str) -> Path:
    return profile_dir / f"{safe_profile_name(name)}.auth.json"


def meta_file(profile_dir: Path) -> Path:
    return profile_dir / META_NAME


def read_json_file(path: Path) -> object:
    try:
        with path.open("r", encoding="utf-8-sig") as fh:
            return json.load(fh)
    except FileNotFoundError as exc:
        raise SwitcherError(f"File does not exist: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SwitcherError(f"File is not valid JSON: {path}") from exc


def validate_auth_json(path: Path) -> None:
    data = read_json_file(path)
    if not isinstance(data, dict):
        raise SwitcherError(f"Expected a JSON object in {path}")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_meta(profile_dir: Path) -> dict[str, dict[str, str]]:
    path = meta_file(profile_dir)
    if not path.exists():
        return {}
    data = read_json_file(path)
    if not isinstance(data, dict):
        raise SwitcherError(f"Metadata is corrupt: {path}")
    profiles = data.get("profiles", {})
    if not isinstance(profiles, dict):
        raise SwitcherError(f"Metadata is corrupt: {path}")
    return profiles


def save_meta(profile_dir: Path, profiles: dict[str, dict[str, str]]) -> None:
    profile_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": 1,
        "updated_at": utc_now(),
        "profiles": profiles,
    }
    atomic_write_json(meta_file(profile_dir), payload)


def atomic_write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
        os.replace(tmp, path)
    finally:
        if tmp.exists():
            tmp.unlink()


def atomic_copy(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{dst.name}.", suffix=".tmp", dir=dst.parent)
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, "wb") as out, src.open("rb") as inp:
            shutil.copyfileobj(inp, out)
        os.replace(tmp, dst)
    finally:
        if tmp.exists():
            tmp.unlink()


def backup_active_auth(auth_path: Path) -> Path | None:
    if not auth_path.exists():
        return None
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = auth_path.with_name(f"{auth_path.name}.backup-{stamp}")
    shutil.copy2(auth_path, backup)
    return backup


def snapshot_active_auth(auth_path: Path) -> Path | None:
    if not auth_path.exists():
        return None
    fd, tmp_name = tempfile.mkstemp(prefix="codex-auth-snapshot-", suffix=".json")
    os.close(fd)
    snapshot = Path(tmp_name)
    shutil.copy2(auth_path, snapshot)
    return snapshot


def restore_active_auth(auth_path: Path, snapshot: Path | None) -> None:
    if snapshot is None:
        if auth_path.exists():
            auth_path.unlink()
        return
    atomic_copy(snapshot, auth_path)


def save_snapshot_backup(auth_path: Path, snapshot: Path | None) -> Path | None:
    if snapshot is None:
        return None
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = auth_path.with_name(f"{auth_path.name}.backup-{stamp}")
    shutil.copy2(snapshot, backup)
    return backup


def save_profile(name: str, source: Path, profile_dir: Path, note: str | None = None, overwrite: bool = False) -> Profile:
    name = safe_profile_name(name)
    source = source.expanduser()
    validate_auth_json(source)
    profile_dir.mkdir(parents=True, exist_ok=True)
    target = profile_file(profile_dir, name)
    if target.exists() and not overwrite:
        raise SwitcherError(f"Profile already exists: {name}. Use --overwrite to replace it.")

    atomic_copy(source, target)
    digest = sha256_file(target)
    profiles = load_meta(profile_dir)
    existing = profiles.get(name, {})
    profiles[name] = {
        "created_at": existing.get("created_at", utc_now()),
        "updated_at": utc_now(),
        "sha256": digest,
    }
    if note:
        profiles[name]["note"] = note
    elif existing.get("note"):
        profiles[name]["note"] = existing["note"]
    save_meta(profile_dir, profiles)
    return Profile(name=name, path=target, sha256=digest, note=profiles[name].get("note"))


def list_profiles(profile_dir: Path) -> list[Profile]:
    profile_dir.mkdir(parents=True, exist_ok=True)
    profiles = load_meta(profile_dir)
    found: list[Profile] = []
    for path in sorted(profile_dir.glob("*.auth.json")):
        name = path.name.removesuffix(".auth.json")
        meta = profiles.get(name, {})
        found.append(
            Profile(
                name=name,
                path=path,
                created_at=meta.get("created_at"),
                last_used_at=meta.get("last_used_at"),
                sha256=meta.get("sha256") or sha256_file(path),
                note=meta.get("note"),
            )
        )
    return found


def switch_profile(name: str, auth_path: Path, profile_dir: Path, no_backup: bool = False) -> tuple[Profile, Path | None]:
    name = safe_profile_name(name)
    src = profile_file(profile_dir, name)
    validate_auth_json(src)
    backup = None if no_backup else backup_active_auth(auth_path)
    atomic_copy(src, auth_path)

    profiles = load_meta(profile_dir)
    entry = profiles.setdefault(name, {})
    entry["last_used_at"] = utc_now()
    entry["sha256"] = sha256_file(src)
    save_meta(profile_dir, profiles)
    return Profile(name=name, path=src, sha256=entry["sha256"], note=entry.get("note")), backup


def active_fingerprint(auth_path: Path) -> str | None:
    if not auth_path.exists():
        return None
    validate_auth_json(auth_path)
    return sha256_file(auth_path)


def detect_active_profile(auth_path: Path, profile_dir: Path) -> Profile | None:
    digest = active_fingerprint(auth_path)
    if not digest:
        return None
    for profile in list_profiles(profile_dir):
        if profile.sha256 == digest:
            return profile
    return None


def delete_profile(name: str, profile_dir: Path) -> None:
    name = safe_profile_name(name)
    path = profile_file(profile_dir, name)
    if not path.exists():
        raise SwitcherError(f"Profile does not exist: {name}")
    path.unlink()
    profiles = load_meta(profile_dir)
    profiles.pop(name, None)
    save_meta(profile_dir, profiles)


def npm_global_bin_dir() -> Path | None:
    try:
        completed = subprocess.run(
            ["npm", "prefix", "-g"],
            capture_output=True,
            text=True,
            timeout=10,
            shell=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if completed.returncode != 0:
        return None
    prefix = completed.stdout.strip()
    return Path(prefix) if prefix else None


def npm_codex_command() -> Path | None:
    npm_bin = npm_global_bin_dir()
    if not npm_bin:
        return None
    for name in ("codex.cmd", "codex.exe", "codex"):
        candidate = npm_bin / name
        if candidate.exists():
            return candidate
    return None


def where_codex_candidates() -> list[str]:
    if os.name == "nt":
        try:
            completed = subprocess.run(
                ["where.exe", "codex"],
                capture_output=True,
                text=True,
                timeout=10,
                shell=False,
            )
        except (OSError, subprocess.SubprocessError):
            return []
        if completed.returncode == 0:
            return [line.strip() for line in completed.stdout.splitlines() if line.strip()]
        return []
    found = shutil.which("codex")
    return [found] if found else []


def codex_cli_status() -> CodexCliStatus:
    npm_cmd = npm_codex_command()
    candidates = where_codex_candidates()
    chosen = str(npm_cmd) if npm_cmd else (candidates[0] if candidates else None)
    if not chosen:
        return CodexCliStatus(
            available=False,
            usable_for_login=False,
            path=None,
            version=None,
            message="Codex CLI is not installed. Install npm package @openai/codex.",
        )

    normalized = chosen.lower()
    if "windowsapps" in normalized and "openai.codex" in normalized and not npm_cmd:
        return CodexCliStatus(
            available=True,
            usable_for_login=False,
            path=chosen,
            version=None,
            message="Found the Microsoft Store Codex app command, not the npm Codex CLI. Install @openai/codex for login automation.",
        )

    version = None
    try:
        completed = subprocess.run(
            [chosen, "--version"],
            capture_output=True,
            text=True,
            timeout=15,
            shell=False,
        )
        if completed.returncode == 0:
            version = (completed.stdout or completed.stderr).strip()
    except (OSError, subprocess.SubprocessError):
        return CodexCliStatus(
            available=True,
            usable_for_login=False,
            path=chosen,
            version=None,
            message="Codex command was found, but it could not be executed.",
        )

    if npm_cmd:
        return CodexCliStatus(
            available=True,
            usable_for_login=True,
            path=str(npm_cmd),
            version=version,
            message="npm Codex CLI is ready.",
        )

    return CodexCliStatus(
        available=True,
        usable_for_login="windowsapps" not in normalized,
        path=chosen,
        version=version,
        message="Codex CLI is ready." if "windowsapps" not in normalized else "Codex command is not suitable for login automation.",
    )


def resolve_login_command(command: str) -> str:
    command = command.strip()
    if command == DEFAULT_LOGIN_COMMAND or command.startswith("codex login"):
        status = codex_cli_status()
        if not status.usable_for_login or not status.path:
            raise SwitcherError(status.message)
        return command.replace("codex", f'"{status.path}"', 1)
    return command


def run_codex_cli_setup(continue_to_login: bool = False) -> int:
    login_line = (
        "& $codexCmd login --device-auth"
        if continue_to_login
        else "Write-Host 'Skipping login. You can run it later from the app.'"
    )
    ps_script = (
        "$ErrorActionPreference = 'Continue'; "
        "Write-Host 'Installing npm Codex CLI (@openai/codex)...' -ForegroundColor Cyan; "
        "npm i -g @openai/codex; "
        "$installCode = $LASTEXITCODE; "
        "$npmPrefix = (npm prefix -g).Trim(); "
        "$codexCmd = Join-Path $npmPrefix 'codex.cmd'; "
        "Write-Host ''; "
        "Write-Host 'where codex:' -ForegroundColor Cyan; "
        "where.exe codex; "
        "Write-Host ''; "
        "Write-Host \"npm codex path: $codexCmd\" -ForegroundColor Cyan; "
        "Write-Host 'codex --version:' -ForegroundColor Cyan; "
        "& $codexCmd --version; "
        "$versionCode = $LASTEXITCODE; "
        "Write-Host ''; "
        "if ($installCode -eq 0 -and $versionCode -eq 0) { "
        "Write-Host 'Codex CLI installation looks good.' -ForegroundColor Green; "
        f"{login_line}; "
        "} else { Write-Host 'Codex CLI setup did not complete cleanly.' -ForegroundColor Red }; "
        "Write-Host ''; "
        "Read-Host 'Press Enter to return to Codex Auth Switcher'; "
        "exit $installCode"
    )
    if os.name == "nt":
        completed = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
            cwd=str(Path.home()),
            creationflags=subprocess.CREATE_NEW_CONSOLE,
        )
        return completed.returncode
    completed = subprocess.run("npm i -g @openai/codex && codex --version", shell=True, cwd=str(Path.home()))
    return completed.returncode


def run_login_command(command: str) -> int:
    command = resolve_login_command(command)
    if not command:
        raise SwitcherError("Login command cannot be empty.")
    try:
        if os.name == "nt":
            ps_script = (
                "$ErrorActionPreference = 'Continue'; "
                "Write-Host 'Codex Auth Switcher login command:'; "
                f"Write-Host {json.dumps(command)}; "
                "Write-Host ''; "
                f"& cmd.exe /d /s /c {json.dumps(command)}; "
                "$code = $LASTEXITCODE; "
                "Write-Host ''; "
                "if ($code -eq 0) { Write-Host 'Login command completed successfully.' -ForegroundColor Green } "
                "else { Write-Host \"Login command failed with exit code $code.\" -ForegroundColor Red }; "
                "Read-Host 'Press Enter to return to Codex Auth Switcher'; "
                "exit $code"
            )
            completed = subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
                cwd=str(Path.home()),
                creationflags=subprocess.CREATE_NEW_CONSOLE,
            )
        else:
            completed = subprocess.run(command, shell=True, cwd=str(Path.home()))
    except OSError as exc:
        raise SwitcherError(f"Could not run login command: {exc}") from exc
    return completed.returncode


def login_and_save_profile(
    name: str,
    command: str,
    auth_path: Path,
    profile_dir: Path,
    note: str | None = None,
    overwrite: bool = False,
) -> LoginResult:
    snapshot = snapshot_active_auth(auth_path)
    backup: Path | None = None
    try:
        code = run_login_command(command)
        if code != 0:
            restore_active_auth(auth_path, snapshot)
            raise SwitcherError(f"Login command exited with code {code}. Previous auth.json was restored.")
        validate_auth_json(auth_path)
        profile = save_profile(name, auth_path, profile_dir, note=note, overwrite=overwrite)
        backup = save_snapshot_backup(auth_path, snapshot)
        return LoginResult(profile=profile, backup=backup, returncode=code)
    except Exception:
        restore_active_auth(auth_path, snapshot)
        raise
    finally:
        if snapshot and snapshot.exists():
            snapshot.unlink()


def print_profiles(profiles: Iterable[Profile], active: Profile | None) -> None:
    active_name = active.name if active else None
    rows = list(profiles)
    if not rows:
        print("No profiles saved yet.")
        return
    for profile in rows:
        mark = "*" if profile.name == active_name else " "
        digest = profile.sha256[:12] if profile.sha256 else "unknown"
        note = f" - {profile.note}" if profile.note else ""
        last = f", last used {profile.last_used_at}" if profile.last_used_at else ""
        print(f"{mark} {profile.name} ({digest}{last}){note}")


def run_gui(auth_path: Path, profile_dir: Path) -> int:
    try:
        import tkinter as tk
        from tkinter import filedialog, messagebox, ttk
    except ImportError as exc:
        raise SwitcherError("Tkinter is not available in this Python installation.") from exc

    lang = {"code": "zh"}

    def tr(key: str, **kwargs: object) -> str:
        text = UI_TEXT[lang["code"]][key]
        if isinstance(text, dict):
            raise KeyError(key)
        return text.format(**kwargs)

    def language_display(code: str) -> str:
        return UI_TEXT[lang["code"]]["language_values"][code]

    class ProfileDialog:
        def __init__(
            self,
            parent: tk.Tk,
            title_key: str,
            action_key: str,
            *,
            include_command: bool = False,
            default_command: str = DEFAULT_LOGIN_COMMAND,
        ) -> None:
            self.result: dict[str, object] | None = None
            self.window = tk.Toplevel(parent)
            self.window.title(tr(title_key))
            self.window.configure(bg=colors["panel"])
            self.window.resizable(False, False)
            self.window.transient(parent)
            self.window.grab_set()

            body = ttk.Frame(self.window, style="Panel.TFrame", padding=18)
            body.grid(row=0, column=0, sticky="nsew")
            ttk.Label(body, text=tr(title_key), style="DialogTitle.TLabel").grid(row=0, column=0, columnspan=2, sticky="w")

            ttk.Label(body, text=tr("profile_name"), style="Field.TLabel").grid(row=1, column=0, sticky="w", pady=(14, 4))
            self.name_var = tk.StringVar()
            name_entry = ttk.Entry(body, textvariable=self.name_var, width=38)
            name_entry.grid(row=2, column=0, columnspan=2, sticky="ew")

            ttk.Label(body, text=tr("note_field"), style="Field.TLabel").grid(row=3, column=0, sticky="w", pady=(12, 4))
            self.note_var = tk.StringVar()
            ttk.Entry(body, textvariable=self.note_var, width=38).grid(row=4, column=0, columnspan=2, sticky="ew")

            self.command_var = tk.StringVar(value=default_command)
            if include_command:
                ttk.Label(body, text=tr("login_command"), style="Field.TLabel").grid(row=5, column=0, sticky="w", pady=(12, 4))
                ttk.Entry(body, textvariable=self.command_var, width=38).grid(row=6, column=0, columnspan=2, sticky="ew")

            self.overwrite_var = tk.BooleanVar(value=False)
            row = 7 if include_command else 5
            ttk.Checkbutton(body, text=tr("overwrite"), variable=self.overwrite_var).grid(
                row=row, column=0, columnspan=2, sticky="w", pady=(12, 2)
            )

            actions = ttk.Frame(body, style="Panel.TFrame")
            actions.grid(row=row + 1, column=0, columnspan=2, sticky="e", pady=(16, 0))
            ttk.Button(actions, text=tr("cancel"), style="Ghost.TButton", command=self.cancel).pack(side="right")
            ttk.Button(actions, text=tr(action_key), style="Accent.TButton", command=self.submit).pack(side="right", padx=(0, 8))

            body.columnconfigure(1, weight=1)
            name_entry.focus_set()
            self.window.bind("<Return>", lambda _event: self.submit())
            self.window.bind("<Escape>", lambda _event: self.cancel())
            self.window.wait_window()

        def submit(self) -> None:
            self.result = {
                "name": self.name_var.get(),
                "note": self.note_var.get(),
                "command": self.command_var.get(),
                "overwrite": self.overwrite_var.get(),
            }
            self.window.destroy()

        def cancel(self) -> None:
            self.result = None
            self.window.destroy()

    root = tk.Tk()
    root.title(tr("window_title"))
    root.geometry("960x620")
    root.minsize(820, 520)

    colors = {
        "bg": "#eef1ed",
        "panel": "#fbf8f0",
        "panel_alt": "#f5efe3",
        "ink": "#151713",
        "muted": "#655f55",
        "line": "#d8ccba",
        "header": "#17211c",
        "accent": "#bd5b2b",
        "accent_dark": "#873915",
        "success": "#24724d",
    }
    root.configure(bg=colors["bg"])

    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure(".", font=("Segoe UI", 10), background=colors["bg"], foreground=colors["ink"])
    style.configure("Shell.TFrame", background=colors["bg"])
    style.configure("Header.TFrame", background=colors["header"])
    style.configure("Panel.TFrame", background=colors["panel"])
    style.configure("Side.TFrame", background=colors["panel_alt"])
    style.configure("Logo.TLabel", background=colors["accent"], foreground="#fff6e6", font=("Segoe UI Semibold", 16), padding=(12, 8))
    style.configure("Title.TLabel", background=colors["header"], foreground="#fff6e6", font=("Segoe UI Semibold", 20))
    style.configure("Subtitle.TLabel", background=colors["header"], foreground="#d8cbb7", font=("Segoe UI", 10))
    style.configure("Kicker.TLabel", background=colors["panel"], foreground=colors["muted"], font=("Segoe UI", 9))
    style.configure("KickerAlt.TLabel", background=colors["panel_alt"], foreground=colors["muted"], font=("Segoe UI", 9))
    style.configure("Active.TLabel", background=colors["panel"], foreground=colors["success"], font=("Segoe UI Semibold", 18))
    style.configure("Pill.TLabel", background="#e8dccb", foreground=colors["ink"], font=("Segoe UI Semibold", 9), padding=(12, 7))
    style.configure("Selected.TLabel", background=colors["panel_alt"], foreground=colors["ink"], font=("Segoe UI Semibold", 11))
    style.configure("Field.TLabel", background=colors["panel"], foreground=colors["muted"], font=("Segoe UI", 9))
    style.configure("FieldAlt.TLabel", background=colors["panel_alt"], foreground=colors["muted"], font=("Segoe UI", 9))
    style.configure("MonoAlt.TLabel", background=colors["panel_alt"], foreground=colors["muted"], font=("Consolas", 9))
    style.configure("DialogTitle.TLabel", background=colors["panel"], foreground=colors["ink"], font=("Segoe UI Semibold", 13))
    style.configure("Status.TLabel", background=colors["bg"], foreground=colors["muted"], font=("Segoe UI", 9))
    style.configure("Treeview", rowheight=34, background="#fffdf7", fieldbackground="#fffdf7", foreground=colors["ink"], borderwidth=0)
    style.configure("Treeview.Heading", background="#ddd0bd", foreground=colors["ink"], font=("Segoe UI Semibold", 9), relief="flat")
    style.map("Treeview", background=[("selected", "#eec49f")], foreground=[("selected", colors["ink"])])
    style.configure("Accent.TButton", background=colors["accent"], foreground="white", padding=(14, 10), borderwidth=0)
    style.map("Accent.TButton", background=[("active", colors["accent_dark"]), ("disabled", "#cdb9a9")])
    style.configure("Tool.TButton", background="#e8dccb", foreground=colors["ink"], padding=(14, 10), borderwidth=0)
    style.map("Tool.TButton", background=[("active", "#d9cbb8"), ("disabled", "#eee9df")])
    style.configure("Ghost.TButton", background=colors["panel"], foreground=colors["muted"], padding=(12, 8), borderwidth=1)
    style.configure("Lang.TCombobox", padding=(8, 4))

    status = tk.StringVar()
    active_var = tk.StringVar()
    auth_var = tk.StringVar(value=str(auth_path))
    profile_dir_var = tk.StringVar(value=str(profile_dir))
    language_var = tk.StringVar()
    busy = {"value": False}
    active_count = {"value": 0}

    shell = ttk.Frame(root, style="Shell.TFrame")
    shell.pack(fill="both", expand=True)

    header = ttk.Frame(shell, style="Header.TFrame", padding=(24, 18))
    header.pack(fill="x")
    ttk.Label(header, text="CA", style="Logo.TLabel").pack(side="left", padx=(0, 14))
    header_text = ttk.Frame(header, style="Header.TFrame")
    header_text.pack(side="left", fill="x", expand=True)
    title_label = ttk.Label(header_text, style="Title.TLabel")
    title_label.pack(anchor="w")
    subtitle_label = ttk.Label(header_text, style="Subtitle.TLabel")
    subtitle_label.pack(anchor="w", pady=(4, 0))

    lang_box = ttk.Frame(header, style="Header.TFrame")
    lang_box.pack(side="right")
    language_label = ttk.Label(lang_box, style="Subtitle.TLabel")
    language_label.pack(anchor="e", pady=(0, 4))
    language_combo = ttk.Combobox(lang_box, textvariable=language_var, state="readonly", width=10, style="Lang.TCombobox")
    language_combo.pack(anchor="e")

    content = ttk.Frame(shell, style="Shell.TFrame", padding=18)
    content.pack(fill="both", expand=True)

    summary = ttk.Frame(content, style="Panel.TFrame", padding=16)
    summary.pack(fill="x")
    left_summary = ttk.Frame(summary, style="Panel.TFrame")
    left_summary.pack(side="left", fill="x", expand=True)
    active_kicker_label = ttk.Label(left_summary, style="Kicker.TLabel")
    active_kicker_label.pack(anchor="w")
    ttk.Label(left_summary, textvariable=active_var, style="Active.TLabel").pack(anchor="w", pady=(3, 0))
    auth_path_label = ttk.Label(left_summary, style="Field.TLabel")
    auth_path_label.pack(anchor="w", pady=(6, 0))
    ttk.Label(left_summary, textvariable=auth_var, style="Field.TLabel").pack(anchor="w", pady=(2, 0))

    count_pill_label = ttk.Label(summary, style="Pill.TLabel")
    count_pill_label.pack(side="right", padx=(10, 0))
    refresh_button = ttk.Button(summary, style="Tool.TButton", command=lambda: refresh())
    refresh_button.pack(side="right")

    main = ttk.Frame(content, style="Shell.TFrame")
    main.pack(fill="both", expand=True, pady=(14, 0))

    table_panel = ttk.Frame(main, style="Panel.TFrame", padding=12)
    table_panel.pack(side="left", fill="both", expand=True)

    tree = ttk.Treeview(
        table_panel,
        columns=("name", "fingerprint", "note", "last_used"),
        show="headings",
        selectmode="browse",
    )
    tree.heading("name", text="Profile")
    tree.heading("fingerprint", text="Fingerprint")
    tree.heading("note", text="Note")
    tree.heading("last_used", text="Last used")
    tree.column("name", width=150, anchor="w")
    tree.column("fingerprint", width=120, anchor="w")
    tree.column("note", width=180, anchor="w")
    tree.column("last_used", width=170, anchor="w")
    tree.tag_configure("odd", background="#fffdf7")
    tree.tag_configure("even", background="#f7f0e6")
    tree.tag_configure("active", background="#dff0e7")
    table_scroll = ttk.Scrollbar(table_panel, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=table_scroll.set)
    tree.pack(side="left", fill="both", expand=True)
    table_scroll.pack(side="right", fill="y")

    side = ttk.Frame(main, style="Side.TFrame", padding=16)
    side.pack(side="right", fill="y", padx=(14, 0))

    actions_label = ttk.Label(side, style="KickerAlt.TLabel")
    actions_label.pack(anchor="w", pady=(0, 8))
    action_buttons: list[ttk.Button] = []
    buttons_by_key: dict[str, ttk.Button] = {}

    def add_button(key: str, command, style_name: str = "Tool.TButton") -> ttk.Button:
        btn = ttk.Button(side, style=style_name, command=command)
        btn.pack(fill="x", pady=4)
        action_buttons.append(btn)
        buttons_by_key[key] = btn
        return btn

    add_button("login_save", lambda: on_login_save(), "Accent.TButton")
    add_button("save_current", lambda: on_save_current())
    add_button("import_file", lambda: on_import())
    add_button("switch_selected", lambda: on_switch())
    add_button("delete_selected", lambda: on_delete())

    selected_label = ttk.Label(side, style="KickerAlt.TLabel")
    selected_label.pack(anchor="w", pady=(20, 6))
    selected_name_var = tk.StringVar()
    selected_fingerprint_var = tk.StringVar()
    selected_note_var = tk.StringVar()
    selected_last_used_var = tk.StringVar()
    selected_name_label = ttk.Label(side, textvariable=selected_name_var, style="Selected.TLabel", wraplength=210)
    selected_name_label.pack(anchor="w", fill="x")
    selected_fingerprint_label = ttk.Label(side, textvariable=selected_fingerprint_var, style="MonoAlt.TLabel", wraplength=210)
    selected_fingerprint_label.pack(anchor="w", fill="x", pady=(8, 0))
    selected_note_label = ttk.Label(side, textvariable=selected_note_var, style="FieldAlt.TLabel", wraplength=210)
    selected_note_label.pack(anchor="w", fill="x", pady=(8, 0))
    selected_last_used_label = ttk.Label(side, textvariable=selected_last_used_var, style="FieldAlt.TLabel", wraplength=210)
    selected_last_used_label.pack(anchor="w", fill="x", pady=(8, 0))

    storage_label = ttk.Label(side, style="KickerAlt.TLabel")
    storage_label.pack(anchor="w", pady=(20, 6))
    storage_hint_label = ttk.Label(side, style="FieldAlt.TLabel", wraplength=210)
    storage_hint_label.pack(anchor="w")
    ttk.Label(side, textvariable=profile_dir_var, style="FieldAlt.TLabel", wraplength=210).pack(anchor="w", pady=(8, 0))

    safety_label = ttk.Label(side, style="KickerAlt.TLabel")
    safety_label.pack(anchor="w", pady=(20, 6))
    safety_hint_label = ttk.Label(side, style="FieldAlt.TLabel", wraplength=210)
    safety_hint_label.pack(anchor="w")

    def selected_name() -> str | None:
        selection = tree.selection()
        if not selection:
            return None
        return str(tree.item(selection[0], "values")[0]).lstrip("* ").strip()

    def update_selected() -> None:
        selection = tree.selection()
        if not selection:
            selected_name_var.set(tr("selected_empty"))
            selected_fingerprint_var.set("")
            selected_note_var.set("")
            selected_last_used_var.set("")
            return
        values = tree.item(selection[0], "values")
        name = str(values[0]).lstrip("* ").strip()
        selected_name_var.set(f"{tr('selected_name_label')}: {name}")
        selected_fingerprint_var.set(f"{tr('selected_fingerprint_label')}: {values[1]}")
        selected_note_var.set(f"{tr('selected_note_label')}: {values[2] or '-'}")
        selected_last_used_var.set(f"{tr('selected_last_used_label')}: {values[3] or '-'}")

    def apply_language() -> None:
        root.title(tr("window_title"))
        title_label.configure(text=tr("app_title"))
        subtitle_label.configure(text=tr("subtitle"))
        language_label.configure(text=tr("language_label"))
        active_kicker_label.configure(text=tr("active_kicker"))
        auth_path_label.configure(text=f"{tr('auth_path')}:")
        count_pill_label.configure(text=tr("profile_count", count=active_count["value"]))
        refresh_button.configure(text=tr("refresh"))
        actions_label.configure(text=tr("actions"))
        selected_label.configure(text=tr("selected_kicker"))
        storage_label.configure(text=tr("storage"))
        storage_hint_label.configure(text=tr("storage_hint"))
        safety_label.configure(text=tr("safety"))
        safety_hint_label.configure(text=tr("safety_hint"))
        tree.heading("name", text=tr("profile"))
        tree.heading("fingerprint", text=tr("fingerprint"))
        tree.heading("note", text=tr("note"))
        tree.heading("last_used", text=tr("last_used"))
        for key, button in buttons_by_key.items():
            button.configure(text=tr(key))
        values = [language_display("zh"), language_display("en")]
        language_combo.configure(values=values)
        language_var.set(language_display(lang["code"]))
        status.set(tr("ready", count=active_count["value"]))
        update_selected()

    def set_busy(value: bool, message: str | None = None) -> None:
        busy["value"] = value
        for btn in action_buttons:
            btn.state(["disabled"] if value else ["!disabled"])
        if message:
            status.set(message)

    def refresh() -> None:
        try:
            profiles = list_profiles(profile_dir)
            active = detect_active_profile(auth_path, profile_dir)
            active_count["value"] = len(profiles)
            active_var.set(active.name if active else tr("active_unknown"))
            tree.delete(*tree.get_children())
            for index, profile in enumerate(profiles):
                is_active = active and active.name == profile.name
                mark = "*" if is_active else " "
                tree.insert(
                    "",
                    "end",
                    values=(
                        f"{mark} {profile.name}",
                        profile.sha256[:12] if profile.sha256 else "unknown",
                        profile.note or "",
                        profile.last_used_at or "",
                    ),
                    tags=("active" if is_active else "even" if index % 2 else "odd",),
                )
            count_pill_label.configure(text=tr("profile_count", count=len(profiles)))
            update_selected()
            status.set(tr("ready", count=len(profiles)))
        except SwitcherError as exc:
            messagebox.showerror(tr("error_title"), str(exc))

    def on_save_current() -> None:
        dialog = ProfileDialog(root, "save_dialog", "save_action")
        if not dialog.result:
            return
        try:
            save_profile(
                str(dialog.result["name"]),
                auth_path,
                profile_dir,
                note=str(dialog.result["note"]) or None,
                overwrite=bool(dialog.result["overwrite"]),
            )
            refresh()
        except SwitcherError as exc:
            messagebox.showerror(tr("error_title"), str(exc))

    def on_import() -> None:
        filename = filedialog.askopenfilename(
            title="Import auth.json",
            filetypes=[(tr("json_files"), "*.json"), (tr("all_files"), "*.*")],
        )
        if not filename:
            return
        dialog = ProfileDialog(root, "import_dialog", "import_action")
        if not dialog.result:
            return
        try:
            save_profile(
                str(dialog.result["name"]),
                Path(filename),
                profile_dir,
                note=str(dialog.result["note"]) or None,
                overwrite=bool(dialog.result["overwrite"]),
            )
            refresh()
        except SwitcherError as exc:
            messagebox.showerror(tr("error_title"), str(exc))

    def on_login_save() -> None:
        if busy["value"]:
            return
        dialog = ProfileDialog(root, "login_dialog", "login_action", include_command=True)
        if not dialog.result:
            return
        name = str(dialog.result["name"])
        command = str(dialog.result["command"])
        note = str(dialog.result["note"]) or None
        overwrite = bool(dialog.result["overwrite"])
        if not messagebox.askyesno(
            tr("confirm_title"),
            tr("confirm_login"),
        ):
            return

        def worker() -> None:
            try:
                result = login_and_save_profile(name, command, auth_path, profile_dir, note=note, overwrite=overwrite)

                def done() -> None:
                    refresh()
                    set_busy(False, tr("saved_after_login", name=result.profile.name))
                    message = tr("saved_after_login", name=result.profile.name)
                    if result.backup:
                        message += f"\n{tr('backup', path=result.backup)}"
                    messagebox.showinfo(tr("info_title"), message)

                root.after(0, done)
            except SwitcherError as exc:
                root.after(0, lambda: (set_busy(False, tr("login_failed")), messagebox.showerror(tr("error_title"), str(exc))))

        set_busy(True, tr("login_busy"))
        threading.Thread(target=worker, daemon=True).start()

    def on_switch() -> None:
        name = selected_name()
        if not name:
            messagebox.showinfo(tr("info_title"), tr("select_first"))
            return
        if not messagebox.askyesno(tr("confirm_title"), tr("confirm_switch", name=name)):
            return
        try:
            _, backup = switch_profile(name, auth_path, profile_dir)
            message = tr("switched", name=name)
            if backup:
                message += f"\n{tr('backup', path=backup)}"
            messagebox.showinfo(tr("info_title"), message)
            refresh()
        except SwitcherError as exc:
            messagebox.showerror(tr("error_title"), str(exc))

    def on_delete() -> None:
        name = selected_name()
        if not name:
            messagebox.showinfo(tr("info_title"), tr("select_first"))
            return
        if not messagebox.askyesno(tr("confirm_title"), tr("confirm_delete", name=name)):
            return
        try:
            delete_profile(name, profile_dir)
            refresh()
        except SwitcherError as exc:
            messagebox.showerror(tr("error_title"), str(exc))

    def on_language_change(_event=None) -> None:
        selected = language_var.get()
        for code in ("zh", "en"):
            if selected == UI_TEXT[lang["code"]]["language_values"][code]:
                lang["code"] = code
                break
        apply_language()
        refresh()

    language_combo.bind("<<ComboboxSelected>>", on_language_change)
    tree.bind("<<TreeviewSelect>>", lambda _event: update_selected())

    footer = ttk.Frame(shell, style="Shell.TFrame", padding=(18, 0, 18, 12))
    footer.pack(fill="x")
    ttk.Label(footer, textvariable=status, style="Status.TLabel").pack(anchor="w")
    apply_language()
    refresh()
    root.mainloop()
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=APP_NAME)
    parser.add_argument("--auth-path", type=Path, default=DEFAULT_AUTH_PATH, help=f"default: {DEFAULT_AUTH_PATH}")
    parser.add_argument("--profile-dir", type=Path, default=DEFAULT_PROFILE_DIR, help=f"default: {DEFAULT_PROFILE_DIR}")
    sub = parser.add_subparsers(dest="command")

    save = sub.add_parser("save", help="save the active or provided auth.json as a named profile")
    save.add_argument("name")
    save.add_argument("--from", dest="source", type=Path, default=None, help="auth.json file to import")
    save.add_argument("--note", default=None)
    save.add_argument("--overwrite", action="store_true")

    login_save = sub.add_parser("login-save", help="run Codex login, then save the resulting auth.json as a profile")
    login_save.add_argument("name")
    login_save.add_argument("--command", default=DEFAULT_LOGIN_COMMAND, help=f'default: "{DEFAULT_LOGIN_COMMAND}"')
    login_save.add_argument("--note", default=None)
    login_save.add_argument("--overwrite", action="store_true")

    switch = sub.add_parser("switch", help="activate a saved profile")
    switch.add_argument("name")
    switch.add_argument("--no-backup", action="store_true", help="do not backup current auth.json before replacing")

    sub.add_parser("list", help="list saved profiles")
    sub.add_parser("current", help="show which saved profile matches active auth.json")

    delete = sub.add_parser("delete", help="delete a saved profile")
    delete.add_argument("name")

    sub.add_parser("gui", help="open the graphical interface")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    command = args.command or "gui"
    auth_path = args.auth_path.expanduser()
    profile_dir = args.profile_dir.expanduser()

    try:
        if command == "save":
            source = args.source.expanduser() if args.source else auth_path
            profile = save_profile(args.name, source, profile_dir, note=args.note, overwrite=args.overwrite)
            print(f"Saved profile '{profile.name}' to {profile.path}")
            return 0
        if command == "login-save":
            result = login_and_save_profile(
                args.name,
                args.command,
                auth_path,
                profile_dir,
                note=args.note,
                overwrite=args.overwrite,
            )
            print(f"Saved profile '{result.profile.name}' after login.")
            if result.backup:
                print(f"Previous auth.json backup: {result.backup}")
            return 0
        if command == "switch":
            profile, backup = switch_profile(args.name, auth_path, profile_dir, no_backup=args.no_backup)
            print(f"Switched to '{profile.name}'.")
            if backup:
                print(f"Previous auth.json backup: {backup}")
            return 0
        if command == "list":
            print_profiles(list_profiles(profile_dir), detect_active_profile(auth_path, profile_dir))
            return 0
        if command == "current":
            active = detect_active_profile(auth_path, profile_dir)
            print(active.name if active else "None or unknown")
            return 0
        if command == "delete":
            delete_profile(args.name, profile_dir)
            print(f"Deleted profile '{args.name}'.")
            return 0
        if command == "gui":
            try:
                from codex_auth_switcher_qt import run_qt_gui

                return run_qt_gui(auth_path, profile_dir)
            except ImportError:
                pass
            return run_gui(auth_path, profile_dir)
        parser.error(f"Unknown command: {command}")
        return 2
    except SwitcherError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
