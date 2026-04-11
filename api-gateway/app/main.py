import os
from typing import Optional

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

load_dotenv()

app = FastAPI(
    title="API Gateway",
    version="1.0.0",
    description="Single entry point for the Smart Food Ordering System microservices.",
)

allowed_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in allowed_origins if origin.strip()] or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SERVICE_MAP = {
    "users": os.getenv("USER_SERVICE_URL", "http://localhost:8001"),
    "products": os.getenv("PRODUCT_SERVICE_URL", "http://localhost:8002"),
    "orders": os.getenv("ORDER_SERVICE_URL", "http://localhost:8003"),
    "payments": os.getenv("PAYMENT_SERVICE_URL", "http://localhost:8004"),
    "reviews": os.getenv("REVIEW_SERVICE_URL", "http://localhost:8005"),
}

METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]


async def forward_request(request: Request, service_prefix: str, path: Optional[str] = "") -> Response:
    base_url = SERVICE_MAP[service_prefix].rstrip("/")
    target_url = f"{base_url}/{service_prefix}"
    if path:
        target_url = f"{target_url}/{path}"

    if request.url.query:
        target_url = f"{target_url}?{request.url.query}"

    headers = {
        key: value
        for key, value in request.headers.items()
        if key.lower() not in {"host", "content-length", "connection"}
    }

    body = await request.body()

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            upstream_response = await client.request(
                method=request.method,
                url=target_url,
                content=body,
                headers=headers,
            )
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail=f"Service '{service_prefix}' is unavailable.") from exc

    excluded_headers = {"content-encoding", "transfer-encoding", "connection"}
    response_headers = {
        key: value
        for key, value in upstream_response.headers.items()
        if key.lower() not in excluded_headers
    }

    return Response(
        content=upstream_response.content,
        status_code=upstream_response.status_code,
        headers=response_headers,
        media_type=upstream_response.headers.get("content-type"),
    )


@app.get("/", tags=["Gateway"])
async def root() -> dict:
    return {
        "message": "API Gateway is running.",
        "routes": {
            "/users": SERVICE_MAP["users"],
            "/products": SERVICE_MAP["products"],
            "/orders": SERVICE_MAP["orders"],
            "/payments": SERVICE_MAP["payments"],
            "/reviews": SERVICE_MAP["reviews"],
        },
        "gateway_swagger": "http://localhost:8000/docs",
    }


@app.api_route("/users", methods=METHODS, include_in_schema=False)
@app.api_route("/users/{path:path}", methods=METHODS, include_in_schema=False)
async def proxy_users(request: Request, path: str = "") -> Response:
    return await forward_request(request, "users", path)


@app.api_route("/products", methods=METHODS, include_in_schema=False)
@app.api_route("/products/{path:path}", methods=METHODS, include_in_schema=False)
async def proxy_products(request: Request, path: str = "") -> Response:
    return await forward_request(request, "products", path)


@app.api_route("/orders", methods=METHODS, include_in_schema=False)
@app.api_route("/orders/{path:path}", methods=METHODS, include_in_schema=False)
async def proxy_orders(request: Request, path: str = "") -> Response:
    return await forward_request(request, "orders", path)


@app.api_route("/payments", methods=METHODS, include_in_schema=False)
@app.api_route("/payments/{path:path}", methods=METHODS, include_in_schema=False)
async def proxy_payments(request: Request, path: str = "") -> Response:
    return await forward_request(request, "payments", path)


@app.api_route("/reviews", methods=METHODS, include_in_schema=False)
@app.api_route("/reviews/{path:path}", methods=METHODS, include_in_schema=False)
async def proxy_reviews(request: Request, path: str = "") -> Response:
    return await forward_request(request, "reviews", path)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # remove generic proxy routes from Swagger
    for path in [
        "/users",
        "/users/{path}",
        "/products",
        "/products/{path}",
        "/orders",
        "/orders/{path}",
        "/payments",
        "/payments/{path}",
        "/reviews",
        "/reviews/{path}",
    ]:
        schema.get("paths", {}).pop(path, None)

    schema.setdefault("paths", {})
    schema.setdefault("components", {})
    schema["components"].setdefault("schemas", {})
    schema.setdefault("tags", [])

    existing_tag_names = {tag["name"] for tag in schema["tags"] if "name" in tag}

    for service_name, service_url in SERVICE_MAP.items():
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(f"{service_url}/openapi.json")
                response.raise_for_status()
                service_schema = response.json()

            # merge paths
            for path, path_item in service_schema.get("paths", {}).items():
                schema["paths"][path] = path_item

            # merge components
            service_components = service_schema.get("components", {})
            for component_type, component_value in service_components.items():
                schema["components"].setdefault(component_type, {})
                if isinstance(component_value, dict):
                    schema["components"][component_type].update(component_value)

            # merge tags
            for tag in service_schema.get("tags", []):
                tag_name = tag.get("name")
                if tag_name and tag_name not in existing_tag_names:
                    schema["tags"].append(tag)
                    existing_tag_names.add(tag_name)

        except Exception:
            # if one service is down, gateway docs will still load with remaining services
            continue

    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = custom_openapi