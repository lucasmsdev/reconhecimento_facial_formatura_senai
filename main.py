import asyncio
import base64
import io
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Set

import face_recognition
import numpy as np
from fastapi import FastAPI, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image
from starlette.middleware.cors import CORSMiddleware

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
known_face_encodings = []
known_face_names = []
telao_connections: Set[WebSocket] = set()
last_recognized: Dict[str, datetime] = {}
DEBOUNCE_SECONDS = 3


def load_known_faces():
    """Carrega as faces conhecidas da pasta de alunos cadastrados."""
    global known_face_encodings, known_face_names

    known_face_encodings = []
    known_face_names = []

    if not ALUNOS_DIR.exists():
        print(f"Pasta {ALUNOS_DIR} não encontrada!")
        return

    image_files = list(ALUNOS_DIR.glob("*.jpg")) + list(ALUNOS_DIR.glob("*.png")) + list(ALUNOS_DIR.glob("*.jpeg"))

    if not image_files:
        print(f"Nenhuma imagem encontrada em {ALUNOS_DIR}")
        return

    print(f"Carregando {len(image_files)} imagens...")

    for image_path in image_files:
        try:
            # Nome do aluno é o nome do arquivo sem extensão
            aluno_name = image_path.stem

            # Carregar imagem
            image = face_recognition.load_image_file(str(image_path))
            face_encodings = face_recognition.face_encodings(image)

            if face_encodings:
                known_face_encodings.append(face_encodings[0])
                known_face_names.append(aluno_name)
                print(f"✓ Carregado: {aluno_name}")
            else:
                print(f"✗ Nenhum rosto detectado em: {image_path.name}")
        except Exception as e:
            print(f"✗ Erro ao processar {image_path.name}: {e}")

    print(f"Total de alunos carregados: {len(known_face_encodings)}")


def recognize_face(image_data: bytes) -> str | None:
    """
    Identifica um rosto em uma imagem.
    Retorna o nome do aluno ou None se não reconhecer.
    """
    try:
        # Converter bytes para imagem PIL
        image = Image.open(io.BytesIO(image_data))

        # Converter para array numpy
        image_array = np.array(image)

        # Se a imagem for RGBA, converter para RGB
        if len(image_array.shape) == 3 and image_array.shape[2] == 4:
            image_array = image_array[:, :, :3]

        # Detectar faces e encodar
        face_locations = face_recognition.face_locations(image_array)
        face_encodings = face_recognition.face_encodings(image_array, face_locations)

        if not face_encodings:
            return None

        # Comparar com faces conhecidas
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(
                known_face_encodings,
                face_encoding,
                tolerance=0.6
            )
            distances = face_recognition.face_distance(
                known_face_encodings,
                face_encoding
            )

            if len(distances) > 0:
                best_match_index = np.argmin(distances)

                if matches[best_match_index]:
                    name = known_face_names[best_match_index]
                    confidence = 1 - distances[best_match_index]

                    # Só reconhecer se confiança > 0.4
                    if confidence > 0.4:
                        return name

        return None
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


@app.on_event("startup")
async def startup_event():
    """Carrega as faces conhecidas ao iniciar o servidor."""
    load_known_faces()


@app.get("/")
async def root():
    """Página raiz com links para câmera e telão."""
    return HTMLResponse("""
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
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }
            .container {
                text-align: center;
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            }
            h1 {
                color: #333;
                margin-bottom: 30px;
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
            }
            .btn-camera {
                background: #667eea;
                color: white;
            }
            .btn-telao {
                background: #764ba2;
                color: white;
            }
            a:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.3);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Sistema de Reconhecimento Facial</h1>
            <div class="buttons">
                <a href="/camera" class="btn-camera">📷 Câmera</a>
                <a href="/telao" class="btn-telao">📺 Telão</a>
            </div>
        </div>
    </body>
    </html>
    """)


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
            # Broadcast para o telão
            await broadcast_to_telao(nome)
            return {"reconhecido": True, "nome": nome}
        elif nome:
            return {"reconhecido": True, "nome": nome, "debounced": True}
        else:
            return {"reconhecido": False}
    except Exception as e:
        print(f"Erro em /recognize: {e}")
        return {"erro": str(e)}, 500


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
