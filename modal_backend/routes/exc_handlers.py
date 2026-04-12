import starlette.requests
from starlette.responses import JSONResponse

from modal_backend.exceptions import (
    AlreadyExists,
    ForbiddenAction,
    ObjectNotFound,
    UpdateError,
)
from modal_backend.schemas.base import StatusResponseModel

from .base import app


@app.exception_handler(ObjectNotFound)
async def not_found_handler(req: starlette.requests.Request, exc: ObjectNotFound):
    return JSONResponse(
        content=StatusResponseModel(status="Error", message=exc.eng, ru=exc.ru).model_dump(), status_code=404
    )


@app.exception_handler(AlreadyExists)
async def already_exists_handler(req: starlette.requests.Request, exc: AlreadyExists):
    return JSONResponse(
        content=StatusResponseModel(status="Error", message=exc.eng, ru=exc.ru).model_dump(), status_code=409
    )


@app.exception_handler(ForbiddenAction)
async def forbidden_action_handler(req: starlette.requests.Request, exc: ForbiddenAction):
    return JSONResponse(
        content=StatusResponseModel(status="Error", message=exc.eng, ru=exc.ru).model_dump(), status_code=403
    )


@app.exception_handler(UpdateError)
async def update_error_handler(req: starlette.requests.Request, exc: UpdateError):
    return JSONResponse(
        content=StatusResponseModel(status="Error", message=exc.eng, ru=exc.ru).model_dump(), status_code=409
    )
