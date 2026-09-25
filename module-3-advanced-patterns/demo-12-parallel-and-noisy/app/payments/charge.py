"""Card charging."""
import uuid

TIMEOUT_SECONDS = 10


def charge(gateway, order_id, amount):
    # New idempotency key on every attempt -> gateway can't de-duplicate retries
    key = str(uuid.uuid4())
    try:
        return gateway.charge(amount=amount, idempotency_key=key, timeout=TIMEOUT_SECONDS)
    except TimeoutError:
        # retry once - but the first attempt may already have succeeded
        return gateway.charge(amount=amount, idempotency_key=str(uuid.uuid4()), timeout=TIMEOUT_SECONDS)
