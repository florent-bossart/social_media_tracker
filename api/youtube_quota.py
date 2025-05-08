
from datetime import datetime
from pathlib import Path

DAILY_QUOTA_LIMIT = 10000
LOGS_DIR = Path("../logs")
LOGS_DIR.mkdir(parents=True, exist_ok=True)

class QuotaManager:
    def __init__(self):
        self.used = 0
        self.log_file = LOGS_DIR / f"{datetime.now().date()}_requests.txt"
        self._load_logged_requests()

    def _load_logged_requests(self):
        """Load the already logged requests from the file to initialize the `used` count."""
        if self.log_file.exists():
            with open(self.log_file, "r") as f:
                try:
                    self.used = int(f.read().strip())  # Read and parse usage count
                except ValueError:
                    self.used = 0  # Default to zero if the file is empty or invalid

    def _log_usage(self):
        """Save the current usage count to the log file."""
        with open(self.log_file, "w") as f:
            f.write(str(self.used))

    def can_use(self, cost: int) -> bool:
        """Check if the requested quota can be used without exceeding the limit."""
        return self.used + cost <= DAILY_QUOTA_LIMIT

    def use(self, cost: int):
        """Use the specified quota cost and log it."""
        if not self.can_use(cost):
            raise RuntimeError("Quota exceeded")
        self.used += cost
        self._log_usage()


    def remaining(self) -> int:
        """Get the remaining quota."""
        return DAILY_QUOTA_LIMIT - self.used

    def optimize_usage(self, max_cost_per_request: int) -> int:
        """
        Suggest the highest possible cost per request to maximize quota usage.
        Args:
            max_cost_per_request (int): Maximum cost a single request can have.
        Returns:
            int: Suggested cost to use per request.
        """
        remaining_quota = self.remaining()
        if remaining_quota <= 0:
            return 0
        return min(max_cost_per_request, remaining_quota)

quota = QuotaManager()
