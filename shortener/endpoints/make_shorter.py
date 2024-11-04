from datetime import datetime, timedelta
from random import choice
from string import ascii_uppercase, digits

from fastapi import APIRouter, Body, Depends
from fastapi.exceptions import HTTPException
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from shortener import utils
from shortener.db.connection import get_session
from shortener.db.models import UrlStorage
from shortener.schemas import MakeShorterRequest, MakeShorterResponse


time_to_second = {"SECONDS": 1, "MINUTES": 60, "HOURS": 3600, "DAYS": 86400}

api_router = APIRouter(tags=["Url"])


async def get_short(session: AsyncSession) -> tuple[str, str]:
    while True:
        suffix = "".join(choice(ascii_uppercase + digits) for _ in range(5))
        exist_query = select(exists().where(UrlStorage.short_url == suffix))
        exist = await session.scalar(exist_query)
        if not exist:
            break
    short_url = utils.url_from_suffix(suffix)
    return short_url, suffix


@api_router.post(
    "/make_shorter",
    response_model=MakeShorterResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": "Сайт с этим URL не существует или статус-код запроса >= 400",
        },
    },
)
async def make_shorter(
    model: MakeShorterRequest = Body(),
    session: AsyncSession = Depends(get_session),
):
    """
    Логика работы ручки:

    Проверяем, что у нас еще нет сокращенного варианта урла для переданного длинного адреса
      - если он уже есть, то возвращаем его
      - если еще нет:
          1) Подбираем маленький суффикс, которого еще нет в базе;
          2) Сохраняем этот суффикс в базу;
          3) На основе этого суффикса и текущих настроек приложения генерируем полноценный урл;
          4) Возвращаем результат работы ручки: урл и secret_key для запроса дополнительной информации.
    """

    current_time = datetime.now()
    db_url_query = select(UrlStorage).where(UrlStorage.long_url == str(model.url), current_time < UrlStorage.dt_deleted)
    db_url = await session.scalar(db_url_query)

    exist = db_url is not None

    valid_site, message = await utils.check_website_exist(str(model.url))
    seconds_to_live = (
        time_to_second[model.time_to_live_unit] * model.time_to_live
        if (model.time_to_live_unit in time_to_second and model.time_to_live_unit is not None)
        else 86400
    )
    vip_key_is_invalid = False
    if model.vip_key is not None:
        query = select(UrlStorage).where(str(model.vip_key) == UrlStorage.short_url)
        query_res = await session.scalar(query)
        if query_res is not None:
            vip_key_is_invalid = True

    if not valid_site or seconds_to_live > 3600 * 48 or vip_key_is_invalid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )

    if exist:
        db_url.short_url = utils.url_from_suffix(db_url.short_url)
        return MakeShorterResponse.from_orm(db_url)

    suffix = model.vip_key
    if suffix is None:
        _, suffix = await get_short(session)

    new_url = UrlStorage(
        long_url=str(model.url), short_url=suffix, dt_deleted=datetime.now() + timedelta(seconds=seconds_to_live)
    )

    session.add(new_url)
    await session.commit()
    await session.refresh(new_url)
    new_url.short_url = utils.url_from_suffix(suffix)
    return MakeShorterResponse.from_orm(new_url)
