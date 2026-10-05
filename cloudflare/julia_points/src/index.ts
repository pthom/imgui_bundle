// The API of the points that users share in the Julia map demo (the playground's explorables/julia_map).
//   GET  /julia_points?voter=<id>  -> the shown points, newest first, with their votes and whether this voter voted
//   POST /julia_points             {name, c_re, c_im, view_width, max_iter, story, author} -> {id}
//   POST /julia_points/<id>/vote   {voter, vote: true | false} -> {votes}
// Errors answer {error: "..."}, with a status of 400, 404 or 429. The tables are in schema.sql.

const MAX_NAME = 40;
const MAX_STORY = 300;
const MAX_AUTHOR = 40;
const MAX_BODY = 4096; // in characters: the largest valid point is far smaller
const SUBMISSIONS_PER_HOUR = 5; // per IP
const VOTER_ID = /^[A-Za-z0-9-]{8,64}$/;

const CORS = {
  "Access-Control-Allow-Origin": "*", // the demo runs on the desktop and in the playground; no cookies to protect
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type",
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
  if (typeof body !== "object" || body === null || Array.isArray(body)) throw new BadRequest("a JSON object is expected");
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

async function listPoints(env: Env, voter: string): Promise<Response> {
  const { results } = await env.DB.prepare(
    `SELECT id, name, c_re, c_im, view_width, max_iter, story, author, created,
            (SELECT COUNT(*) FROM votes WHERE point_id = points.id) AS votes,
            EXISTS (SELECT 1 FROM votes WHERE point_id = points.id AND voter = ?1) AS voted_by_me
     FROM points WHERE status = 'shown' ORDER BY created DESC LIMIT 1000`,
  ).bind(voter).all<{ voted_by_me: number }>();
  return json(results.map((point) => ({ ...point, voted_by_me: point.voted_by_me === 1 })));
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
        if (request.method === "GET") return await listPoints(env, url.searchParams.get("voter") ?? "");
        if (request.method === "POST") return await addPoint(request, env);
      }
      if (path.length === 3 && path[0] === "julia_points" && path[2] === "vote" && request.method === "POST") {
        return await vote(request, env, Number.parseInt(path[1], 10));
      }
      return json({ error: "not found" }, 404);
    } catch (e) {
      if (e instanceof BadRequest) return json({ error: e.message }, 400);
      throw e;
    }
  },
} satisfies ExportedHandler<Env>;
