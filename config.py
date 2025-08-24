import os

# ✅ Database settings
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", 3306)
DB_USER = os.getenv("DB_USER", "pennyroot")
DB_PASSWORD = os.getenv("DB_PASSWORD", "penny123")
DB_NAME = os.getenv("DB_NAME", "pennybank")

# Railway provides DATABASE_URL, so use that if available
DB_CONNECTION_STRING = os.getenv(
    "DATABASE_URL",
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# DB_HOST='localhost'
# DB_PORT=3306
# DB_USER='pennyroot'
# DB_PASSWORD='penny123'
# DB_NAME='pennybank'
# DB_CONNECTION_STRING = (f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"f"@{DB_HOST}:{DB_PORT}/{DB_NAME}" )

'''(
        f"mysql+pymysql://{app.config['DB_USER']}:{app.config['DB_PASSWORD']}"
        f"@{app.config['DB_HOST']}:{app.config['DB_PORT']}/{app.config['DB_NAME']}"
    )'''

EMAIL_PREFIX =('.com','.co')

BASIC_AUTH_PASSWORD = 'password'
BASIC_AUTH_USERNAME = 'username'
BASIC_AUTH_USER_PROMPT = 'Username and password is required'

SAVINGS_LIMIT_MAX = 20000000.00
CURRENT_LIMIT_MAX = 10000000.00