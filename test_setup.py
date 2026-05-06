#!/usr/bin/env python
"""
Script para testar se o ambiente está configurado corretamente.
"""

import sys
from pathlib import Path


def test_imports():
    """Testa se todas as bibliotecas necessárias podem ser importadas."""
    print("🔍 Testando importações...")

    required_modules = {
        'fastapi': 'FastAPI',
        'uvicorn': 'Uvicorn',
        'cv2': 'OpenCV',
        'numpy': 'NumPy',
        'PIL': 'Pillow',
        'websockets': 'WebSockets',
    }

    all_ok = True
    for module, name in required_modules.items():
        try:
            __import__(module)
            print(f"  ✓ {name}")
        except ImportError as e:
            print(f"  ✗ {name}: {e}")
            all_ok = False

    return all_ok


def test_directories():
    """Testa se as pastas necessárias existem."""
    print("\n📁 Testando diretórios...")

    required_dirs = {
        'templates': 'Pasta templates',
        'alunos_cadastrados': 'Pasta alunos_cadastrados',
    }

    all_ok = True
    for dir_name, desc in required_dirs.items():
        path = Path(dir_name)
        if path.exists() and path.is_dir():
            print(f"  ✓ {desc}")
        else:
            print(f"  ✗ {desc}: não encontrada")
            all_ok = False

    return all_ok


def test_files():
    """Testa se os arquivos necessários existem."""
    print("\n📄 Testando arquivos...")

    required_files = {
        'main.py': 'Servidor principal',
        'requirements.txt': 'Dependências',
        'templates/camera.html': 'Página da câmera',
        'templates/telao.html': 'Página do telão',
    }

    all_ok = True
    for file_name, desc in required_files.items():
        path = Path(file_name)
        if path.exists() and path.is_file():
            print(f"  ✓ {desc}")
        else:
            print(f"  ✗ {desc}: não encontrado")
            all_ok = False

    return all_ok


def test_student_photos():
    """Testa se há fotos de alunos cadastrados."""
    print("\n📷 Testando fotos dos alunos...")

    alunos_dir = Path('alunos_cadastrados')
    if not alunos_dir.exists():
        print("  ⚠ Pasta alunos_cadastrados não existe")
        return False

    photos = list(alunos_dir.glob('*.jpg')) + \
             list(alunos_dir.glob('*.jpeg')) + \
             list(alunos_dir.glob('*.png'))

    if photos:
        print(f"  ✓ {len(photos)} foto(s) encontrada(s):")
        for photo in photos:
            print(f"    - {photo.name}")
        return True
    else:
        print("  ⚠ Nenhuma foto encontrada em alunos_cadastrados/")
        print("    Adicione fotos dos alunos com os nomes deles:")
        print("    ex: alunos_cadastrados/João Silva.jpg")
        return False


def main():
    """Executa todos os testes."""
    print("=" * 50)
    print("🧪 Verificação de Instalação")
    print("=" * 50 + "\n")

    results = []

    results.append(("Importações", test_imports()))
    results.append(("Diretórios", test_directories()))
    results.append(("Arquivos", test_files()))
    test_student_photos()  # Este é opcional

    print("\n" + "=" * 50)
    print("📊 Resumo:")
    print("=" * 50)

    all_ok = True
    for test_name, passed in results:
        status = "✓ PASSOU" if passed else "✗ FALHOU"
        print(f"{test_name}: {status}")
        all_ok = all_ok and passed

    print("\n" + "=" * 50)

    if all_ok:
        print("✅ Tudo está configurado corretamente!")
        print("\nPara iniciar o servidor, execute:")
        print("  python main.py")
        print("\nDepois acesse: http://localhost:8000")
        return 0
    else:
        print("❌ Há problemas na configuração.")
        print("\nExecute:")
        print("  pip install -r requirements.txt")
        return 1


if __name__ == '__main__':
    sys.exit(main())
