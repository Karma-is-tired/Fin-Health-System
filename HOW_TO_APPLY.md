# How to apply this update (about 10 minutes)

1. Copy everything in this folder into your project and overwrite when asked.
   (Backend files go in the project root. The `frontend` folder merges into your `frontend` folder.)
2. Delete the old database from Git so it stops being public:
       git rm --cached database/finance_tool.db
   (The new .gitignore keeps it out from now on.)
3. On Render, open your service > Environment and add:
       SECRET_KEY       a long random value (generate: python -c "import secrets; print(secrets.token_urlsafe(48))")
       ALLOWED_ORIGINS  https://fin-health-system.vercel.app
   The old secret from main.py is public, so do not reuse it.
4. Commit and push:
       git add -A
       git commit -m "Redesign, security fixes, per-user data"
       git push
5. Wait for Render and Vercel to redeploy, then sign up again. Old accounts were stored in the
   database file that is now gone, so everyone signs up fresh.
6. Optional: delete tests that call old routes (the new test_main.py replaces the old one).
   Run `python -m pytest -q` locally to confirm everything passes.
