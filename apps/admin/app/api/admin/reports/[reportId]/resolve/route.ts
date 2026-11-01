import { NextRequest, NextResponse } from "next/server";
import { adminApiFetch } from "@/lib/admin-api";

export async function POST(request: NextRequest, context: { params: Promise<{ reportId: string }> }) {
  const { reportId } = await context.params;
  const body = await request.json().catch(() => ({}));
  if (!["resolved", "dismissed"].includes(body.status)) return NextResponse.json({ error: "Invalid report decision" }, { status: 400 });
  try {
    const { response: upstream, rotated } = await adminApiFetch(
      "/api/v1/admin/reports/" + encodeURIComponent(reportId) + "/resolve",
      { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) },
    );
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
