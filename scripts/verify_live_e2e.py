import asyncio
import httpx
import json

BASE_URL = "http://127.0.0.1:8000"

async def run_live_e2e():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # 1. Health
        r = await client.get("/health")
        print(f"[1] Health check: {r.status_code} => {r.json()}")
        assert r.status_code == 200

        # 2. Get Tasks
        r = await client.get("/tasks")
        tasks = r.json()
        print(f"[2] Tasks available: {len(tasks)}")
        assert len(tasks) >= 1
        task_id = tasks[0]["id"]

        # 3. Test A: Normal Run
        print("\n--- [3] Executing Normal Run ---")
        payload_normal = {
            "task_id": task_id,
            "scenario_mode": "normal",
            "agent_type": "deterministic",
            "agent_retry_policy": "unsafe_retry"
        }
        r = await client.post("/runs", json=payload_normal)
        run_normal = r.json()
        print(f"Normal Run ID: {run_normal['id']}")
        print(f"Status: {run_normal['status']}")
        print(f"Evaluation: Success={run_normal['evaluation']['success']}")
        print(f"Side effects: Total={run_normal['evaluation']['side_effects']['total_reservations_created']}, Duplicates={run_normal['evaluation']['side_effects']['duplicate_reservations_detected']}")
        print(f"Trace events count: {len(run_normal['trace'])}")
        assert run_normal["status"] == "completed"
        assert run_normal["evaluation"]["success"] is True
        assert run_normal["evaluation"]["side_effects"]["duplicate_reservations_detected"] == 0

        # 4. Test B: Injected Fault Run (Timeout after commit + Unsafe retry)
        print("\n--- [4] Executing Timeout-After-Commit (Unsafe Retry) ---")
        payload_fault = {
            "task_id": task_id,
            "scenario_mode": "timeout_after_commit",
            "agent_type": "deterministic",
            "agent_retry_policy": "unsafe_retry"
        }
        r = await client.post("/runs", json=payload_fault)
        run_fault = r.json()
        print(f"Fault Run ID: {run_fault['id']}")
        print(f"Status: {run_fault['status']}")
        print(f"Evaluation: Success={run_fault['evaluation']['success']}")
        print(f"Side effects: Total={run_fault['evaluation']['side_effects']['total_reservations_created']}, Duplicates={run_fault['evaluation']['side_effects']['duplicate_reservations_detected']}")
        print(f"Diagnosis category: {run_fault['diagnosis']['failure_category']}")
        print(f"Remediation recommended: {run_fault['diagnosis']['recommended_remediation']}")
        assert run_fault["status"] == "failed"
        assert run_fault["evaluation"]["success"] is False
        assert run_fault["evaluation"]["side_effects"]["duplicate_reservations_detected"] == 1
        assert run_fault["diagnosis"] is not None

        # 5. Test C: Remediated Run (Timeout after commit + Safe Idempotent retry)
        print("\n--- [5] Executing Remediated Run (Idempotent Retry) ---")
        payload_safe = {
            "task_id": task_id,
            "scenario_mode": "timeout_after_commit",
            "agent_type": "deterministic",
            "agent_retry_policy": "idempotent_retry"
        }
        r = await client.post("/runs", json=payload_safe)
        run_safe = r.json()
        print(f"Safe Run ID: {run_safe['id']}")
        print(f"Status: {run_safe['status']}")
        print(f"Evaluation: Success={run_safe['evaluation']['success']}")
        print(f"Side effects: Total={run_safe['evaluation']['side_effects']['total_reservations_created']}, Duplicates={run_safe['evaluation']['side_effects']['duplicate_reservations_detected']}")
        assert run_safe["status"] == "completed"
        assert run_safe["evaluation"]["success"] is True
        assert run_safe["evaluation"]["side_effects"]["duplicate_reservations_detected"] == 0

        # 6. Test D: Run Comparison (Before vs After)
        print("\n--- [6] Executing Before/After Comparison ---")
        r = await client.get(f"/comparison?baseline_run_id={run_fault['id']}&remediated_run_id={run_safe['id']}")
        comp = r.json()
        print(f"Status transition: {comp['status_transition']}")
        print(f"Side effect delta: {comp['side_effect_delta']}")
        print(f"Remediation effective: {comp['remediation_effective']}")
        print(f"Key findings: {comp['key_findings']}")
        assert comp["remediation_effective"] is True
        assert "FAILED -> COMPLETED" in comp["status_transition"]

        # 7. Test E: Invalid Parameter Recovery
        print("\n--- [7] Executing Invalid Parameter Scenario ---")
        payload_invalid_param = {
            "task_id": task_id,
            "scenario_mode": "invalid_parameter",
            "agent_type": "deterministic",
            "agent_retry_policy": "unsafe_retry"
        }
        r = await client.post("/runs", json=payload_invalid_param)
        run_invalid_param = r.json()
        print(f"Invalid Param Run ID: {run_invalid_param['id']}")
        print(f"Status: {run_invalid_param['status']}")
        print(f"Evaluation: Success={run_invalid_param['evaluation']['success']}")
        assert run_invalid_param["status"] == "completed"
        assert run_invalid_param["evaluation"]["success"] is True

        # 8. Test F: Constraint Violation Scenario
        print("\n--- [8] Executing Constraint Violation Scenario ---")
        payload_violating = {
            "task_id": task_id,
            "scenario_mode": "constraint_violation",
            "agent_type": "violating_agent",
            "agent_retry_policy": "unsafe_retry"
        }
        r = await client.post("/runs", json=payload_violating)
        run_violating = r.json()
        print(f"Violating Run ID: {run_violating['id']}")
        print(f"Status: {run_violating['status']}")
        print(f"Evaluation: Success={run_violating['evaluation']['success']}")
        print(f"Evaluation reasons: {run_violating['evaluation']['reasons']}")
        print(f"Diagnosis: {run_violating['diagnosis']['failure_category'] if run_violating['diagnosis'] else 'None'}")
        assert run_violating["status"] == "failed"
        assert run_violating["evaluation"]["success"] is False

        # 9. Test G: Reliability Overview
        print("\n--- [9] Fetching Empirical Reliability Overview ---")
        r = await client.get("/reliability")
        rel = r.json()
        print(f"Total runs recorded: {rel['total_runs']}")
        print(f"Successful runs: {rel['successful_runs']}")
        print(f"Failed runs: {rel['failed_runs']}")
        print(f"Overall reliability: {rel['overall_reliability_percentage']}%")
        print(f"By scenario breakdown: {rel['by_scenario']}")
        assert rel["total_runs"] >= 5
        assert rel["successful_runs"] >= 3
        assert rel["failed_runs"] >= 2

        print("\n=======================================================")
        print(">>> ALL LIVE E2E SCENARIOS VERIFIED SUCCESSFULLY! <<<")
        print("=======================================================")

if __name__ == "__main__":
    asyncio.run(run_live_e2e())
