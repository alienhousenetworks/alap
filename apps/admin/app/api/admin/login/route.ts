import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  const api = process.env.ALAP_API_URL;
  if (!api) return NextResponse.json({ error: "ALAP_API_URL is not configured" }, { status: 503 });
  const body = await request.json();
  const upstream = await fetch(api.replace(/\/$/, "") + "/api/v1/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email: body.email, password: body.password }),
    cache: "no-store",
  });
  if (!upstream.ok) return NextResponse.json({ error: "Sign-in failed" }, { status: upstream.status });
  const tokens = await upstream.json();
  const response = NextResponse.json({ ok: true });
  const secure = process.env.NODE_ENV === "production";
  response.cookies.set("alap_admin_access", tokens.access_token, { httpOnly: true, secure, sameSite: "strict", path: "/", maxAge: tokens.expires_in });
  response.cookies.set("alap_admin_refresh", tokens.refresh_token, { httpOnly: true, secure, sameSite: "strict", path: "/", maxAge: 60 * 60 * 24 * 30 });
  return response;
}
