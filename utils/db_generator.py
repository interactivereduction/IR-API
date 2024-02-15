"""
Script to generate a database for a development environment
"""
import os
import random
import sys

from faker import Faker
from sqlalchemy import create_engine, NullPool
from sqlalchemy.orm import sessionmaker

from ir_api.core.model import Base, Instrument
from test.utils import IR_FAKER_PROVIDER, InteractiveReductionProvider

random.seed(1)
Faker.seed(1)
faker = Faker()

DB_USERNAME = os.environ.get("DB_USERNAME", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "password")
DB_IP = os.environ.get("DB_IP", "localhost")

ENGINE = create_engine(
    f"postgresql+psycopg2://{DB_USERNAME}:{DB_PASSWORD}@{DB_IP}:5432/interactive-reduction",
    poolclass=NullPool,
    echo=True,
)

SESSION = sessionmaker(ENGINE)


def main():
    ir_provider = IR_FAKER_PROVIDER

    if "localhost" not in ENGINE.url:
        # Someone already overwrote all of production with this. Proceed with caution.
        sys.exit(f"Script is not pointing at localhost {ENGINE.url}: Don't even think about it")

    Base.metadata.drop_all(ENGINE)
    Base.metadata.create_all(ENGINE)

    with SESSION() as session:
        instruments = []
        for instrument in InteractiveReductionProvider.INSTRUMENTS:
            instrument_ = Instrument()
            instrument_.instrument_name = instrument
            instruments.append(instrument_)

        for i in range(10000):
            session.add(ir_provider.insertable_reduction(random.choice(instruments)))
        session.commit()


if __name__ == "__main__":
    main()
