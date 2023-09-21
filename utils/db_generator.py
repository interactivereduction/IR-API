"""
Script to generate a database for a development environment
"""
import random

from faker import Faker

from ir_api.core.model import Instrument, Base
from ir_api.core.repositories import SESSION, ENGINE
from test.utils import InteractiveReductionProvider, IR_FAKER_PROVIDER

random.seed(1)
Faker.seed(1)
faker = Faker()


def main():
    ir_provider = IR_FAKER_PROVIDER

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
