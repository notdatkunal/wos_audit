"""Data access layer: database queries with exception handling."""

from .user_repository import (
    get_user_count,
    get_all_users,
    get_user_by_login_id,
    seed_users,
    sync_db_users,
)
from .wos_repository import (
    get_wos_masters_with_description,
    get_wos_master_by_serial,
    get_wos_lines,
    get_wos_line,
    update_wos_line_vetted_qty,
    bulk_update_wos_lines_vetted_qty,
)
from .correspondence_repository import get_correspondence_by_wos_serial
from .codetable_repository import get_codetable_by_column_name
from .reset_repository import (
    get_user_email_by_email,
    create_password_reset,
    get_password_reset_by_token,
    delete_password_reset,
    update_sybase_password,
)
from .database_repository import run_test_query

__all__ = [
    "get_user_count",
    "get_all_users",
    "get_user_by_login_id",
    "seed_users",
    "sync_db_users",
    "get_wos_masters_with_description",
    "get_wos_master_by_serial",
    "get_wos_lines",
    "get_wos_line",
    "update_wos_line_vetted_qty",
    "bulk_update_wos_lines_vetted_qty",
    "get_correspondence_by_wos_serial",
    "get_codetable_by_column_name",
    "get_user_email_by_email",
    "create_password_reset",
    "get_password_reset_by_token",
    "delete_password_reset",
    "update_sybase_password",
    "run_test_query",
]
