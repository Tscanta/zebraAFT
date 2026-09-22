from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from supabase import create_client
from dotenv import load_dotenv

from datetime import datetime, timedelta

import asyncio
import mimetypes
import os
import secrets
import string

import psycopg2


# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv(
    "SUPABASE_SERVICE_ROLE_KEY"
)

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

if not SUPABASE_URL:
    raise RuntimeError("SUPABASE_URL is not set")

if not SUPABASE_SERVICE_ROLE_KEY:
    raise RuntimeError(
        "SUPABASE_SERVICE_ROLE_KEY is not set"
    )


# Connect to Supabase Storage
supabase = create_client(
    SUPABASE_URL,
    SUPABASE_SERVICE_ROLE_KEY
)


# Connect to the Supabase PostgreSQL database
def get_db_connection():
    return psycopg2.connect(DATABASE_URL)


app = FastAPI(title="Anonymous File Transfer")


# Allow requests from the Svelte development server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Start the background cleanup worker when the server starts
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(
        cleanup_expired_drops()
    )


# Generate a short code used to identify a Drop
def generate_drop_id(length: int = 8) -> str:
    characters = string.ascii_uppercase + string.digits

    return "".join(
        secrets.choice(characters)
        for _ in range(length)
    )


# Generate a unique ID for a file
def generate_file_id() -> str:
    return secrets.token_urlsafe(16)


# Delete expired Drops and their files from Storage
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

                # Keep the database record if Storage cleanup failed.
                # This allows the next cleanup cycle to try again.
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

        # Check for expired Drops every 60 seconds
        await asyncio.sleep(60)


# API status
@app.get("/")
def root():
    return {
        "message": "Anonymous File Transfer API is running"
    }


# Create a new Drop
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

    return {
        "drop_id": drop_id,
        "delete_token": delete_token,
        "expires_at": expires_at
    }


# Upload a file to Supabase Storage
@app.post("/drops/{drop_id}/files")
async def upload_file(
    drop_id: str,
    file: UploadFile = File(...)
):

    conn = get_db_connection()
    cursor = conn.cursor()

    # Make sure the Drop exists
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

    # Keep the original filename for downloads,
    # but use a safe generated name in Storage.
    file_id = generate_file_id()

    filename = os.path.basename(
        file.filename
    )

    _, extension = os.path.splitext(filename)

    storage_path = (
        f"{drop_id}/{file_id}{extension}"
    )

    file_bytes = await file.read()

    try:
        supabase.storage.from_(
            "uploads"
        ).upload(
            storage_path,
            file_bytes,
            {
                "content-type": (
                    file.content_type
                    or "application/octet-stream"
                )
            }
        )

    except Exception as error:
        cursor.close()
        conn.close()

        print(
            f"Could not upload {filename}: {error}"
        )

        raise HTTPException(
            status_code=500,
            detail="Could not upload file"
        )

    # Save file metadata in the database
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


# Get Drop information and its files
@app.get("/drops/{drop_id}")
def get_drop(drop_id: str):

    conn = get_db_connection()
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
        conn.close()

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


# Download a file from Supabase Storage
@app.get("/files/{file_id}/download")
def download_file(file_id: str):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            filename,
            storage_path
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

    media_type, _ = mimetypes.guess_type(
        filename
    )

    return Response(
        content=file_bytes,
        media_type=(
            media_type
            or "application/octet-stream"
        ),
        headers={
            "Content-Disposition": (
                f'attachment; filename="{filename}"'
            )
        }
    )


# Delete a Drop using its private delete token
@app.delete("/drops/{drop_id}")
def delete_drop(
    drop_id: str,
    delete_token: str
):

    conn = get_db_connection()
    cursor = conn.cursor()

    # Get the Drop's delete token
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

    # Only the creator with the correct token can delete the Drop
    if stored_token != delete_token:
        cursor.close()
        conn.close()

        raise HTTPException(
            status_code=403,
            detail="Invalid delete token"
        )

    # Get all files belonging to the Drop
    cursor.execute(
        """
        SELECT storage_path
        FROM files
        WHERE drop_id = %s
        """,
        (drop_id,)
    )

    storage_files = cursor.fetchall()

    # Remove the actual files from Supabase Storage
    for (storage_path,) in storage_files:
        try:
            supabase.storage.from_(
                "uploads"
            ).remove(
                [storage_path]
            )

        except Exception as error:
            cursor.close()
            conn.close()

            print(
                f"Could not delete "
                f"{storage_path}: {error}"
            )

            raise HTTPException(
                status_code=500,
                detail="Could not delete Drop files"
            )

    # Delete the Drop metadata.
    # File metadata is removed automatically through
    # the ON DELETE CASCADE relationship.
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