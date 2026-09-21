# Promptwright

Turn a rough idea into a ready-to-use AI prompt, at the length and theme you choose. A single static page with eight views:
Home, Guide, Templates, Prompt Lab, Glossary, Library, Help and About.

The full version, with prompt writing powered by Claude, runs on claude.ai:
https://claude.ai/artifact/YRcxvGSSV7sBpRehnH8gyx

## What is in this repo

| File | Purpose |
|------|---------|
| `index.html` | The whole site, with a strict Content-Security-Policy meta tag |
| `_headers` | Security headers for Netlify and Cloudflare Pages |
| `vercel.json` | The same headers for Vercel |
| `scripts/preflight.py` | Production checks: secrets, debug code, CSP hashes |
| `.github/workflows/pages.yml` | Runs preflight, then deploys to GitHub Pages |
| `.github/workflows/secret-scan.yml` | Scans every push for leaked secrets |
| `SECURITY.md` | The 20-point security checklist, item by item |
| `.env.example` | Documents that no environment variables are needed |

## Run it locally

```bash
python3 -m http.server 8000
# open http://localhost:8000
```

Prompt writing needs Claude, so locally it shows a notice. Every other page works.

## Before you publish

```bash
python3 scripts/preflight.py          # checks for secrets, debug code and stale CSP hashes
python3 scripts/preflight.py --fix    # after editing index.html, refreshes the CSP hashes
```

Editing either inline script changes its hash. Run `--fix` afterwards or the browser will block the script.

## Publish to GitHub

```bash
git init -b main
git add .
git status                            # confirm no .env or key files are listed
git commit -m "Initial commit: Promptwright"
gh repo create promptwright --public --source=. --push
```

Without the GitHub CLI, create an empty repository on github.com, then:

```bash
git remote add origin https://github.com/<your-username>/promptwright.git
git push -u origin main
```

Then on GitHub: **Settings, Pages, Source: GitHub Actions**, and tick **Enforce HTTPS**.
The push deploys the site, and the secret scan runs on every push.

## Security

See [SECURITY.md](SECURITY.md). In short: no server, no keys, no cookies, all user text rendered as plain text,
and a strict CSP. Sign up and log in are a local convenience, not real authentication.
