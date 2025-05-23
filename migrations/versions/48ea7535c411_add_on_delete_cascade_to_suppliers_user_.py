"""Add ON DELETE CASCADE to suppliers.user_id and customers.user_id

Revision ID: 48ea7535c411
Revises: 31db6e43e111
Create Date: 2025-05-10 21:43:36.708928

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '48ea7535c411'
down_revision = '31db6e43e111'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('customers', schema=None) as batch_op:
        batch_op.drop_constraint('customers_user_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(None, 'users', ['user_id'], ['id'], ondelete='CASCADE')

    with op.batch_alter_table('suppliers', schema=None) as batch_op:
        batch_op.drop_constraint('suppliers_user_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(None, 'users', ['user_id'], ['id'], ondelete='CASCADE')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('suppliers', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('suppliers_user_id_fkey', 'users', ['user_id'], ['id'])

    with op.batch_alter_table('customers', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('customers_user_id_fkey', 'users', ['user_id'], ['id'])

    # ### end Alembic commands ###
