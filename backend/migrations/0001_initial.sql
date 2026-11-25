CREATE TABLE profiles (
  user_id TEXT PRIMARY KEY,
  display_name TEXT NOT NULL DEFAULT '',
  allergens_json TEXT NOT NULL DEFAULT '[]',
  updated_at TEXT NOT NULL
);
CREATE TABLE scans (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  product_name TEXT NOT NULL,
  label_text TEXT NOT NULL,
  analysis_json TEXT NOT NULL,
  favorite INTEGER NOT NULL DEFAULT 0 CHECK (favorite IN (0,1)),
  created_at TEXT NOT NULL
);
CREATE INDEX scans_user_created ON scans(user_id, created_at DESC, id DESC);
