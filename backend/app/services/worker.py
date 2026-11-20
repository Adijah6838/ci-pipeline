import time
REPOS = {}
BUILDS = {}
QUEUE = []
NEXT_REPO = [1]
NEXT_BUILD = [1]
ALLOWED_STEPS = ["install", "lint", "test", "build"]
def create_repo(name, url, config=None):
    rid = NEXT_REPO[0]; NEXT_REPO[0] += 1
    cfg = config or {"steps": ["install", "lint", "test", "build"], "timeout": 30}
    REPOS[rid] = {"id": rid, "name": name, "url": url, "config": cfg}
    return REPOS[rid]
def queue_build(repo_id, branch="main", commit="abc123"):
    if repo_id not in REPOS:
        return {"error": "repo not found"}
    bid = NEXT_BUILD[0]; NEXT_BUILD[0] += 1
    b = {"id": bid, "repo_id": repo_id, "repo_name": REPOS[repo_id]["name"], "branch": branch, "commit": commit, "status": "queued", "logs": ["Queued - waiting for worker"], "artifacts": [], "summary": ""}
    BUILDS[bid] = b; QUEUE.append(bid)
    return b
def run_build(bid):
    b = BUILDS.get(bid)
    if not b:
        return {"error": "build not found"}
    if b["status"] not in ("queued", "pending"):
        return b
    repo = REPOS[b["repo_id"]]
    cfg = repo["config"]
    steps = cfg.get("steps", [])
    # Validate config
    for s in steps:
        if s not in ALLOWED_STEPS:
            b["status"] = "failed"; b["logs"].append(f"ERROR: Unknown step '{s}'. Allowed: {ALLOWED_STEPS}"); b["summary"] = "Failed - invalid config"; return b
    if cfg.get("missing_deps"):
        b["status"] = "failed"; b["logs"].append("ERROR: Missing dependency 'requests' - pip install failed"); b["summary"] = "Failed - missing dependencies"; return b
    if cfg.get("timeout_seconds", 999) < 5:
        b["status"] = "timeout"; b["logs"].append("ERROR: Build timed out after 5s"); b["summary"] = "Timeout - worker interrupted"; return b
    if cfg.get("worker_killed"):
        b["status"] = "interrupted"; b["logs"].append("ERROR: Worker interrupted - build cancelled"); b["summary"] = "Interrupted - worker killed"; return b
    b["status"] = "running"; b["logs"].append("Worker picked up job - running in isolated simulator (no real code executed)")
    passed = 0; failed = 0
    for s in steps:
        b["logs"].append(f"Step: {s} ...")
        if s == "test" and cfg.get("fail_tests"):
            b["logs"].append("FAIL: test_login failed - expected 200 got 500")
            failed += 1
        else:
            b["logs"].append(f"Step: {s} PASSED")
            passed += 1
    if failed > 0:
        b["status"] = "failed"; b["summary"] = f"Failed - {failed} test(s) failed, {passed} passed"
    else:
        b["status"] = "success"; b["summary"] = f"Success - {passed}/{len(steps)} steps passed"; b["artifacts"] = [f"{repo['name']}-{b['commit']}.zip", "test-report.html"]
    if bid in QUEUE:
        QUEUE.remove(bid)
    return b
def run_next():
    if not QUEUE:
        return {"message": "queue empty"}
    return run_build(QUEUE[0])
def summary():
    total = len(BUILDS)
    succ = sum(1 for b in BUILDS.values() if b["status"] == "success")
    fail = sum(1 for b in BUILDS.values() if b["status"] == "failed")
    return {"total_builds": total, "success": succ, "failed": fail, "timeout": sum(1 for b in BUILDS.values() if b["status"] == "timeout"), "interrupted": sum(1 for b in BUILDS.values() if b["status"] == "interrupted"), "queued": len(QUEUE), "success_rate": round(succ / max(total, 1) * 100, 1)}