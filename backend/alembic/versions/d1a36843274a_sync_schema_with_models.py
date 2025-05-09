"""Sync schema with models

Revision ID: d1a36843274a
Revises: 2d6b1792b566
Create Date: 2025-05-07 15:17:45.939500

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd1a36843274a'
down_revision: Union[str, None] = '2d6b1792b566'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


