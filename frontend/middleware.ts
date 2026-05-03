import { NextRequest, NextResponse } from "next/server";

export function middleware(request: NextRequest) {
  // In production this frontend is on a different domain than the API.
  // API auth cookies are scoped to the API domain, so they aren't readable
  // by frontend middleware cookies(). Enforce auth on backend endpoints.
  void request;
  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!api).*)"]
};
