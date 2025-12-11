import NextAuth, { type DefaultSession } from "next-auth";

declare module "next-auth" {
  interface Session {
    accessToken?: string;
    refreshToken?: string;
    tier?: string;
    user: {
      id?: string;
      email?: string | null;
      name?: string | null;
    } & DefaultSession["user"];
  }

  interface User {
    accessToken?: string;
    refreshToken?: string;
    subscription_tier?: string;
  }
}

declare module "next-auth/jwt" {
  interface JWT {
    accessToken?: string;
    refreshToken?: string;
    tier?: string;
    user?: {
      id?: string;
      email?: string | null;
      name?: string | null;
    };
  }
}

