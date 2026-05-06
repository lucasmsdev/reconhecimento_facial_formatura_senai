# 🪟 Guia para Windows

## Problemas Comuns e Soluções

### 1. **Erro: "Cannot import 'setuptools.build_meta'"**

#### Causa
Python 3.14+ não vem com setuptools pré-instalado e algumas dependências antigas tentam compilar do source.

#### Solução A (Rápida)
```bash
pip install --upgrade setuptools wheel
pip install -r requirements.txt
```

#### Solução B (Recomendada - Use Python 3.11 ou 3.12)
1. Desinstale Python 3.14
2. Baixe Python 3.12 em https://www.python.org/downloads/
3. **Importante:** Marque a opção "Add Python to PATH" durante a instalação
4. Crie novo ambiente virtual:
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

---

### 2. **Erro: "Microsoft C++ Build Tools"**

#### Causa
Algumas bibliotecas (como numpy, face-recognition) precisam compilar código C++.

#### Solução
Baixe e instale Microsoft C++ Build Tools (gratuito):
https://visualstudio.microsoft.com/visual-cpp-build-tools/

Siga os passos:
1. Na instalação, selecione **"Desktop development with C++"**
2. Clique em Install
3. Reinicie o computador
4. Tente `pip install -r requirements.txt` novamente

---

### 3. **Erro: "No module named 'face_recognition'"**

#### Causa
O pacote não foi instalado ou o ambiente virtual não está ativado.

#### Solução
Verifique se o ambiente virtual está ativado:

```bash
# Você deve ver "(venv)" no início da linha no terminal
# Se não tiver, ative:
venv\Scripts\activate
```

Depois instale novamente:
```bash
pip install -r requirements.txt
```

---

### 4. **Erro: "Modelo de câmera não conecta"**

#### Causa
Permissões do navegador ou driver de câmera.

#### Solução
- **Chrome/Edge:** Clique no ícone do cadeado na URL → Permissões → Câmera → Permitir
- **Firefox:** Quando pedir permissão, clique "Permitir"
- **Verifique o driver:** Abra Gerenciador de Dispositivos (devmgmt.msc) e procure por câmera
- **Reinicie o navegador** após mudar permissões

---

### 5. **Erro de compilação de numpy**

#### Causa
Versão antiga de numpy com Python 3.14.

#### Solução
O arquivo requirements.txt foi atualizado para usar versões flexíveis. Tente:

```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

---

## ✅ Checklist de Instalação (Windows)

- [ ] Python 3.11+ instalado (verifique: `python --version`)
- [ ] Python adicionado ao PATH
- [ ] Arquivo requirements.txt atualizado (com `>=` em vez de `==`)
- [ ] setuptools e wheel instalados
- [ ] C++ Build Tools instalado (se houver erro de compilação)
- [ ] Ambiente virtual criado e ativado: `venv\Scripts\activate`
- [ ] Dependências instaladas: `pip install -r requirements.txt`
- [ ] Teste passou: `python test_setup.py`

---

## 🚀 Comando Passo a Passo (Windows)

```bash
# 1. Abra PowerShell ou CMD como Administrador
# 2. Navegue para a pasta do projeto
cd Desktop\reconhecimento_facial_formatura_senai

# 3. Crie ambiente virtual
python -m venv venv

# 4. Ative (nota o backslash)
venv\Scripts\activate

# 5. Atualize ferramentas
python -m pip install --upgrade pip setuptools wheel

# 6. Instale dependências
pip install -r requirements.txt

# 7. Teste a instalação
python test_setup.py

# 8. Se tudo passou, adicione fotos em alunos_cadastrados/

# 9. Inicie o servidor
python main.py
```

---

## 📝 Versões Testadas no Windows

| Python | Status | Notas |
|--------|--------|-------|
| 3.11   | ✅ Funciona | Recomendado |
| 3.12   | ✅ Funciona | Recomendado |
| 3.13   | ⚠️ Pode funcionar | Exigir C++ Build Tools |
| 3.14   | ⚠️ Problemático | Exigir setuptools manual |

---

## 🔧 Solução Nuclear (Se nada funcionar)

```bash
# 1. Delete o ambiente virtual
rmdir /s venv

# 2. Delete cache pip
rmdir /s %APPDATA%\pip

# 3. Crie novo ambiente
python -m venv venv

# 4. Ative
venv\Scripts\activate

# 5. Instale do zero
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 💡 Dicas Extras

### Usar venv em um terminal específico
Se quiser um terminal que já abra com venv ativado, crie um arquivo `ativar_venv.bat`:

```batch
@echo off
cmd /k "cd /d %~dp0 && venv\Scripts\activate"
```

Coloque na pasta do projeto e clique 2x para abrir um terminal com venv já ativado.

### Editar PATH do Windows
Se tiver problema com Python não reconhecido:

1. Pressione `Win + X` → "Editar variáveis de ambiente do sistema"
2. Clique em "Variáveis de Ambiente"
3. Sob "Variáveis do sistema", encontre PATH
4. Clique em "Editar"
5. Adicione o caminho Python: `C:\Users\lucas\AppData\Local\Programs\Python\Python312\`
6. Clique OK várias vezes
7. **Reinicie o CMD/PowerShell**

---

## 🆘 Ainda Com Problema?

Rode este comando para enviar diagnóstico:

```bash
python -m pip list > diagnostic.txt
python --version >> diagnostic.txt
systeminfo >> diagnostic.txt
type diagnostic.txt
```

Compartilhe o conteúdo para diagnosis!

---

**Última atualização:** 2026-05-06
