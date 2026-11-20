from app.services.worker import create_repo, queue_build, run_build
def test_success_build():
    r = create_repo("ok", "https://github.com/x/ok", {"steps": ["install", "lint", "test", "build"], "timeout": 30})
    b = queue_build(r["id"], "main", "a1")
    out = run_build(b["id"])
    assert out["status"] == "success" and len(out["artifacts"]) == 2
def test_failed_tests():
    r = create_repo("fail", "https://github.com/x/fail", {"steps": ["install", "lint", "test", "build"], "timeout": 30, "fail_tests": True})
    b = queue_build(r["id"], "main", "a2")
    out = run_build(b["id"])
    assert out["status"] == "failed" and "test_login" in " ".join(out["logs"])
def test_missing_deps():
    r = create_repo("deps", "https://github.com/x/deps", {"steps": ["install"], "timeout": 30, "missing_deps": True})
    b = queue_build(r["id"], "main", "a3")
    out = run_build(b["id"])
    assert out["status"] == "failed" and "Missing dependency" in " ".join(out["logs"])
def test_timeout():
    r = create_repo("to", "https://github.com/x/to", {"steps": ["install"], "timeout_seconds": 2})
    b = queue_build(r["id"], "main", "a4")
    out = run_build(b["id"])
    assert out["status"] == "timeout"
def test_worker_interruption():
    r = create_repo("kill", "https://github.com/x/kill", {"steps": ["install"], "timeout": 30, "worker_killed": True})
    b = queue_build(r["id"], "main", "a5")
    out = run_build(b["id"])
    assert out["status"] == "interrupted"