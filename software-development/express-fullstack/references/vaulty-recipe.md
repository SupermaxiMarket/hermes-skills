# Vaulty Build Recipe

Complete full-stack Express app built in one session. App lifecycle organizer (documents, warranties, subscriptions) with freemium model, 5 languages, and Stripe payments.

## Source

`/root/projets/vaulty/` — full source on disk.

## File structure

```
/root/projets/vaulty/
├── index.html          # 25KB — landing page + auth + SPA app
├── styles.css          # 11KB — Linear-inspired dark theme design system
├── app.js              # 38KB — full frontend logic (v2 with API calls)
├── i18n.js             # 16KB — 5 languages x 102 keys each
├── i18n.json           # Raw i18n data
├── server/
│   ├── server.js       # Express entry point
│   ├── db.js           # SQLite schema + WAL mode
│   ├── auth.js         # JWT generation + middleware
│   ├── .env            # PORT, JWT_SECRET, STRIPE_KEY
│   ├── routes/
│   │   ├── auth.js     # register, login, me, profile
│   │   ├── api.js      # CRUD documents/warranties/subscriptions + stats
│   │   └── stripe.js   # create-checkout + webhook
│   └── data/           # SQLite DB
├── package.json
└── serve.sh
```

## Demo account

- Email: pierre@test.ch
- Password: test123
- Pre-loaded: 3 documents, 2 warranties, 3 subscriptions

## API endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | /api/auth/register | No | Create account |
| POST | /api/auth/login | No | Login, returns JWT |
| GET | /api/auth/me | JWT | Get profile |
| PUT | /api/auth/profile | JWT | Update name/lang/theme |
| GET | /api/documents | JWT | List documents (no file_data) |
| POST | /api/documents | JWT | Add document (base64 file) |
| DELETE | /api/documents/:id | JWT | Delete document |
| GET | /api/warranties | JWT | List warranties |
| POST | /api/warranties | JWT | Add warranty |
| DELETE | /api/warranties/:id | JWT | Delete warranty |
| GET | /api/subscriptions | JWT | List subscriptions |
| POST | /api/subscriptions | JWT | Add subscription |
| DELETE | /api/subscriptions/:id | JWT | Delete subscription |
| GET | /api/stats | JWT | Dashboard stats + expiring |
| POST | /api/stripe/create-checkout | JWT | Stripe Checkout session |
| POST | /api/stripe/webhook | Sig | Stripe webhook |
| GET | /api/health | No | Health check |

## Key SQLite schema

```sql
CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  plan TEXT DEFAULT 'free',
  stripe_customer_id TEXT,
  stripe_subscription_id TEXT,
  lang TEXT DEFAULT 'fr',
  theme TEXT DEFAULT 'dark',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE documents (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  type TEXT DEFAULT 'Other',
  date TEXT,
  file_name TEXT, file_type TEXT, file_data TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Same pattern for warranties (product, store, expiry, price)
-- and subscriptions (name, amount, period, next_date)
```

## Stripe integration

Monthly: CHF 9.90, Yearly: CHF 99 (badge: -20%). Prices hardcoded in `routes/stripe.js` as 990 / 9900 cents CHF. Webhook URL: `POST /api/stripe/webhook` with `express.raw()` body parser.

Demo mode: if `STRIPE_SECRET_KEY` contains "placeholder", upgrade fires locally with confetti.

## Deployment

```bash
cd /root/projets/vaulty && node server/server.js
# Then in another terminal:
cloudflared tunnel --url http://localhost:8765
```

URL extraction: `grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' /tmp/vaulty_server/tunnel.log | tail -1`

Store URL to `/tmp/vaulty-url.txt` for recovery.