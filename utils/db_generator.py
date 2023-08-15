"""
Script to generate a database for a development environment
"""
import random
from datetime import datetime, timedelta

from faker import Faker
from faker.providers import BaseProvider

from ir_api.core.model import Instrument, Run, Reduction, ReductionState, Script, Base
from ir_api.core.repositories import SESSION, ENGINE

random.seed(1)
Faker.seed(1)
faker = Faker()


class InteractiveReductionProvider(BaseProvider):
    INSTRUMENTS = [
        "ALF",
        "ARGUS",
        "CHIPIR",
        "CHRONUS",
        "CRISP",
        "DEVA",
        "EMMAA",
        "EMU",
        "ENGINX",
        "EVS",
        "GEM",
        "HET",
        "HIFI",
        "HRPD",
        "IMAT",
        "INES",
        "INTER",
        "IRIS",
        "LAD",
        "LARMOR",
        "LET",
        "LOQ",
        "MAPS",
        "MARI",
        "MERLIN",
        "MUSR",
        "NILE",
        "NIMROD",
        "OFFSPEC",
        "OSIRIS",
        "PEARL",
        "POLARIS",
        "POLREF",
        "PRISMA",
        "ROTAX",
        "SANDALS",
        "SANS2D",
        "SURF",
        "SXD",
        "TFXA",
        "TOSCA",
        "VESUVIO",
        "WISH",
        "ZOOM",
    ]

    def start_time(self) -> datetime:
        return datetime(
            faker.pyint(min_value=2017, max_value=2023),
            faker.pyint(min_value=1, max_value=12),
            faker.pyint(min_value=1, max_value=28),
            faker.pyint(min_value=1, max_value=23),
            faker.pyint(min_value=1, max_value=59),
            faker.pyint(min_value=1, max_value=59),
        )

    def instrument(self) -> Instrument:
        instrument = Instrument()
        instrument.instrument_name = random.choice(self.INSTRUMENTS)
        return instrument

    def run(self, instrument: Instrument) -> Run:
        run = Run()
        run_start = self.start_time()
        run_end = run_start + timedelta(minutes=faker.pyint(max_value=50))
        experiment_number = faker.unique.pyint(min_value=10000, max_value=99999)
        raw_frames = faker.pyint(min_value=1000)
        good_frames = faker.pyint(max_value=raw_frames)
        title = faker.unique.sentence(nb_words=10)
        run.filename = (
            f"/archive/NDX{instrument.instrument_name}/Instrument/data/"
            f"cycle_{faker.pyint(min_value=15, max_value=23)}_0{faker.pyint(min_value=1, max_value=3)}/"
            f"{instrument.instrument_name}{experiment_number}.nxs"
        )
        run.title = title
        run.instrument = instrument
        run.raw_frames = raw_frames
        run.good_frames = good_frames
        run.users = f"{faker.first_name()} {faker.last_name()}, {faker.first_name()} {faker.last_name()}"
        run.experiment_number = experiment_number
        run.run_start = run_start
        run.run_end = run_end

        return run

    def reduction(self) -> Reduction:
        reduction = Reduction()
        reduction_state = faker.enum(ReductionState)
        if reduction_state != ReductionState.NOT_STARTED:
            reduction.reduction_start = self.start_time()
            reduction.reduction_end = reduction.reduction_start + timedelta(minutes=faker.pyint(max_value=50))
            reduction.reduction_status_message = faker.sentence(nb_words=10)
            reduction.reduction_outputs = "What should this be?"
        reduction.reduction_inputs = faker.pydict(
            nb_elements=faker.pyint(min_value=1, max_value=10), value_types=[str, int, bool, float]
        )
        reduction.reduction_state = reduction_state
        return reduction

    def script(self) -> Script:
        script = Script()
        script.sha = faker.unique.sha1()
        script.script = "import os\nprint('foo')\n"
        return script

    def insertable_reduction(self, instrument: Instrument) -> Reduction:
        reduction = self.reduction()
        reduction.runs = [self.run(instrument)]
        reduction.script = self.script()

        return reduction


def main():
    ir_provider = InteractiveReductionProvider(faker)

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
