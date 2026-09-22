from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from supabase import create_client

from datetime import datetime, timedelta
from dotenv import load_dotenv

import secrets
import string
import os
import shutil
import mimetypes
import asyncio
import psycopg2


# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv(
    "SUPABASE_SERVICE_ROLE_KEY"
)

if not SUPABASE_URL:
    raise RuntimeError("SUPABASE_URL is not set")

if not SUPABASE_SERVICE_ROLE_KEY:
    raise RuntimeError(
        "SUPABASE_SERVICE_ROLE_KEY is not set"
    )

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_SERVICE_ROLE_KEY
)

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")


# Connect to Supabase PostgreSQL
def get_db_connection():
    return psycopg2.connect(DATABASE_URL)


app = FastAPI(title="Anonymous File Transfer")


# Start expiration cleanup worker
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(
        cleanup_expired_drops()
    )


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


UPLOAD_DIR = "uploads"

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)


# Generate Drop ID
def generate_drop_id(length: int = 8) -> str:
    characters = string.ascii_uppercase + string.digits

    return "".join(
        secrets.choice(characters)
        for _ in range(length)
    )


# Generate File ID
def generate_file_id() -> str:
    return secrets.token_urlsafe(16)


# Automatically delete expired Drops
async def cleanup_expired_drops():
    while True:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT drop_id
                FROM drops
                WHERE expires_at IS NOT NULL
                AND expires_at <= NOW()
                """
            )

            expired_drops = cursor.fetchall()

            for (drop_id,) in expired_drops:

                cursor.execute(
                    """
                    SELECT storage_path
                    FROM files
                    WHERE drop_id = %s
                    """,
                    (drop_id,)
                )

                storage_files = cursor.fetchall()

                storage_delete_failed = False

                for (storage_path,) in storage_files:
                    try:
                        supabase.storage.from_(
                            "uploads"
                        ).remove(
                            [storage_path]
                        )

                        print(
                            f"Deleted storage file: {storage_path}"
                        )

                    except Exception as error:
                        storage_delete_failed = True

                        print(
                            f"Could not delete storage file "
                            f"{storage_path}: {error}"
                        )

                # IMPORTANT:
                # Do not delete the database record if
                # Storage deletion failed.
                if storage_delete_failed:
                    print(
                        f"Skipping database deletion "
                        f"for Drop: {drop_id}"
                    )
                    continue

                cursor.execute(
                    """
                    DELETE FROM drops
                    WHERE drop_id = %s
                    """,
                    (drop_id,)
                )

                print(
                    f"Expired Drop deleted: {drop_id}"
                )

            conn.commit()

            cursor.close()
            conn.close()

        except Exception as error:
            print(
                f"Could not clean expired Drops: {error}"
            )

        await asyncio.sleep(60)
    while True:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT drop_id
                FROM drops
                WHERE expires_at IS NOT NULL
                AND expires_at <= NOW()
                """
            )

            expired_drops = cursor.fetchall()

            for (drop_id,) in expired_drops:

                # Get Storage paths
                cursor.execute(
                    """
                    SELECT storage_path
                    FROM files
                    WHERE drop_id = %s
                    """,
                    (drop_id,)
                )

                storage_files = cursor.fetchall()

                # Delete files from Supabase Storage
                for (storage_path,) in storage_files:
                    try:
                        supabase.storage.from_(
                            "uploads"
                        ).remove(
                            [storage_path]
                        )
                    except Exception as error:
                        print(
                            f"Could not delete "
                            f"{storage_path}: {error}"
                        )

                # Delete Drop from database
                cursor.execute(
                    """
                    DELETE FROM drops
                    WHERE drop_id = %s
                    """,
                    (drop_id,)
                )

                print(
                    f"Expired Drop deleted: {drop_id}"
                )

            conn.commit()

            cursor.close()
            conn.close()

        except Exception as error:
            print(
                f"Could not clean expired Drops: {error}"
            )

        await asyncio.sleep(60)
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT drop_id
                FROM drops
                WHERE expires_at IS NOT NULL
                AND expires_at <= NOW()
                """
            )

            expired_drops = cursor.fetchall()

            for (drop_id,) in expired_drops:

                cursor.execute(
                    """
                    DELETE FROM drops
                    WHERE drop_id = %s
                    """,
                    (drop_id,)
                )

                print(
                    f"Expired Drop deleted: {drop_id}"
                )

            conn.commit()
            cursor.close()
            conn.close()

        except Exception as error:
            print(
                f"Could not clean expired Drops: {error}"
            )

        await asyncio.sleep(60)


# API status
@app.get("/")
def root():
    return {
        "message": "Anonymous File Transfer API is running"
    }


# Create Drop
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
        expires_at = (
            created_at +
            timedelta(hours=24)
        )
    else:
        expires_at = None

    conn = get_db_connection()
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
    conn.close()

    # Create local folder for actual files
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


# Upload file
@app.post("/drops/{drop_id}/files")
async def upload_file(
    drop_id: str,
    file: UploadFile = File(...)
):

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check Drop exists
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
        conn.close()

        raise HTTPException(
            status_code=404,
            detail="Drop not found"
        )

    # Generate file information
    file_id = generate_file_id()

    filename = os.path.basename(
        file.filename
    )

    drop_folder = os.path.join(
        UPLOAD_DIR,
        drop_id
    )

    os.makedirs(
        drop_folder,
        exist_ok=True
    )

    _, extension = os.path.splitext(filename)

    storage_path = f"{drop_id}/{file_id}{extension}"

    file_bytes = await file.read()

    supabase.storage.from_("uploads").upload(
        storage_path,
        file_bytes,
        {
            "content-type": file.content_type
            or "application/octet-stream"
        }
    )

    # Save metadata in Supabase
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
    conn.close()

    return {
        "message": "File uploaded successfully",
        "drop_id": drop_id,
        "file_id": file_id,
        "filename": filename
    }


# Get Drop
@app.get("/drops/{drop_id}")
def get_drop(drop_id: str):

    conn = get_db_connection()
    cursor = conn.cursor()

    # Get Drop metadata
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
        conn.close()

        raise HTTPException(
            status_code=404,
            detail="Drop not found"
        )

    # Get files belonging to Drop
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
    conn.close()

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


# Download file
@app.get("/files/{file_id}/download")
def download_file(file_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT filename, storage_path
        FROM files
        WHERE file_id = %s
        """,
        (file_id,)
    )

    result = cursor.fetchone()

    cursor.close()
    conn.close()

    if not result:
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )

    filename, storage_path = result

    try:
        file_bytes = supabase.storage.from_(
            "uploads"
        ).download(storage_path)

    except Exception:
        raise HTTPException(
            status_code=404,
            detail="File not found in storage"
        )

    media_type, _ = mimetypes.guess_type(filename)

    from fastapi.responses import Response

    return Response(
        content=file_bytes,
        media_type=media_type or "application/octet-stream",
        headers={
            "Content-Disposition": (
                f'attachment; filename="{filename}"'
            )
        }
    )

    for drop_id in os.listdir(UPLOAD_DIR):

        drop_folder = os.path.join(
            UPLOAD_DIR,
            drop_id
        )

        if not os.path.isdir(drop_folder):
            continue

        for stored_filename in os.listdir(
            drop_folder
        ):

            if stored_filename.startswith(
                file_id + "_"
            ):

                file_path = os.path.join(
                    drop_folder,
                    stored_filename
                )

                filename = stored_filename.split(
                    "_",
                    1
                )[1]

                media_type, _ = mimetypes.guess_type(
                    filename
                )

                return FileResponse(
                    path=file_path,
                    filename=filename,
                    media_type=(
                        media_type
                        or "application/octet-stream"
                    )
                )

    raise HTTPException(
        status_code=404,
        detail="File not found"
    )


# Delete Drop
@app.delete("/drops/{drop_id}")
def delete_drop(
    drop_id: str,
    delete_token: str
):

    conn = get_db_connection()
    cursor = conn.cursor()

    # Get stored delete token
    cursor.execute(
        """
        SELECT delete_token
        FROM drops
        WHERE drop_id = %s
        """,
        (drop_id,)
    )

    result = cursor.fetchone()

    if not result:
        cursor.close()
        conn.close()

        raise HTTPException(
            status_code=404,
            detail="Drop not found"
        )

    stored_token = result[0]

    # Verify creator token
    if stored_token != delete_token:
        cursor.close()
        conn.close()

        raise HTTPException(
            status_code=403,
            detail="Invalid delete token"
        )

    # Delete local files
    drop_folder = os.path.join(
        UPLOAD_DIR,
        drop_id
    )

    if os.path.exists(drop_folder):
        shutil.rmtree(drop_folder)

        # Get all storage paths for this Drop
        cursor.execute(
            """
            SELECT storage_path
            FROM files
            WHERE drop_id = %s
            """,
            (drop_id,)
        )

        storage_files = cursor.fetchall()

        # Delete files from Supabase Storage
        for (storage_path,) in storage_files:
            try:
                supabase.storage.from_("uploads").remove(
                    [storage_path]
                )
            except Exception as error:
                print(
                    f"Could not delete {storage_path}: {error}"
                )

    # Delete database record
    # files are automatically deleted because
    # drop_id uses ON DELETE CASCADE
    cursor.execute(
        """
        DELETE FROM drops
        WHERE drop_id = %s
        """,
        (drop_id,)
    )

    conn.commit()

    cursor.close()
    conn.close()

    return {
        "message": "Drop deleted successfully",
        "drop_id": drop_id
    }