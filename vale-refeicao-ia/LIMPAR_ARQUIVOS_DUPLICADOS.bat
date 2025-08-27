@echo off
echo ========================================
echo  LIMPEZA DE ARQUIVOS DUPLICADOS
echo  Projeto: CRMIA-VR
echo ========================================
echo.

REM Navegar para o diretório pai
cd /d D:\Dados\Sites\Cursor\CRMIA-VR

echo [1/3] Removendo arquivos do projeto antigo na raiz...
echo.

REM Remover arquivos Python do projeto antigo
if exist app.py (
    del /f /q app.py
    echo - Removido: app.py
)
if exist app_original.py (
    del /f /q app_original.py
    echo - Removido: app_original.py
)

REM Remover arquivos de configuração antigos
if exist requirements.txt (
    del /f /q requirements.txt
    echo - Removido: requirements.txt
)
if exist cloudbuild.yaml (
    del /f /q cloudbuild.yaml
    echo - Removido: cloudbuild.yaml
)
if exist deploy.ps1 (
    del /f /q deploy.ps1
    echo - Removido: deploy.ps1
)
if exist Dockerfile (
    del /f /q Dockerfile
    echo - Removido: Dockerfile
)
if exist Dockerfile.complex (
    del /f /q Dockerfile.complex
    echo - Removido: Dockerfile.complex
)

REM Remover arquivos com erro de digitação
if exist aindo (
    del /f /q aindo
    echo - Removido: aindo
)
if exist tatus (
    del /f /q tatus
    echo - Removido: tatus
)
if exist "h origin docker-support" (
    del /f /q "h origin docker-support"
    echo - Removido: h origin docker-support
)

echo.
echo [2/3] Verificando pastas duplicadas...
echo.

REM Verificar se o usuário quer remover a pasta CRM-IA-VR
if exist CRM-IA-VR (
    echo ATENCAO: Encontrada pasta CRM-IA-VR (possivel backup)
    echo Deseja remove-la? (S/N)
    choice /c SN /n
    if errorlevel 2 goto skip_crmia
    if errorlevel 1 (
        echo Removendo pasta CRM-IA-VR...
        rmdir /s /q CRM-IA-VR
        echo - Removido: pasta CRM-IA-VR
    )
)
:skip_crmia

REM Verificar se o usuário quer remover a pasta docs
if exist docs (
    echo.
    echo ATENCAO: Encontrada pasta docs (documentacao do projeto antigo)
    echo Deseja remove-la? (S/N)
    choice /c SN /n
    if errorlevel 2 goto skip_docs
    if errorlevel 1 (
        echo Removendo pasta docs...
        rmdir /s /q docs
        echo - Removido: pasta docs
    )
)
:skip_docs

echo.
echo [3/3] Limpeza concluida!
echo.
echo ========================================
echo  RESUMO:
echo  - Arquivos do projeto antigo removidos
echo  - Pasta vale-refeicao-ia mantida intacta
echo  - Workspace limpo e organizado
echo ========================================
echo.
pause
