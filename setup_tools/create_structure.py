import os
from pathlib import Path

"""
Este script é multiplataforma (funciona onde o Python estiver instalado) e usa o módulo pathlib.
Ele cria uma estrutura de diretórios e arquivos para um projeto Python, incluindo um arquivo .gitignore com conteúdo padrão.
Cria um arquivo chamado "create_structure.py"
Isso também criará a pasta simulador_honorarios com toda a estrutura dentro dela.
Lembre-se de preencher o requirements.txt (usando pip freeze > requirements.txt dentro do ambiente virtual ativado) e adicionar uma descrição ao README.md posteriormente
"""
# Nome do diretório raiz do projeto
PROJECT_NAME = "simulador_honorarios"

# Conteúdo padrão para o arquivo .gitignore
GITIGNORE_CONTENT = """
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

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
"""

# Define a estrutura: diretórios e os arquivos dentro deles
STRUCTURE = {
    ".": ["main.py", "requirements.txt", "README.md", ".gitignore"], # Adicionado .gitignore
    "core": ["__init__.py", "constants.py", "inputs.py", "formulas.py", "utils.py"],
    "reports": ["__init__.py", "pdf_generator.py"],
    "output": [], # Diretório para arquivos gerados
    "images": []  # Diretório para imagens, adicionado
}

def create_project_structure(base_path_str: str):
    """Cria a estrutura de pastas e arquivos do projeto."""
    base_path = Path(base_path_str)
    print(f"Criando estrutura para o projeto em: {base_path.resolve()}")

    if base_path.exists() and not base_path.is_dir():
        print(f"Erro: Já existe um arquivo chamado '{base_path_str}' neste local.")
        return

    base_path.mkdir(exist_ok=True) # Cria o diretório raiz

    for dir_name, filenames in STRUCTURE.items():
        if dir_name == ".":
            current_dir_path = base_path
        else:
            current_dir_path = base_path / dir_name
            print(f"  Criando diretório: {current_dir_path}")
            current_dir_path.mkdir(exist_ok=True) # Cria subdiretórios

        for filename in filenames:
            file_path = current_dir_path / filename
            print(f"    Criando arquivo: {file_path}")
            # Cria o arquivo vazio ou sobrescreve se for o .gitignore
            if filename == ".gitignore":
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(GITIGNORE_CONTENT.strip() + "\n") # Escreve o conteúdo
                except IOError as e:
                    print(f"      Erro ao escrever em {filename}: {e}")
            else:
                # Cria arquivo vazio se não existir
                 if not file_path.exists():
                    try:
                        file_path.touch()
                    except IOError as e:
                         print(f"      Erro ao criar {filename}: {e}")
                 else:
                     print(f"      Arquivo {filename} já existe, não modificado.")


    print("\nEstrutura do projeto criada com sucesso!")

if __name__ == "__main__":
    # Cria a estrutura no diretório onde o script for executado
    create_project_structure(PROJECT_NAME)

    # Opcional: Listar a estrutura básica
    print("\nEstrutura básica criada:")
    for root, dirs, files in os.walk(PROJECT_NAME, topdown=True):
        # Ignora diretórios comuns que podem poluir a listagem
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.venv', 'venv', '.vscode', '.idea']]
        files = [f for f in files if f not in ['.DS_Store']]

        level = root.replace(PROJECT_NAME, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print(f'{indent}{os.path.basename(root)}/')
        subindent = ' ' * 4 * (level + 1)
        for f in sorted(files): # Ordena os arquivos para consistência
            print(f'{subindent}{f}')
        # Ordena os diretórios também
        dirs.sort()