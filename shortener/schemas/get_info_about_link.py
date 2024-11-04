from datetime import datetime

from pydantic import BaseModel, HttpUrl


class GetInfoAboutLinkResponse(BaseModel):
    short_url: HttpUrl
    long_url: HttpUrl
    number_of_clicks: int
    dt_created: datetime

    class Config:
        from_attributes = True
