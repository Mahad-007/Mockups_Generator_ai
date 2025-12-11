export { default } from "next-auth/middleware";

export const config = {
  matcher: ["/generate/:path*", "/dashboard/:path*", "/brands/:path*", "/editor/:path*", "/teams/:path*"],
};

