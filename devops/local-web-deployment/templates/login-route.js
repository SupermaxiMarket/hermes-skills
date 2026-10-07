/* login-route.js — self-service login for Hermes3D Studio access gate

   Usage in server/index.js:
     const { handleLogin } = require('./login-route');
     // Inside createServer(), BEFORE accessGate.handleHttp:
     handleLogin(req, res, process.env.STUDIO_ACCESS_TOKEN).then(
       (handled) => { if (handled) return; if (accessGate.handleHttp(req, res)) return; handle(req, res); },
       () => { if (accessGate.handleHttp(req, res)) return; handle(req, res); }
     );

   Environment:
     STUDIO_ACCESS_TOKEN — the same token the access gate checks.
     No other env needed: reads it from argument so the caller passes it.

   Endpoints:
     GET  /login           → form HTML
     POST /login token=…   → constant-time compare → Set-Cookie → 303 /office
     GET  /login?token=…   → same as POST (bookmark/QR friendly)

   Cookie:
     Name:     studio_access
     Path:     /
     HttpOnly: true
     SameSite: Lax
     Max-Age:  1209600 (14 days)

   Dependencies: Node.js built-in modules only (crypto, no npm deps).
*/
const crypto = require('node:crypto');
const COOKIE_NAME = 'studio_access';
const COOKIE_MAX_AGE = 14 * 24 * 60 * 60;

function safeCompare(a, b) {
  if (typeof a !== 'string' || typeof b !== 'string') return false;
  const bufA = Buffer.from(a, 'utf8');
  const bufB = Buffer.from(b, 'utf8');
  if (bufA.length !== bufB.length) {
    crypto.timingSafeEqual(bufA, bufA);
    return false;
  }
  return crypto.timingSafeEqual(bufA, bufB);
}

const LOGIN_PAGE = (action) => `<!doctype html>
<html lang="fr">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Accès Studio</title>
<style>
  body{min-height:100vh;display:grid;place-items:center;font-family:system-ui,sans-serif;
    background:radial-gradient(1200px 600px at 20% 10%,#1a2436 0%,#0b0f17 60%,#05070c 100%);color:#e6e9f0}
  .card{width:min(92vw,420px);padding:2.2rem;border:1px solid #2a3550;border-radius:16px;
    background:rgba(13,18,30,.82);box-shadow:0 24px 60px rgba(0,0,0,.45);backdrop-filter:blur(6px)}
  h1{font-size:1.15rem;font-weight:650;margin-bottom:.35rem}
  .sub{font-size:.82rem;color:#8b95a8;margin-bottom:1.4rem}
  label{display:block;font-size:.78rem;text-transform:uppercase;letter-spacing:.08em;color:#aab3c5;margin-bottom:.45rem}
  input[type=password]{width:100%;padding:.8rem .9rem;font-size:.95rem;color:#eef1f6;background:#0d1220;
    border:1px solid #33405c;border-radius:10px;outline:none}
  input[type=password]:focus{border-color:#6f8fff;box-shadow:0 0 0 3px rgba(111,143,255,.18)}
  button{width:100%;margin-top:1.1rem;padding:.85rem;font-size:.95rem;font-weight:600;
    color:#0b0f17;background:linear-gradient(135deg,#ffbf00,#ff9500);border:0;border-radius:10px;cursor:pointer}
  button:hover{filter:brightness(1.08)}.brand{text-align:center;margin-bottom:1.3rem}
  .brand span{font-size:1.65rem;font-weight:700;background:linear-gradient(90deg,#ffbf00,#ff7a00);
    -webkit-background-clip:text;background-clip:text;color:transparent}
</style></head>
<body>
<div class="card">
  <div class="brand"><span>Studio</span></div>
  <h1>Accès au Studio</h1>
  <p class="sub">Entre le code d'accès pour accéder à l'application.</p>
  <form method="POST" action="${action}">
    <label for="token">Code d'accès</label>
    <input type="password" id="token" name="token" autocomplete="current-password" autofocus required>
    <button type="submit">Entrer</button>
  </form>
</div></body></html>`;

function parseBody(req) {
  return new Promise((resolve) => {
    let data = '';
    req.on('data', (chunk) => { data += chunk; if (data.length > 65536) { req.destroy(); resolve(null); } });
    req.on('end', () => resolve(data || null));
    req.on('error', () => resolve(null));
  });
}

async function handleLogin(req, res, configuredToken) {
  const token = String(configuredToken ?? '').trim();
  if (!token) return false;
  const rawUrl = String(req.url || '/');
  const qi = rawUrl.indexOf('?');
  const pathname = qi === -1 ? rawUrl : rawUrl.slice(0, qi);
  if (pathname !== '/login') return false;
  const qs = qi === -1 ? '' : rawUrl.slice(qi + 1);
  tokenMatch = qs.match(/(?:^|&)token=([^&]+)/);
  let provided = '';
  if (req.method === 'POST') {
    const body = await parseBody(req);
    if (body) { const m = body.match(/token=([^&]+)/); if (m) provided = decodeURIComponent(m[1].replace(/\+/g, ' ')); }
  } else if (tokenMatch) {
    provided = decodeURIComponent(tokenMatch[1]);
  }
  const ok = provided ? safeCompare(provided, token) : false;
  res.setHeader('Content-Type', 'text/html; charset=utf-8');
  if (ok) {
    res.setHeader('Set-Cookie', `${COOKIE_NAME}=${encodeURIComponent(token)}; Path=/; HttpOnly; SameSite=Lax; Max-Age=${COOKIE_MAX_AGE}`);
    res.statusCode = 303;
    res.setHeader('Location', '/office');
    res.end('<html><head><meta http-equiv="refresh" content="0;url=/office"></head><body>OK</body></html>');
    return true;
  }
  res.statusCode = 200;
  res.end(LOGIN_PAGE('/login'));
  return true;
}
module.exports = { handleLogin, COOKIE_NAME };