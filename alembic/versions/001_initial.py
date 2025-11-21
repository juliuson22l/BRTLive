"""create_all_tables_correct

Revision ID: 001_initial
Revises: 
Create Date: 2025-10-27 18:26:39.573562

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('role', sa.Enum('ADMIN', 'DRIVER', 'VIEWER', name='userrole'), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # Create terminals table
    op.create_table(
        'terminals',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('address', sa.String(), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('capacity', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_terminals_id'), 'terminals', ['id'], unique=False)

    # Create drivers table
    op.create_table(
        'drivers',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), unique=True, nullable=False),
        sa.Column('license_number', sa.String(), unique=True, nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('phone_number', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('phone_number'),
        sa.UniqueConstraint('license_number'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_drivers_id'), 'drivers', ['id'], unique=False)
    op.create_index(op.f('ix_drivers_user_id'), 'drivers', ['user_id'], unique=True)
    op.create_index(op.f('ix_drivers_phone_number'), 'drivers', ['phone_number'], unique=True)

    # Create buses table
    op.create_table(
        'buses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('plate_number', sa.String(), nullable=False),
        sa.Column('capacity', sa.Integer(), nullable=True),
        sa.Column('current_terminal_id', sa.String(), nullable=True),
        sa.Column('driver_id', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('speed', sa.Float(), nullable=True),
        sa.Column('last_updated', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['current_terminal_id'], ['terminals.id'], ),
        sa.ForeignKeyConstraint(['driver_id'], ['drivers.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('plate_number')
    )
    op.create_index(op.f('ix_buses_id'), 'buses', ['id'], unique=False)

    # Create daily_assignments table
    op.create_table(
        'daily_assignments',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('driver_id', sa.String(), nullable=False),
        sa.Column('bus_id', sa.Integer(), nullable=False),
        sa.Column('assignment_date', sa.Date(), nullable=False),
        sa.Column('shift', sa.Enum('MORNING', 'AFTERNOON', 'EVENING', name='shifttype'), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['bus_id'], ['buses.id'], ),
        sa.ForeignKeyConstraint(['driver_id'], ['drivers.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_daily_assignments_assignment_date'), 'daily_assignments', ['assignment_date'], unique=False)
    op.create_index(op.f('ix_daily_assignments_id'), 'daily_assignments', ['id'], unique=False)
    op.create_unique_constraint('uq_driver_date_shift', 'daily_assignments', ['driver_id', 'assignment_date', 'shift'])

    # Create location_history table
    op.create_table(
        'location_history',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('bus_id', sa.Integer(), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('speed', sa.Float(), nullable=True),
        sa.Column('heading', sa.Float(), nullable=True),
        sa.Column('accuracy', sa.Float(), nullable=True),
        sa.Column('recorded_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['bus_id'], ['buses.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_location_history_id'), 'location_history', ['id'], unique=False)
    op.create_index(op.f('ix_location_history_recorded_at'), 'location_history', ['recorded_at'], unique=False)
    op.create_index(op.f('ix_location_history_bus_id'), 'location_history', ['bus_id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_location_history_bus_id'), table_name='location_history')
    op.drop_index(op.f('ix_location_history_recorded_at'), table_name='location_history')
    op.drop_index(op.f('ix_location_history_id'), table_name='location_history')
    op.drop_table('location_history')
    
    op.drop_constraint('uq_driver_date_shift', 'daily_assignments', type_='unique')
    op.drop_index(op.f('ix_daily_assignments_id'), table_name='daily_assignments')
    op.drop_index(op.f('ix_daily_assignments_assignment_date'), table_name='daily_assignments')
    op.drop_table('daily_assignments')
    
    op.drop_index(op.f('ix_buses_id'), table_name='buses')
    op.drop_table('buses')
    
    op.drop_index(op.f('ix_drivers_phone_number'), table_name='drivers')
    op.drop_index(op.f('ix_drivers_id'), table_name='drivers')
    op.drop_table('drivers')
    
    op.drop_index(op.f('ix_terminals_id'), table_name='terminals')
    op.drop_table('terminals')
    
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    
    # Drop enum types
    sa.Enum(name='shifttype').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='userrole').drop(op.get_bind(), checkfirst=True)