from __future__ import annotations

import sys
from pathlib import Path

try:
    from PySide6.QtCore import QThread, Qt, Signal
    from PySide6.QtGui import QFont
    from PySide6.QtWidgets import (
        QApplication,
        QCheckBox,
        QComboBox,
        QDialog,
        QFileDialog,
        QFrame,
        QHBoxLayout,
        QHeaderView,
        QLabel,
        QLineEdit,
        QMainWindow,
        QMessageBox,
        QPushButton,
        QScrollArea,
        QSizePolicy,
        QSpacerItem,
        QTableWidget,
        QTableWidgetItem,
        QVBoxLayout,
        QWidget,
    )
except ImportError:
    from PyQt6.QtCore import QThread, Qt, pyqtSignal as Signal
    from PyQt6.QtGui import QFont
    from PyQt6.QtWidgets import (
        QApplication,
        QCheckBox,
        QComboBox,
        QDialog,
        QFileDialog,
        QFrame,
        QHBoxLayout,
        QHeaderView,
        QLabel,
        QLineEdit,
        QMainWindow,
        QMessageBox,
        QPushButton,
        QScrollArea,
        QSizePolicy,
        QSpacerItem,
        QTableWidget,
        QTableWidgetItem,
        QVBoxLayout,
        QWidget,
    )

from codex_auth_switcher import (
    APP_NAME,
    CodexCliStatus,
    Profile,
    SwitcherError,
    codex_cli_status,
    delete_profile,
    detect_active_profile,
    DEFAULT_LOGIN_COMMAND,
    list_profiles,
    login_and_save_profile,
    run_codex_cli_setup,
    save_profile,
    switch_profile,
)


TEXT = {
    "zh": {
        "window_title": "Codex 账号切换器",
        "subtitle": "本地保存、登录、切换 Codex 账号；不会显示 token 内容。",
        "language_label": "界面语言 / Language",
        "language_values": {"zh": "中文", "en": "English"},
        "active": "当前账号",
        "unknown": "未识别或未保存",
        "auth_file": "认证文件",
        "profiles": "{count} 个账号",
        "table_profile": "账号",
        "table_fingerprint": "指纹",
        "table_note": "备注",
        "table_last_used": "上次使用",
        "actions": "操作",
        "cli_status": "Codex CLI 状态",
        "cli_ready": "CLI 就绪",
        "cli_not_ready": "CLI 不可用",
        "install_cli": "安装/修复 CLI",
        "install_cli_login": "安装 CLI 并登录",
        "login_save": "登录并保存",
        "save_current": "保存当前认证",
        "import_file": "导入认证文件",
        "switch": "切换选中账号",
        "delete": "删除选中账号",
        "refresh": "刷新",
        "selected": "选中账号",
        "not_selected": "尚未选中账号",
        "storage": "保存位置",
        "storage_hint": "账号文件只保存在本机 .codex 目录，请不要提交到 GitHub。",
        "safety": "安全提示",
        "safety_hint": "登录并保存是事务式流程：失败或中途退出会恢复旧 auth.json。",
        "ready": "就绪。找到 {count} 个账号。",
        "dialog_profile": "账号备注",
        "dialog_note": "备注",
        "dialog_command": "登录命令",
        "dialog_overwrite": "如果同名账号已存在，则覆盖",
        "save_title": "保存当前认证",
        "import_title": "导入认证文件",
        "login_title": "登录并保存新账号",
        "cancel": "取消",
        "save": "保存",
        "import": "导入",
        "start_login": "开始登录",
        "select_first": "请先选中一个账号。",
        "confirm": "确认操作",
        "confirm_login": "现在会运行登录命令。登录成功并保存 profile 后，新 auth.json 才会保留。",
        "confirm_switch": "确认切换当前 Codex 认证到“{name}”？",
        "confirm_delete": "确认删除保存的账号“{name}”？这不会删除当前 active auth.json。",
        "switched": "已切换到 {name}。",
        "saved_after_login": "登录完成，已保存账号“{name}”。",
        "backup": "备份文件：{path}",
        "login_busy": "正在运行登录命令。完成浏览器或终端登录后，请回到这里等待。",
        "login_failed": "登录失败或账号没有保存；旧 auth.json 已恢复。",
        "cli_setup_busy": "正在打开 PowerShell 安装 Codex CLI，请在终端中完成流程。",
        "cli_setup_done": "CLI 安装流程结束。请刷新状态后再登录。",
        "error": "出错了",
        "info": "提示",
        "json_files": "JSON 文件 (*.json);;所有文件 (*.*)",
    },
    "en": {
        "window_title": "Codex Auth Switcher",
        "subtitle": "Save, log in, and switch Codex accounts locally without exposing tokens.",
        "language_label": "Language / 界面语言",
        "language_values": {"zh": "中文", "en": "English"},
        "active": "Active Profile",
        "unknown": "None or unknown",
        "auth_file": "Auth file",
        "profiles": "{count} profile(s)",
        "table_profile": "Profile",
        "table_fingerprint": "Fingerprint",
        "table_note": "Note",
        "table_last_used": "Last used",
        "actions": "Actions",
        "cli_status": "Codex CLI Status",
        "cli_ready": "CLI ready",
        "cli_not_ready": "CLI unavailable",
        "install_cli": "Install / Repair CLI",
        "install_cli_login": "Install CLI & Login",
        "login_save": "Login & Save",
        "save_current": "Save Current",
        "import_file": "Import File",
        "switch": "Switch Selected",
        "delete": "Delete Selected",
        "refresh": "Refresh",
        "selected": "Selected Profile",
        "not_selected": "No profile selected",
        "storage": "Storage",
        "storage_hint": "Profiles stay under your local .codex folder. Do not commit them to GitHub.",
        "safety": "Safety",
        "safety_hint": "Login & Save is transactional: failed or interrupted login restores the previous auth.json.",
        "ready": "Ready. {count} profile(s) found.",
        "dialog_profile": "Profile name",
        "dialog_note": "Note",
        "dialog_command": "Login command",
        "dialog_overwrite": "Overwrite profile if it already exists",
        "save_title": "Save Current Auth",
        "import_title": "Import Auth File",
        "login_title": "Login and Save New Auth",
        "cancel": "Cancel",
        "save": "Save",
        "import": "Import",
        "start_login": "Start Login",
        "select_first": "Select a profile first.",
        "confirm": "Confirm",
        "confirm_login": "The login command will run now. The new auth.json remains active only after the profile is saved.",
        "confirm_switch": "Switch active Codex auth.json to '{name}'?",
        "confirm_delete": "Delete saved profile '{name}'? This does not delete active auth.json.",
        "switched": "Switched to {name}.",
        "saved_after_login": "Saved profile '{name}' after login.",
        "backup": "Backup: {path}",
        "login_busy": "Running login command. Complete the browser or terminal login flow, then wait here.",
        "login_failed": "Login failed or profile was not saved; previous auth.json was restored.",
        "cli_setup_busy": "Opening PowerShell to install Codex CLI. Complete the terminal flow.",
        "cli_setup_done": "CLI setup finished. Refresh status before logging in.",
        "error": "Error",
        "info": "Info",
        "json_files": "JSON files (*.json);;All files (*.*)",
    },
}


STYLE = """
QWidget {
    background: #eef1ed;
    color: #151713;
    font-family: "Microsoft YaHei UI", "Segoe UI";
    font-size: 10pt;
}
QFrame#Header {
    background: #111b17;
    border-bottom: 1px solid #314239;
}
QFrame#Panel {
    background: #fbf8f0;
    border: 1px solid #ded4c2;
    border-radius: 14px;
}
QFrame#SidePanel {
    background: #f5efe3;
    border: 1px solid #d8ccba;
    border-radius: 14px;
}
QScrollArea#SideScroll {
    background: transparent;
    border: none;
}
QScrollArea#SideScroll > QWidget > QWidget {
    background: transparent;
}
QLabel#Logo {
    background: #bd5b2b;
    color: #fff6e6;
    border-radius: 12px;
    font-size: 18pt;
    font-weight: 800;
    padding: 10px 13px;
}
QLabel#Title {
    background: transparent;
    color: #fff6e6;
    font-size: 22pt;
    font-weight: 800;
}
QLabel#Subtitle, QLabel#HeaderSmall {
    background: transparent;
    color: #d8cbb7;
}
QLabel#Kicker {
    background: transparent;
    color: #6b6257;
    font-size: 8.5pt;
    font-weight: 700;
    letter-spacing: 0px;
}
QLabel#Active {
    background: transparent;
    color: #24724d;
    font-size: 19pt;
    font-weight: 800;
}
QLabel#Muted {
    background: transparent;
    color: #6d675f;
}
QLabel#Pill {
    background: #e6dccb;
    color: #151713;
    border-radius: 12px;
    padding: 7px 12px;
    font-weight: 700;
}
QPushButton {
    background: #e7dac7;
    color: #151713;
    border: none;
    border-radius: 10px;
    min-height: 34px;
    padding: 10px 14px;
    font-weight: 700;
}
QPushButton:hover {
    background: #dac9b4;
}
QPushButton:disabled {
    background: #e7e1d8;
    color: #9a9288;
}
QPushButton#Primary {
    background: #bd5b2b;
    color: white;
}
QPushButton#Primary:hover {
    background: #9f461e;
}
QPushButton#Danger {
    background: #ead7d0;
    color: #8a2c1f;
}
QTableWidget {
    background: #fffdf7;
    border: 1px solid #ded4c2;
    border-radius: 12px;
    gridline-color: #eee4d5;
    selection-background-color: #eec49f;
    selection-color: #151713;
}
QHeaderView::section {
    background: #ded1bd;
    color: #151713;
    border: none;
    padding: 10px;
    font-weight: 800;
}
QLineEdit, QComboBox {
    background: #fffdf7;
    border: 1px solid #d8ccba;
    border-radius: 9px;
    padding: 9px 10px;
}
QCheckBox {
    background: transparent;
}
"""


class ProfileDialog(QDialog):
    def __init__(self, parent: QWidget, lang: str, title_key: str, action_key: str, include_command: bool = False) -> None:
        super().__init__(parent)
        self.lang = lang
        self.setWindowTitle(self.t(title_key))
        self.setModal(True)
        self.setMinimumWidth(420)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(14)

        title = QLabel(self.t(title_key))
        title.setObjectName("Active")
        layout.addWidget(title)

        self.name_input = self._field(layout, "dialog_profile")
        self.note_input = self._field(layout, "dialog_note")
        self.command_input: QLineEdit | None = None
        if include_command:
            self.command_input = self._field(layout, "dialog_command")
            self.command_input.setText(DEFAULT_LOGIN_COMMAND)

        self.overwrite = QCheckBox(self.t("dialog_overwrite"))
        layout.addWidget(self.overwrite)

        actions = QHBoxLayout()
        actions.addStretch()
        cancel = QPushButton(self.t("cancel"))
        cancel.clicked.connect(self.reject)
        submit = QPushButton(self.t(action_key))
        submit.setObjectName("Primary")
        submit.clicked.connect(self.accept)
        actions.addWidget(cancel)
        actions.addWidget(submit)
        layout.addLayout(actions)

    def _field(self, layout: QVBoxLayout, key: str) -> QLineEdit:
        label = QLabel(self.t(key))
        label.setObjectName("Kicker")
        edit = QLineEdit()
        layout.addWidget(label)
        layout.addWidget(edit)
        return edit

    def t(self, key: str, **kwargs: object) -> str:
        return TEXT[self.lang][key].format(**kwargs)

    def values(self) -> dict[str, object]:
        return {
            "name": self.name_input.text(),
            "note": self.note_input.text(),
            "command": self.command_input.text() if self.command_input else "",
            "overwrite": self.overwrite.isChecked(),
        }


class LoginWorker(QThread):
    succeeded = Signal(object)
    failed = Signal(str)

    def __init__(self, name: str, command: str, auth_path: Path, profile_dir: Path, note: str | None, overwrite: bool) -> None:
        super().__init__()
        self.name = name
        self.command = command
        self.auth_path = auth_path
        self.profile_dir = profile_dir
        self.note = note
        self.overwrite = overwrite

    def run(self) -> None:
        try:
            self.succeeded.emit(login_and_save_profile(self.name, self.command, self.auth_path, self.profile_dir, self.note, self.overwrite))
        except Exception as exc:
            self.failed.emit(str(exc))


class CliSetupWorker(QThread):
    finished_setup = Signal(int)

    def __init__(self, continue_to_login: bool) -> None:
        super().__init__()
        self.continue_to_login = continue_to_login

    def run(self) -> None:
        self.finished_setup.emit(run_codex_cli_setup(self.continue_to_login))


class MainWindow(QMainWindow):
    def __init__(self, auth_path: Path, profile_dir: Path) -> None:
        super().__init__()
        self.auth_path = auth_path
        self.profile_dir = profile_dir
        self.lang = "zh"
        self.profiles: list[Profile] = []
        self.active: Profile | None = None
        self.worker: LoginWorker | None = None
        self.cli_worker: CliSetupWorker | None = None
        self.cli_status: CodexCliStatus | None = None

        self.setMinimumSize(1040, 680)
        self.setWindowTitle(self.t("window_title"))

        root = QWidget()
        self.setCentralWidget(root)
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        root_layout.addWidget(self._build_header())

        body = QVBoxLayout()
        body.setContentsMargins(22, 22, 22, 14)
        body.setSpacing(16)
        root_layout.addLayout(body, 1)

        body.addWidget(self._build_summary())

        content = QHBoxLayout()
        content.setSpacing(16)
        body.addLayout(content, 1)
        content.addWidget(self._build_table_panel(), 1)
        content.addWidget(self._build_side_panel())

        self.status = QLabel()
        self.status.setObjectName("Muted")
        body.addWidget(self.status)

        self.apply_language()
        self.refresh()

    def _build_header(self) -> QWidget:
        header = QFrame()
        header.setObjectName("Header")
        layout = QHBoxLayout(header)
        layout.setContentsMargins(24, 18, 24, 18)
        layout.setSpacing(16)

        logo = QLabel("CA")
        logo.setObjectName("Logo")
        layout.addWidget(logo)

        text_box = QVBoxLayout()
        text_box.setSpacing(3)
        self.title = QLabel()
        self.title.setObjectName("Title")
        self.subtitle = QLabel()
        self.subtitle.setObjectName("Subtitle")
        text_box.addWidget(self.title)
        text_box.addWidget(self.subtitle)
        layout.addLayout(text_box, 1)

        lang_box = QVBoxLayout()
        lang_box.setSpacing(6)
        self.language_label = QLabel()
        self.language_label.setObjectName("HeaderSmall")
        self.language_combo = QComboBox()
        self.language_combo.currentIndexChanged.connect(self._language_changed)
        lang_box.addWidget(self.language_label, alignment=Qt.AlignmentFlag.AlignRight)
        lang_box.addWidget(self.language_combo)
        layout.addLayout(lang_box)
        return header

    def _build_summary(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("Panel")
        layout = QHBoxLayout(panel)
        layout.setContentsMargins(18, 16, 18, 16)

        left = QVBoxLayout()
        left.setSpacing(5)
        self.active_kicker = QLabel()
        self.active_kicker.setObjectName("Kicker")
        self.active_label = QLabel()
        self.active_label.setObjectName("Active")
        self.auth_label = QLabel()
        self.auth_label.setObjectName("Muted")
        left.addWidget(self.active_kicker)
        left.addWidget(self.active_label)
        left.addWidget(self.auth_label)
        layout.addLayout(left, 1)

        self.count_label = QLabel()
        self.count_label.setObjectName("Pill")
        layout.addWidget(self.count_label)
        self.refresh_button = QPushButton()
        self.refresh_button.clicked.connect(self.refresh)
        layout.addWidget(self.refresh_button)
        return panel

    def _build_table_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("Panel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(14, 14, 14, 14)

        self.table = QTableWidget(0, 4)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.itemSelectionChanged.connect(self.update_selected)
        layout.addWidget(self.table)
        return panel

    def _build_side_panel(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setObjectName("SideScroll")
        scroll.setWidgetResizable(True)
        scroll.setFixedWidth(325)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        panel = QFrame()
        panel.setObjectName("SidePanel")
        scroll.setWidget(panel)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)

        self.actions_label = QLabel()
        self.actions_label.setObjectName("Kicker")
        layout.addWidget(self.actions_label)

        self.buttons: dict[str, QPushButton] = {}
        self.cli_status_label = QLabel()
        self.cli_status_label.setObjectName("Muted")
        self.cli_status_label.setWordWrap(True)
        layout.addWidget(self.cli_status_label)
        self._add_button(layout, "install_cli", lambda: self.install_cli(False))
        self._add_button(layout, "install_cli_login", lambda: self.install_cli(True))
        layout.addSpacing(8)
        self._add_button(layout, "login_save", self.login_save, primary=True)
        self._add_button(layout, "save_current", self.save_current)
        self._add_button(layout, "import_file", self.import_file)
        self._add_button(layout, "switch", self.switch_selected)
        self._add_button(layout, "delete", self.delete_selected, danger=True)

        self.selected_label = QLabel()
        self.selected_label.setObjectName("Kicker")
        layout.addSpacing(12)
        layout.addWidget(self.selected_label)
        self.selected_name = QLabel()
        self.selected_name.setWordWrap(True)
        self.selected_name.setObjectName("Muted")
        self.selected_meta = QLabel()
        self.selected_meta.setWordWrap(True)
        self.selected_meta.setObjectName("Muted")
        layout.addWidget(self.selected_name)
        layout.addWidget(self.selected_meta)

        self.storage_label = QLabel()
        self.storage_label.setObjectName("Kicker")
        self.storage_hint = QLabel()
        self.storage_hint.setObjectName("Muted")
        self.storage_hint.setWordWrap(True)
        self.profile_dir_label = QLabel(str(self.profile_dir))
        self.profile_dir_label.setObjectName("Muted")
        self.profile_dir_label.setWordWrap(True)
        layout.addSpacing(12)
        layout.addWidget(self.storage_label)
        layout.addWidget(self.storage_hint)
        layout.addWidget(self.profile_dir_label)

        self.safety_label = QLabel()
        self.safety_label.setObjectName("Kicker")
        self.safety_hint = QLabel()
        self.safety_hint.setObjectName("Muted")
        self.safety_hint.setWordWrap(True)
        layout.addSpacing(12)
        layout.addWidget(self.safety_label)
        layout.addWidget(self.safety_hint)

        layout.addItem(QSpacerItem(1, 1, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        return scroll

    def _add_button(self, layout: QVBoxLayout, key: str, callback, primary: bool = False, danger: bool = False) -> None:
        button = QPushButton()
        button.setFixedHeight(46)
        button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        font = button.font()
        font.setFamily("Microsoft YaHei UI")
        font.setPointSize(10)
        font.setBold(True)
        button.setFont(font)
        if primary:
            button.setObjectName("Primary")
        if danger:
            button.setObjectName("Danger")
        button.clicked.connect(callback)
        layout.addWidget(button)
        self.buttons[key] = button

    def t(self, key: str, **kwargs: object) -> str:
        return TEXT[self.lang][key].format(**kwargs)

    def apply_language(self) -> None:
        self.setWindowTitle(self.t("window_title"))
        self.title.setText(self.t("window_title"))
        self.subtitle.setText(self.t("subtitle"))
        self.language_label.setText(self.t("language_label"))
        self.active_kicker.setText(self.t("active"))
        self.auth_label.setText(f"{self.t('auth_file')}: {self.auth_path}")
        self.refresh_button.setText(self.t("refresh"))
        self.actions_label.setText(self.t("actions"))
        self.selected_label.setText(self.t("selected"))
        self.storage_label.setText(self.t("storage"))
        self.storage_hint.setText(self.t("storage_hint"))
        self.safety_label.setText(self.t("safety"))
        self.safety_hint.setText(self.t("safety_hint"))

        self.table.setHorizontalHeaderLabels([
            self.t("table_profile"),
            self.t("table_fingerprint"),
            self.t("table_note"),
            self.t("table_last_used"),
        ])
        for key, button in self.buttons.items():
            button.setText(self.t(key))
            button.setToolTip(self.t(key))
            button.repaint()
        self.update_cli_status()

        values = [TEXT[self.lang]["language_values"]["zh"], TEXT[self.lang]["language_values"]["en"]]
        self.language_combo.blockSignals(True)
        self.language_combo.clear()
        self.language_combo.addItems(values)
        self.language_combo.setCurrentIndex(0 if self.lang == "zh" else 1)
        self.language_combo.blockSignals(False)

        self.count_label.setText(self.t("profiles", count=len(self.profiles)))
        self.active_label.setText(self.active.name if self.active else self.t("unknown"))
        self.status.setText(self.t("ready", count=len(self.profiles)))
        self.update_selected()

    def _language_changed(self, index: int) -> None:
        self.lang = "zh" if index == 0 else "en"
        self.apply_language()

    def refresh(self) -> None:
        try:
            self.update_cli_status()
            self.profiles = list_profiles(self.profile_dir)
            self.active = detect_active_profile(self.auth_path, self.profile_dir)
            self.table.setRowCount(0)
            active_name = self.active.name if self.active else None
            for profile in self.profiles:
                row = self.table.rowCount()
                self.table.insertRow(row)
                display_name = f"* {profile.name}" if profile.name == active_name else profile.name
                values = [display_name, (profile.sha256 or "unknown")[:12], profile.note or "", profile.last_used_at or ""]
                for col, value in enumerate(values):
                    item = QTableWidgetItem(value)
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    if profile.name == active_name:
                        item.setBackground(Qt.GlobalColor.transparent)
                    self.table.setItem(row, col, item)
            self.table.resizeRowsToContents()
            self.apply_language()
        except SwitcherError as exc:
            QMessageBox.critical(self, self.t("error"), str(exc))

    def selected_profile_name(self) -> str | None:
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 0)
        if not item:
            return None
        return item.text().lstrip("* ").strip()

    def update_selected(self) -> None:
        name = self.selected_profile_name()
        if not name:
            self.selected_name.setText(self.t("not_selected"))
            self.selected_meta.setText("")
            return
        profile = next((item for item in self.profiles if item.name == name), None)
        if not profile:
            self.selected_name.setText(self.t("not_selected"))
            self.selected_meta.setText("")
            return
        self.selected_name.setText(name)
        self.selected_meta.setText(
            f"{self.t('table_fingerprint')}: {(profile.sha256 or 'unknown')[:12]}\n"
            f"{self.t('table_note')}: {profile.note or '-'}\n"
            f"{self.t('table_last_used')}: {profile.last_used_at or '-'}"
        )

    def set_busy(self, busy: bool, message: str | None = None) -> None:
        for button in self.buttons.values():
            button.setEnabled(not busy)
        self.refresh_button.setEnabled(not busy)
        if not busy:
            self.update_cli_status()
        if message:
            self.status.setText(message)

    def _profile_dialog(self, title_key: str, action_key: str, include_command: bool = False) -> dict[str, object] | None:
        dialog = ProfileDialog(self, self.lang, title_key, action_key, include_command)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return None
        return dialog.values()

    def save_current(self) -> None:
        data = self._profile_dialog("save_title", "save")
        if not data:
            return
        try:
            save_profile(str(data["name"]), self.auth_path, self.profile_dir, str(data["note"]) or None, bool(data["overwrite"]))
            self.refresh()
        except SwitcherError as exc:
            QMessageBox.critical(self, self.t("error"), str(exc))

    def import_file(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(self, self.t("import_title"), str(Path.home()), self.t("json_files"))
        if not filename:
            return
        data = self._profile_dialog("import_title", "import")
        if not data:
            return
        try:
            save_profile(str(data["name"]), Path(filename), self.profile_dir, str(data["note"]) or None, bool(data["overwrite"]))
            self.refresh()
        except SwitcherError as exc:
            QMessageBox.critical(self, self.t("error"), str(exc))

    def login_save(self) -> None:
        status = self.update_cli_status()
        if not status.usable_for_login:
            QMessageBox.information(self, self.t("info"), status.message)
            return
        data = self._profile_dialog("login_title", "start_login", include_command=True)
        if not data:
            return
        if QMessageBox.question(self, self.t("confirm"), self.t("confirm_login")) != QMessageBox.StandardButton.Yes:
            return
        self.set_busy(True, self.t("login_busy"))
        self.worker = LoginWorker(
            str(data["name"]),
            str(data["command"]),
            self.auth_path,
            self.profile_dir,
            str(data["note"]) or None,
            bool(data["overwrite"]),
        )
        self.worker.succeeded.connect(self._login_succeeded)
        self.worker.failed.connect(self._login_failed)
        self.worker.start()

    def update_cli_status(self) -> CodexCliStatus:
        self.cli_status = codex_cli_status()
        if self.cli_status.usable_for_login:
            label = self.t("cli_ready")
            detail = self.cli_status.version or self.cli_status.path or ""
        else:
            label = self.t("cli_not_ready")
            detail = self.cli_status.message
        self.cli_status_label.setText(f"{self.t('cli_status')}: {label}\n{detail}")
        if "login_save" in self.buttons:
            self.buttons["login_save"].setEnabled(self.cli_status.usable_for_login)
        return self.cli_status

    def install_cli(self, continue_to_login: bool) -> None:
        self.set_busy(True, self.t("cli_setup_busy"))
        self.cli_worker = CliSetupWorker(continue_to_login)
        self.cli_worker.finished_setup.connect(self._cli_setup_finished)
        self.cli_worker.start()

    def _cli_setup_finished(self, code: int) -> None:
        self.set_busy(False, self.t("cli_setup_done"))
        self.update_cli_status()

    def _login_succeeded(self, result) -> None:
        self.set_busy(False)
        self.refresh()
        message = self.t("saved_after_login", name=result.profile.name)
        if result.backup:
            message += f"\n{self.t('backup', path=result.backup)}"
        QMessageBox.information(self, self.t("info"), message)

    def _login_failed(self, error: str) -> None:
        self.set_busy(False, self.t("login_failed"))
        QMessageBox.critical(self, self.t("error"), error)

    def switch_selected(self) -> None:
        name = self.selected_profile_name()
        if not name:
            QMessageBox.information(self, self.t("info"), self.t("select_first"))
            return
        if QMessageBox.question(self, self.t("confirm"), self.t("confirm_switch", name=name)) != QMessageBox.StandardButton.Yes:
            return
        try:
            _, backup = switch_profile(name, self.auth_path, self.profile_dir)
            message = self.t("switched", name=name)
            if backup:
                message += f"\n{self.t('backup', path=backup)}"
            QMessageBox.information(self, self.t("info"), message)
            self.refresh()
        except SwitcherError as exc:
            QMessageBox.critical(self, self.t("error"), str(exc))

    def delete_selected(self) -> None:
        name = self.selected_profile_name()
        if not name:
            QMessageBox.information(self, self.t("info"), self.t("select_first"))
            return
        if QMessageBox.question(self, self.t("confirm"), self.t("confirm_delete", name=name)) != QMessageBox.StandardButton.Yes:
            return
        try:
            delete_profile(name, self.profile_dir)
            self.refresh()
        except SwitcherError as exc:
            QMessageBox.critical(self, self.t("error"), str(exc))


def run_qt_gui(auth_path: Path, profile_dir: Path) -> int:
    app = QApplication.instance() or QApplication(sys.argv[:1])
    app.setApplicationName(APP_NAME)
    app.setStyleSheet(STYLE)
    font = QFont("Microsoft YaHei UI", 10)
    font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
    app.setFont(font)
    window = MainWindow(auth_path, profile_dir)
    window.show()
    return app.exec()
