from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base



DB_URL = "postgresql+asyncpg://neondb_owner:npg_P2IKyBe9qoWQ@ep-gentle-brook-adnbaddh-pooler.c-2.us-east-1.aws.neon.tech/neondb?ssl=require"

engine = create_async_engine(DB_URL, echo=False)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

#Base class for models
Base = declarative_base()

async def get_session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()