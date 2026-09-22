from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from dotenv import load_dotenv

import secrets
import string
import os
import shutil
import mimetypes
import json
import asyncio
import psycopg2

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

conn = psycopg2.connect(DATABASE_URL)

app = FastAPI(title="Anonymous File Transfer")

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(
        cleanup_expired_drops()
    )

# Fixing Cors Error - Cors = error when connecting frontend and backend, because both have different links
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


UPLOAD_DIR = "uploads"
drop_tokens = {}
os.makedirs(UPLOAD_DIR, exist_ok=True)

def generate_drop_id(length: int = 8) -> str:
    characters = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(characters) for _ in range(length))


def generate_file_id() -> str:
    return secrets.token_urlsafe(16)

async def cleanup_expired_drops():
    while True:

        now = datetime.utcnow()

        if os.path.exists(UPLOAD_DIR):

            for drop_id in os.listdir(UPLOAD_DIR):

                drop_folder = os.path.join(
                    UPLOAD_DIR,
                    drop_id
                )

                if not os.path.isdir(drop_folder):
                    continue

                metadata_path = os.path.join(
                    drop_folder,
                    "metadata.json"
                )

                if not os.path.exists(metadata_path):
                    continue

                try:
                    with open(
                        metadata_path,
                        "r",
                        encoding="utf-8"
                    ) as file:
                        metadata = json.load(file)

                    expires_at = metadata.get("expires_at")

                    # Permanent Drop
                    if expires_at is None:
                        continue

                    expiration_time = datetime.fromisoformat(
                        expires_at
                    )

                    if now >= expiration_time:

                        shutil.rmtree(drop_folder)

                        drop_tokens.pop(
                            drop_id,
                            None
                        )

                        print(
                            f"Expired Drop deleted: {drop_id}"
                        )

                except Exception as error:
                    print(
                        f"Could not check Drop {drop_id}: {error}"
                    )

        # Check once every minute
        await asyncio.sleep(60)

@app.get("/")
def root():
    return {
        "message": "Anonymous File Transfer API is running"
    }


@app.post("/drops")
def create_drop(lifetime: str = "24h"):
    if lifetime not in ["24h", "permanent"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid drop lifetime"
        )

    drop_id = generate_drop_id()
    delete_token = secrets.token_urlsafe(32)

    created_at = datetime.utcnow()

    if lifetime == "24h":
        expires_at = created_at + timedelta(hours=24)
    else:
        expires_at = None

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO drops (
            drop_id,
            delete_token,
            lifetime,
            created_at,
            expires_at
        )
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            drop_id,
            delete_token,
            lifetime,
            created_at,
            expires_at
        )
    )

    conn.commit()
    cursor.close()

    drop_folder = os.path.join(
        UPLOAD_DIR,
        drop_id
    )

    os.makedirs(
        drop_folder,
        exist_ok=True
    )

    return {
        "drop_id": drop_id,
        "delete_token": delete_token,
        "expires_at": expires_at
    }
    if lifetime not in ["24h", "permanent"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid drop lifetime"
        )

    drop_id = generate_drop_id()
    delete_token = secrets.token_urlsafe(32)

    created_at = datetime.utcnow()

    if lifetime == "24h":
        expires_at = created_at + timedelta(hours=24)
    else:
        expires_at = None

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO drops (
            drop_id,
            delete_token,
            lifetime,
            created_at,
            expires_at
        )
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            drop_id,
            delete_token,
            lifetime,
            created_at,
            expires_at
        )
    )

    conn.commit()
    cursor.close()

    drop_folder = os.path.join(
        UPLOAD_DIR,
        drop_id
    )

    os.makedirs(
        drop_folder,
        exist_ok=True
    )

    return {
        "drop_id": drop_id,
        "delete_token": delete_token,
        "expires_at": expires_at
    }
    drop_id = generate_drop_id()
    delete_token = secrets.token_urlsafe(32)

    if lifetime not in ["24h", "permanent"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid drop lifetime"
        )

    drop_folder = os.path.join(
        UPLOAD_DIR,
        drop_id
    )

    os.makedirs(
        drop_folder,
        exist_ok=True
    )

    drop_tokens[drop_id] = delete_token

    created_at = datetime.utcnow()

    if lifetime == "24h":
        expires_at = created_at + timedelta(hours=24)
        expires_at = expires_at.isoformat()
    else:
        expires_at = None

    metadata = {
        "drop_id": drop_id,
        "delete_token": delete_token,
        "created_at": created_at.isoformat(),
        "expires_at": expires_at
    }

    metadata_path = os.path.join(
        drop_folder,
        "metadata.json"
    )

    with open(
        metadata_path,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            metadata,
            file,
            indent=2
        )

    return {
        "drop_id": drop_id,
        "delete_token": delete_token,
        "expires_at": expires_at
    }


@app.post("/drops/{drop_id}/files")
def upload_file(drop_id: str, file: UploadFile = File(...)):
    cursor = conn.cursor()

    # Check that the Drop exists
    cursor.execute(
        """
        SELECT drop_id
        FROM drops
        WHERE drop_id = %s
        """,
        (drop_id,)
    )

    drop = cursor.fetchone()

    if not drop:
        cursor.close()
        raise HTTPException(
            status_code=404,
            detail="Drop not found"
        )

    # Generate file information
    file_id = generate_file_id()
    filename = os.path.basename(file.filename)

    drop_folder = os.path.join(
        UPLOAD_DIR,
        drop_id
    )

    os.makedirs(
        drop_folder,
        exist_ok=True
    )

    storage_path = os.path.join(
        drop_folder,
        f"{file_id}_{filename}"
    )

    # Save the actual file locally
    with open(storage_path, "wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer
        )

    # Save file metadata in Supabase
    cursor.execute(
        """
        INSERT INTO files (
            file_id,
            drop_id,
            filename,
            storage_path
        )
        VALUES (%s, %s, %s, %s)
        """,
        (
            file_id,
            drop_id,
            filename,
            storage_path
        )
    )

    conn.commit()
    cursor.close()

    return {
        "message": "File uploaded successfully",
        "drop_id": drop_id,
        "file_id": file_id,
        "filename": filename
    }

@app.get("/drops/{drop_id}")
def get_drop(drop_id: str):
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            drop_id,
            created_at,
            expires_at
        FROM drops
        WHERE drop_id = %s
        """,
        (drop_id,)
    )

    drop = cursor.fetchone()

    if not drop:
        cursor.close()
        raise HTTPException(
            status_code=404,
            detail="Drop not found"
        )

    cursor.execute(
        """
        SELECT
            file_id,
            filename
        FROM files
        WHERE drop_id = %s
        ORDER BY created_at
        """,
        (drop_id,)
    )

    file_rows = cursor.fetchall()

    cursor.close()

    files = []

    for file_id, filename in file_rows:
        files.append({
            "file_id": file_id,
            "filename": filename
        })

    return {
        "drop_id": drop[0],
        "created_at": drop[1],
        "expires_at": drop[2],
        "files": files
    }

    drop_folder = os.path.join(
        UPLOAD_DIR,
        drop_id
    )

    if not os.path.exists(drop_folder):
        raise HTTPException(
            status_code=404,
            detail="Drop not found"
        )

    metadata_path = os.path.join(
        drop_folder,
        "metadata.json"
    )

    if not os.path.exists(metadata_path):
        raise HTTPException(
            status_code=500,
            detail="Drop metadata not found"
        )

    with open(
        metadata_path,
        "r",
        encoding="utf-8"
    ) as file:
        metadata = json.load(file)

    files = []

    for stored_filename in os.listdir(drop_folder):

        if stored_filename == "metadata.json":
            continue

        file_path = os.path.join(
            drop_folder,
            stored_filename
        )

        if os.path.isfile(file_path):

            file_id, filename = stored_filename.split("_", 1)

            files.append({
                "file_id": file_id,
                "filename": filename
            })

    return {
        "drop_id": drop_id,
        "created_at": metadata.get("created_at"),
        "expires_at": metadata.get("expires_at"),
        "files": files
    }


@app.get("/files/{file_id}/download")
def download_file(file_id: str):
    for drop_id in os.listdir(UPLOAD_DIR):

        drop_folder = os.path.join(UPLOAD_DIR, drop_id)

        if not os.path.isdir(drop_folder):
            continue

        for stored_filename in os.listdir(drop_folder):

            if stored_filename.startswith(file_id + "_"):

                file_path = os.path.join(
                    drop_folder,
                    stored_filename
                )

                filename = stored_filename.split("_", 1)[1]

                from fastapi.responses import FileResponse

                media_type, _ = mimetypes.guess_type(filename)

                return FileResponse(
                    path=file_path,
                    filename=filename,
                    media_type=media_type or "application/octet-stream"
                )

    raise HTTPException(
        status_code=404,
        detail="File not found"
    )

@app.delete("/drops/{drop_id}")
def delete_drop(
    drop_id: str,
    delete_token: str
):
    drop_folder = os.path.join(UPLOAD_DIR, drop_id)

    if not os.path.exists(drop_folder):
        raise HTTPException(
            status_code=404,
            detail="Drop not found"
        )

    # Temporary MVP protection.
    # The creator's delete token will be stored in memory.
    stored_token = drop_tokens.get(drop_id)

    if stored_token != delete_token:
        raise HTTPException(
            status_code=403,
            detail="Invalid delete token"
        )

    shutil.rmtree(drop_folder)

    del drop_tokens[drop_id]

    return {
        "message": "Drop deleted successfully",
        "drop_id": drop_id
    }