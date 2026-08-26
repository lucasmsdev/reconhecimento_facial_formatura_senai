import asyncio
import io
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Set, Optional

import boto3
import cv2
import numpy as np
from botocore.exceptions import ClientError, NoCredentialsError
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
student_face_images = {}  # {nome: features}
student_audio_cache: Dict[str, bytes] = {}  # {nome: audio mp3 bytes}
telao_connections: Set[WebSocket] = set()
last_recognized: Dict[str, datetime] = {}
DEBOUNCE_SECONDS = 3
CONFIDENCE_THRESHOLD = 0.6


# Load Haar Cascade classifier para detecção de faces
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# AWS S3 Configuration
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
S3_PREFIX = "alunos/"

s3_client = boto3.client("s3", region_name=AWS_REGION) if S3_BUCKET_NAME else None


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
    """Carrega as faces (e áudios) conhecidas.
    Usa o bucket S3 se configurado, senão cai para a pasta local."""
    if S3_BUCKET_NAME and s3_client:
        load_known_faces_from_s3()
    else:
        load_known_faces_from_local()


def load_known_faces_from_s3():
    """Carrega fotos e áudios dos alunos a partir do bucket S3.
    Estrutura esperada: alunos/<Nome do Aluno>/fotoN.jpg + audio.mp3"""
    global student_face_images, student_audio_cache

    student_face_images = {}
    student_audio_cache = {}

    students: Dict[str, Dict[str, list]] = {}

    try:
        paginator = s3_client.get_paginator("list_objects_v2")
        pages = paginator.paginate(Bucket=S3_BUCKET_NAME, Prefix=S3_PREFIX)

        for page in pages:
            for obj in page.get("Contents", []):
                key = obj["Key"]
                relative = key[len(S3_PREFIX):]
                parts = relative.split("/")

                if len(parts) != 2 or not parts[1]:
                    continue

                aluno_name, filename = parts
                filename_lower = filename.lower()
                entry = students.setdefault(aluno_name, {"photos": [], "audio": None})

                if filename_lower.endswith((".jpg", ".jpeg", ".png")):
                    entry["photos"].append(key)
                elif filename_lower.endswith(".mp3"):
                    entry["audio"] = key
    except NoCredentialsError:
        print("Credenciais AWS não encontradas! Configure AWS_ACCESS_KEY_ID e AWS_SECRET_ACCESS_KEY no .env")
        return
    except ClientError as e:
        print(f"Erro ao listar objetos no bucket S3: {e}")
        return

    if not students:
        print(f"Nenhum aluno encontrado em s3://{S3_BUCKET_NAME}/{S3_PREFIX}")
        return

    print(f"Carregando {len(students)} aluno(s) do bucket S3...")

    for aluno_name, data in students.items():
        print(f"\nAluno: {aluno_name}")

        features_list = []
        for key in data["photos"]:
            try:
                response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=key)
                image_bytes = response["Body"].read()
                image_array = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)

                if image_array is None:
                    print(f"  Erro ao decodificar: {key}")
                    continue

                features = extract_face_features(image_array)
                if features is not None:
                    features_list.append(features)
                    print(f"  Carregado: {key}")
                else:
                    print(f"  Nenhum rosto detectado em: {key}")
            except ClientError as e:
                print(f"  Erro ao baixar {key}: {e}")

        if features_list:
            student_face_images[aluno_name] = np.mean(features_list, axis=0)
            print(f"  Total de {len(features_list)} foto(s) carregada(s)")
        else:
            print(f"  Nenhuma foto valida para {aluno_name}")

        if data["audio"]:
            try:
                response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=data["audio"])
                student_audio_cache[aluno_name] = response["Body"].read()
                print(f"  Audio carregado: {data['audio']}")
            except ClientError as e:
                print(f"  Erro ao baixar audio {data['audio']}: {e}")
        else:
            print(f"  Nenhum audio.mp3 encontrado para {aluno_name}")

    print(f"\nTotal de alunos carregados do S3: {len(student_face_images)}")


def load_known_faces_from_local():
    """Carrega as faces conhecidas da pasta local de alunos cadastrados.
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
    """Retorna o áudio (audio.mp3) do aluno, pré-gerado com Amazon Polly e cacheado do S3."""
    audio_data = student_audio_cache.get(nome)

    if audio_data:
        return StreamingResponse(
            io.BytesIO(audio_data),
            media_type="audio/mpeg",
            headers={"Content-Disposition": f"inline; filename={nome}.mp3"},
        )
    else:
        return {"erro": "Áudio não encontrado para este aluno"}, 404


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
