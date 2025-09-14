@echo off
setlocal

:: =================================================================
:: Git Main 分支代码同步脚本
::
:: 功能:
:: 1. 自动检查 Git 是否安装。
:: 2. 如果当前目录是 Git 仓库，则自动从 main 分支拉取最新代码。
:: 3. 如果当前目录不是 Git 仓库，则引导用户输入地址并克隆仓库。
:: =================================================================

:: 设置窗口标题
title Git 代码同步工具

echo.
echo ===================================
echo  Git Main 分支代码同步脚本
echo ===================================
echo.

:: --- 步骤 1: 检查 Git 是否已安装 ---
echo 正在检查 Git 环境...
git --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [错误] 未检测到 Git 命令。
    echo 请先安装 Git 并确保已将其添加到系统的 PATH 环境变量中。
    echo.
    echo 您可以从官方网站下载 Git: https://git-scm.com/
    goto :end
)
echo Git 环境正常。
echo.


:: --- 步骤 2: 检查当前目录是否为 Git 仓库 ---
echo 正在检查当前目录状态...
if exist .git (
    goto :pull_code
) else (
    goto :clone_repo
)


:: --- 分支 1: 拉取代码 (如果已经是仓库) ---
:pull_code
echo 当前目录是一个 Git 仓库。
echo 准备从远程 main 分支拉取最新代码...
echo.

:: 为确保操作在主分支上，先尝试切换到 main 分支
echo 正在切换到 main 分支...
git checkout main
if errorlevel 1 (
    echo.
    echo [错误] 切换到 main 分支失败。请联系技术支持。
    goto :end
)

echo.
echo 正在拉取最新代码...
git pull origin main
if errorlevel 1 (
    echo.
    echo [错误] 从 main 分支拉取代码失败。
    echo 这可能是由于网络问题或本地有文件修改冲突。请联系技术支持。
    goto :end
)

echo.
echo ===================================
echo  操作成功! 代码已更新至最新版本。
echo ===================================
goto :end


:: --- 分支 2: 克隆仓库 (如果不是仓库) ---
:clone_repo
echo 当前目录不是一个 Git 仓库。
echo 在首次使用时，您需要提供仓库的 Git 地址来下载代码。
echo.
echo (Git 地址通常以 https:// 开头，以 .git 结尾)
echo.

:: 提示用户输入仓库地址
set /p REPO_URL="请输入您的 Git 仓库地址并按回车: "

:: 检查用户是否输入了地址
if not defined REPO_URL (
    echo.
    echo 您没有输入任何地址。操作已取消。
    goto :end
)

echo.
echo 准备从以下地址克隆仓库到当前目录:
echo %REPO_URL%
echo.

:: 克隆仓库到当前目录。注意：克隆要求当前文件夹必须为空。
git clone %REPO_URL% .
if errorlevel 1 (
    echo.
    echo [错误] 克隆仓库失败!
    echo 请检查以下几点:
    echo 1. 仓库地址是否复制正确。
    echo 2. 您是否有权限访问该仓库。
    echo 3. 当前文件夹是否为 空文件夹。
    goto :end
)

echo.
echo ===================================
echo  操作成功! 仓库已成功下载到当前文件夹。
echo ===================================
goto :end


:: --- 脚本结尾 ---
:end
echo.
echo 按任意键退出...
pause >nul
endlocal