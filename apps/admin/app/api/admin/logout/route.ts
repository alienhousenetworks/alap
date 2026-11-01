import { NextResponse } from "next/server";
export async function POST() {
  const response = NextResponse.json({ ok: true });
  response.cookies.set("alap_admin_access", "", { httpOnly: true, path: "/", maxAge: 0 });
  response.cookies.set("alap_admin_refresh", "", { httpOnly: true, path: "/", maxAge: 0 });
  return response;
}
