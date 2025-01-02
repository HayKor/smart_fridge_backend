from fastapi import APIRouter, Response

from smart_fridge.core.dependencies.fastapi import (
    ClientHostDependency,
    DatabaseDependency,
    EncryptorDependency,
    RedisDependency,
    RefreshTokenDependency,
    TokenDataDependency,
    UserAgentDependency,
)
from smart_fridge.lib.db import auth as auth_db, auth_session as auth_session_db
from smart_fridge.lib.schemas.auth import TokenCreateSchema, TokenSchema


router = APIRouter(tags=["auth"], prefix="/auth")


@router.post("/login", response_model=TokenSchema)
async def login(
    response: Response,
    db: DatabaseDependency,
    redis: RedisDependency,
    encryptor: EncryptorDependency,
    user_agent: UserAgentDependency,
    client_host: ClientHostDependency,
    schema: TokenCreateSchema,
) -> TokenSchema:
    result = await auth_db.create_token(db, redis, encryptor, client_host, user_agent, schema)
    response.set_cookie(
        "refresh_token", result.refresh_token, httponly=True, max_age=result.refresh_token_expires_in * 60 * 60 * 24
    )
    return result


@router.post("/refresh_tokens", response_model=TokenSchema)
async def refresh_tokens(
    response: Response,
    db: DatabaseDependency,
    redis: RedisDependency,
    encryptor: EncryptorDependency,
    user_agent: UserAgentDependency,
    client_host: ClientHostDependency,
    refresh_token: RefreshTokenDependency,
) -> TokenSchema:
    result = await auth_db.refresh_token(db, redis, encryptor, client_host, user_agent, refresh_token)
    response.set_cookie(
        "refresh_token", result.refresh_token, httponly=True, max_age=result.refresh_token_expires_in * 60 * 60 * 24
    )
    return result


@router.delete("/logout", status_code=204)
async def logout(
    response: Response,
    db: DatabaseDependency,
    redis: RedisDependency,
    token_data: TokenDataDependency,
) -> None:
    response.delete_cookie("refresh_token")
    return await auth_session_db.delete_auth_session(db, redis, token_data.session_id, token_data.user_id)
