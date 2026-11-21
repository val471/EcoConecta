
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from backend.config import settings


engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verificar_tablas():
    from sqlalchemy import text

    with engine.connect() as conexion:
        base = conexion.execute(
            text("SELECT current_database()")
        ).scalar()

        tablas = conexion.execute(
            text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
        ).scalars().all()

        print("Base de datos:", base)
        print("Tablas encontradas:", tablas)