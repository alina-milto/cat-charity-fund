"""Database operations for charity projects."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.charity_project import CharityProject


class CRUDCharityProject(CRUDBase):
    """Database operations for charity projects."""

    async def get_project_id_by_name(
        self,
        project_name: str,
        session: AsyncSession,
    ):
        """Return the id of the project with this name or None."""
        project_id = await session.execute(
            select(CharityProject.id).where(
                CharityProject.name == project_name
            )
        )
        return project_id.scalars().first()

    async def get_projects_by_completion_rate(
        self,
        session: AsyncSession,
    ) -> list[CharityProject]:
        """Return closed projects, the fastest funded first."""
        projects = await session.execute(
            select(CharityProject).where(
                CharityProject.fully_invested.is_(True)
            )
        )
        projects = projects.scalars().all()
        return sorted(
            projects,
            key=lambda project: project.close_date - project.create_date,
        )


charity_project_crud = CRUDCharityProject(CharityProject)
