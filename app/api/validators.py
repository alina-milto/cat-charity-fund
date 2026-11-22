"""Request checks that respond with an HTTP error when they fail."""

from http import HTTPStatus
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charity_project import charity_project_crud
from app.models.charity_project import CharityProject


async def check_name_duplicate(
    project_name: str,
    session: AsyncSession,
    project_id: Optional[int] = None,
) -> None:
    """Respond 400 if another project already has this name.

    ``project_id`` is the project being updated: keeping its own name
    is allowed.
    """
    existing_id = await charity_project_crud.get_project_id_by_name(
        project_name, session
    )
    if existing_id is not None and existing_id != project_id:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='A project with this name already exists.',
        )


async def check_charity_project_exists(
    project_id: int,
    session: AsyncSession,
) -> CharityProject:
    """Return the project or respond 404."""
    charity_project = await charity_project_crud.get(project_id, session)
    if charity_project is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Project not found.',
        )
    return charity_project


def check_project_is_open(
    charity_project: CharityProject,
) -> None:
    """Respond 400 if the project is already closed."""
    if charity_project.fully_invested:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='A closed project cannot be edited.',
        )


def check_full_amount_not_less_than_invested(
    charity_project: CharityProject,
    new_full_amount: int,
) -> None:
    """Respond 400 if the new amount is less than already invested."""
    if new_full_amount < charity_project.invested_amount:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=(
                'full_amount cannot be less than the amount '
                'already invested.'
            ),
        )


def check_project_has_no_investments(
    charity_project: CharityProject,
) -> None:
    """Respond 400 if money has already been invested in the project."""
    if charity_project.invested_amount > 0:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='The project has received money and cannot be deleted.',
        )
