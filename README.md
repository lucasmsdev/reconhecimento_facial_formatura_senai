# Sistema de Reconhecimento Facial para Formatura SENAI

Um sistema em tempo real que reconhece o rosto de alunos através da câmera e anuncia seus nomes em voz alta em um telão.

## 🎯 Funcionalidades

- ✅ Reconhecimento facial em tempo real
- ✅ Câmera web integrada
- ✅ Comunicação via WebSocket (tempo real)
- ✅ Síntese de fala em português (Web Speech API)
- ✅ Telão com exibição de nomes em grande escala
- ✅ Sistema de debounce (não anuncia o mesmo aluno repetidas vezes)
- ✅ Histórico de alunos reconhecidos
- ✅ Interface responsiva e moderna

## 📋 Pré-requisitos

- Python 3.8+
- Navegador moderno com suporte a:
  - WebRTC (getUserMedia)
  - WebSocket
  - Web Speech API
  - Canvas API

## 🚀 Instalação

### 1. Clonar o repositório

```bash
git clone https://github.com/lucasmsdev/reconhecimento_facial_formatura_senai.git
cd reconhecimento_facial_formatura_senai
```

### 2. Criar ambiente virtual (recomendado)

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Preparar imagens dos alunos

Coloque as fotos dos alunos cadastrados na pasta `alunos_cadastrados/`:

```
alunos_cadastrados/
├── João Silva.jpg
├── Maria Santos.png
├── Pedro Oliveira.jpg
└── ...
```

**Importante:** O nome do arquivo (sem extensão) será usado como identificador do aluno.

### 5. Executar o servidor

```bash
python main.py
```

O servidor estará disponível em: **http://localhost:8000**

## 🎮 Como Usar

### Página Principal
Acesse `http://localhost:8000` para ver os links para as duas páginas.

### Página da Câmera (`/camera`)
1. Clique em **"Iniciar Câmera"** para acessar sua webcam
2. Clique em **"Iniciar Captura"** para começar o reconhecimento
3. Fique em frente à câmera para ser reconhecido
4. Seu nome será enviado ao telão quando detectado

### Página do Telão (`/telao`)
1. Abra em um monitor/TV de grande tamanho
2. A página ficará aguardando eventos do backend
3. Quando um aluno for reconhecido, seu nome será exibido em grande escala
4. O nome será anunciado automaticamente em português

## 📁 Estrutura do Projeto

```
reconhecimento_facial_formatura_senai/
├── main.py                      # Servidor FastAPI
├── requirements.txt             # Dependências Python
├── alunos_cadastrados/          # Pasta com fotos dos alunos
│   ├── João Silva.jpg
│   └── ...
├── templates/
│   ├── camera.html              # Página da câmera
│   └── telao.html               # Página do telão
└── static/                      # Arquivos estáticos (CSS, JS)
```

## 🔧 Configuração Avançada

### Ajustar tempo de debounce

No `main.py`, altere a constante:

```python
DEBOUNCE_SECONDS = 3  # Tempo em segundos
```

### Ajustar tolerância de reconhecimento

No `main.py`, na função `recognize_face()`:

```python
matches = face_recognition.compare_faces(
    known_face_encodings,
    face_encoding,
    tolerance=0.6  # Aumentar para ser mais tolerante, diminuir para mais restritivo
)
```

### Alterar intervalo de captura de frames

No `camera.html`, na função `startCapture()`:

```javascript
captureInterval = setInterval(captureFrame, 500);  // 500ms = 2 frames/segundo
```

## 🌐 Deploy

### Local Network
Para acessar de outros dispositivos na mesma rede:

```bash
python main.py
```

Então acesse: `http://seu-ip-do-servidor:8000`

### Docker (opcional)

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

Build e run:
```bash
docker build -t face-recognition .
docker run -p 8000:8000 -v $(pwd)/alunos_cadastrados:/app/alunos_cadastrados face-recognition
```

## 🐛 Troubleshooting

### "Nenhuma imagem encontrada em alunos_cadastrados"
- Verifique se as imagens estão na pasta correta
- Formatos suportados: `.jpg`, `.png`, `.jpeg`
- O nome do arquivo deve incluir a extensão

### Nenhum rosto detectado
- Certifique-se de que a foto é clara e bem iluminada
- Tente usar diferentes ângulos ou distâncias
- Aumentar a tolerância em `recognize_face()` pode ajudar

### Câmera não conecta
- Verifique as permissões do navegador
- Chrome/Firefox podem exigir HTTPS para produção
- Tente em outro navegador

### Web Speech API não funciona
- Nem todos os navegadores suportam fala em português
- Chrome e Firefox têm melhor suporte
- Alguns navegadores requerem interação do usuário primeiro

## 📝 Notas Importantes

1. **Privacidade**: As imagens dos alunos são processadas localmente. Nenhuma imagem é enviada para servidores externos.

2. **Performance**: Para melhor performance com muitos alunos (100+), considere:
   - Reduzir a resolução das imagens de entrada
   - Aumentar o intervalo de captura
   - Usar um servidor mais potente

3. **Segurança**: Para produção:
   - Adicionar autenticação
   - Usar HTTPS
   - Validar origem das requisições
   - Implementar rate limiting

## 📚 Dependências

- **FastAPI**: Framework web moderno
- **Uvicorn**: Servidor ASGI
- **face_recognition**: Biblioteca de reconhecimento facial
- **OpenCV**: Processamento de imagens
- **Pillow**: Manipulação de imagens
- **NumPy**: Operações numéricas

## 📄 Licença

MIT License - veja LICENSE para detalhes

## 👥 Autor

Desenvolvido para a Formatura SENAI

## 🤝 Contribuições

Sugestões e melhorias são bem-vindas!
