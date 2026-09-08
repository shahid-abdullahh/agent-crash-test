import asyncio
import httpx
import json

BASE_URL = "http://127.0.0.1:8000"

async def run_live_e2e():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        print("==================================================================")
        print(">>> AGENT CRASH TEST — FULL END-TO-END VERIFICATION SUITE <<<")
        print("==================================================================")

        # 1. Health
        r = await client.get("/health")
        print(f"\n[1] Health Check: {r.status_code} => {r.json()}")
        assert r.status_code == 200

        # 2. Integrations & Connectors
        print("\n[2] Smart API Integration & Connector Framework:")
        r = await client.get("/integrations")
        integrations = r.json()
        print(f"    - Discovered Integrations: {len(integrations)}")
        assert len(integrations) >= 1
        int_id = integrations[0]["id"]
        print(f"    - Base Integration: {integrations[0]['name']} ({len(integrations[0]['operations'])} operations)")

        r = await client.get("/connectors")
        connectors = r.json()
        print(f"    - Registered Connectors: {len(connectors)} ({[c['name'] for c in connectors]})")
        assert len(connectors) >= 1

        # 3. Integration Code Artifact Generation
        print("\n[3] Integration Code Generation:")
        r = await client.get(f"/integrations/{int_id}/code")
        code_pkg = r.json()
        print(f"    - Generated Files: {list(code_pkg.keys())}")
        assert "client.py" in code_pkg
        assert "tools.json" in code_pkg
        assert "README.md" in code_pkg

        # 4. AI-Based API Documentation Builder
        print("\n[4] API Documentation Builder:")
        r = await client.get(f"/documentation/{int_id}")
        doc = r.json()
        print(f"    - Documented Endpoints: {len(doc['endpoints'])}")
        print(f"    - Agent Decision Rules: {len(doc['agent_usage_rules'])}")
        print(f"    - Markdown Size: {len(doc['markdown_content'])} characters")
        assert len(doc["endpoints"]) >= 4

        # 5. Multi-Service Connectivity Workflow (Flight Search -> Reservation -> Payment)
        print("\n[5] Multi-Service Coordination Workflow (Flight -> Reservation -> Payment):")
        r = await client.get("/sandbox/flights?origin=DEL&destination=BOM")
        flights = r.json()
        flight_id = flights[0]["flight_id"]
        flight_price = flights[0]["price"]
        print(f"    - Step 1: Discovered Flight {flight_id} @ INR {flight_price}")

        r = await client.post("/sandbox/reservations", json={
            "flight_id": flight_id,
            "passenger_name": "Multi-Service Agent",
            "idempotency_key": "IDEM-SVC-001"
        })
        res = r.json()
        res_id = res["reservation_id"]
        print(f"    - Step 2: Created Reservation {res_id}")

        r = await client.post("/sandbox/payments", json={
            "reservation_id": res_id,
            "amount": flight_price,
            "payment_method": "CARD",
            "idempotency_key": "PAY-IDEM-SVC-001"
        })
        payment = r.json()
        print(f"    - Step 3: Settled Payment {payment['payment_id']} (Status: {payment['status']})")
        assert payment["status"] == "completed"

        # 6. Task Verification
        r = await client.get("/tasks")
        tasks = r.json()
        task_id = tasks[0]["id"]
        print(f"\n[6] Active Evaluation Task: {task_id}")

        # 7. Test A: Normal Happy Path Run
        print("\n[7] Crash Test A: Normal Run (Nominal API)")
        r = await client.post("/runs", json={
            "task_id": task_id,
            "scenario_mode": "normal",
            "agent_type": "deterministic",
            "agent_retry_policy": "unsafe_retry"
        })
        run_normal = r.json()
        print(f"    - Run ID: {run_normal['id']} | Status: {run_normal['status']} | Success: {run_normal['evaluation']['success']}")
        print(f"    - Trace Events: {len(run_normal['trace'])}")
        assert run_normal["status"] == "completed"
        assert run_normal["evaluation"]["success"] is True

        # 8. Test B: Injected Ambiguous Timeout Fault
        print("\n[8] Crash Test B: Injected Fault (Timeout-After-Commit + Unsafe Retry)")
        r = await client.post("/runs", json={
            "task_id": task_id,
            "scenario_mode": "timeout_after_commit",
            "agent_type": "deterministic",
            "agent_retry_policy": "unsafe_retry"
        })
        run_fault = r.json()
        print(f"    - Run ID: {run_fault['id']} | Status: {run_fault['status']} | Success: {run_fault['evaluation']['success']}")
        print(f"    - Duplicates Detected: {run_fault['evaluation']['side_effects']['duplicate_reservations_detected']}")
        print(f"    - Root Cause Diagnosis: {run_fault['diagnosis']['failure_category']}")
        assert run_fault["status"] == "failed"
        assert run_fault["evaluation"]["side_effects"]["duplicate_reservations_detected"] == 1

        # 9. Test C: Remediated Safe Run
        print("\n[9] Crash Test C: Safe Remediation (Idempotency Key Recovery)")
        r = await client.post("/runs", json={
            "task_id": task_id,
            "scenario_mode": "timeout_after_commit",
            "agent_type": "deterministic",
            "agent_retry_policy": "idempotent_retry"
        })
        run_safe = r.json()
        print(f"    - Run ID: {run_safe['id']} | Status: {run_safe['status']} | Success: {run_safe['evaluation']['success']}")
        print(f"    - Duplicates: {run_safe['evaluation']['side_effects']['duplicate_reservations_detected']}")
        assert run_safe["status"] == "completed"
        assert run_safe["evaluation"]["side_effects"]["duplicate_reservations_detected"] == 0

        # 10. Test D: Before/After Comparison
        print("\n[10] Before / After Remediation Diff:")
        r = await client.get(f"/comparison?baseline_run_id={run_fault['id']}&remediated_run_id={run_safe['id']}")
        comp = r.json()
        print(f"    - Transition: {comp['status_transition']}")
        print(f"    - Side-Effect Delta: {comp['side_effect_delta']}")
        print(f"    - Remediation Effective: {comp['remediation_effective']}")
        assert comp["remediation_effective"] is True

        # 11. Test E: Invalid Parameter Recovery
        print("\n[11] Crash Test E: Invalid Parameter Recovery (HTTP 422 -> Self-Correction)")
        r = await client.post("/runs", json={
            "task_id": task_id,
            "scenario_mode": "invalid_parameter",
            "agent_type": "deterministic",
            "agent_retry_policy": "unsafe_retry"
        })
        run_invalid = r.json()
        print(f"    - Run ID: {run_invalid['id']} | Status: {run_invalid['status']} | Success: {run_invalid['evaluation']['success']}")
        assert run_invalid["status"] == "completed"

        # 12. Test F: Constraint Violation (API 200 != Task Success)
        print("\n[12] Crash Test F: Constraint Violation (Budget Breach)")
        r = await client.post("/runs", json={
            "task_id": task_id,
            "scenario_mode": "constraint_violation",
            "agent_type": "violating_agent",
            "agent_retry_policy": "unsafe_retry"
        })
        run_violating = r.json()
        print(f"    - Run ID: {run_violating['id']} | Status: {run_violating['status']} | Success: {run_violating['evaluation']['success']}")
        print(f"    - Violation Caught: {run_violating['evaluation']['reasons']}")
        assert run_violating["status"] == "failed"

        # 13. Test G: Empirical Reliability
        print("\n[13] Empirical Reliability Analytics:")
        r = await client.get("/reliability")
        rel = r.json()
        print(f"    - Total Runs: {rel['total_runs']}")
        print(f"    - Success / Fail: {rel['successful_runs']} / {rel['failed_runs']}")
        print(f"    - Overall Reliability: {rel['overall_reliability_percentage']}%")
        print(f"    - Scenario Breakdown: {rel['by_scenario']}")

        print("\n==================================================================")
        print(">>> ALL 13 END-TO-END PRODUCT WORKFLOWS VERIFIED CLEANLY! <<<")
        print("==================================================================")

if __name__ == "__main__":
    asyncio.run(run_live_e2e())
