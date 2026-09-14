"""seed default working hours for all seven days

Строки рабочего времени раньше появлялись только после того, как админ
нажимал «Сохранить» на конкретном дне. До этого админка показывала 10:00-21:00
как заполненные поля (это дефолты формы), а бэкенд для того же дня отвечал
«не рабочий день» — расхождение, которое невозможно заметить в интерфейсе.
Миграция создаёт недостающие дни, чтобы состояние в БД совпадало с тем,
что видно на экране.

Revision ID: d3b8c9e21a7f
Revises: c1f4a7d2e8b3
Create Date: 2026-09-14

"""
from typing import Sequence, Union

from alembic import op


revision: str = 'd3b8c9e21a7f'
down_revision: Union[str, None] = 'c1f4a7d2e8b3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

DEFAULT_WORK_START = '10:00'
DEFAULT_WORK_END = '21:00'
DEFAULT_TIMEZONE = 'Europe/Moscow'


def upgrade() -> None:
    # Только недостающие дни: уже настроенные админом строки не трогаем.
    op.execute(
        f"""
        INSERT INTO working_hours (day_of_week, work_start, work_end, is_enabled, timezone)
        SELECT d, '{DEFAULT_WORK_START}', '{DEFAULT_WORK_END}', true, '{DEFAULT_TIMEZONE}'
        FROM generate_series(0, 6) AS d
        WHERE NOT EXISTS (
            SELECT 1 FROM working_hours wh WHERE wh.day_of_week = d
        )
        """
    )


def downgrade() -> None:
    # Обратной операции нет намеренно: к этому моменту строки уже могли быть
    # отредактированы админом, и отличить их от засеянных невозможно.
    # Удаление здесь стёрло бы рабочий график.
    pass
