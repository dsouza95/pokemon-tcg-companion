import { auth } from "@clerk/nextjs/server";
import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL;

async function handler(req: NextRequest) {
  const { getToken } = await auth();
  const token = await getToken();

  const path =
    req.nextUrl.pathname.replace(/^\/api/, "").replace(/\/$/, "") || "/";
  const url = `${BACKEND_URL}${path}${req.nextUrl.search}`;

  const headers = new Headers(req.headers);
  headers.delete("host");
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const res = await fetch(url, {
    method: req.method,
    headers,
    body: req.method !== "GET" && req.method !== "HEAD" ? req.body : undefined,
    // @ts-expect-error duplex required for streaming request body
    duplex: "half",
  });

  return new NextResponse(res.body, {
    status: res.status,
    statusText: res.statusText,
    headers: res.headers,
  });
}

export const GET = handler;
export const POST = handler;
export const PUT = handler;
export const DELETE = handler;
export const PATCH = handler;
