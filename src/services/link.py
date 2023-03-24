import uuid
from abc import ABC, abstractmethod
from typing import Optional

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.config import app_config
from db.config import get_session
from db.models.link import Link as LinkDbModel
from db.models.link import LinkClick as LinkClickDbModel
from models.links import ClickData, ClientData, Link, Links, ShortLink, ShortLinks


class BaseLinkService(ABC):
    @abstractmethod
    async def get_short_url(self, link: Link) -> ShortLink:
        raise NotImplementedError

    @abstractmethod
    async def get_short_urls(self, links: Links) -> ShortLinks:
        raise NotImplementedError

    @abstractmethod
    async def get_link(self, short_url: str, client_data: ClientData):
        raise NotImplementedError

    @abstractmethod
    async def delete_link(self, short_url: str):
        raise NotImplementedError

    @abstractmethod
    async def get_status(
        self, short_url: str, max_result: int, offset: int
    ) -> list[ClickData]:
        raise NotImplementedError

    @abstractmethod
    async def get_ping(self):
        raise NotImplementedError


class LinkService(BaseLinkService):
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def get_short_url(self, link: Link) -> ShortLink:
        return await self.__add_link(link)

    async def get_short_urls(self, links: Links) -> ShortLinks:
        result = []
        for link in links.links:
            _ = await self.__add_link(link)
            result.append(_)
        return ShortLinks(links=result)

    async def get_link(self, short_url: str, client_data: ClientData) -> Optional[Link]:
        query = select(LinkDbModel).where(
            (LinkDbModel.short_link == short_url)
            & (LinkDbModel.is_deleted == False)  # noqa E712
        )
        result = await self.session.execute(query)
        result = result.scalar_one_or_none()
        if not result:
            return None

        await self.__add_click(result, client_data)

        return Link(url=result.link)

    async def delete_link(self, short_url: str) -> None:
        query = select(LinkDbModel).where(LinkDbModel.short_link == short_url)
        result = await self.session.execute(query)
        result = result.scalar_one_or_none()
        if not result:
            return None

        result.is_deleted = True
        self.session.add(result)
        await self.session.commit()

    async def get_status(
        self, short_url: str, max_result: int = 10, offset: int = 0
    ) -> list[ClickData]:
        query = select(LinkDbModel).where(
            (LinkDbModel.short_link == short_url)
            & (LinkDbModel.is_deleted == False)  # noqa E712
        )
        link = await self.session.execute(query)
        link = link.scalar_one_or_none()
        if not link:
            return []

        query = (
            select(LinkClickDbModel)
            .where(LinkClickDbModel.link == link)
            .order_by(LinkClickDbModel.created_at.desc())
            .offset(offset)
            .limit(max_result)
        )
        clicks = await self.session.execute(query)
        clicks = clicks.scalars().all()

        return [
            ClickData(visited=click.created_at, client_data=click.client)
            for click in clicks
        ]

    async def get_ping(self) -> bool:
        is_database_working = True

        try:
            await self.session.execute("SELECT 1")
        except Exception:
            is_database_working = False

        return is_database_working

    async def __add_link(self, link: Link) -> ShortLink:
        link = LinkDbModel(
            link=link.url,
            short_link=str(uuid.uuid4()),
        )
        self.session.add(link)
        await self.session.commit()
        return ShortLink(url=f"{app_config.url_prefix}{link.short_link}")

    async def __add_click(self, link: LinkDbModel, client_data: ClientData):
        record = LinkClickDbModel(
            link=link,
            client=str(client_data),
        )
        self.session.add(record)
        await self.session.commit()


def get_link_service(
    session: AsyncSession = Depends(get_session),
) -> BaseLinkService:
    return LinkService(session)
