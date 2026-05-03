import { NextRequest, NextResponse } from "next/server";

const publicRoutes = ["/login", "/signup"];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  if (pathname.startsWith("/_next") || pathname.startsWith("/favicon")) {
    return NextResponse.next();
  }

  const hasToken = Boolean(request.cookies.get("access_token")?.value);
  const isPublic = publicRoutes.some((route) => pathname.startsWith(route));

  if (!hasToken && !isPublic) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  if (hasToken && isPublic) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!api).*)"]
};
