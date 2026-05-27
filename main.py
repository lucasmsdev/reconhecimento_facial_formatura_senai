import asyncio
import io
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Set, Optional

import cv2
import numpy as np
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image
from starlette.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI(title="Sistema de Reconhecimento Facial")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Paths
ALUNOS_DIR = Path("alunos_cadastrados")
ALUNOS_DIR.mkdir(exist_ok=True)

# Global state
student_face_images = {}  # {nome: [imagens processadas]}
telao_connections: Set[WebSocket] = set()
last_recognized: Dict[str, datetime] = {}
DEBOUNCE_SECONDS = 3
CONFIDENCE_THRESHOLD = 0.6


# Load Haar Cascade classifier para detecção de faces
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# ElevenLabs Configuration
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"
ELEVENLABS_URL = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"


def extract_face_features(image_array) -> Optional[np.ndarray]:
    """Extrai features de um rosto usando OpenCV Haar Cascade."""
    try:
        # Converter para escala de cinza
        gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)

        # Detectar rostos
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)

        if len(faces) == 0:
            return None

        # Pegar o primeiro rosto detectado
        x, y, w, h = faces[0]

        # Extrair região do rosto
        face_region = image_array[y : y + h, x : x + w]

        if face_region.size == 0:
            return None

        # Redimensionar para tamanho fixo para consistência
        face_resized = cv2.resize(face_region, (224, 224))

        # Criar um "fingerprint" simples usando histogramas
        hist_b = cv2.calcHist([face_resized], [0], None, [32], [0, 256])
        hist_g = cv2.calcHist([face_resized], [1], None, [32], [0, 256])
        hist_r = cv2.calcHist([face_resized], [2], None, [32], [0, 256])

        # Concatenar histogramas
        features = np.concatenate([hist_b.flatten(), hist_g.flatten(), hist_r.flatten()])
        features = features / (np.linalg.norm(features) + 1e-6)  # Normalizar

        return features
    except Exception as e:
        print(f"Erro ao extrair features: {e}")
        return None


def load_known_faces():
    """Carrega as faces conhecidas da pasta de alunos cadastrados.
    Busca por subpastas nomeadas com o nome do aluno."""
    global student_face_images

    student_face_images = {}

    if not ALUNOS_DIR.exists():
        print(f"Pasta {ALUNOS_DIR} não encontrada!")
        return

    # Buscar subpastas (cada pasta é um aluno)
    student_folders = [d for d in ALUNOS_DIR.iterdir() if d.is_dir()]

    if not student_folders:
        # Se não houver pastas, buscar imagens diretamente
        image_files = (
            list(ALUNOS_DIR.glob("*.jpg"))
            + list(ALUNOS_DIR.glob("*.png"))
            + list(ALUNOS_DIR.glob("*.jpeg"))
        )

        if not image_files:
            print(f"Nenhuma imagem encontrada em {ALUNOS_DIR}")
            return

        print(f"Carregando {len(image_files)} imagens...")

        for image_path in image_files:
            try:
                aluno_name = image_path.stem
                image = cv2.imread(str(image_path))
                if image is None:
                    print(f"Erro ao ler: {image_path.name}")
                    continue

                features = extract_face_features(image)
                if features is not None:
                    student_face_images[aluno_name] = features
                    print(f"Carregado: {aluno_name}")
                else:
                    print(f"Nenhum rosto detectado em: {image_path.name}")
            except Exception as e:
                print(f"Erro ao processar {image_path.name}: {e}")
    else:
        # Carregar imagens de subpastas
        print(f"Carregando imagens de {len(student_folders)} aluno(s)...")

        for student_folder in student_folders:
            aluno_name = student_folder.name
            print(f"\nAluno: {aluno_name}")

            image_files = (
                list(student_folder.glob("*.jpg"))
                + list(student_folder.glob("*.png"))
                + list(student_folder.glob("*.jpeg"))
            )

            if not image_files:
                print(f"  Nenhuma imagem encontrada em {aluno_name}/")
                continue

            features_list = []

            for image_path in image_files:
                try:
                    image = cv2.imread(str(image_path))
                    if image is None:
                        print(f"  Erro ao ler: {image_path.name}")
                        continue

                    features = extract_face_features(image)
                    if features is not None:
                        features_list.append(features)
                        print(f"  Carregado: {image_path.name}")
                    else:
                        print(f"  Nenhum rosto detectado em: {image_path.name}")
                except Exception as e:
                    print(f"  Erro ao processar {image_path.name}: {e}")

            if features_list:
                # Usar a média de todas as features
                student_face_images[aluno_name] = np.mean(features_list, axis=0)
                print(f"  Total de {len(features_list)} foto(s) carregada(s)")
            else:
                print(f"  Nenhuma foto valida para {aluno_name}")

    print(f"\nTotal de alunos carregados: {len(student_face_images)}")


def recognize_face(image_data: bytes) -> Optional[str]:
    """
    Identifica um rosto em uma imagem.
    Retorna o nome do aluno ou None se não reconhecer.
    """
    try:
        # Converter bytes para imagem
        image = Image.open(io.BytesIO(image_data))
        image_array = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        # Extrair features
        face_features = extract_face_features(image_array)

        if face_features is None:
            return None

        # Comparar com rostos conhecidos
        best_match = None
        best_score = CONFIDENCE_THRESHOLD

        for aluno_name, stored_features in student_face_images.items():
            # Calcular similaridade (cosseno)
            similarity = np.dot(face_features, stored_features) / (
                np.linalg.norm(face_features) * np.linalg.norm(stored_features) + 1e-6
            )

            if similarity > best_score:
                best_score = similarity
                best_match = aluno_name

        return best_match
    except Exception as e:
        print(f"Erro ao reconhecer rosto: {e}")
        return None


def should_announce(nome: str) -> bool:
    """
    Verifica se o aluno deve ser anunciado (debounce).
    """
    now = datetime.now()

    if nome not in last_recognized:
        last_recognized[nome] = now
        return True

    last_time = last_recognized[nome]
    if (now - last_time).total_seconds() >= DEBOUNCE_SECONDS:
        last_recognized[nome] = now
        return True

    return False


async def broadcast_to_telao(nome: str):
    """Envia o nome para todos os clientes do telão conectados."""
    if not telao_connections:
        return

    message = f"ALUNO:{nome}"

    disconnected = set()
    for websocket in telao_connections:
        try:
            await websocket.send_text(message)
        except Exception as e:
            print(f"Erro ao enviar para telão: {e}")
            disconnected.add(websocket)

    # Remover conexões desconectadas
    for ws in disconnected:
        telao_connections.discard(ws)


def generate_audio_elevenlabs(nome: str) -> Optional[bytes]:
    """Gera áudio com ElevenLabs para o nome do aluno."""
    if not ELEVENLABS_API_KEY:
        print("ELEVENLABS_API_KEY não configurada!")
        return None

    try:
        headers = {
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json",
        }

        data = {
            "text": nome,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
            },
        }

        response = requests.post(ELEVENLABS_URL, json=data, headers=headers, timeout=10)

        if response.status_code == 200:
            return response.content
        else:
            print(f"Erro ElevenLabs: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Erro ao gerar áudio: {e}")
        return None


@app.on_event("startup")
async def startup_event():
    """Carrega as faces conhecidas ao iniciar o servidor."""
    load_known_faces()


@app.get("/")
async def root():
    """Página raiz com links para câmera e telão."""
    return HTMLResponse(
        """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Sistema de Reconhecimento Facial</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background: white;
            }
            .container {
                text-align: center;
                background: white;
                padding: 40px;
                border: 3px solid #000;
                border-radius: 10px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            }
            h1 {
                color: #000;
                margin-bottom: 30px;
                border-bottom: 3px solid #c41e3a;
                padding-bottom: 15px;
            }
            .buttons {
                display: flex;
                gap: 20px;
                justify-content: center;
            }
            a {
                display: inline-block;
                padding: 15px 30px;
                font-size: 16px;
                text-decoration: none;
                border-radius: 5px;
                transition: transform 0.2s, box-shadow 0.2s;
                border: 2px solid #000;
                font-weight: 600;
            }
            .btn-camera {
                background: #c41e3a;
                color: white;
                border-color: #c41e3a;
            }
            .btn-camera:hover {
                background: white;
                color: #c41e3a;
            }
            .btn-telao {
                background: #c41e3a;
                color: white;
                border-color: #c41e3a;
            }
            .btn-telao:hover {
                background: white;
                color: #c41e3a;
            }
            a:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(196, 30, 58, 0.3);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Sistema de Reconhecimento Facial</h1>
            <div class="buttons">
                <a href="/camera" class="btn-camera">Câmera</a>
                <a href="/telao" class="btn-telao">Telão</a>
            </div>
        </div>
    </body>
    </html>
    """
    )


@app.get("/camera")
async def camera_page():
    """Página da câmera."""
    with open("templates/camera.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())


@app.get("/telao")
async def telao_page():
    """Página do telão."""
    with open("templates/telao.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())


@app.post("/api/recognize")
async def recognize(file: UploadFile = File(...)):
    """Endpoint para reconhecimento de rosto."""
    try:
        image_data = await file.read()
        nome = recognize_face(image_data)

        if nome and should_announce(nome):
            await broadcast_to_telao(nome)
            return {"reconhecido": True, "nome": nome}
        elif nome:
            return {"reconhecido": True, "nome": nome, "debounced": True}
        else:
            return {"reconhecido": False}
    except Exception as e:
        print(f"Erro em /recognize: {e}")
        return {"erro": str(e)}, 500


@app.get("/api/speak/{nome}")
async def speak(nome: str):
    """Gera áudio com ElevenLabs para o nome do aluno."""
    audio_data = generate_audio_elevenlabs(nome)

    if audio_data:
        return StreamingResponse(
            io.BytesIO(audio_data),
            media_type="audio/mpeg",
            headers={"Content-Disposition": f"inline; filename={nome}.mp3"},
        )
    else:
        return {"erro": "Não foi possível gerar o áudio"}, 500


@app.websocket("/ws/telao")
async def websocket_telao(websocket: WebSocket):
    """WebSocket para a página do telão."""
    await websocket.accept()
    telao_connections.add(websocket)
    print(f"✓ Cliente telão conectado. Total: {len(telao_connections)}")

    try:
        while True:
            # Manter a conexão aberta
            await websocket.receive_text()
    except WebSocketDisconnect:
        telao_connections.discard(websocket)
        print(f"✗ Cliente telão desconectado. Total: {len(telao_connections)}")
    except Exception as e:
        print(f"Erro em WebSocket telão: {e}")
        telao_connections.discard(websocket)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
