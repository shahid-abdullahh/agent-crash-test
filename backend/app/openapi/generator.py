from typing import Dict, Any, List, Optional
import copy


def resolve_ref(schema: Dict[str, Any], openapi_spec: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively resolve $ref pointers within an OpenAPI specification."""
    if not isinstance(schema, dict):
        return schema

    if "$ref" in schema:
        ref_path = schema["$ref"].lstrip("#/").split("/")
        target = openapi_spec
        for part in ref_path:
            target = target.get(part, {})
        return resolve_ref(copy.deepcopy(target), openapi_spec)

    resolved = {}
    for key, value in schema.items():
        if isinstance(value, dict):
            resolved[key] = resolve_ref(value, openapi_spec)
        elif isinstance(value, list):
            resolved[key] = [resolve_ref(item, openapi_spec) if isinstance(item, dict) else item for item in value]
        else:
            resolved[key] = value
    return resolved


class OpenAPIToolGenerator:
    """Generates standardized ToolDefinitions from an OpenAPI 3.x specification."""

    def __init__(self, openapi_spec: Dict[str, Any]):
        self.spec = openapi_spec

    def generate_tools(self, path_prefix: Optional[str] = "/sandbox") -> List["ToolDefinition"]:
        from app.agent.tools import ToolDefinition

        tools: List[ToolDefinition] = []
        paths = self.spec.get("paths", {})

        for path, path_item in paths.items():
            if path_prefix and not path.startswith(path_prefix):
                continue

            for method in ["get", "post", "put", "delete", "patch"]:
                if method not in path_item:
                    continue

                operation = path_item[method]
                # Determine tool name from operationId or operation_id or fallback to method_path
                tool_name = operation.get("operationId") or operation.get("operation_id") or f"{method}_{path.strip('/').replace('/', '_').replace('{', '').replace('}', '')}"

                description = operation.get("description") or operation.get("summary") or f"{method.upper()} {path}"

                # Extract Path and Query parameters
                path_params: List[str] = []
                query_params: List[str] = []
                properties: Dict[str, Any] = {}
                required: List[str] = []

                for param in operation.get("parameters", []):
                    param_resolved = resolve_ref(param, self.spec)
                    name = param_resolved.get("name")
                    param_in = param_resolved.get("in")
                    schema = param_resolved.get("schema", {"type": "string"})
                    desc = param_resolved.get("description", "")

                    if param_in == "path":
                        path_params.append(name)
                    elif param_in == "query":
                        query_params.append(name)

                    prop_def = copy.deepcopy(schema)
                    if desc:
                        prop_def["description"] = desc
                    properties[name] = prop_def

                    if param_resolved.get("required"):
                        required.append(name)

                # Extract Request Body parameters (for POST/PUT)
                request_body_schema = None
                request_body = operation.get("requestBody")
                if request_body:
                    rb_resolved = resolve_ref(request_body, self.spec)
                    content = rb_resolved.get("content", {})
                    json_content = content.get("application/json", {})
                    body_schema = json_content.get("schema", {})
                    if body_schema:
                        resolved_body_schema = resolve_ref(body_schema, self.spec)
                        request_body_schema = resolved_body_schema
                        body_props = resolved_body_schema.get("properties", {})
                        for prop_name, prop_schema in body_props.items():
                            properties[prop_name] = prop_schema
                        body_required = resolved_body_schema.get("required", [])
                        for req_prop in body_required:
                            if req_prop not in required:
                                required.append(req_prop)

                parameters_schema = {
                    "type": "object",
                    "properties": properties,
                }
                if required:
                    parameters_schema["required"] = required

                tool_def = ToolDefinition(
                    name=tool_name,
                    description=description,
                    method=method.upper(),
                    path=path,
                    parameters=parameters_schema,
                    path_param_names=path_params,
                    query_param_names=query_params,
                    request_body_schema=request_body_schema,
                )
                tools.append(tool_def)

        return tools
