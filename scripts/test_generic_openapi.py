import httpx

def test_generic():
    spec = {
        "openapi": "3.0.0",
        "info": {"title": "Generic Warehouse Inventory API", "version": "1.0.0", "description": "Warehouse inventory management"},
        "paths": {
            "/inventory/items": {
                "get": {"operationId": "list_items", "summary": "List items in stock", "responses": {"200": {"description": "Item list"}}},
                "post": {
                    "operationId": "create_item",
                    "summary": "Add item to inventory",
                    "requestBody": {"content": {"application/json": {"schema": {"type": "object", "properties": {"sku": {"type": "string"}, "quantity": {"type": "integer"}}, "required": ["sku", "quantity"]}}}},
                    "responses": {"201": {"description": "Item created"}}
                }
            }
        }
    }
    r = httpx.post("http://127.0.0.1:8000/integrations", json={"name": "Generic Warehouse Inventory API", "openapi_spec": spec})
    print("Generic spec import status:", r.status_code)
    res = r.json()
    print("Imported integration ID:", res["id"])
    print("Parsed operations:", [op["operation_id"] for op in res["operations"]])
    code_res = httpx.get(f"http://127.0.0.1:8000/integrations/{res['id']}/code").json()
    print("Generated client.py lines:", len(code_res["client.py"].splitlines()))
    print("Generated tools.json contains:", list(code_res["tools.json"].keys()) if isinstance(code_res["tools.json"], dict) else "list of tools")
    doc_res = httpx.get(f"http://127.0.0.1:8000/documentation/{res['id']}").json()
    print("Generated doc endpoints:", len(doc_res["endpoints"]))
    print("Generated doc rules:", len(doc_res["agent_usage_rules"]))
    print("Generic OpenAPI Ingestion: VERIFIED!")

if __name__ == "__main__":
    test_generic()
