# Custom Continuous Integration Pipeline
Simulated CI. Register repos, configure builds, queue jobs, run worker, track status, logs, failed-job reporting, history, artifacts, summaries.
## Safety
Worker is simulated - no real repo code is executed. Only allow-listed steps: install, lint, test, build.
## Run Backend (Terminal 1)
cd backend; uvicorn app.main:app --port 8009 --reload
## Run Frontend (Terminal 2)
cd frontend; npm run dev
# http://localhost:5173/
## Test
cd backend; python -m pytest tests -v
## Endpoints
- POST /api/repos {name, url, config}
- GET /api/repos
- POST /api/builds {repo_id, branch, commit}
- GET /api/builds?status=
- POST /api/builds/{id}/run
- POST /api/worker/run-next
- GET /api/queue
- GET /api/summary
## Scenarios
- success: all steps pass, artifacts created
- fail_tests: test_login fails
- missing_deps: pip install fails
- timeout: timeout_seconds < 5
- interrupted: worker_killed true