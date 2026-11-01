import { NextRequest, NextResponse } from "next/server";
import { adminApiFetch } from "@/lib/admin-api";

export async function POST(request: NextRequest, context: { params: Promise<{ characterId: string; decision: string }> }) {
  const { characterId, decision } = await context.params;
  if (!["approve", "reject"].includes(decision)) return NextResponse.json({ error: "Invalid moderation decision" }, { status: 400 });
  let body = {};
  if (decision === "reject") body = await request.json().catch(() => ({ reason: "Rejected by moderator" }));
  try {
    const { response: upstream, rotated } = await adminApiFetch(
      "/api/v1/admin/characters/" + encodeURIComponent(characterId) + "/" + decision,
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
