from app.database import _normalize_database_url


def test_render_postgresql_url_uses_installed_psycopg_driver():
    assert (
        _normalize_database_url("postgresql://user:secret@db.internal:5432/example")
        == "postgresql+psycopg://user:secret@db.internal:5432/example"
    )
    assert (
        _normalize_database_url("postgres://user:secret@db.internal:5432/example")
        == "postgresql+psycopg://user:secret@db.internal:5432/example"
    )


def test_explicit_driver_and_sqlite_urls_are_preserved():
    assert (
        _normalize_database_url("postgresql+psycopg://user:secret@db:5432/example")
        == "postgresql+psycopg://user:secret@db:5432/example"
    )
    assert _normalize_database_url("sqlite:///./test.db") == "sqlite:///./test.db"
