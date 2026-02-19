from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.logger import log
from app.exceptions import BaseAppError
from app.majors.router import router as router_majors
from app.students.router import router as router_students


app = FastAPI()


@app.exception_handler(BaseAppError)
async def app_exception_handler(request: Request, exc: BaseAppError):
    log.error(f"Ошибка {exc.status_code}: {exc.detail}", exc_info=True)
    return JSONResponse(
        status_code=getattr(exc, "status_code", 500),
        content={"detail": exc.detail}
    )

app.include_router(router_students)
app.include_router(router_majors)
