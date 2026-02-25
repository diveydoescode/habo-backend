from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import geoalchemy2

revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")

    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), unique=True, nullable=False),
        sa.Column('avatar_url', sa.String(), nullable=True),
        sa.Column('public_key', sa.String(), nullable=True),
        sa.Column('rating', sa.Float(), default=5.0),
        sa.Column('tasks_posted', sa.Integer(), default=0),
        sa.Column('tasks_completed', sa.Integer(), default=0),
        sa.Column('member_since', sa.DateTime(timezone=True)),
    )
    op.execute("CREATE INDEX ix_users_name_trgm ON users USING gin(name gin_trgm_ops);")
    op.create_index('ix_users_email', 'users', ['email'])

    op.create_table(
        'followers',
        sa.Column('follower_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), primary_key=True),
        sa.Column('following_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), primary_key=True),
    )

    op.create_table(
        'tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('category', sa.Enum('Academic', 'Roadside Help', 'Labor', 'Custom', name='taskcategory'), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('budget', sa.Integer(), nullable=False),
        sa.Column('is_negotiable', sa.Boolean(), default=False),
        sa.Column('location', geoalchemy2.types.Geometry(geometry_type='POINT', srid=4326), nullable=False),
        sa.Column('radius_metres', sa.Integer(), default=10000),
        sa.Column('status', sa.Enum('Active', 'Accepted', 'Completed', 'Cancelled', name='taskstatus'), default='Active'),
        sa.Column('created_at', sa.DateTime(timezone=True)),
        sa.Column('creator_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('accepted_by_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
    )
    op.execute("CREATE INDEX ix_tasks_location ON tasks USING gist(location);")

    op.create_table(
        'chat_messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tasks.id'), nullable=False),
        sa.Column('sender_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('ciphertext', sa.Text(), nullable=False),
        sa.Column('nonce', sa.String(64), nullable=False),
        sa.Column('sent_at', sa.DateTime(timezone=True)),
    )
    op.create_index('ix_chat_messages_task_id', 'chat_messages', ['task_id'])


def downgrade() -> None:
    op.drop_table('chat_messages')
    op.drop_table('tasks')
    op.drop_table('followers')
    op.drop_table('users')
    op.execute("DROP TYPE IF EXISTS taskcategory;")
    op.execute("DROP TYPE IF EXISTS taskstatus;")