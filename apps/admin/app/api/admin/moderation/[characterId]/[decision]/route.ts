import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest, context: { params: Promise<{ characterId: string; decision: string }> }) {
  const api = process.env.ALAP_API_URL;
  const access = (await cookies()).get("alap_admin_access")?.value;
  if (!api) return NextResponse.json({ error: "ALAP_API_URL is not configured" }, { status: 503 });
  if (!access) return NextResponse.json({ error: "Authentication required" }, { status: 401 });
  const { characterId, decision } = await context.params;
  if (!["approve", "reject"].includes(decision)) return NextResponse.json({ error: "Invalid moderation decision" }, { status: 400 });
  const upstream = await fetch(api.replace(/\/$/, "") + "/api/v1/admin/characters/" + encodeURIComponent(characterId) + "/" + decision, {
    method: "POST",
    headers: { Authorization: "Bearer " + access, "Content-Type": "application/json" },
    body: JSON.stringify(decision === "reject" ? await request.json().catch(() => ({ reason: "Rejected by moderator" })) : {}),
    cache: "no-store",
  });
  const data = await upstream.json().catch(() => ({}));
  return NextResponse.json(data, { status: upstream.status });
}
