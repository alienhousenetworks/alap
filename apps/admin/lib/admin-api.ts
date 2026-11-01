import { cookies } from "next/headers";

export type RotatedTokens = { access_token: string; refresh_token: string; expires_in: number };
export async function adminApiFetch(path: string, init: RequestInit = {}) {
  const api = process.env.ALAP_API_URL;
  const store = await cookies();
  let access = store.get("alap_admin_access")?.value;
  const refresh = store.get("alap_admin_refresh")?.value;
  if (!api) throw new Error("ALAP_API_URL is not configured");
  const url = api.replace(/\/$/, "") + path;
  const send = (token: string) => fetch(url, {
    ...init,
    headers: { ...(init.headers || {}), Authorization: "Bearer " + token },
    cache: "no-store",
  });
  let response = access ? await send(access) : new Response(null, { status: 401 });
  let rotated: RotatedTokens | undefined;
  if (response.status === 401 && refresh) {
    const refreshed = await fetch(api.replace(/\/$/, "") + "/api/v1/auth/refresh", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refresh }),
      cache: "no-store",
    });
    if (refreshed.ok) {
      rotated = await refreshed.json();
      access = rotated!.access_token;
      response = await send(access);
    }
  }
  return { response, rotated };
}
