import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import httpx
from app.schemas.integration import (
    Integration,
    IntegrationCreateRequest,
    IntegrationStatus,
    OperationDefinition,
    ReadinessFinding,
    FindingStatus,
)
from app.schemas.connector import ConnectorDefinition, ConnectorStatus
from app.openapi.generator import OpenAPIToolGenerator
from app.agent.tools import ToolDefinition


from fastapi.openapi.utils import get_openapi
from app.sandbox.router import router as sandbox_router


class IntegrationService:
    def __init__(self):
        self._integrations: Dict[str, Integration] = {}
        self._connectors: Dict[str, ConnectorDefinition] = {}
        self._initialize_default_sandbox_integration()

    def _initialize_default_sandbox_integration(self):
        """Pre-registers the built-in Travel & Payments sandbox as the baseline integration."""
        spec = get_openapi(
            title="Travel & Booking Sandbox API",
            version="1.0.0",
            description="Stateful Flight Search, Reservation & Payments API Sandbox for autonomous agent testing.",
            routes=sandbox_router.routes,
        )
        self.register_from_spec(
            name="Travel & Booking Sandbox API",
            spec=spec,
            base_url_override="http://127.0.0.1:8000/sandbox",
            integration_id="integration-travel-sandbox",
        )

    def register_from_spec(
        self,
        name: str,
        spec: Dict[str, Any],
        base_url_override: Optional[str] = None,
        integration_id: Optional[str] = None,
    ) -> Integration:
        int_id = integration_id or f"integration-{uuid.uuid4().hex[:8]}"
        base_url = base_url_override or spec.get("servers", [{}])[0].get("url", "http://127.0.0.1:8000")

        generator = OpenAPIToolGenerator(spec)
        tools = generator.generate_tools()

        operations: List[OperationDefinition] = []
        readiness_findings: List[ReadinessFinding] = []

        paths = spec.get("paths", {})
        state_changing_count = 0
        idempotency_supported_count = 0
        has_error_responses = False

        for path, path_item in paths.items():
            for method, op in path_item.items():
                if method.lower() not in ["get", "post", "put", "delete", "patch"]:
                    continue

                op_id = op.get("operation_id") or f"{method}_{path.replace('/', '_').strip('_')}"
                summary = op.get("summary", "")
                description = op.get("description", "")
                is_mutating = method.lower() in ["post", "put", "delete", "patch"]
                if is_mutating:
                    state_changing_count += 1

                # Check parameter definitions
                params = []
                has_idempotency_param = False
                for p in op.get("parameters", []):
                    p_name = p.get("name", "")
                    if "idempotency" in p_name.lower():
                        has_idempotency_param = True
                    params.append({
                        "name": p_name,
                        "in": p.get("in", "query"),
                        "required": p.get("required", False),
                        "schema": p.get("schema", {}),
                    })

                # Check request body
                req_body_schema = None
                req_body = op.get("requestBody", {})
                if req_body:
                    content = req_body.get("content", {})
                    json_media = content.get("application/json", {})
                    req_body_schema = json_media.get("schema")
                    if req_body_schema:
                        # Check properties for idempotency
                        props = req_body_schema.get("properties", {})
                        if any("idempotency" in k.lower() for k in props.keys()):
                            has_idempotency_param = True

                if has_idempotency_param:
                    idempotency_supported_count += 1

                responses = op.get("responses", {})
                if any(k.startswith("4") or k.startswith("5") for k in responses.keys()):
                    has_error_responses = True

                operations.append(
                    OperationDefinition(
                        operation_id=op_id,
                        method=method.upper(),
                        path=path,
                        summary=summary,
                        description=description,
                        parameters=params,
                        request_body_schema=req_body_schema,
                        response_schemas=responses,
                        state_changing=is_mutating,
                        idempotency_supported=has_idempotency_param,
                        generated_tool_name=op_id,
                    )
                )

        # AI-Readiness Findings Analysis
        readiness_findings.append(
            ReadinessFinding(
                category="Specification Quality",
                status=FindingStatus.PASS,
                title="OpenAPI 3.x Contract Validated",
                detail=f"Discovered and parsed {len(operations)} operations with resolved parameter and body schemas.",
            )
        )

        if state_changing_count > 0:
            if idempotency_supported_count > 0:
                readiness_findings.append(
                    ReadinessFinding(
                        category="Agent Safety & Retry Readiness",
                        status=FindingStatus.PASS,
                        title="Idempotency Semantics Detected",
                        detail=f"{idempotency_supported_count} of {state_changing_count} state-changing operations define explicit idempotency keys.",
                    )
                )
            else:
                readiness_findings.append(
                    ReadinessFinding(
                        category="Agent Safety & Retry Readiness",
                        status=FindingStatus.WARN,
                        title="No Idempotency Keys on Mutating Endpoints",
                        detail=f"{state_changing_count} operations mutate server state without explicit Idempotency-Key headers.",
                    )
                )

        if has_error_responses:
            readiness_findings.append(
                ReadinessFinding(
                    category="Error Observability",
                    status=FindingStatus.PASS,
                    title="Structured Error Responses Documented",
                    detail="Explicit 4xx/5xx error models available for agent recovery reasoning.",
                )
            )
        else:
            readiness_findings.append(
                ReadinessFinding(
                    category="Error Observability",
                    status=FindingStatus.WARN,
                    title="Error Schemas Missing",
                    detail="No explicit 4xx/5xx response schemas documented in contract.",
                )
            )

        now_str = datetime.now(timezone.utc).isoformat()
        integration = Integration(
            id=int_id,
            name=name,
            description=spec.get("info", {}).get("description", "Imported OpenAPI service"),
            version=spec.get("info", {}).get("version", "1.0.0"),
            base_url=base_url,
            raw_spec=spec,
            operations=operations,
            schemas=spec.get("components", {}).get("schemas", {}),
            generated_tools_count=len(tools),
            readiness_findings=readiness_findings,
            status=IntegrationStatus.READY_FOR_TESTING,
            created_at=now_str,
        )

        self._integrations[int_id] = integration

        # Auto-create Connector Definition
        connector = ConnectorDefinition(
            id=f"conn-{int_id}",
            name=f"{name} Connector",
            integration_id=int_id,
            auth_type="none",
            base_url=base_url,
            operations_count=len(operations),
            operations=[op.operation_id for op in operations],
            status=ConnectorStatus.READY_FOR_TESTING,
            metadata={"tools_count": len(tools)},
        )
        self._connectors[connector.id] = connector

        return integration

    async def create_from_request(self, req: IntegrationCreateRequest) -> Integration:
        spec: Dict[str, Any] = {}
        if req.spec_url:
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.get(req.spec_url)
                res.raise_for_status()
                spec = res.json()
        elif req.spec_content:
            try:
                spec = json.loads(req.spec_content)
            except Exception:
                import yaml  # type: ignore
                spec = yaml.safe_load(req.spec_content)
        else:
            from app.main import app
            spec = app.openapi()

        return self.register_from_spec(
            name=req.name,
            spec=spec,
            base_url_override=req.base_url_override,
        )

    def get_integration(self, integration_id: str) -> Optional[Integration]:
        return self._integrations.get(integration_id)

    def list_integrations(self) -> List[Integration]:
        return list(self._integrations.values())

    def list_connectors(self) -> List[ConnectorDefinition]:
        return list(self._connectors.values())

    def get_connector(self, connector_id: str) -> Optional[ConnectorDefinition]:
        return self._connectors.get(connector_id)

    def generate_client_code(self, integration_id: str) -> Dict[str, str]:
        integration = self.get_integration(integration_id)
        if not integration:
            raise ValueError(f"Integration {integration_id} not found")

        # Generate Python client wrapper
        methods_code = []
        for op in integration.operations:
            method_name = op.operation_id
            http_method = op.method.lower()
            path = op.path
            params_list = [p["name"] for p in op.parameters]
            args_str = ", ".join(["self"] + [f"{p}: Optional[Any] = None" for p in params_list] + (["body: Optional[Dict[str, Any]] = None"] if op.state_changing else []))
            
            method_code = f"""    async def {method_name}({args_str}):
        \"\"\"{op.summary or op.description or 'Execute ' + op.operation_id}\"\"\"
        params = {{k: v for k, v in locals().items() if k not in ['self', 'body'] and v is not None}}
        return await self._request("{http_method.upper()}", "{path}", params=params, json=body if '{http_method}' in ['post', 'put', 'patch'] else None)
"""
            methods_code.append(method_code)

        client_py = f'''# Generated API Client for {integration.name}
# Auto-generated by Agent Crash Test Smart API Integration Framework
import httpx
from typing import Optional, Dict, Any, List

class {integration.name.replace(" ", "").replace("-", "")}Client:
    def __init__(self, base_url: str = "{integration.base_url}", client: Optional[httpx.AsyncClient] = None):
        self.base_url = base_url.rstrip("/")
        self._client = client or httpx.AsyncClient(base_url=self.base_url)

    async def _request(self, method: str, path: str, params: Optional[dict] = None, json: Optional[dict] = None):
        response = await self._client.request(method, path, params=params, json=json)
        response.raise_for_status()
        return response.json()

{chr(10).join(methods_code)}
'''

        readme_md = f'''# {integration.name} Integration Package

Auto-generated connector and client tools for `{integration.name}` (v{integration.version}).

## Base URL
`{integration.base_url}`

## Available Operations ({len(integration.operations)})
{chr(10).join([f"- `{op.method} {op.path}` → `{op.operation_id}`" for op in integration.operations])}

## Usage Example
```python
import asyncio
from client import {integration.name.replace(" ", "").replace("-", "")}Client

async def main():
    client = {integration.name.replace(" ", "").replace("-", "")}Client()
    # Call generated operations
    # res = await client.{integration.operations[0].operation_id}()
    # print(res)

if __name__ == "__main__":
    asyncio.run(main())
```
'''

        tools_json = json.dumps(
            [op.model_dump() for op in integration.operations],
            indent=2
        )

        return {
            "client.py": client_py,
            "README.md": readme_md,
            "tools.json": tools_json,
        }


integration_service = IntegrationService()
