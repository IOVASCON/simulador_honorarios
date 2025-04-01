#!/bin/bash

# Script para criar a estrutura de diretórios e arquivos
# para o projeto simulador_honorarios, incluindo images e .gitignore

# Usando um Script Shell (Bash/Zsh - para Linux/macOS/Git Bash no Windows)
# Este script é conciso e usa comandos comuns do terminal.
# Cria um arquivo chamado create_project_structure.sh.
# Dê permissão de execução (no terminal):
#    chmod +x create_project_structure.sh
# Execute o script (no terminal, no diretório onde você salvou o script):
#    ./create_project_structure.sh
# Isso criará a pasta simulador_honorarios com toda a estrutura dentro dela, no local onde você executou o script.

Este script é conciso e usa comandos comuns do terminal.

Crie um arquivo chamado create_project_structure.sh.

PROJECT_NAME="simulador_honorarios"

echo "Criando estrutura para o projeto: $PROJECT_NAME"

# Cria o diretório raiz do projeto
mkdir -p "$PROJECT_NAME"
cd "$PROJECT_NAME" || exit # Entra no diretório ou sai se falhar

# Cria subdiretórios principais
echo "Criando diretórios..."
mkdir -p core reports output images # Adicionado 'images'

# Cria arquivos vazios no diretório raiz
echo "Criando arquivos na raiz..."
touch main.py
touch requirements.txt
touch README.md
# Cria o .gitignore com conteúdo inicial
echo "Criando .gitignore..."
cat << EOF > .gitignore
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*\$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
# Usually these files are written by a python script from a template
# before PyInstaller builds the exe, so as to inject date/other infos into it.
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
.python-version

# pipenv
# According to pypa/pipenv#598, it is recommended to include Pipfile.lock in version control.
# Pipfile.lock

# PEP 582; used by poetry and pdm
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyderworkspace

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# pytype static checker
.pytype/

# Output directory for this project
output/
*.pdf

# IDE / Editor specific files
.vscode/
.idea/
*.swp
*.swo
*~
EOF

# Cria arquivos vazios no diretório core
echo "Criando arquivos em core/..."
touch core/__init__.py
touch core/constants.py
touch core/inputs.py
touch core/formulas.py
touch core/utils.py

# Cria arquivos vazios no diretório reports
echo "Criando arquivos em reports/..."
touch reports/__init__.py
touch reports/pdf_generator.py

# (O diretório output/ e images/ permanecem vazios inicialmente)

echo "Estrutura do projeto $PROJECT_NAME criada com sucesso!"
echo "Diretório atual: $(pwd)"

# Lista a estrutura criada (opcional)
# tree -L 2 # Se tiver o comando tree instalado

cd .. # Volta para o diretório anterior (opcional)