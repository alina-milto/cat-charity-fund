import io
from datetime import datetime, timedelta, timezone

import xlsxwriter

from app.core.config import settings
from app.core.yandex_client import YandexDiskClient
from app.models.charity_project import CharityProject


SECONDS_IN_HOUR = 3600
SECONDS_IN_MINUTE = 60

SHEET_NAME = 'Отчёт'
FILE_NAME = 'Отчёт_от_{date}.xlsx'
REPORT_TITLE = 'Отчёт от {date}'
TABLE_HEADERS = ('Название проекта', 'Время сбора', 'Описание')
TOTAL_LABEL = 'Всего проектов:'
COLUMN_WIDTHS = (35, 20, 60)
HEADER_BG_COLOR = '#2F75B5'
TITLE_ROW = 0
HEADERS_ROW = 1
FIRST_DATA_ROW = 2


def format_time_delta(delta: timedelta) -> str:
    days = delta.days
    hours = delta.seconds // SECONDS_IN_HOUR
    minutes = (delta.seconds % SECONDS_IN_HOUR) // SECONDS_IN_MINUTE
    if days:
        return f'{days} дн. {hours} ч.'
    return f'{hours} ч. {minutes} мин.'


async def create_simple_report(
    projects: list[CharityProject],
    yandex_client: YandexDiskClient,
) -> str:
    report_date = datetime.now(timezone.utc).strftime(settings.report_format)
    upload_url, file_path = await yandex_client.create_excel_file(
        FILE_NAME.format(date=report_date)
    )
    with io.BytesIO() as output:
        with xlsxwriter.Workbook(output, {'in_memory': True}) as workbook:
            worksheet = workbook.add_worksheet(SHEET_NAME)
            title_format = workbook.add_format({
                'bold': True,
                'font_size': 14,
                'align': 'center',
                'valign': 'vcenter',
                'border': 1,
            })
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': HEADER_BG_COLOR,
                'font_color': 'white',
                'align': 'center',
                'valign': 'vcenter',
                'border': 1,
            })
            cell_format = workbook.add_format({
                'border': 1,
                'valign': 'vcenter',
            })
            total_format = workbook.add_format({
                'bold': True,
                'border': 1,
                'valign': 'vcenter',
            })
            worksheet.merge_range(
                TITLE_ROW,
                0,
                TITLE_ROW,
                len(TABLE_HEADERS) - 1,
                REPORT_TITLE.format(date=report_date),
                title_format,
            )
            worksheet.write_row(HEADERS_ROW, 0, TABLE_HEADERS, header_format)
            row = FIRST_DATA_ROW
            for project in projects:
                worksheet.write(row, 0, project.name, cell_format)
                worksheet.write(
                    row,
                    1,
                    format_time_delta(
                        project.close_date - project.create_date
                    ),
                    cell_format,
                )
                worksheet.write(row, 2, project.description, cell_format)
                row += 1
            worksheet.write(row, 0, TOTAL_LABEL, total_format)
            worksheet.write(row, 1, len(projects), total_format)
            worksheet.write(row, 2, '', total_format)
            for column, width in enumerate(COLUMN_WIDTHS):
                worksheet.set_column(column, column, width)
        await yandex_client.upload_file(upload_url, output.getvalue())
    return await yandex_client.publish_file(file_path)
