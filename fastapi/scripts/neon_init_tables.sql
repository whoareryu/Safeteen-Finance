-- Neon SQL Editor — 통합 users 테이블 (auth + secom)

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(64) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    nickname VARCHAR(64) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(16) NOT NULL DEFAULT 'user' CHECK (role IN ('admin', 'user', 'partner')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_login_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS ix_users_username ON users (username);
CREATE INDEX IF NOT EXISTS ix_users_email ON users (email);
CREATE INDEX IF NOT EXISTS ix_users_nickname ON users (nickname);
CREATE INDEX IF NOT EXISTS ix_users_role ON users (role);

-- 이전 secom_users 가 있으면 수동 삭제 (데이터 이전 후):
-- DROP TABLE IF EXISTS secom_users;
