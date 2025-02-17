import uuid

from sqlalchemy import and_, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from db import Customer, connection
from db import Mail as mail_model


class Mail:
    @connection
    async def create(self, session: AsyncSession, user_id: int):
        # Получаем активные почты пользователя
        query = (
            select(Customer.status.label("user_status"), mail_model.owner)
            .join(mail_model, mail_model.owner == Customer.tg_id)
            .where(and_(mail_model.owner == user_id, mail_model.is_active.__eq__(True)))
        )
        mails = (await session.execute(query)).all()

        # Если уже есть почты и статус обычный,
        # то больше почту создать не дадим
        if mails and mails.user_status == 0:
            raise BaseException()
        del mails

        # Если почт нет / пользователь - VIP
        mail_name = uuid.uuid4()
        query = insert(mail_model)
        await session.execute(
            query, {"name": f"{mail_name}", "owner": user_id, "is_active": True}
        )
        await session.commit()

        return mail_name

    @connection
    async def deactivate(self, session: AsyncSession, user_id: int, mail_name: str):
        """
        Обработка удаления почты. Удалять могут только пользователи с статусом 1
        По факту не удаляем, а помечаем как неактивную
        """
        # Получаем почтовый ящик и статус пользователя
        query = (
            select(mail_model.id, Customer.status)
            .join(Customer, Customer.tg_id == mail_model.owner)
            .where(
                and_(
                    mail_model.owner == user_id,
                    mail_model.name == mail_name,
                    mail_model.is_active.__eq__(True),
                )
            )
        )

        mails = (await session.execute(query)).first()

        # Если есть требуемая почта
        if mails and mails.status == 1:
            query = (
                update(mail_model)
                .where(mails["id"] == mail_model.id)
                .values({"is_active": False})
            )
            await session.execute(query)
            await session.commit()
            return 1
        elif mails:
            return 2
        return 3

    @connection
    async def get_active_mails(self, session: AsyncSession, user_id: int):
        query = select(mail_model.name).where(
            and_(mail_model.owner == user_id, mail_model.is_active.__eq__(True))
        )
        return (await session.execute(query)).all()
