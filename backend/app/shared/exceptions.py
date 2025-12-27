from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR


async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "data": None,
            "meta": {"request_id": request.headers.get("x-request-id")},
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "Une erreur interne est survenue.",
            },
        },
    )
