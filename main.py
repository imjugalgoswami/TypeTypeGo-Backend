from fastapi import FastAPI
from core.security import JWTAuth
from users.apis import router as guest_router, user_router
from auth.apis import router as auth_router
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.authentication import AuthenticationMiddleware


app = FastAPI(title="TypeTypeGo")


app.add_middleware(AuthenticationMiddleware, backend=JWTAuth())

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




app.include_router(guest_router)
app.include_router(user_router)
app.include_router(auth_router)

