import { NextApiRequest, NextApiResponse } from "next";

// Minimal stub for NextAuth endpoints so client won't fail when NextAuth isn't set up.
// This returns a safe empty session for GET /api/auth/session and 200 for GET /api/auth/_log.
export default function handler(req: NextApiRequest, res: NextApiResponse) {
  const parts = Array.isArray(req.query.nextauth) ? req.query.nextauth : [];
  const subpath = parts.join("/");

  if (
    req.method === "GET" &&
    (subpath === "session" || subpath === "session/")
  ) {
    return res.status(200).json({ user: null });
  }

  if (req.method === "GET" && (subpath === "_log" || subpath === "_log/")) {
    return res.status(200).json({ ok: true });
  }

  // For other NextAuth endpoints, return 204 No Content as a harmless default.
  return res.status(204).end();
}
