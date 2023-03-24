from datetime import datetime

from pydantic import BaseModel


class Link(BaseModel):
    url: str


class ShortLink(BaseModel):
    url: str


class Links(BaseModel):
    links: list[Link]


class ShortLinks(BaseModel):
    links: list[ShortLink]


class ClientData(BaseModel):
    ip: str
    user_agent: str

    def __str__(self):
        return f"[{self.ip}]: {self.user_agent}"


class ClickData(BaseModel):
    visited: datetime
    client_data: str


class ClickDataShortResponse(BaseModel):
    count: int


class ClickDataFullResponse(BaseModel):
    count: int
    clicks: list[ClickData]


class DbStatus(BaseModel):
    status: str
