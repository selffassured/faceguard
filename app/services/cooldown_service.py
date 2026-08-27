import time


class CooldownService:
    def __init__(self, cooldown_seconds: int = 300):
        self.cooldown_seconds = cooldown_seconds
        self.last_events = {}

    def can_trigger(self, person_id: int) -> bool:
        now = time.time()

        last_time = self.last_events.get(person_id)

        if last_time is None:
            return True

        elapsed = now - last_time

        return elapsed >= self.cooldown_seconds

    def trigger(self, person_id: int):
        self.last_events[person_id] = time.time()

    def reset(self, person_id: int | None = None):
        if person_id is None:
            self.last_events.clear()
            return

        self.last_events.pop(person_id, None)