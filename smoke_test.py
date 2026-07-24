"""Smoke test for LaniakeA Protocol API - exercises every public endpoint."""
import sys
from fastapi.testclient import TestClient

sys.path.insert(0, "/workspace/laniakea-protocol")
from laniakea.api.main import app

client = TestClient(app)


def assert_ok(resp, expected=200, label=""):
    """Helper: assert status code and return JSON."""
    if resp.status_code != expected:
        print(f"FAIL {label}: status={resp.status_code} body={resp.text[:200]}")
        return False
    try:
        return resp.json()
    except Exception:
        return resp.text


results = {"pass": 0, "fail": 0}


def run(label, ok):
    if ok:
        results["pass"] += 1
    else:
        results["fail"] += 1
    print(("PASS" if ok else "FAIL"), label)


# --- System ---
run("GET /", assert_ok(client.get("/")) is not None)
run("GET /health", assert_ok(client.get("/health")) is not None)
run("GET /version", assert_ok(client.get("/version")) is not None)
run("GET /core/status", assert_ok(client.get("/core/status")) is not None)
run("GET /token/info", assert_ok(client.get("/token/info")) is not None)
run("GET /discovery", assert_ok(client.get("/discovery")) is not None)
run("GET /observability/requests", assert_ok(client.get("/observability/requests")) is not None)

# --- Blockchain ---
run("GET /blockchain/info", assert_ok(client.get("/blockchain/info")) is not None)
run("GET /blockchain/chain", assert_ok(client.get("/blockchain/chain")) is not None)
run("POST /blockchain/transactions/new", assert_ok(
    client.post("/blockchain/transactions/new", json={"sender": "alice", "recipient": "bob", "amount": 5.0})
) is not None)
run("POST /blockchain/mine (valid)", assert_ok(
    client.post("/blockchain/mine?authority_address=Validator_A")
) is not None)

# --- SCDA ---
scda = client.post("/scda/create", json={"identity": "smoke_user"})
run("POST /scda/create", scda.status_code == 200)
state = client.get("/scda/state/smoke_user")
run("GET /scda/state/{id}", state.status_code == 200)

solve = client.post("/scda/solve", json={
    "identity": "smoke_user", "problem_difficulty": 0.5, "solution_quality": 0.8, "is_valid": True
})
run("POST /scda/solve", solve.status_code == 200)

bad_solve = client.post("/scda/solve", json={
    "identity": "smoke_user", "problem_difficulty": 1.5, "solution_quality": 0.8, "is_valid": True
})
run("POST /scda/solve (validation)", bad_solve.status_code in (400, 422))

run("GET /scda/identities", assert_ok(client.get("/scda/identities")) is not None)
run("GET /scda/states", assert_ok(client.get("/scda/states")) is not None)
run("GET /scda/leaderboard", assert_ok(client.get("/scda/leaderboard")) is not None)
run("GET /scda/leaderboard/5", assert_ok(client.get("/scda/leaderboard/5")) is not None)
run("GET /scda/summary", assert_ok(client.get("/scda/summary")) is not None)
run("GET /scda/identities/smoke_user/knowledge", assert_ok(
    client.get("/scda/identities/smoke_user/knowledge")
) is not None)
run("POST /scda/passive", assert_ok(
    client.post("/scda/passive", json={"identity": "smoke_user"})
) is not None)

# --- Cross-chain ---
xc = client.post("/crosschain/transfer/initiate", json={
    "source_chain": "Laniakea_Main", "target_chain": "Ethereum_Sim",
    "asset": "LANA", "amount": 100.0, "sender": "alice", "recipient": "bob"
})
run("POST /crosschain/transfer/initiate (LANA)", xc.status_code == 200)
run("GET /crosschain/supported", assert_ok(client.get("/crosschain/supported")) is not None)

# --- Quantum ---
q = client.post("/quantum/job/submit", json={"num_qubits": 2, "gates": [{"type": "H", "target": 0}]})
run("POST /quantum/job/submit", q.status_code == 200)
run("POST /quantum/job/process", assert_ok(client.post("/quantum/job/process")) is not None)
qbad = client.post("/quantum/job/submit", json={"num_qubits": 10, "gates": []})
run("POST /quantum/job/submit (over-qubit)", qbad.status_code == 400)

# --- Governance ---
p = client.post("/governance/proposals/new", json={
    "title": "Test", "description": "d", "proposer": "alice"
})
run("POST /governance/proposals/new", p.status_code == 200)
run("GET /governance/proposals", assert_ok(client.get("/governance/proposals")) is not None)

# --- DeFi ---
run("GET /defi/pools", assert_ok(client.get("/defi/pools")) is not None)
s = client.post("/defi/swap", json={"token_in": "LANA", "token_out": "USDC", "amount_in": 50.0})
run("POST /defi/swap", s.status_code == 200)

# --- Knowledge Market ---
km = client.post("/knowledge_market/tokenize", json={
    "owner_scda_id": "smoke_user", "scda_knowledge_vector": [0.1]*8,
    "complexity_index": 1.5, "knowledge_type": "Mathematics"
})
run("POST /knowledge_market/tokenize", km.status_code == 200)
run("GET /knowledge_market/listed", assert_ok(client.get("/knowledge_market/listed")) is not None)
run("GET /knowledge_market/stats", assert_ok(client.get("/knowledge_market/stats")) is not None)

# --- Diplomacy ---
d = client.post("/diplomacy/alliance", json={
    "name": "Alliance1", "founder_scda_id": "smoke_user", "members": ["user2"]
})
run("POST /diplomacy/alliance", d.status_code == 200)
run("GET /diplomacy/alliances", assert_ok(client.get("/diplomacy/alliances")) is not None)
run("GET /diplomacy/stats", assert_ok(client.get("/diplomacy/stats")) is not None)

# --- Marketplace ---
nft = client.post("/marketplace/nft/mint", json={
    "owner": "alice", "metadata_uri": "ipfs://x", "asset_type": "Test"
})
run("POST /marketplace/nft/mint", nft.status_code == 200)

# --- Simulation ---
run("POST /simulation/step", assert_ok(client.post("/simulation/step")) is not None)
run("GET /simulation/entities", assert_ok(client.get("/simulation/entities")) is not None)

# --- AI / LLM ---
run("POST /ai/query", assert_ok(
    client.post("/ai/query", json={"prompt": "hello"})
) is not None)
run("POST /llm/generate", assert_ok(
    client.post("/llm/generate", json={"prompt": "hi"})
) is not None)
run("GET /llm/status", assert_ok(client.get("/llm/status")) is not None)

# --- Achievements ---
run("GET /achievements/all", assert_ok(client.get("/achievements/all")) is not None)
run("GET /achievements/catalog", assert_ok(client.get("/achievements/catalog")) is not None)

# --- Dashboard ---
run("GET /dashboard/metrics", assert_ok(client.get("/dashboard/metrics")) is not None)

# --- WebSocket stats ---
run("GET /ws/stats", assert_ok(client.get("/ws/stats")) is not None)

# --- OpenAPI ---
run("GET /openapi.json", assert_ok(client.get("/openapi.json")) is not None)
run("GET /docs", client.get("/docs").status_code == 200)

print(f"\n=== RESULTS: {results['pass']} passed, {results['fail']} failed ===")
sys.exit(0 if results["fail"] == 0 else 1)
