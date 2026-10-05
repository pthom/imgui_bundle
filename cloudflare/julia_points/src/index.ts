// The API of the points that users share in the Julia map demo (the playground's explorables/julia_map).
//   GET  /julia_points?voter=<id>  -> the shown points, newest first, with their votes and whether this voter voted
//   POST /julia_points             {name, c_re, c_im, view_width, max_iter, story, author} -> {id}
//   POST /julia_points/<id>/vote   {voter, vote: true | false} -> {votes}
// The admin (header "Authorization: Bearer <ADMIN_TOKEN>") also gets the hidden points, may hide or show one, and
// may delete a hidden one (with its votes):
//   POST   /julia_points/<id>/status {status: "shown" | "hidden"} -> {status}
//   DELETE /julia_points/<id> -> {deleted: <id>}
// Errors answer {error: "..."}, with a status of 400, 403, 404 or 429. The tables are in schema.sql.

// ADMIN_TOKEN: a secret (wrangler secret put ADMIN_TOKEN; locally, in .dev.vars). Without it, nobody is admin
type AdminEnv = Env & { ADMIN_TOKEN?: string };

const MAX_NAME = 40;
const MAX_STORY = 300;
const MAX_AUTHOR = 40;
const MAX_BODY = 4096; // in characters: the largest valid point is far smaller
const SUBMISSIONS_PER_HOUR = 5; // per IP
const VOTER_ID = /^[A-Za-z0-9-]{8,64}$/;

const CORS = {
  "Access-Control-Allow-Origin": "*", // the demo runs on the desktop and in the playground; no cookies to protect
  "Access-Control-Allow-Methods": "GET, POST, DELETE, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization",
};

class BadRequest extends Error {}

function json(body: unknown, status = 200): Response {
  return Response.json(body, { status, headers: CORS });
}

async function readBody(request: Request): Promise<Record<string, unknown>> {
  const raw = await request.text();
  if (raw.length > MAX_BODY) throw new BadRequest("the request is too large");
  let body: unknown = null;
  try {
    body = JSON.parse(raw);
  } catch {
    // reported below
  }
  if (typeof body !== "object" || body === null || Array.isArray(body)) {
    throw new BadRequest("a JSON object is expected");
  }
  return body as Record<string, unknown>;
}

function text(body: Record<string, unknown>, field: string, maxLength: number, required: boolean): string {
  const value = body[field] ?? "";
  if (typeof value !== "string") throw new BadRequest(`${field}: a string is expected`);
  const s = value.trim();
  if (required && s.length === 0) throw new BadRequest(`${field} is required`);
  if ([...s].length > maxLength) throw new BadRequest(`${field}: at most ${maxLength} characters`);
  if (/[\u0000-\u001f\u007f]/.test(s)) throw new BadRequest(`${field}: no control characters`); // one line of text
  return s;
}

function number(body: Record<string, unknown>, field: string, isValid: (x: number) => boolean): number {
  const value = body[field];
  if (typeof value !== "number" || !Number.isFinite(value) || !isValid(value)) {
    throw new BadRequest(`${field}: a number in range is expected`);
  }
  return value;
}

async function sha256(s: string): Promise<string> {
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(s));
  return [...new Uint8Array(digest)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

async function isAdmin(request: Request, env: AdminEnv): Promise<boolean> {
  if (!env.ADMIN_TOKEN) return false;
  const sent = new TextEncoder().encode(request.headers.get("Authorization") ?? "");
  const expected = new TextEncoder().encode(`Bearer ${env.ADMIN_TOKEN}`);
  return sent.byteLength === expected.byteLength && crypto.subtle.timingSafeEqual(sent, expected);
}

async function listPoints(env: Env, voter: string, admin: boolean): Promise<Response> {
  const { results } = await env.DB.prepare(
    `SELECT id, name, c_re, c_im, view_width, max_iter, story, author, created, status,
            (SELECT COUNT(*) FROM votes WHERE point_id = points.id) AS votes,
            EXISTS (SELECT 1 FROM votes WHERE point_id = points.id AND voter = ?1) AS voted_by_me
     FROM points WHERE status = 'shown' OR ?2 ORDER BY created DESC LIMIT 1000`,
  ).bind(voter, admin ? 1 : 0).all<{ voted_by_me: number }>();
  return json(results.map((point) => ({ ...point, voted_by_me: point.voted_by_me === 1 })));
}

async function setStatus(request: Request, env: Env, pointId: number): Promise<Response> {
  const status = (await readBody(request)).status;
  if (status !== "shown" && status !== "hidden") throw new BadRequest('status: "shown" or "hidden" is expected');
  const changed = await env.DB.prepare("UPDATE points SET status = ?1 WHERE id = ?2").bind(status, pointId).run();
  if (changed.meta.changes === 0) return json({ error: "no such point" }, 404);
  return json({ status });
}

async function deletePoint(env: Env, pointId: number): Promise<Response> {
  // Only a hidden point: a deletion takes two steps. Its votes go first (they refer to it), in the same transaction
  const [, deleted] = await env.DB.batch([
    env.DB.prepare(`DELETE FROM votes WHERE point_id = ?1
                    AND EXISTS (SELECT 1 FROM points WHERE id = ?1 AND status = 'hidden')`).bind(pointId),
    env.DB.prepare("DELETE FROM points WHERE id = ?1 AND status = 'hidden'").bind(pointId),
  ]);
  if (deleted.meta.changes === 0) return json({ error: "no such hidden point (hide it first)" }, 404);
  return json({ deleted: pointId });
}

async function addPoint(request: Request, env: Env): Promise<Response> {
  const body = await readBody(request);
  const name = text(body, "name", MAX_NAME, true);
  const story = text(body, "story", MAX_STORY, false);
  const author = text(body, "author", MAX_AUTHOR, false);
  const c_re = number(body, "c_re", (x) => Math.abs(x) <= 2.5);
  const c_im = number(body, "c_im", (x) => Math.abs(x) <= 2.5);
  if (Math.hypot(c_re, c_im) > 2.5) throw new BadRequest("c: |c| <= 2.5 is expected");
  const view_width = number(body, "view_width", (x) => x > 0 && x <= 10);
  const max_iter = number(body, "max_iter", (x) => Number.isInteger(x) && x >= 10 && x <= 250);

  // The rate limit counts the submissions of the last hour, per IP
  const ipHash = await sha256(request.headers.get("CF-Connecting-IP") ?? "");
  const now = new Date();
  const hourAgo = new Date(now.getTime() - 3600_000).toISOString();
  await env.DB.prepare("DELETE FROM submissions WHERE created < ?1").bind(hourAgo).run();
  const recent = await env.DB.prepare("SELECT COUNT(*) AS n FROM submissions WHERE ip_hash = ?1")
    .bind(ipHash).first<number>("n");
  if ((recent ?? 0) >= SUBMISSIONS_PER_HOUR) {
    return json({ error: `at most ${SUBMISSIONS_PER_HOUR} points per hour: try again later` }, 429);
  }
  await env.DB.prepare("INSERT INTO submissions (ip_hash, created) VALUES (?1, ?2)")
    .bind(ipHash, now.toISOString()).run();
  const id = await env.DB.prepare(
    `INSERT INTO points (name, c_re, c_im, view_width, max_iter, story, author, created)
     VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8) RETURNING id`,
  ).bind(name, c_re, c_im, view_width, max_iter, story, author, now.toISOString()).first<number>("id");
  return json({ id }, 201);
}

async function vote(request: Request, env: Env, pointId: number): Promise<Response> {
  const body = await readBody(request);
  const voter = body.voter;
  if (typeof voter !== "string" || !VOTER_ID.test(voter)) {
    throw new BadRequest("voter: 8 to 64 letters, digits or dashes are expected");
  }
  if (typeof body.vote !== "boolean") throw new BadRequest("vote: true or false is expected");
  const shown = await env.DB.prepare("SELECT 1 AS shown FROM points WHERE id = ?1 AND status = 'shown'")
    .bind(pointId).first();
  if (shown === null) return json({ error: "no such point" }, 404);
  const statement = body.vote
    ? "INSERT OR IGNORE INTO votes (point_id, voter) VALUES (?1, ?2)"
    : "DELETE FROM votes WHERE point_id = ?1 AND voter = ?2";
  await env.DB.prepare(statement).bind(pointId, voter).run();
  const votes = await env.DB.prepare("SELECT COUNT(*) AS n FROM votes WHERE point_id = ?1")
    .bind(pointId).first<number>("n");
  return json({ votes });
}

export default {
  async fetch(request, env): Promise<Response> {
    if (request.method === "OPTIONS") return new Response(null, { headers: CORS });
    const url = new URL(request.url);
    const path = url.pathname.split("/").filter(Boolean);
    try {
      if (path.length === 1 && path[0] === "julia_points") {
        const admin = await isAdmin(request, env);
        if (request.method === "GET") return await listPoints(env, url.searchParams.get("voter") ?? "", admin);
        if (request.method === "POST") return await addPoint(request, env);
      }
      if (path.length === 2 && path[0] === "julia_points" && request.method === "DELETE") {
        if (!(await isAdmin(request, env))) return json({ error: "for the admin only" }, 403);
        return await deletePoint(env, Number.parseInt(path[1], 10));
      }
      if (path.length === 3 && path[0] === "julia_points" && request.method === "POST") {
        const pointId = Number.parseInt(path[1], 10);
        if (path[2] === "vote") return await vote(request, env, pointId);
        if (path[2] === "status") {
          if (!(await isAdmin(request, env))) return json({ error: "for the admin only" }, 403);
          return await setStatus(request, env, pointId);
        }
      }
      return json({ error: "not found" }, 404);
    } catch (e) {
      if (e instanceof BadRequest) return json({ error: e.message }, 400);
      throw e;
    }
  },
} satisfies ExportedHandler<AdminEnv>;
