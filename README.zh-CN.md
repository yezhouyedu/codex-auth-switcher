# Codex Auth Switcher

一个本地小工具，用来在多个 Codex 账号的 `auth.json` 之间快速切换。

它提供两种使用方式：

- 图形界面：适合日常点击切换
- 命令行：适合脚本或快速操作

工具不会打印 token 内容，也不会解析你的账号敏感字段。它只做三件事：校验文件是合法 JSON、完整复制认证文件、记录 SHA-256 指纹用于判断当前正在使用哪个 profile。

## 为什么需要它

Codex 默认只读取一份认证文件，通常是：

```text
C:\Users\<你的用户名>\.codex\auth.json
```

如果你有多个 Codex 账号，每个账号登录后都可以把当时的 `auth.json` 保存为一个 profile。之后需要切换账号时，工具会把对应 profile 复制回 active `auth.json`。

## 快速开始

需要 Python 3.10 或更高版本。

进入工具目录：

```powershell
cd E:\Own_program\openclaw\tools\codex-auth-switcher
```

安装图形界面依赖：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Windows 下也可以直接双击 `setup-venv.bat` 完成安装。

如果安装后 Qt 界面仍提示 `QtCore` DLL 加载失败，请安装或修复 Microsoft Visual C++ Redistributable：

```powershell
winget install Microsoft.VCRedist.2015+.x64
```

打开图形界面：

```powershell
.\.venv\Scripts\python.exe .\codex_auth_switcher.py
```

Windows 下也可以直接双击：

```text
run-gui.bat
```

## 图形界面怎么用

打开 GUI 后，你可以：

- 在右上角 `界面语言` 里切换中文或英文，界面文案会整体切换，不会中英混杂
- `安装/修复 CLI`：自动安装 npm 版 Codex CLI，并显示 `where codex` 与版本
- `安装 CLI 并登录`：自动安装 npm 版 Codex CLI，然后继续运行 `codex login --device-auth`
- `Login & Save`：调用 Codex 登录命令，登录完成后把新的 `auth.json` 保存成 profile
- `Save Current`：把当前 `C:\Users\<你>\.codex\auth.json` 保存成一个 profile
- `Import File`：从其他位置导入一个 `auth.json` 文件作为 profile
- `Switch`：把选中的 profile 切换为当前 Codex 认证
- `Delete`：删除保存的 profile，不会删除当前 active `auth.json`
- `Refresh`：刷新列表

列表里带 `*` 的 profile 表示它和当前 active `auth.json` 的 SHA-256 指纹一致。

`登录并保存` 默认运行：

```powershell
codex login --device-auth
```

如果你的本机 Codex 登录命令不同，可以在弹窗里的 `Login command` 里改成实际命令，例如：

```powershell
codex login
```

Windows 下工具会打开一个独立 PowerShell 终端来执行登录命令。请在那个终端里完成 Codex 提示的网页登录或设备码登录，最后按 Enter 返回工具。

如果系统里只有 Microsoft Store / WindowsApps 版 Codex，工具会禁用 `登录并保存`，并提示先安装 npm 版 CLI。原因是 WindowsApps 里的 `codex.exe` 不适合作为命令行登录入口。

## 命令行用法

把当前 Codex 认证保存成 profile：

```powershell
python .\codex_auth_switcher.py save main --note "主账号"
```

从其他位置导入认证文件：

```powershell
python .\codex_auth_switcher.py save alt --from C:\path\to\auth.json --note "备用账号"
```

调用 Codex 登录并把登录后的认证保存成 profile：

```powershell
python .\codex_auth_switcher.py login-save alt --note "备用账号"
```

如果登录命令不是默认的 `codex login --device-auth`：

```powershell
python .\codex_auth_switcher.py login-save alt --command "codex login"
```

查看所有 profile：

```powershell
python .\codex_auth_switcher.py list
```

切换到某个 profile：

```powershell
python .\codex_auth_switcher.py switch alt
```

查看当前 active `auth.json` 匹配哪个 profile：

```powershell
python .\codex_auth_switcher.py current
```

打开 GUI：

```powershell
python .\codex_auth_switcher.py gui
```

## 文件保存在哪里

默认 active 认证文件：

```text
C:\Users\<你的用户名>\.codex\auth.json
```

默认 profile 目录：

```text
C:\Users\<你的用户名>\.codex\auth_profiles\
```

每个 profile 会保存成：

```text
<profile-name>.auth.json
```

切换前，工具会自动备份原来的 active 文件：

```text
auth.json.backup-YYYYMMDD-HHMMSS
```

## 安全提醒

这些 profile 文件等同于账号凭据，请像密码一样保护。

`Login & Save` 和 `login-save` 会调用 Codex 登录命令，并在登录成功后读取 active `auth.json` 保存成 profile。测试这个功能时，建议先用 `--auth-path` 和 `--profile-dir` 指到临时目录，确认流程无误后再操作真实账号。

登录保存流程是事务式的：工具会先复制一份旧 `auth.json` 快照；如果登录命令失败、你中途退出、或者 profile 保存失败，旧 `auth.json` 会自动恢复。只有登录成功并且 profile 保存成功后，新的 `auth.json` 才会留在 active 位置。

不要把真实认证文件提交到 GitHub。本项目的 `.gitignore` 已经排除了：

- `auth.json`
- `*.auth.json`
- `auth_profiles/`
- `profiles.json`
- `auth.json.backup-*`
- `*.backup-*`

上传仓库前可以先运行：

```powershell
git status --short
```

确认没有真实认证文件出现在待提交列表里。

## 自定义路径

如果你想测试，或者 Codex 配置目录不在默认位置，可以指定路径：

```powershell
python .\codex_auth_switcher.py --auth-path C:\tmp\auth.json --profile-dir C:\tmp\profiles list
```

这样不会影响真实的 Codex 认证文件。
