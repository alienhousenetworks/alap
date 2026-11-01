import { cookies } from "next/headers";
import { NextResponse } from "next/server";

export async function GET() {
  const api = process.env.ALAP_API_URL;
  const access = (await cookies()).get("alap_admin_access")?.value;
  if (!api) return NextResponse.json({ error: "ALAP_API_URL is not configured" }, { status: 503 });
  if (!access) return NextResponse.json({ error: "Authentication required" }, { status: 401 });
  const upstream = await fetch(api.replace(/\/$/, "") + "/api/v1/admin/moderation/characters?status=pending", {
    headers: { Authorization: "Bearer " + access }, cache: "no-store",
  });
  const data = await upstream.json().catch(() => ({}));
  return NextResponse.json(data, { status: upstream.status });
}
