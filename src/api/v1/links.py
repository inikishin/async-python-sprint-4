import logging
from typing import Annotated, Optional, Union

from fastapi import APIRouter, Depends, Request, Query

from models.links import (
    ClickDataFullResponse,
    ClickDataShortResponse,
    ClientData,
    DbStatus,
    Link,
    Links,
    ShortLink,
)
from services.link import BaseLinkService, get_link_service

logger = logging.getLogger(__name__)
TAGS = ["short links"]
router = APIRouter()


@router.post(
    "/",
    name="Получить сокращенный url",
    tags=TAGS,
    description="Получить сокращённый вариант переданного URL",
)
async def post_link(
    link: Link,
    link_service: BaseLinkService = Depends(get_link_service),
) -> ShortLink:
    short_link = await link_service.get_short_url(link)
    return short_link


@router.post(
    "/shorten",
    name="Получить список сокращённых вариантов переданных url",
    tags=TAGS,
    description="Получить список сокращённых вариантов переданных URL",
)
async def post_link_shorten(
    links: Links,
    link_service: BaseLinkService = Depends(get_link_service),
):
    return await link_service.get_short_urls(links)


@router.get(
    "/{shorten_url_id}",
    name="Получить оригинальный url",
    tags=TAGS,
    description="Вернуть оригинальный URL",
)
async def get_link(
    shorten_url_id: str,
    request: Request,
    link_service: BaseLinkService = Depends(get_link_service),
) -> Optional[Link]:
    client_data = ClientData(
        ip=f"{request.client.host}:{request.client.port}",
        user_agent=request.headers.get("user-agent"),
    )
    return await link_service.get_link(shorten_url_id, client_data)


# GET /<shorten-url-id>/status?[full-info]&[max-result=10]&[offset=0]
@router.get(
    "/{shorten-url-id}/status",
    name="Получить статус по url",
    tags=TAGS,
    description="Вернуть статус по URL",
)
async def get_link_status(
    shorten_url_id: str,
    full_info: bool,
    max_result: Annotated[int, Query(gt=1)],
    offset: Annotated[int, Query(gt=0)],
    link_service: BaseLinkService = Depends(get_link_service),
) -> Union[ClickDataFullResponse, ClickDataShortResponse]:
    result = await link_service.get_status(shorten_url_id, max_result, offset)

    if full_info:
        resp = ClickDataFullResponse(count=len(result), clicks=result)
    else:
        resp = ClickDataShortResponse(count=len(result))
    return resp


@router.get(
    "/ping",
    name="Статус доступности бд",
    tags=TAGS,
    description="Возвращает информацию о статусе доступности БД",
)
async def get_ping(
    link_service: BaseLinkService = Depends(get_link_service),
) -> DbStatus:
    ping = await link_service.get_ping()
    if ping:
        status = DbStatus(status="OK")
    else:
        status = DbStatus(status="DOWN")
    return status


@router.delete(
    "/{shorten-url-id}",
    name="Удаление сохранённого url",
    tags=TAGS,
    description="Удаление сохранённого URL",
)
async def delete_link(
    shorten_url_id: str,
    link_service: BaseLinkService = Depends(get_link_service),
):
    return await link_service.delete_link(shorten_url_id)
