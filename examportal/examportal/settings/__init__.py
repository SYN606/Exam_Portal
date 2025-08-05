import os
from dotenv import load_dotenv

load_dotenv()

env = os.getenv("ENV", "development")

if env == "production":
    from .prod import *
else:
    from .dev import *
