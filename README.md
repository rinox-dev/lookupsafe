# lookupsafe

Android and Astro web product-label reader, built from the supplied lookupsafe mockups. Kotlin + Jetpack Compose runs on Android; a Hono TypeScript API runs on Cloudflare Workers; Cloudflare D1 stores profiles and scans; Supabase Auth handles email/password accounts.

## Web app

The Astro frontend is in [`web/`](web/README.md), with desktop/mobile layouts, browser OCR, Supabase login, and the same Hono API. Run `npm ci && npm run dev` from `web/`, then open http://localhost:4321. A labeled example mode works before service setup. See the [web setup guide](web/README.md) for public environment variables, browser CORS configuration, and Cloudflare deployment.

## Included

- Spanish interface, light/dark theme, email registration with confirmation and email/password login.
- Full-resolution camera capture or photo import, bundled on-device ML Kit text recognition, and editable text before submission.
- Ingredient splitting, a limited English/Spanish allergen mention catalog, and personal allergen preferences.
- Private scan history with pagination, search within loaded history, favorites, details, deletion, and PNG summary sharing.
- Encrypted session persistence through Android Keystore, token refresh, sign-out, and profile/history deletion.
- D1 migrations, API tests, Gradle wrapper, and CI checks for web, backend, plus an Android 13 emulator UI smoke test and APK artifact.

The mockup's numerical scores and risk classifications were illustrative. The implementation does **not** invent health scores or certify safety: all ingredients remain unreviewed, and results identify text mentions only. It can match negated phrases such as “sin leche”; the UI explains this limitation. Sources are general context, not ingredient-specific assessments. There is no barcode product database, Google/Apple OAuth, anonymous mode, or password-recovery flow in this first version.

## 1. Supabase Auth

Create a Supabase project. Under Authentication, enable email/password sign-in and keep email confirmation enabled. Obtain its project URL and **publishable key** (or legacy public anon key). Never place a service-role/secret key in the Android app.

Configure Supabase's Site URL to a confirmation landing page you control. Registration sends Supabase's confirmation email; after confirming in the browser, the user returns to the app and signs in. This version does not require an OAuth redirect or app deep link. Configure production email delivery in Supabase before public use.

## 2. Backend locally

Use Node.js 24 or later (tests use `node:sqlite`).

```sh
cd backend
npm ci
cp .dev.vars.example .dev.vars
# Set SUPABASE_URL and SUPABASE_PUBLISHABLE_KEY in .dev.vars.
npm run db:local
npm run dev
```

The local API runs at `http://localhost:8787`. `/health` is public; every `/v1/*` request requires `Authorization: Bearer <Supabase access token>`. The server verifies the token with Supabase Auth and scopes every database operation to that returned user ID. There is no development auth bypass. Local scans live in Wrangler's local D1 storage; even local sign-in needs the configured Supabase project and network access.

Docker option: stop any host `wrangler dev` process already using port 8787, then run `docker compose up --build -d`. The container applies D1 migrations on startup and keeps local state in the `lookupsafe-wrangler` volume. Create `backend/.dev.vars` from its example and add Supabase settings when available; the container publishes port 8787 on the host/LAN for debug builds.

## 3. Android

Open `android/` in Android Studio. Install Android SDK 35 and use JDK 17. The wrapper downloads verified Gradle 8.11.1.

```sh
cd android
cp lookupsafe.properties.example lookupsafe.properties
# Fill SUPABASE_URL and SUPABASE_PUBLISHABLE_KEY.
# Android emulator: API_BASE_URL=http://10.0.2.2:8787
./gradlew assembleDebug lintDebug
```

In this workspace, `./scripts/build-android.sh` also uses the locally installed JDK/SDK under git-ignored `.tooling/` when present.

Install `android/app/build/outputs/apk/debug/app-debug.apk`, or use Android Studio's Run action. For a physical device, use a reachable development host address or the deployed Worker HTTPS URL. With USB, `adb reverse tcp:8787 tcp:8787` allows `API_BASE_URL=http://127.0.0.1:8787`. Rebuild after editing properties. These values may also be supplied as environment variables.

Without Supabase settings, the app opens with a configuration message and disabled login. The public Supabase key is intended for inclusion in clients. `.dev.vars`, `lookupsafe.properties`, signing keys, generated builds, and local tooling are git-ignored.

**Pending in this workspace:** Supabase project URL and publishable/anon key have not been supplied. Add them to `backend/.dev.vars` and `android/lookupsafe.properties`, then rebuild the APK to enable sign-in and authenticated API features.

HTTP is allowed only in debug builds. Use an HTTPS API URL for release builds. Configure your own Android signing key for release; none is generated or embedded here.

## 4. Deploy Cloudflare

```sh
cd backend
npx wrangler login
npx wrangler d1 create lookupsafe
```

Copy the returned D1 database ID into `backend/wrangler.jsonc`, replacing the all-zero local placeholder. Then:

```sh
npx wrangler secret put SUPABASE_URL
npx wrangler secret put SUPABASE_PUBLISHABLE_KEY
npm run db:remote
npm run deploy
```

Set Android's `API_BASE_URL` to the resulting HTTPS Worker URL and rebuild. No Cloudflare or Supabase resources are automatically provisioned by the code. D1 holds application data; Supabase's database is not used for scans. Native Android requests do not require browser CORS.

## API

| Method | Path | Behavior |
| --- | --- | --- |
| GET | `/health` | Public liveness |
| GET / PUT | `/v1/profile` | Read/save `{displayName, allergens}` |
| GET | `/v1/scans?limit=30&offset=0` | Newest first, `{items,nextOffset}` |
| POST | `/v1/scans` | Analyze/save `{productName,labelText}` |
| POST | `/v1/evidence` | Search PubMed for biomedical publications about `{ingredient}`; returns up to five citations |
| GET | `/v1/scans/:id` | Read owned scan |
| PATCH | `/v1/scans/:id` | Set `{favorite: boolean}` |
| DELETE | `/v1/scans/:id` | Delete owned scan |
| DELETE | `/v1/data` | Delete own scans/profile; keep Supabase account |

Preference IDs include food allergens and common fragrance, preservative, deodorant, and antiperspirant ingredients. Preferences are snapshotted into each analysis; updating your profile affects future analyses. Deleting app data does not delete the Supabase authentication account. Account lifecycle management remains in Supabase.

Ingredient evidence lookups use NCBI PubMed E-utilities (ESearch + ESummary), querying exact ingredient phrases alongside health-related terms. The app shows linked citations and search counts, not a harm/safety verdict. Search results can include different study designs, doses, and exposure routes; read the abstract and discuss health concerns with a qualified professional. This feature requires a signed-in account in the app; example mode links directly to PubMed. PubMed is subject to NCBI rate limits.

## Verification

```sh
cd backend
npm run typecheck
npm test
npm run db:local
npx wrangler deploy --dry-run
```

Local verification: the debug APK builds, Android lint reports zero errors (dependency-update/style warnings remain), and the app launches on an Android 35 emulator. Login/registration navigation and light/dark layouts were inspected. Twelve backend tests (including browser CORS), the local D1 migration, Worker health/auth smoke checks, and deployment dry run pass. No remote deployment or live Supabase login has been performed.

API tests execute the real SQL migration in SQLite with mocked Supabase responses. They cover user isolation, input validation, persistence, pagination, SQL injection strings, deletion, upstream failure, and label-matching limitations. Live Supabase email delivery and real-device camera behavior require configured services/device testing.

## References

- [Hono on Cloudflare Workers](https://hono.dev/docs/getting-started/cloudflare-workers)
- [Cloudflare D1 with Hono](https://developers.cloudflare.com/d1/examples/d1-and-hono/)
- [Supabase Auth endpoints](https://supabase.github.io/auth/)
- [Android ML Kit text recognition](https://developers.google.com/ml-kit/vision/text-recognition/v2/android)
- [FDA cosmetics overview](https://www.fda.gov/cosmetics/cosmetics-science-research/it-here-cosmetics)
- [NCBI E-utilities](https://www.ncbi.nlm.nih.gov/books/NBK25501/)
- [PubMed](https://pubmed.ncbi.nlm.nih.gov/)

Original SVG mockups and their Python generators remain alongside the app.
