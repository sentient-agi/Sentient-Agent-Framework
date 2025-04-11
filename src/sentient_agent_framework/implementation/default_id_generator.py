from asyncio import Lock
from ulid import ULID


class DefaultIdGenerator:
    """
    ULID generator that tracks the latest identifier and ensures that the
    next identifier is always greater than the latest.
    """
    
    def __init__(
        self, 
        seed_id: ULID | None = None,
    ):
        self._latest_id = seed_id or ULID()
        self._lock = Lock()


    async def get_next_id(
            self,
            new_id: ULID | None = None,
            offset: int = 10
    ) -> ULID:
        """
        Generate the next identifier.

        Args:
            new_id: The user suggested new identifier to use. If one is 
            specified, we will try to use this identifier provided it is
            greater than the latest one.  If not specified, we create a
            new ULID.
            offset: The offset in milliseconds that needs to be added to
            the timestamp of the latest identifier if the new one is less
            than or equal to it.
        """

        # If the user has specified a new identifier, use that, else we
        # create a new one.
        resolved_new_id = new_id or ULID()

        async with self._lock:
            if resolved_new_id <= self._latest_id:
                # Extract the timestamp from the previous event identifier
                # and add the offset to it.
                resolved_new_id = ULID.from_timestamp(
                    self._latest_id.milliseconds + offset
                )
            self._latest_id = resolved_new_id
            
        return resolved_new_id