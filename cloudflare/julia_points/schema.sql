-- The points that users share in the Julia map demo (the API: src/index.ts)
CREATE TABLE IF NOT EXISTS points (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  c_re REAL NOT NULL,
  c_im REAL NOT NULL,
  view_width REAL NOT NULL,              -- the width of the map's view when shared
  max_iter INTEGER NOT NULL,             -- the iterations when shared
  story TEXT NOT NULL DEFAULT '',
  author TEXT NOT NULL DEFAULT '',
  status TEXT NOT NULL DEFAULT 'shown',  -- shown | hidden (the curation)
  created TEXT NOT NULL                  -- ISO 8601, UTC
);

CREATE TABLE IF NOT EXISTS votes (
  point_id INTEGER NOT NULL REFERENCES points(id),
  voter TEXT NOT NULL,                   -- a random id, kept by the client
  PRIMARY KEY (point_id, voter)
);

-- The rate limits (src/index.ts, rateLimited): one row per event, by kind ("submit", "vote", "list"...), with the
-- sender's IP hashed, deleted after an hour. Replaces the former `submissions` table (drop it after the deploy).
CREATE TABLE IF NOT EXISTS rate_limits (
  kind TEXT NOT NULL,
  sender TEXT NOT NULL,
  created TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS rate_limits_by_sender ON rate_limits (kind, sender);

-- The guestbook of the Minard animation (the API: src/index.ts, /minard_guestbook). An entry waits for the admin's
-- reading (pending) before it is shown; hidden: read and refused.
CREATE TABLE IF NOT EXISTS guestbook (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  place TEXT NOT NULL DEFAULT '',          -- where the reader writes from
  message TEXT NOT NULL,                   -- several lines
  lang TEXT NOT NULL DEFAULT '',           -- the app's language when written: fr, en, ru
  status TEXT NOT NULL DEFAULT 'pending',  -- pending | shown | hidden (the moderation)
  created TEXT NOT NULL                    -- ISO 8601, UTC
);
