// src/api.ts

const API_BASE_URL = 'http://127.0.0.1:8000/api/v1'; // Change this if your FastAPI runs on a different port

export const enrollUser = async (formData: FormData) => {
  const response = await fetch(`${API_BASE_URL}/enroll`, {
    method: 'POST',
    body: formData, // FormData automatically sets the correct multipart/form-data headers
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || response.statusText || 'Enrollment failed');
  }

  return response.json();
};

export const loginUser = async (formData: FormData) => {
  const response = await fetch(`${API_BASE_URL}/login`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || response.statusText || 'Login failed');
  }

  return response.json();
};