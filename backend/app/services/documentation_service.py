from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from app.schemas.documentation import APIDocumentation, EndpointDoc
from app.schemas.integration import Integration
from app.services.integration_service import integration_service


class DocumentationService:
    def generate_documentation(self, integration: Integration) -> APIDocumentation:
        now_str = datetime.now(timezone.utc).isoformat()
        endpoints: List[EndpointDoc] = []

        for op in integration.operations:
            req_example = None
            if op.request_body_schema:
                # Build mock example from schema properties
                props = op.request_body_schema.get("properties", {})
                req_example = {k: "example_value" if v.get("type") == "string" else (1 if v.get("type") == "integer" else 100.0) for k, v in props.items()}

            resp_examples = {
                "200": {"status": "success", "message": f"{op.operation_id} executed successfully"}
            }

            if op.state_changing:
                agent_guidance = (
                    f"This operation modifies server state via `{op.method}`. "
                    "Autonomous agents MUST pass an `idempotency_key` or verify entity status before repeating requests."
                )
                recovery_considerations = (
                    "In the event of network drop (HTTP 504) or timeout, DO NOT blindly retry without checking "
                    "whether state mutation already committed upstream."
                )
            else:
                agent_guidance = (
                    f"Read-only idempotent query via `{op.method}`. Safe for unconditional agent retry upon network error."
                )
                recovery_considerations = "Safe to retry with exponential backoff upon transient 5xx errors."

            endpoints.append(
                EndpointDoc(
                    operation_id=op.operation_id,
                    method=op.method,
                    path=op.path,
                    summary=op.summary or op.operation_id,
                    description=op.description or f"Executes {op.method} on {op.path}",
                    parameters=op.parameters,
                    request_example=req_example,
                    response_examples=resp_examples,
                    state_changing=op.state_changing,
                    agent_guidance=agent_guidance,
                    recovery_considerations=recovery_considerations,
                )
            )

        agent_usage_rules = [
            "1. Tool Schema Adherence: Agents must strictly validate arguments against parameter JSON schemas before dispatch.",
            "2. Idempotency on State Mutations: All mutating operations (POST/PUT/DELETE) must supply an Idempotency-Key.",
            "3. Ambiguous Outcome Handling: When receiving HTTP 504/502 on a state-changing call, verify current state before retrying.",
            "4. Constraint Verification: An HTTP 200 OK does not indicate task goal completion; verify returned payload against task criteria.",
        ]

        failure_and_recovery_guide = [
            "HTTP 422 (Validation Error): Agent must inspect error details, correct the malformed parameter format, and retry.",
            "HTTP 504 (Gateway Timeout): Indicates server drop after mutation or upstream timeout. Check GET endpoints first to avoid duplicate side effects.",
            "HTTP 404 (Not Found): Resource ID is invalid or not yet committed.",
        ]

        # Assemble comprehensive Markdown documentation
        md_lines = [
            f"# {integration.name} — API Usage Documentation",
            "",
            f"> **Version**: {integration.version} | **Base URL**: `{integration.base_url}` | **Generated**: {now_str}",
            "",
            "## 1. Overview",
            f"{integration.description or 'Auto-generated API documentation for autonomous agent and developer integration.'}",
            "",
            "## 2. Authentication",
            "This API currently accepts standard Bearer token or operates in open-access sandbox mode.",
            "",
            "## 3. Endpoints Reference",
            "",
        ]

        for ep in endpoints:
            md_lines.extend([
                f"### `{ep.method} {ep.path}` (`{ep.operation_id}`)",
                f"**Summary**: {ep.summary}",
                "",
                f"**Description**: {ep.description}",
                "",
                f"- **State Changing**: {'⚠️ YES (Mutating)' if ep.state_changing else '✅ NO (Read-Only)'}",
                "",
                "#### Parameters",
                "| Name | Location | Required | Type |",
                "| :--- | :--- | :--- | :--- |",
            ])
            if ep.parameters:
                for p in ep.parameters:
                    md_lines.append(f"| `{p.get('name')}` | `{p.get('in')}` | {'Yes' if p.get('required') else 'No'} | `{p.get('schema', {}).get('type', 'any')}` |")
            else:
                md_lines.append("| *None* | - | - | - |")
            md_lines.append("")

            if ep.request_example:
                md_lines.extend([
                    "#### Request Body Example",
                    "```json",
                    f"{ep.request_example}",
                    "```",
                    "",
                ])

            md_lines.extend([
                "#### Agent Guidance",
                f"> 💡 **Autonomous Decision Rules**: {ep.agent_guidance}",
                "",
                f"> ⚠️ **Failure Recovery Considerations**: {ep.recovery_considerations}",
                "",
                "---",
                "",
            ])

        md_lines.extend([
            "## 4. Agent Usage Rules & Best Practices",
            "",
            "\n".join([f"- {r}" for r in agent_usage_rules]),
            "",
            "## 5. Failure & Recovery Guidelines",
            "",
            "\n".join([f"- {g}" for g in failure_and_recovery_guide]),
            "",
        ])

        markdown_content = "\n".join(md_lines)

        return APIDocumentation(
            integration_id=integration.id,
            title=f"{integration.name} Documentation",
            version=integration.version,
            base_url=integration.base_url,
            overview=integration.description or "API Integration Specification",
            auth_summary="Open sandbox / standard Bearer",
            endpoints=endpoints,
            agent_usage_rules=agent_usage_rules,
            failure_and_recovery_guide=failure_and_recovery_guide,
            markdown_content=markdown_content,
            generated_at=now_str,
        )


documentation_service = DocumentationService()
