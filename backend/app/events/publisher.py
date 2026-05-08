import json
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import aio_pika
from pydantic import BaseModel
from app.core.config import get_settings


@asynccontextmanager
async def get_connection() -> AsyncGenerator[aio_pika.RobustConnection, None]:
    settings = get_settings()
    connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
    try:
        yield connection
    finally:
        await connection.close()


async def publish_event(exchange_name: str, routing_key: str, event: BaseModel) -> None:
    async with get_connection() as connection:
        async with connection.channel() as channel:
            exchange = await channel.declare_exchange(
                exchange_name, aio_pika.ExchangeType.TOPIC, durable=True
            )
            message = aio_pika.Message(
                body=event.model_dump_json().encode(),
                content_type="application/json",
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            )
            await exchange.publish(message, routing_key=routing_key)
