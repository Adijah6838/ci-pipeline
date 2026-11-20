from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from ..services.worker import REPOS, BUILDS, QUEUE, create_repo, queue_build, run_build, run_next, summary
router = APIRouter()
class RepoIn(BaseModel):
    name: str
    url: str = "https://github.com/example/repo"
    config: Optional[Dict[str, Any]] = None
class BuildIn(BaseModel):
    repo_id: int
    branch: str = "main"
    commit: str = "abc123"
@router.post("/repos")
def add_repo(body: RepoIn):
    return create_repo(body.name, body.url, body.config)
@router.get("/repos")
def list_repos():
    return {"total": len(REPOS), "repos": list(REPOS.values())}
@router.post("/builds")
def trigger(body: BuildIn):
    return queue_build(body.repo_id, body.branch, body.commit)
@router.get("/builds")
def list_builds(status: str = ""):
    items = list(BUILDS.values())
    if status:
        items = [b for b in items if b["status"] == status]
    return {"total": len(items), "builds": items}
@router.get("/builds/{bid}")
def get_build(bid: int):
    return BUILDS.get(bid, {"error": "not found"})
@router.post("/builds/{bid}/run")
def run_one(bid: int):
    return run_build(bid)
@router.post("/worker/run-next")
def worker_next():
    return run_next()
@router.get("/queue")
def queue():
    return {"queued": len(QUEUE), "ids": QUEUE}
@router.get("/summary")
def summ():
    return summary()
@router.get("/sample")
def sample():
    return {"name": "shop-api", "url": "https://github.com/Adijah6838/shop-api", "config": {"steps": ["install", "lint", "test", "build"], "timeout": 30}}