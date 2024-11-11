from fastapi import FastAPI
from .api.endpoints import auth, items
from .db import models
from .db.database import engine
from fastapi.security import OAuth2PasswordBearer

from fastapi.middleware.cors import CORSMiddleware


# Create the database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this list with allowed origins for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Point OAuth2PasswordBearer to /auth/token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# 2. Save the original openapi method
_original_openapi = app.openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    # 3. Generate the original OpenAPI schema
    openapi_schema = _original_openapi()

    # 4. Modify the tokenUrl in the OAuth2PasswordBearer security scheme
    if "components" in openapi_schema:
        if "securitySchemes" in openapi_schema["components"]:
            if "OAuth2PasswordBearer" in openapi_schema["components"]["securitySchemes"]:
                openapi_schema["components"]["securitySchemes"]["OAuth2PasswordBearer"]["flows"]["password"]["tokenUrl"] = "/auth/token"
    
    # 5. Cache the modified schema
    app.openapi_schema = openapi_schema
    return app.openapi_schema

# 6. Override the app's openapi method with the custom one
app.openapi = custom_openapi


# Include Routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(items.router, prefix="/items", tags=["items"])

@app.get("/")
async def read_main():
    return {"msg": "Service Online"}