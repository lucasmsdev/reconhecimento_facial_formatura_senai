# 🚀 Guia de Instalação Rápida

## Windows

### 1. Pré-requisitos
- Baixe e instale Python 3.10+ em https://www.python.org
- Certifique-se de marcar "Add Python to PATH" durante a instalação

### 2. Clone o repositório
```bash
git clone https://github.com/lucasmsdev/reconhecimento_facial_formatura_senai.git
cd reconhecimento_facial_formatura_senai
```

### 3. Crie um ambiente virtual
```bash
python -m venv venv
venv\Scripts\activate
```

### 4. Instale as dependências
```bash
pip install -r requirements.txt
```

**Nota:** A instalação pode levar alguns minutos pois `face_recognition` compila código C.

### 5. Adicione as fotos dos alunos
- Crie a pasta `alunos_cadastrados` (já existe)
- Coloque as fotos dos alunos com o nome deles:
  ```
  alunos_cadastrados/
  ├── João Silva.jpg
  ├── Maria Santos.jpg
  └── ...
  ```

### 6. Inicie o servidor
```bash
python main.py
```

### 7. Acesse a aplicação
- Abra seu navegador em http://localhost:8000
- Use a aba "Câmera" para capturar
- Use a aba "Telão" em outro monitor

---

## Linux (Ubuntu/Debian)

### 1. Instale dependências do sistema
```bash
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv cmake libopenblas-dev liblapack-dev libx11-dev
```

### 2. Clone o repositório
```bash
git clone https://github.com/lucasmsdev/reconhecimento_facial_formatura_senai.git
cd reconhecimento_facial_formatura_senai
```

### 3. Crie um ambiente virtual
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Instale as dependências
```bash
pip install -r requirements.txt
```

### 5. Adicione as fotos dos alunos
```bash
mkdir -p alunos_cadastrados
# Copie as fotos para alunos_cadastrados/
```

### 6. Inicie o servidor
```bash
python main.py
```

### 7. Acesse em outro dispositivo (opcional)
```bash
# Descubra seu IP local
hostname -I

# Acesse de outro dispositivo
# http://seu-ip-local:8000
```

---

## macOS

### 1. Instale Homebrew (se não tiver)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. Instale dependências
```bash
brew install python3 cmake
```

### 3. Clone o repositório
```bash
git clone https://github.com/lucasmsdev/reconhecimento_facial_formatura_senai.git
cd reconhecimento_facial_formatura_senai
```

### 4. Crie um ambiente virtual
```bash
python3 -m venv venv
source venv/bin/activate
```

### 5. Instale as dependências
```bash
pip install -r requirements.txt
```

### 6. Adicione as fotos dos alunos
```bash
mkdir -p alunos_cadastrados
# Copie as fotos para alunos_cadastrados/
```

### 7. Inicie o servidor
```bash
python main.py
```

---

## ⚡ Solução de Problemas

### Problema: "ModuleNotFoundError: No module named 'face_recognition'"
**Solução:** Certifique-se de que o ambiente virtual está ativado:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### Problema: "Erro ao instalar face_recognition"
**Solução Windows:**
- Baixe e instale "Microsoft C++ Build Tools"
- Ou instale "Visual Studio Community" com suporte C++

**Solução Linux:**
```bash
sudo apt-get install -y build-essential cmake
```

### Problema: Câmera não funciona
- Verifique as permissões do navegador (clique no ícone do cadeado na URL)
- Tente em outro navegador (Chrome, Firefox)
- Reinicie o navegador

### Problema: Nenhum rosto detectado
- Use fotos em boa iluminação
- Certifique-se de que o rosto ocupa ~30% da imagem
- Tente com múltiplas fotos do mesmo aluno em ângulos diferentes

### Problema: Voz não funciona
- Nem todos navegadores suportam fala em português
- Chrome e Firefox têm melhor suporte
- No macOS, verifique Preferências do Sistema > Acessibilidade > Fala

---

## 🔧 Personalização Rápida

### Alterar porta do servidor
Edite `main.py`:
```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)  # Mude 8000 para outra porta
```

### Mudar intervalo de captura
Edite `templates/camera.html`:
```javascript
captureInterval = setInterval(captureFrame, 1000);  // Mude 500 para 1000 (mais lento)
```

### Aumentar sensibilidade de reconhecimento
Edite `main.py`:
```python
if confidence > 0.4:  # Mude para 0.3 (mais sensível)
```

---

## 📺 Configuração para Múltiplas Telas

1. **PC Câmera:**
   - Abra http://localhost:8000/camera
   - Clique "Iniciar Câmera" → "Iniciar Captura"

2. **Monitor Telão:**
   - Pode estar no mesmo PC ou em outro da rede
   - Acesse http://seu-ip-local:8000/telao
   - Coloque em tela cheia (F11)

---

## 🐳 Usando Docker

### Build
```bash
docker build -t face-recognition .
```

### Run
```bash
docker run -p 8000:8000 \
  -v $(pwd)/alunos_cadastrados:/app/alunos_cadastrados \
  face-recognition
```

### Acesse
```
http://localhost:8000
```

---

## ✅ Verificar Instalação

```bash
# Teste as dependências
python -c "import fastapi, face_recognition, cv2, numpy; print('✓ Todas as dependências OK!')"

# Verifique a estrutura
ls -la
# Deve conter: main.py, requirements.txt, templates/, alunos_cadastrados/
```

---

Pronto! Se tudo funcionou, você deve ver a página inicial em http://localhost:8000 🎉
