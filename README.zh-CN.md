# Codex Auth Switcher

[English](README.md) | [Simplified Chinese / 简体中文](README.zh-CN.md)

一个本地小工具，用来在多个 Codex 账号的 `auth.json` 之间快速切换。

## 最简单安装方式

直接从 Release 下载 Windows exe：

[下载 CodexAuthSwitcher.exe](https://github.com/yezhouyedu/codex-auth-switcher/releases/download/v0.1.0/CodexAuthSwitcher.exe)

下载后双击运行即可。

使用 exe 版本不需要安装 Python。

## 它能做什么

- 保存当前 `C:\Users\<你>\.codex\auth.json` 为一个账号 profile
- 导入其他位置的 `auth.json`
- 在多个账号 profile 之间切换
- 自动识别当前 active `auth.json` 对应哪个 profile
- 事务式登录并保存：失败或中途退出会恢复旧 `auth.json`
- 检测 npm 版 Codex CLI 是否可用
- 一键安装 / 修复 npm 版 Codex CLI
- 支持中文 / 英文界面切换

工具不会显示 token 内容。它只校验 JSON、复制完整认证文件，并用 SHA-256 指纹判断当前使用的是哪个 profile。

## 为什么需要它

Codex 默认只读取一份认证文件，通常是：

```text
C:\Users\<你的用户名>\.codex\auth.json
```

如果你有多个 Codex 账号，可以把每个账号登录后的 `auth.json` 保存成一个 profile。之后需要切换账号时，工具会把对应 profile 复制回 active `auth.json`。

## 图形界面怎么用

打开 GUI 后，你可以：

- `界面语言 / Language`：切换中文或英文
- `安装/修复 CLI`：自动安装 npm 版 Codex CLI，并显示 `where codex` 与版本
- `安装 CLI 并登录`：安装 npm 版 Codex CLI 后继续运行 `codex login --device-auth`
- `登录并保存`：调用 Codex CLI 登录，登录完成后把新的 `auth.json` 保存成 profile
- `保存当前认证`：把当前 active `auth.json` 保存成 profile
- `导入认证文件`：从其他位置导入一个 `auth.json`
- `切换选中账号`：把选中的 profile 切换为当前 Codex 认证
- `删除选中账号`：删除保存的 profile，不会删除当前 active `auth.json`
- `刷新`：刷新列表和 CLI 状态

如果系统里只有 Microsoft Store / WindowsApps 版 Codex，工具会禁用 `登录并保存`，并提示先安装 npm 版 CLI。原因是 WindowsApps 里的 `codex.exe` 不适合作为命令行登录入口。

## 登录命令

默认登录命令是：

```powershell
codex login --device-auth
```

Windows 下工具会打开一个独立 PowerShell 终端来执行登录命令。请在那个终端里完成 Codex 提示的网页登录或设备码登录，最后按 Enter 返回工具。

## 从源码运行

需要 Python 3.10 或更高版本。

```powershell
git clone https://github.com/yezhouyedu/codex-auth-switcher.git
cd codex-auth-switcher
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe .\codex_auth_switcher.py
```

Windows 下也可以双击：

```text
setup-venv.bat
run-gui.bat
```

## 命令行用法

保存当前 Codex 认证：

```powershell
python .\codex_auth_switcher.py save main --note "主账号"
```

从其他位置导入认证文件：

```powershell
python .\codex_auth_switcher.py save alt --from C:\path\to\auth.json --note "备用账号"
```

调用 Codex 登录并保存：

```powershell
python .\codex_auth_switcher.py login-save alt --note "备用账号"
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

登录保存流程是事务式的：工具会先复制一份旧 `auth.json` 快照；如果登录命令失败、你中途退出、或者 profile 保存失败，旧 `auth.json` 会自动恢复。只有登录成功并且 profile 保存成功后，新的 `auth.json` 才会留在 active 位置。

不要把真实认证文件提交到 GitHub。本项目的 `.gitignore` 已经排除了：

- `auth.json`
- `*.auth.json`
- `auth_profiles/`
- `profiles.json`
- `auth.json.backup-*`
- `*.backup-*`

## 打包 exe

```powershell
build-exe.bat
```

构建产物会生成在：

```text
dist\CodexAuthSwitcher.exe
```
