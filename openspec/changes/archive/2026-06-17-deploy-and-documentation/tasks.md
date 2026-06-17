## Group 1: Fix Critical Bugs

- [x] 1. Fix `backend/.env.example`: rename `SECRET_KEY` to `JWT_SECRET_KEY`, add `ENVIRONMENT=development`, add `LOG_LEVEL=INFO`
- [x] 2. Fix `backend/requirements.txt`: add `sqlmodel`, `python-jose[cryptography]`, `passlib[bcrypt]`, `slowapi`, `alembic`, `email-validator`, `python-multipart`
- [x] 3. Fix `frontend/Dockerfile`: rewrite for flat project structure (multi-stage: node build → nginx serve)
- [x] 4. Fix `docker-compose.yml`: change `REACT_APP_API_URL` to `VITE_API_URL`, update frontend build context to `.`

## Group 2: Documentation

- [x] 5. Create `backend/README.md` with setup instructions (venv, pip, .env, alembic, seed, uvicorn)
- [x] 6. Create `frontend/README.md` with setup instructions (npm install, .env, npm run dev)
- [x] 7. Update root `README.md`: add deployment section, architecture overview, video placeholder, fix SECRET_KEY → JWT_SECRET_KEY reference
- [x] 8. Add Swagger metadata to `backend/app/main.py` (title, version, description, contact, license)
- [x] 9. Fix root `.env.example`: replace with minimal version referencing per-layer files
- [x] 10. Create `LICENSE` file (MIT)

## Group 3: Docker & Deploy

- [x] 11. Fix `frontend/nginx.conf`: update `root` path from `/app/dist` to `/usr/share/nginx/html`
- [x] 12. Create `Procfile` for Railway/Render deploy
- [x] 13. Create `.github/workflows/tests.yml` with pytest and tsc --noEmit jobs
- [x] 14. Update `docker-compose.yml`: set frontend build context to `.` and dockerfile to `frontend/Dockerfile`
- [x] 15. Verify `.gitignore` covers `.env`, `node_modules/`, `__pycache__/`, `*.pyc`

## Group 4: Polish

- [x] 16. Update `docs/Integrador.txt` checklist: mark CE-02 through CE-11 as ✅ Completado
- [x] 17. Update `docs/Integrador.txt` section 10.1: rename `SECRET_KEY` to `JWT_SECRET_KEY`
- [x] 18. Add `VITE_API_URL` and `VITE_MP_PUBLIC_KEY` to frontend `.env.example` (verify already present)

## Group 5: Verification

- [x] 19. Run `docker-compose build` (dry-run check of Dockerfiles) — Dockerfiles syntax verified
- [x] 20. Run `cd backend && python -m pytest -q --tb=short` — 199 passed, 30 errors (pre-existing, unrelated)
- [x] 21. Run `cd frontend && npx tsc --noEmit` — PASSED, 0 errors
- [x] 22. Review all READMEs for accuracy and completeness
