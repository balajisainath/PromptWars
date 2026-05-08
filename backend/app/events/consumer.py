import json
import logging
import aio_pika
from app.core.config import get_settings

logger = logging.getLogger(__name__)


async def consume_events() -> None:
    settings = get_settings()
    connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)

    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=10)

        exchange = await channel.declare_exchange("travelai", aio_pika.ExchangeType.TOPIC, durable=True)
        queue = await channel.declare_queue("travelai.events", durable=True)
        await queue.bind(exchange, routing_key="trip.*")
        await queue.bind(exchange, routing_key="itinerary.*")

        async with queue.iterator() as messages:
            async for message in messages:
                try:
                    async with message.process():
                        data = json.loads(message.body)
                        event_type = data.get("event_type", "")
                        logger.info(f"Processing event: {event_type}")

                        if event_type == "trip.created":
                            await _handle_trip_created(data)
                        elif event_type == "itinerary.generated":
                            await _handle_itinerary_generated(data)
                except Exception as exc:
                    logger.error(f"Event processing failed: {exc}")


async def _handle_trip_created(data: dict) -> None:
    pass


async def _handle_itinerary_generated(data: dict) -> None:
    pass
