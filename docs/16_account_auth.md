# Signup, login and logout

Scope: email/password accounts through Supabase Auth. Private saved PDFs and
chat are now implemented separately; see [saved workspaces](17_saved_workspaces.md).
Chroma indexes remain ephemeral and per browser session.

## Account configuration

1. Create/select your Supabase project and enable email/password Auth with email
   confirmation enabled. Set the Auth Site URL to your Streamlit app URL. Configure
   email delivery in Supabase for your intended users; test confirmation delivery
   and provider rate limits before inviting users.
2. In Streamlit Cloud app settings, add these top-level secrets:

```toml
SUPABASE_URL = "https://YOUR_PROJECT.supabase.co"
SUPABASE_PUBLISHABLE_KEY = "YOUR_PUBLISHABLE_KEY"
```

A legacy anon key is also accepted under the same key name. Never use service-role
or secret keys. Locally, use environment variables or `.streamlit/secrets.toml`.
Do not commit real credentials. Authentication itself needs no application tables. Saved workspaces separately
require the deployed database/storage schema; see the storage guide.
3. Deploy the reviewed commit. Missing/invalid configuration blocks the workspace
   rather than bypassing login. Authentication is already merged into main.
4. Sign up, open the confirmation email, then return to the app and log in with your
   email/password. This app does not consume URL token fragments or auto-login from
   confirmation callbacks. Existing accounts receive neutral signup instructions.

## Session behavior

The server calls Supabase Auth REST over HTTPS with a 15-second timeout and refuses
redirects. It validates the user remotely on every workspace rerun. No global cached
client, password database, refresh token or persistent login cookie is used. Password
form inputs clear on submission. Only the access token and verified account ID remain
in the individual Streamlit session. Expired/invalid sessions must log in again;
provider failures fail closed. Refresh or a lost Streamlit session may require login.

Logout requests revocation for the current Supabase session and clears local account,
upload, index, preview, consent and chat state even if remote logout/cleanup fails.
A warning distinguishes unconfirmed remote sign-out or failed index deletion. Failed
index cleanup can leave ephemeral data until server restart; do not promise immediate
erasure. Supabase access JWTs can remain valid until expiry after logout; this app
removes its token and does not expose other authenticated APIs.

## Validation

Offline tests mock Supabase and cover missing configuration, signup without automatic
login, invalid credentials, account mismatch, per-session separation, logout despite
remote/cleanup errors, and sanitized provider errors. Existing document-flow tests
explicitly mock the gate; they do not bypass authentication in production.

The owner reported signup/login/logout working on the hosted app. Remaining release
acceptance must verify email delivery, confirmed login,
wrong password, two independent accounts/browser sessions, logout, expiration and
network failure. No real Supabase account or authentication request was created during
implementation. This is not persistent multi-user document-storage acceptance.

References: https://github.com/supabase/auth/blob/master/openapi.yaml
and https://supabase.com/docs/reference/python/auth-signup .
