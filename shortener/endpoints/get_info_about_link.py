from datetime import datetime

from fastapi import APIRouter, Depends, Path
from fastapi.exceptions import HTTPException
from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from shortener.db.connection import get_session
from shortener.db.models import UrlStorage
from shortener.schemas import GetInfoAboutLinkResponse
from shortener.utils import url_from_suffix


api_router = APIRouter(tags=["Url"])


@api_router.get(
    "/admin/{secret_key}",
    status_code=status.HTTP_200_OK,
    response_model=GetInfoAboutLinkResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Link with this secret key is not found.",
        }
    },
)
async def get_info_about_link(
    secret_key: UUID4 = Path(...),
    session: AsyncSession = Depends(get_session),
):
    current_time = datetime.now()
    db_url_query = select(UrlStorage).where(UrlStorage.secret_key == secret_key, current_time < UrlStorage.dt_deleted)
    db_url = await session.scalar(db_url_query)
    if db_url is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link with this secret key is not found.",
        )
    db_url.short_url = url_from_suffix(db_url.short_url)
    return GetInfoAboutLinkResponse.from_orm(db_url)
