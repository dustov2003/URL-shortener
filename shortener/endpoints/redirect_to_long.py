from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Path, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from shortener.db.connection import get_session
from shortener.db.models import UrlStorage


api_router = APIRouter(tags=["Url"])


@api_router.get(
    "/{short_code}",
    response_class=RedirectResponse,
    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    responses={status.HTTP_404_NOT_FOUND: {"description": "URL `request.url` doesn't exist"}},
)
async def get_long_url(
    request: Request,
    short_code: str = Path(...),
    session: AsyncSession = Depends(get_session),
):
    """
    Логика работы ручки:

    Проверяем, что у нас есть short_code в базе:
      - если он уже есть, то совершаем редирект на длинный урл + увеличиваем счетчик переходов на 1
      - если нет, то кидаем ошибку;
    """
    current_time = datetime.now()
    query = delete(UrlStorage).where(current_time > UrlStorage.dt_deleted)
    await session.execute(query)
    await session.commit()
    current_time = datetime.now()
    db_url_query = (
        select(UrlStorage)
        .where(UrlStorage.short_url == short_code, current_time < UrlStorage.dt_deleted)
        .with_for_update()
    )
    db_url = await session.scalar(db_url_query)
    if db_url:
        update_query = (
            update(UrlStorage)
            .where(UrlStorage.short_url == short_code)
            .values(number_of_clicks=db_url.number_of_clicks + 1)
        )
        await session.execute(update_query)
        await session.commit()
        return RedirectResponse(db_url.long_url)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"URL '{request.url}' doesn't exist")
