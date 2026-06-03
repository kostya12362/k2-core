from typing import Any

from fastapi import FastAPI


def custom_openapi(app: FastAPI) -> FastAPI:
    openapi_schema: dict[str, Any] = app.openapi()
    openapi_schema["servers"] = [{"url": getattr(app, "root_path", None) or "/"}]

    for _path, detail in openapi_schema["paths"].items():
        for method in detail.values():
            if not method.get("parameters"):
                continue

            for parameter in method["parameters"]:
                if parameter["schema"].get("type") == "array":
                    parameter |= {"explode": False, "style": "form"}

    app.openapi_schema = openapi_schema
    return app
