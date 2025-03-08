import asyncio
import os
from functools import partial

import aiofiles.os as aios
import pandas as pd

from core.settings import settings

# import xlwt


async def convert_xlsx_to_xls(file_name: str) -> None:
    """
    Преобразует XLSX файл в XLS.

    :param file_name: .
    """
    pd.set_option("io.excel.xls.writer", "xlwt")

    file = os.path.join(settings.BASE_DIR, settings.UPLOAD_DIR, "%s", file_name)
    input_file = file % ("in")
    output_file = file % ("out")
    if not await aios.path.exists(input_file):
        print(f"Файл {input_file} не найден")
        return

    loop = asyncio.get_event_loop()

    try:
        df = await loop.run_in_executor(None, pd.read_excel, input_file)
    except Exception as e:
        print(f"Файл {input_file} не прочитан")
        print(e)

    try:
        await loop.run_in_executor(
            None, partial(df.to_excel, output_file, index=False, engine="xlwt")
        )
    except Exception as e:
        print(f"Файл {output_file} не записан")
        print(e)
