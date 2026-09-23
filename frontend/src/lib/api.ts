const API_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export async function createDrop(lifetime: string) {
  const response = await fetch(
    `${API_URL}/drops?lifetime=${encodeURIComponent(lifetime)}`,
    {
      method: "POST"
    }
  );

  if (!response.ok) {
    throw new Error("Failed to create drop");
  }

  return await response.json();
}

export async function uploadFile(dropId: string, file: File) {
  const formData = new FormData();

  formData.append("file", file);

  const response = await fetch(
    `${API_URL}/drops/${dropId}/files`,
    {
      method: "POST",
      body: formData
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to upload ${file.name}`);
  }

  return await response.json();
}

export async function getDrop(dropId: string) {
  const response = await fetch(
    `${API_URL}/drops/${dropId}`
  );

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error("Drop not found");
    }

    throw new Error("Failed to load drop");
  }

  return await response.json();
}

export async function deleteDrop(
  dropId: string,
  deleteToken: string
) {
  const response = await fetch(
    `${API_URL}/drops/${dropId}?delete_token=${encodeURIComponent(deleteToken)}`,
    {
      method: "DELETE"
    }
  );

  if (!response.ok) {
    if (response.status === 403) {
      throw new Error("Invalid delete token.");
    }

    if (response.status === 404) {
      throw new Error("Drop not found.");
    }

    throw new Error("Failed to delete drop.");
  }

  return await response.json();
}