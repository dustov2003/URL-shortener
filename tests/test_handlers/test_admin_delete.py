from uuid import uuid4

import pytest
from sqlalchemy import select
from starlette import status

from shortener.db.models import UrlStorage


class TestAdminInfoHandler:
    @staticmethod
    def get_url(short_code: str) -> str:
        return f"/api/v1/admin/{short_code}"

    @pytest.mark.parametrize(
        "func, base_must_be_empty",
        (
            (lambda x: x, True),
            (lambda x: str(uuid4()), False),
        ),
    )
    async def test_not_found(self, client, data_sample, func, base_must_be_empty, session):
        correct_secret_key = data_sample.secret_key
        response = await client.delete(url=self.get_url(func(correct_secret_key)))
        assert response.status_code == status.HTTP_204_NO_CONTENT

        if base_must_be_empty:
            query = select(UrlStorage).where()
            assert len((await session.scalars(query)).all()) == 0
