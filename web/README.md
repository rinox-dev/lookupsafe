# lookupsafe · Astro web app

Responsive Spanish web frontend for the existing lookupsafe Hono/Cloudflare D1 API. Astro renders the application shell; one React island handles navigation, Supabase Auth, browser OCR, and account data.

## Run

From the repository root:

```sh
cd web
npm ci
cp .env.example .env
npm run dev
```

Open http://localhost:4321. Without service settings, the app remains usable in a **clearly labeled, in-memory example mode**: import an ingredient photo, review the recognized text, run the shared label matcher, update example preferences, favorite/delete examples, and export a PNG summary. Example changes disappear on reload and never reach the backend.

## Connect a real account

Set these build-time public variables in `web/.env`:

```dotenv
PUBLIC_API_BASE_URL=https://lookupsafe-api.YOUR_SUBDOMAIN.workers.dev
PUBLIC_SUPABASE_URL=https://YOUR_PROJECT.supabase.co
PUBLIC_SUPABASE_PUBLISHABLE_KEY=YOUR_PUBLIC_SUPABASE_KEY
```

Use the same Supabase project as Android and the API. Only the publishable/anon key belongs in this file; never use a service-role or secret key. Supabase's browser SDK persists and refreshes the session. Add the web origin to Supabase Authentication's Site URL/allowed redirect URLs so confirmation emails can return to the web app. Login and registration use email/password; OAuth and password recovery are not included.

In the API's local `.dev.vars`, set:

```dotenv
WEB_ORIGINS=http://localhost:4321,http://127.0.0.1:4321
```

For deployment set `WEB_ORIGINS` to a comma-separated list of exact allowed frontend origins (no trailing slash). In `backend/` run `npx wrangler secret put WEB_ORIGINS`, enter the origin(s), and redeploy the API. Unlisted origins receive no CORS grant. Preflight requests are allowed for configured origins; all data requests still need a verified Supabase access token. Native Android behavior is unchanged.

Run the API using the root README instructions. A signed-in web session reads real private data and never falls back to example data when the API fails. Retry history loading with its refresh control after correcting a connection issue.

## Build and deploy to Cloudflare

```sh
npm run build
npm run preview
# After setting public build variables and signing in to Cloudflare:
npx wrangler login
npm run deploy
```

The static output is `web/dist/`, and `wrangler.jsonc` deploys it as a separate Cloudflare Worker with static assets. Hono remains in `backend/`, and D1 remains bound only to that API. The web frontend can also be hosted on Cloudflare Pages using build command `npm run build`, root directory `web`, and output directory `dist` (the checkout must include `shared/`). Public settings are embedded during the build; rebuild after changing them.

## Behavior and limits

- JPG/PNG/WebP image import up to 10 MB, camera capture on supported mobile browsers, and manual text entry.
- Tesseract.js recognizes Spanish/English text locally. When confidence is below 72%, the browser retries with an enlarged grayscale/contrast-enhanced copy. The displayed OCR confidence is a recognition signal, not a guarantee; review every ingredient before submitting. Its worker and language models download on first use, so first recognition needs internet access. No image is sent to the API.
- Signed-in scans can search PubMed for biomedical publications about each recognized text segment and show available abstracts. Open each citation to review full abstracts and methods: a search hit is not evidence by itself that an ingredient is harmful or safe. Example mode opens the corresponding PubMed search directly.
- The API and example mode use `shared/analysis.ts`. It finds text mentions, including negations and traces, in a limited catalog. It does not certify product safety or generate medical scores.
- History is paginated; search and favorites filter the currently loaded items. Use “Cargar más consultas” to search older entries.
- Profile changes affect future analyses. Deleting profile/history retains the Supabase authentication account.
- Theme preference persists locally; example data does not. Account data belongs to the authenticated user.

`npm run build` performs Astro/TypeScript checks before producing static output. API tests in `backend/` cover cross-user isolation, validation, SQL persistence and CORS. Live email delivery and real-account synchronization require configured external services.

Reference: [Astro client scripts](https://docs.astro.build/en/guides/client-side-scripts/), [public environment variables](https://docs.astro.build/en/guides/environment-variables/), [Supabase browser auth](https://supabase.com/docs/reference/javascript/initializing), [Hono CORS](https://hono.dev/docs/middleware/builtin/cors).

## Verified locally

- Astro/TypeScript build: zero errors, warnings, or hints.
- Cloudflare static frontend and Hono API deployment dry runs pass.
- All 12 backend tests pass, including exact-origin CORS and unchanged Android-style access.
- Orca browser checks: desktop and 390px mobile layouts, no horizontal overflow, light/dark themes, real OCR of a generated label image, example analysis, favorite toggle, deletion confirmation, PNG download, preference updates, and login/registration dialog navigation.
- The browser reported no application console errors during these checks. Live Supabase login/email delivery and remote deployment remain untested because service settings are not configured.
