"""Investment logic: distributing donations across projects."""

from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession


def get_remain_amount(obj) -> int:
    """Return how much is still left to invest."""
    return obj.full_amount - obj.invested_amount


def close_obj(obj) -> None:
    """Mark the object as fully invested and set the close date."""
    obj.invested_amount = obj.full_amount
    obj.fully_invested = True
    obj.close_date = datetime.now()


async def investing(
    target,
    sources: list,
    session: AsyncSession,
):
    """Distribute money between ``target`` and open ``sources``.

    A new project takes money from open donations, and a new donation
    goes to open projects, oldest first. Each source gives as much as
    both sides still need; objects that reach their full amount are
    closed. Changes are not committed: the caller commits them.
    """
    if target.invested_amount is None:
        target.invested_amount = 0
    for source in sources:
        if source.invested_amount is None:
            source.invested_amount = 0
        investment = min(
            get_remain_amount(target),
            get_remain_amount(source),
        )
        target.invested_amount += investment
        source.invested_amount += investment
        if get_remain_amount(source) == 0:
            close_obj(source)
        if get_remain_amount(target) == 0:
            close_obj(target)
            break
    return target
