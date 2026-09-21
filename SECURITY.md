# Security

Promptwright is a static, single-file web page. It has no server, no database, no cookies and no API keys.
That removes most of the classic web risks, so this file is honest about which checks apply, which are done,
and which would only matter if you add a backend later.

**Status key:** Done, Partial (helps, but is not a server-side guarantee), N/A (the thing does not exist in this project).

| # | Check | Status | What was done or why it does not apply |
|---|-------|--------|-----------------------------------------|
| 1 | Hide API keys | Done | There are no keys in the code. Claude access is granted by the host page on the visitor's own account. `scripts/preflight.py` scans for key patterns. |
| 2 | Check env variables | Done | None are needed. `.env.example` documents this, and `.env` files are git-ignored. |
| 3 | Check keys in git | Done | `.gitignore` blocks secrets, the `secret-scan` workflow runs gitleaks on every push, and preflight scans all files. |
| 4 | Protect admin routes | N/A | There is no admin area or server. The "pages" are client-side views with no privileged content. |
| 5 | Add auth | Partial | **There is no real authentication.** Sign up and log in create a local profile in the browser (name and email, no password). It is a convenience, not a security boundary. Real accounts need a backend with a hosted auth provider. |
| 6 | Check user permissions | N/A | No multi-user data exists. Each browser holds only its own profile and library. |
| 7 | Sanitize user inputs | Done | Length caps on every field, control and bidirectional-override characters stripped, prompt delimiters neutralised, email format validated, and everything read back from browser storage is re-validated on load. |
| 8 | Protect against XSS | Done | Every dynamic string goes through `textContent`. `innerHTML` is only used to clear a container or to insert fixed strings. No inline event handlers, `eval`, or `document.write`. The GitHub build adds a strict CSP that allows only the two inline scripts by SHA-256 hash. |
| 9 | SQL injection protection | N/A | There is no database or SQL. |
| 10 | Check DB rules | N/A | There is no database. If you add shared storage later, write per-user access rules first. |
| 11 | Add rate limiting | Partial | Client-side limits of one request per 1.5 s, 8 per minute and 60 per day per device. These stop accidents and runaway loops but can be bypassed by a determined user. Real limits are enforced by the Claude platform. Server-side limiting needs a server. |
| 12 | Set spend cap | Partial | The same 60-per-day client cap plus input length caps. Usage is billed to the visitor's own Claude account, not to you. If you ever add your own API key on a backend, set a hard spend limit in the provider's console. |
| 13 | Secure file uploads | N/A | There are no uploads. The Download buttons only save text created in the page. |
| 14 | CSRF protection | N/A | No cookies, no sessions and no server endpoints. The CSP sets `form-action 'none'`. |
| 15 | Check CORS settings | N/A | The page makes no cross-origin requests (`connect-src 'none'`). Cross-Origin-Opener and Resource policies are set to same-origin. |
| 16 | Enable HTTPS | Done | HSTS and `upgrade-insecure-requests` in the headers, plus a guard in the script that redirects plain HTTP. On GitHub Pages, tick **Enforce HTTPS** in Settings, Pages. |
| 17 | Add security headers | Done | See `_headers` (Netlify, Cloudflare Pages) and `vercel.json`. **GitHub Pages cannot set custom headers**, so there `index.html` carries a CSP and referrer policy as meta tags. Meta tags cannot set HSTS, X-Frame-Options or `frame-ancestors`. Use Netlify, Cloudflare Pages or Vercel if you need those. |
| 18 | Secure cookies | N/A | No cookies are used. Preflight fails if `document.cookie` ever appears. |
| 19 | Disable debug mode | Done | No console output and no `debugger`. Preflight enforces this. |
| 20 | Check prod settings and publish | Done | `scripts/preflight.py` runs before every deploy in `.github/workflows/pages.yml`. See README for the publish commands. |

## Known limitations

- Browser storage can be read or edited by anything running on the same origin, and the email in a local profile is stored unencrypted. Do not treat the local profile as private from other people using the same browser.
- The daily cap lives in browser storage, so clearing site data resets it.
- Text generation only works when the page is hosted where Claude is available (claude.ai). Elsewhere the writing tool shows a notice and every other page still works.
- The only third-party request is for fonts from Google Fonts.

## Reporting a problem

Open a private security advisory on the repository (Security tab, Report a vulnerability), or open an issue if the report contains nothing sensitive.
