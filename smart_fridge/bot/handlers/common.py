from aiogram import Router, types
from aiogram.filters import CommandObject, CommandStart
from dishka.integrations.aiogram import FromDishka
from sqlalchemy.ext.asyncio import AsyncSession

from smart_fridge.lib.db import user as users_db
from smart_fridge.lib.schemas.user import UserPatchSchema


router = Router(name=__name__)


@router.message(CommandStart(deep_link=True))
async def handle_start(message: types.Message, command: CommandObject, db: FromDishka[AsyncSession]):
    args = command.args
    if args is None:
        await message.reply("Corrupted link. No <code>/start</code> deep-linking payload.")
        return
    # So the compiler is satisfied
    assert int(args)
    assert message.from_user

    schema = UserPatchSchema(tg_id=message.from_user.id)
    await users_db.update_user(db, user_id=int(args), schema=schema)

    await message.reply("<b>Успех</b>! Теперь вы будете получать уведомления о своих продуктах в Telegram!")


@router.message(CommandStart())
async def handle_bare_start(message: types.Message):
    await message.reply(text="Пожалуйста, перейдите по ссылке из вашего ЛК на сайте.")
