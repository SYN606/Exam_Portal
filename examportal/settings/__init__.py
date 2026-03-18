import os
from dotenv import load_dotenv

load_dotenv()

env = os.getenv("ENV", "development")

if env == "production":
    from .prod import *  # noqa: F403
else:
    from .dev import *  # noqa: F403
