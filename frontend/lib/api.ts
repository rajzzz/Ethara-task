const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

export async function apiRequest<T>(
  path: string,
  init?: RequestInit,
  options?: { skipJson?: boolean; skipAuthRefresh?: boolean }
): Promise<T> {
  const requestInit: RequestInit = {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {})
    },
    credentials: "include",
    cache: "no-store"
  };
  let response = await fetch(`${API_URL}${path}`, requestInit);

  const canRefresh =
    response.status === 401 &&
    !options?.skipAuthRefresh &&
    path !== "/auth/refresh" &&
    path !== "/auth/login" &&
    path !== "/auth/signup";

  if (canRefresh) {
    const refreshResponse = await fetch(`${API_URL}/auth/refresh`, {
      method: "POST",
      credentials: "include",
      cache: "no-store"
    });
    if (refreshResponse.ok) {
      response = await fetch(`${API_URL}${path}`, requestInit);
    }
  }

  if (!response.ok) {
    let detail = `Request failed (${response.status})`;
    try {
      const data = await response.json();
      detail = data.detail ?? detail;
    } catch {
      // ignore
    }
    throw new ApiError(detail, response.status);
  }

  if (options?.skipJson || response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}
