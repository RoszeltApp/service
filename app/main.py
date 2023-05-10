from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from app.libs.jwt import ValidationError
from app.routes.ProductRoutes import product_router
from app.routes.UserRoutes import user_router
from fastapi import Request

app = FastAPI()

origins = [
    'http://localhost',
    'http://172.17.0.1',
    'http://localhost:5173',
    'http://127.0.0.1:5173/'

]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=exc.status_code,
        content={'err': True, 'msg': exc.msg}
    )


app.include_router(product_router)
app.include_router(user_router)
