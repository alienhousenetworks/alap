import { NextResponse } from "next/server";
import { adminApiFetch } from "@/lib/admin-api";

export async function GET() {
  try {
    const { response: upstream, rotated } = await adminApiFetch("/api/v1/admin/reports?status=open&limit=100");
    const data = await upstream.json().catch(() => ({}));
    const response = NextResponse.json(data, { status: upstream.status });
    if (rotated) {
      const secure = process.env.NODE_ENV === "production";
      response.cookies.set("alap_admin_access", rotated.access_token, { httpOnly: true, secure, sameSite: "strict", path: "/", maxAge: rotated.expires_in });
      response.cookies.set("alap_admin_refresh", rotated.refresh_token, { httpOnly: true, secure, sameSite: "strict", path: "/", maxAge: 60 * 60 * 24 * 30 });
    }
    return response;
  } catch {
    return NextResponse.json({ error: "Admin API is unavailable" }, { status: 503 });
  }
}
