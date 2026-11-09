from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser
from app.core.yandex_client import YandexDiskClient, get_yandex_client
from app.crud.charity_project import charity_project_crud
from app.services.yandex_api import create_simple_report


PROJECTS_NOT_FOUND = (
    'Закрытые проекты не найдены, отчёт формировать не из чего.')
REPORT_ERROR = 'Не удалось сформировать отчёт: {error}'

router = APIRouter()


@router.post(
    '/',
    response_model=str,
    dependencies=[Depends(current_superuser)],
    summary='Сформировать отчёт на Яндекс Диске',
    description=(
        'Формирует Excel-отчёт по закрытым проектам, '
        'отсортированным по скорости сбора средств, '
        'загружает его на Яндекс Диск и возвращает публичную ссылку. '
        'Только для суперпользователей.'
    ),
)
async def create_report(
    session: AsyncSession = Depends(get_async_session),
    yandex_client: YandexDiskClient = Depends(get_yandex_client),
) -> str:
    projects = await charity_project_crud.get_projects_by_completion_rate(
        session
    )
    if not projects:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=PROJECTS_NOT_FOUND,
        )
    try:
        return await create_simple_report(projects, yandex_client)
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=REPORT_ERROR.format(error=error),
        )
