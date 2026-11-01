import { cookies } from "next/headers";
import { NextResponse } from "next/server";
export async function POST() {
  const store = await cookies();
  const refresh = store.get("alap_admin_refresh")?.value;
  const api = process.env.ALAP_API_URL;
  if (refresh && api) {
    try {
      await fetch(api.replace(/\/$/, "") + "/api/v1/auth/logout", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refresh }), cache: "no-store",
      });
    } catch { /* Local cookie cleanup must still proceed. */ }
  }
  const response = NextResponse.json({ ok: true });
  response.cookies.set("alap_admin_access", "", { httpOnly: true, path: "/", maxAge: 0 });
  response.cookies.set("alap_admin_refresh", "", { httpOnly: true, path: "/", maxAge: 0 });
  return response;
}
