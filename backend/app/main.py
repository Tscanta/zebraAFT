from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from supabase import create_client
from dotenv import load_dotenv

from datetime import datetime, timedelta, timezone

import asyncio
import mimetypes
import os
import secrets
import string
import re
import psycopg2


MAX_FILE_SIZE = 100 * 1024 * 1024


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


# Start the expiration cleanup worker
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(
        cleanup_expired_drops()
    )


# Generate a short Drop code
def generate_drop_id(length: int = 8) -> str:
    characters = string.ascii_uppercase + string.digits

    return "".join(
        secrets.choice(characters)
        for _ in range(length)
    )


# Generate a unique file ID
def generate_file_id() -> str:
    return secrets.token_urlsafe(16)

# Validate a Drop code before processing the request
def validate_drop_id(drop_id: str):
    if not re.fullmatch(r"[A-Z0-9]{8}", drop_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid Drop code"
        )

# Validate a file ID before querying the database
def validate_file_id(file_id: str):
    if not re.fullmatch(r"[A-Za-z0-9_-]{20,30}", file_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid file ID"
        )

# Clean and validate an uploaded filename
def sanitize_filename(filename: str) -> str:
    filename = os.path.basename(filename).strip()

    if not filename:
        raise HTTPException(
            status_code=400,
            detail="Invalid filename"
        )

    if len(filename) > 255:
        raise HTTPException(
            status_code=400,
            detail="Filename is too long"
        )

    # Prevent control characters from being stored
    if any(ord(char) < 32 for char in filename):
        raise HTTPException(
            status_code=400,
            detail="Filename contains invalid characters"
        )

    return filename


# Delete expired Drops and their files
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

                # Keep the Drop if Storage cleanup failed.
                # The next cycle will try again.
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

        # Run cleanup every 60 seconds
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

    created_at = datetime.now(timezone.utc)

    if lifetime == "24h":
        expires_at = (
            created_at +
            timedelta(hours=24)
        )
    else:
        expires_at = None

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
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

    except Exception:
        conn.rollback()
        cursor.close()
        conn.close()

        raise HTTPException(
            status_code=500,
            detail="Could not create Drop"
        )

    cursor.close()
    conn.close()

    return {
        "drop_id": drop_id,
        "delete_token": delete_token,
        "expires_at": expires_at
    }


# Upload a file to a Drop
@app.post("/drops/{drop_id}/files")
async def upload_file(
    drop_id: str,
    file: UploadFile = File(...)
):
    validate_drop_id(drop_id)
    conn = get_db_connection()

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check that the Drop exists and has not expired
    cursor.execute(
        """
        SELECT
            drop_id,
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

    if (
        drop[1] is not None
        and drop[1] <= datetime.now(timezone.utc)
    ):
        cursor.close()
        conn.close()

        raise HTTPException(
            status_code=404,
            detail="Drop has expired"
        )

    # Keep the original filename for the user.
    # Use a generated filename in Storage.
    file_id = generate_file_id()

    filename = sanitize_filename(
        file.filename
    )

    _, extension = os.path.splitext(filename)

    storage_path = (
        f"{drop_id}/{file_id}{extension}"
    )

    # Read the file into memory
    file_bytes = await file.read()

    # Prevent very large uploads
    if len(file_bytes) > MAX_FILE_SIZE:
        cursor.close()
        conn.close()

        raise HTTPException(
            status_code=413,
            detail="File is too large. Maximum size is 100 MB."
        )

    # Upload the actual file to Supabase Storage
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

    # Save file information in PostgreSQL
    try:
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

    except Exception as error:
        conn.rollback()

        # The Storage upload succeeded,
        # so remove it if the database insert fails.
        try:
            supabase.storage.from_(
                "uploads"
            ).remove(
                [storage_path]
            )

            print(
                f"Removed orphaned storage file: "
                f"{storage_path}"
            )

        except Exception as storage_error:
            print(
                f"Could not remove orphaned storage file "
                f"{storage_path}: {storage_error}"
            )

        cursor.close()
        conn.close()

        print(
            f"Could not save file metadata: {error}"
        )

        raise HTTPException(
            status_code=500,
            detail="Could not save file information"
        )

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

    validate_drop_id(drop_id)

    conn = get_db_connection()

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

    # Prevent access to expired Drops
    if (
        drop[2] is not None
        and drop[2] <= datetime.now(timezone.utc)
    ):
        cursor.close()
        conn.close()

        raise HTTPException(
            status_code=404,
            detail="Drop has expired"
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

    validate_file_id(file_id)

    conn = get_db_connection()
    cursor = conn.cursor()

    # Get the file and the expiration time of its Drop
    cursor.execute(
        """
        SELECT
            files.filename,
            files.storage_path,
            drops.expires_at
        FROM files
        JOIN drops
            ON files.drop_id = drops.drop_id
        WHERE files.file_id = %s
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

    filename, storage_path, expires_at = result

    # Prevent downloading files from expired Drops
    if (
        expires_at is not None
        and expires_at <= datetime.now(timezone.utc)
    ):
        raise HTTPException(
            status_code=404,
            detail="Drop has expired"
        )

    # Download the actual file from Supabase Storage
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
# Delete a Drop using its private delete token
@app.delete("/drops/{drop_id}")
def delete_drop(
    drop_id: str,
    delete_token: str
):

    validate_drop_id(drop_id)

    conn = get_db_connection()
    cursor = conn.cursor()

    # Get the stored delete token
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

    # Only the creator can delete the Drop
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

    # Delete every file from Supabase Storage
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
                f"Could not delete storage file "
                f"{storage_path}: {error}"
            )

            raise HTTPException(
                status_code=500,
                detail="Could not delete Drop files"
            )

    # Only delete the database record after
    # every Storage file has been removed.
    try:
        cursor.execute(
            """
            DELETE FROM drops
            WHERE drop_id = %s
            """,
            (drop_id,)
        )

        conn.commit()

    except Exception as error:
        conn.rollback()

        cursor.close()
        conn.close()

        print(
            f"Could not delete Drop {drop_id}: {error}"
        )

        raise HTTPException(
            status_code=500,
            detail="Could not delete Drop"
        )

    cursor.close()
    conn.close()

    return {
        "message": "Drop deleted successfully",
        "drop_id": drop_id
    }