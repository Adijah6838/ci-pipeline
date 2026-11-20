import { useState, useEffect } from "react";
const API = "http://127.0.0.1:8009/api";
export default function App() {
  const [repos, setRepos] = useState([]);
  const [builds, setBuilds] = useState([]);
  const [summ, setSumm] = useState(null);
  const [name, setName] = useState("shop-api");
  const [url, setUrl] = useState("https://github.com/Adijah6838/shop-api");
  const [scenario, setScenario] = useState("success");
  const [repoId, setRepoId] = useState(1);
  const [result, setResult] = useState(null);
  const load = async () => { const r = await (await fetch(`${API}/repos`)).json(); setRepos(r.repos); const b = await (await fetch(`${API}/builds`)).json(); setBuilds(b.builds); const s = await (await fetch(`${API}/summary`)).json(); setSumm(s); };
  useEffect(() => { load(); }, []);
  const getConfig = () => { if (scenario === "fail_tests") return { steps: ["install", "lint", "test", "build"], timeout: 30, fail_tests: true }; if (scenario === "missing_deps") return { steps: ["install", "lint", "test", "build"], timeout: 30, missing_deps: true }; if (scenario === "timeout") return { steps: ["install", "lint", "test", "build"], timeout_seconds: 2 }; if (scenario === "interrupted") return { steps: ["install", "lint", "test", "build"], timeout: 30, worker_killed: true }; return { steps: ["install", "lint", "test", "build"], timeout: 30 }; };
  const addRepo = async () => { const r = await fetch(`${API}/repos`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ name, url, config: getConfig() }) }); setResult(await r.json()); load(); };
  const trigger = async () => { const r = await fetch(`${API}/builds`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ repo_id: repoId, branch: "main", commit: "abc123" }) }); const d = await r.json(); setResult(d); if (d.id) { const run = await fetch(`${API}/builds/${d.id}/run`, { method: "POST" }); setResult(await run.json()); } load(); };
  const runBuild = async (id) => { const r = await fetch(`${API}/builds/${id}/run`, { method: "POST" }); setResult(await r.json()); load(); };
  return (<div style={{ maxWidth: 900, margin: "auto", padding: 20, fontFamily: "sans-serif" }}>
    <h1>⚙️ CI Pipeline</h1><p>Simulated worker - no real code executed. Safe allow-listed steps only.</p>
    {summ && <div style={{ background: "#eef", padding: 12 }}><b>Summary:</b> Total {summ.total_builds} | Success {summ.success} | Failed {summ.failed} | Timeout {summ.timeout} | Interrupted {summ.interrupted} | Queued {summ.queued} | Success Rate {summ.success_rate}%</div>}
    <h3>Register Repo</h3><input value={name} onChange={e => setName(e.target.value)} style={{ padding: 10 }} /><input value={url} onChange={e => setUrl(e.target.value)} style={{ padding: 10, marginLeft: 8, width: 350 }} /><select value={scenario} onChange={e => setScenario(e.target.value)} style={{ padding: 10, marginLeft: 8 }}><option value="success">Success</option><option value="fail_tests">Fail Tests</option><option value="missing_deps">Missing Deps</option><option value="timeout">Timeout</option><option value="interrupted">Worker Interrupted</option></select><button onClick={addRepo} style={{ padding: 10, marginLeft: 8 }}>Register</button>
    <h3>Trigger Build</h3><select value={repoId} onChange={e => setRepoId(Number(e.target.value))} style={{ padding: 10 }}>{repos.map(r => <option key={r.id} value={r.id}>{r.id} - {r.name} - {JSON.stringify(r.config)}</option>)}</select><button onClick={trigger} style={{ padding: 10, marginLeft: 8 }}>Trigger + Run</button><button onClick={load} style={{ padding: 10, marginLeft: 8 }}>Refresh</button>
    {result && <pre style={{ background: result.status === "success" ? "#e6ffe6" : "#ffe6e6", padding: 12 }}>{JSON.stringify(result, null, 2)}</pre>}
    <h3>Build History ({builds.length})</h3>{builds.slice().reverse().map(b => <div key={b.id} style={{ border: "1px solid #ddd", padding: 10, marginTop: 8 }}><b>#{b.id} {b.repo_name} {b.branch}@{b.commit}</b> | {b.status} | {b.summary}<br /><small>{b.logs.join(" | ")}</small><br />{b.artifacts.length > 0 && <span>Artifacts: {b.artifacts.join(", ")}</span>}{b.status === "queued" && <button onClick={() => runBuild(b.id)} style={{ marginLeft: 8 }}>Run</button>}</div>)}
  </div>);
}