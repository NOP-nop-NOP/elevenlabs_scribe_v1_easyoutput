@echo off
setlocal

:: =================================================================
:: Git Main ��֧����ͬ���ű�
::
:: ����:
:: 1. �Զ���� Git �Ƿ�װ��
:: 2. �����ǰĿ¼�� Git �ֿ⣬���Զ��� main ��֧��ȡ���´��롣
:: 3. �����ǰĿ¼���� Git �ֿ⣬�������û������ַ����¡�ֿ⡣
:: =================================================================

:: ���ô��ڱ���
title Git ����ͬ������

echo.
echo ===================================
echo  Git Main ��֧����ͬ���ű�
echo ===================================
echo.

:: --- ���� 1: ��� Git �Ƿ��Ѱ�װ ---
echo ���ڼ�� Git ����...
git --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [����] δ��⵽ Git ���
    echo ���Ȱ�װ Git ��ȷ���ѽ�����ӵ�ϵͳ�� PATH ���������С�
    echo.
    echo �����Դӹٷ���վ���� Git: https://git-scm.com/
    goto :end
)
echo Git ����������
echo.


:: --- ���� 2: ��鵱ǰĿ¼�Ƿ�Ϊ Git �ֿ� ---
echo ���ڼ�鵱ǰĿ¼״̬...
if exist .git (
    goto :pull_code
) else (
    goto :clone_repo
)


:: --- ��֧ 1: ��ȡ���� (����Ѿ��ǲֿ�) ---
:pull_code
echo ��ǰĿ¼��һ�� Git �ֿ⡣
echo ׼����Զ�� main ��֧��ȡ���´���...
echo.

:: Ϊȷ������������֧�ϣ��ȳ����л��� main ��֧
echo �����л��� main ��֧...
git checkout main
if errorlevel 1 (
    echo.
    echo [����] �л��� main ��֧ʧ�ܡ�����ϵ����֧�֡�
    goto :end
)

echo.
echo ������ȡ���´���...
git pull origin main
if errorlevel 1 (
    echo.
    echo [����] �� main ��֧��ȡ����ʧ�ܡ�
    echo �������������������򱾵����ļ��޸ĳ�ͻ������ϵ����֧�֡�
    goto :end
)

echo.
echo ===================================
echo  �����ɹ�! �����Ѹ��������°汾��
echo ===================================
goto :end


:: --- ��֧ 2: ��¡�ֿ� (������ǲֿ�) ---
:clone_repo
echo ��ǰĿ¼����һ�� Git �ֿ⡣
echo ���״�ʹ��ʱ������Ҫ�ṩ�ֿ�� Git ��ַ�����ش��롣
echo.
echo (Git ��ַͨ���� https:// ��ͷ���� .git ��β)
echo.

:: ��ʾ�û�����ֿ��ַ
set /p REPO_URL="���������� Git �ֿ��ַ�����س�: "

:: ����û��Ƿ������˵�ַ
if not defined REPO_URL (
    echo.
    echo ��û�������κε�ַ��������ȡ����
    goto :end
)

echo.
echo ׼�������µ�ַ��¡�ֿ⵽��ǰĿ¼:
echo %REPO_URL%
echo.

:: ��¡�ֿ⵽��ǰĿ¼��ע�⣺��¡Ҫ��ǰ�ļ��б���Ϊ�ա�
git clone %REPO_URL% .
if errorlevel 1 (
    echo.
    echo [����] ��¡�ֿ�ʧ��!
    echo �������¼���:
    echo 1. �ֿ��ַ�Ƿ�����ȷ��
    echo 2. ���Ƿ���Ȩ�޷��ʸòֿ⡣
    echo 3. ��ǰ�ļ����Ƿ�Ϊ ���ļ��С�
    goto :end
)

echo.
echo ===================================
echo  �����ɹ�! �ֿ��ѳɹ����ص���ǰ�ļ��С�
echo ===================================
goto :end


:: --- �ű���β ---
:end
echo.
echo ��������˳�...
pause >nul
endlocal