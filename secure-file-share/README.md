# Vault — secure file sharing

A small, complete file-sharing server: sign in, upload a file, and hand out a
link that expires, caps its own downloads, and can carry a password. Files are
encrypted before they reach the disk, so the storage directory is useless on its
own.

Flask + SQLite + `cryptography`. No build step, no external services.

## Run it

```bash
cd secure-file-share
python -m venv .venv && source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python run.py --init      # writes .env with a fresh SECRET_KEY and MASTER_KEY
python run.py             # http://127.0.0.1:5000
```

Open the site, create an account, upload something, then open the file and press
**Create link**. The link is shown once.

```bash
python -m pytest -q       # 19 tests covering crypto, auth, and sharing
```

## How the encryption works

Envelope encryption, in `app/crypto.py`:

1. Each uploaded file gets its own random 256-bit data key (DEK).
2. The file is encrypted with that DEK in 64 KB chunks of AES-256-GCM, streamed
   straight from the upload socket to disk. Nothing is buffered in memory, so a
   2 GB upload costs 64 KB of RAM.
3. The DEK is then wrapped with the master key (`MASTER_KEY`, held in the
   environment) and stored in the database. The plaintext DEK is never written
   anywhere.

Each chunk's nonce is `base_nonce || counter`, so nonces never repeat under a
given key. The last chunk is tagged as final in its associated data, which means
a truncated file fails authentication instead of silently decrypting short.

**Losing `MASTER_KEY` means losing every stored file.** Back it up. Rotating it
requires re-encrypting existing blobs.

## What else is in place

| Concern | How it's handled |
| --- | --- |
| Passwords | scrypt via Werkzeug, 12-character minimum |
| Share tokens | 256-bit `secrets.token_urlsafe`, stored as SHA-256 — a database dump yields no working links |
| Link lifetime | Expiry timestamp, optional download cap enforced by a conditional `UPDATE` so it holds under concurrent requests, revocation any time |
| Link passwords | Hashed separately from the token; unlock state lives in the visitor's session |
| CSRF | Per-session token required on every POST |
| Brute force | Per-IP rate limits on sign-in and on link-password attempts |
| Enumeration | Sign-in returns one message whether or not the email exists |
| Headers | CSP without `unsafe-inline`, `nosniff`, `frame-ancestors 'none'`, `Referrer-Policy: no-referrer`, HSTS when `COOKIE_SECURE=1` |
| Uploads | Filenames sanitised, size capped, `Content-Disposition: attachment` with `nosniff` so nothing renders inline |
| Audit | Every upload, link, download and failed unlock recorded with IP, visible at `/activity` |

## Layout

```
secure-file-share/
├── run.py                 entry point and --init key generation
├── requirements.txt
├── .env.example
├── app/
│   ├── __init__.py        app factory, security headers, error pages
│   ├── config.py          settings and .env loading
│   ├── crypto.py          chunked AES-256-GCM, key wrapping
│   ├── storage.py         encrypted blob put / get / delete
│   ├── db.py              SQLite schema and connection handling
│   ├── security.py        passwords, CSRF, rate limiting, audit log
│   ├── views/
│   │   ├── auth.py        register, sign in, sign out
│   │   ├── files.py       dashboard, upload, download, links
│   │   └── shares.py      public /d/<token> pages
│   ├── templates/         Jinja templates
│   └── static/            stylesheet and one small script
├── tests/test_vault.py
└── storage/               encrypted blobs + vault.db (gitignored)
```

## Routes

| Method | Path | Who |
| --- | --- | --- |
| GET/POST | `/register`, `/login` | anyone |
| POST | `/logout` | signed in |
| GET | `/files` | owner — dashboard |
| POST | `/files` | owner — upload |
| GET | `/files/<id>` | owner — file and its links |
| GET | `/files/<id>/download` | owner |
| POST | `/files/<id>/delete` | owner |
| POST | `/files/<id>/links` | owner — create a link |
| POST | `/links/<id>/revoke` | owner |
| GET | `/activity` | owner |
| GET | `/d/<token>` | anyone with the link |
| POST | `/d/<token>/unlock` | anyone with the link |
| GET | `/d/<token>/file` | anyone with the link |

## Before putting this on the internet

This is a solid foundation, not a hardened deployment. At minimum:

- Serve over TLS and set `COOKIE_SECURE=1`. Share links leak in transit otherwise.
- Run under gunicorn (`gunicorn -w 4 "run:app"`) behind nginx or Caddy.
- The rate limiter is per-process and in-memory; with multiple workers, move it
  to Redis.
- SQLite is fine for a team. For heavy concurrent writes, move to Postgres —
  the schema in `app/db.py` ports directly.
- Keep `MASTER_KEY` in a secrets manager or KMS rather than a file on the box,
  and consider per-user keys if you want the server to be unable to read files
  even with the master key.
- Add malware scanning on upload if you accept files from outside your org.
- Set up a job to purge blobs for expired shares if you want storage to shrink
  on its own.
