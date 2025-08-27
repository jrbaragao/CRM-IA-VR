@echo off
echo Restaurando arquivos do Git...

cd /d D:\Dados\Sites\Cursor\CRMIA-VR\vale-refeicao-ia

REM Restaurar arquivos principais
git checkout HEAD~1 -- app.py
git checkout HEAD~1 -- .gitignore
git checkout HEAD~1 -- LICENSE
git checkout HEAD~1 -- README.md
git checkout HEAD~1 -- CONTRIBUTING.md
git checkout HEAD~1 -- DEPLOY.md
git checkout HEAD~1 -- pyproject.toml

REM Restaurar diretórios
git checkout HEAD~1 -- .streamlit/
git checkout HEAD~1 -- src/
git checkout HEAD~1 -- prompts/

echo.
echo Arquivos restaurados!
echo.
dir /b

pause
