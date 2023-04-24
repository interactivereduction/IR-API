"""
Inegration tests for data access.
Requires postgres running with user postgres and password password
"""
from datetime import datetime

import pytest

from ir_api.core.exceptions import NonUniqueRecordError
from ir_api.core.model import Base, Script, Instrument, Reduction, ReductionState, Run
from ir_api.core.repositories import ScriptRepo, ENGINE, SESSION, ReductionRepo, RunRepo, InstrumentRepo

# pylint: disable = redefined-outer-name

TEST_SCRIPT = Script(script="print('Script 1')")
TEST_REDUCTION = Reduction(
    reduction_start=datetime.utcnow(),
    reduction_state=ReductionState.NOT_STARTED,
    reduction_inputs={"input": "value"},
    script=TEST_SCRIPT,
)

TEST_INSTRUMENT_1 = Instrument(instrument_name="instrument 1")
TEST_INSTRUMENT_2 = Instrument(instrument_name="instrument 2")

TEST_RUN_1 = Run(
    filename="test_run",
    experiment_number=1,
    title="Test Run",
    users="User1, User2",
    run_start=datetime.utcnow(),
    run_end=datetime.utcnow(),
    good_frames=100,
    raw_frames=200,
    instrument=TEST_INSTRUMENT_1,
)
TEST_RUN_2 = Run(
    filename="test_run",
    experiment_number=2,
    title="Test Run 2",
    users="User1, User2",
    run_start=datetime.utcnow(),
    run_end=datetime.utcnow(),
    good_frames=100,
    raw_frames=200,
    instrument=TEST_INSTRUMENT_1,
)
TEST_RUN_3 = Run(
    filename="test_run",
    experiment_number=2,
    title="Test Run 3",
    users="User1, User2",
    run_start=datetime.utcnow(),
    run_end=datetime.utcnow(),
    good_frames=100,
    raw_frames=200,
    instrument=TEST_INSTRUMENT_2,
)


@pytest.fixture(scope="module", autouse=True)
def setup() -> None:
    """
    Set up the test database before module
    :return: None
    """
    Base.metadata.drop_all(ENGINE)
    Base.metadata.create_all(ENGINE)
    TEST_RUN_1.reductions.append(TEST_REDUCTION)

    with SESSION() as session:
        session.add(TEST_SCRIPT)
        session.add(TEST_INSTRUMENT_1)
        session.add(TEST_INSTRUMENT_2)
        session.add(TEST_RUN_1)
        session.add(TEST_RUN_2)
        session.add(TEST_RUN_3)
        session.add(TEST_REDUCTION)
        session.commit()
        session.refresh(TEST_SCRIPT)
        session.refresh(TEST_INSTRUMENT_1)
        session.refresh(TEST_INSTRUMENT_2)
        session.refresh(TEST_RUN_1)
        session.refresh(TEST_RUN_2)
        session.refresh(TEST_RUN_3)
        session.refresh(TEST_REDUCTION)

    yield


@pytest.fixture()
def script_repo() -> ScriptRepo:
    """
    ScriptRepo fixture
    :return: ScriptRepo
    """
    return ScriptRepo()


@pytest.fixture()
def reduction_repo() -> ReductionRepo:
    """
    ReductionRepo fixture
    :return: ReductionRepo
    """
    return ReductionRepo()


@pytest.fixture()
def run_repo() -> RunRepo:
    """
    RunRepo fixture
    :return: RunRepo
    """
    return RunRepo()


@pytest.fixture()
def instrument_repo() -> InstrumentRepo:
    """
    InstrumentRepo fixture
    :return: InstrumentRepo
    """
    return InstrumentRepo()


def test_script_repo_find_one(script_repo):
    """
    Test find_one for script repo
    :param script_repo: script repo fixture
    :return: None
    """
    found_script = script_repo.find_one(lambda s: s.id == 1)
    assert found_script == TEST_SCRIPT


def test_reduction_repo_find_one(reduction_repo):
    """
    Test find_one for reduction repo
    :param reduction_repo: reduction repo fixture
    :return: None
    """
    found_reduction = reduction_repo.find_one(lambda r: r.id == 1)
    assert found_reduction == TEST_REDUCTION


def test_run_repo_find_one(run_repo):
    """
    Test find_one for run repo
    :param run_repo: run repo fixture
    :return: None
    """
    found_run = run_repo.find_one(lambda r: r.id == 1)
    assert found_run == TEST_RUN_1

    # Test relationship between Run and Reduction
    assert len(found_run.reductions) == 1
    assert found_run.reductions[0] == TEST_REDUCTION


def test_instrument_repo_find_one_none_exist_returns_none(instrument_repo):
    """
    Test none is returned when nothing is found from a find_one call
    :param instrument_repo: InstrumentRepo fixture
    :return: None
    """
    assert instrument_repo.find_one(lambda i: i.instrument_name == "baz") is None


def test_run_repo_find_one_multiple_returned_raises_error(run_repo):
    """
    Test a multiple record exception will be raised if more than one result will be found
    :param run_repo: run repo fixture
    :return: none
    """
    with pytest.raises(NonUniqueRecordError):
        run_repo.find_one(lambda r: r.users == "User1, User2")


def test_instrument_repo_find_one(instrument_repo, run_repo):
    """
    Test find one returns one for instrument repo
    :param instrument_repo: instrument repo fixture
    :param run_repo: None
    :return:
    """
    found_instrument = instrument_repo.find_one(lambda i: i.id == 1)
    assert found_instrument == TEST_INSTRUMENT_1

    # Test relationship between Run and Instrument
    found_run = run_repo.find_one(lambda r: r.id == 1)
    assert found_run.instrument == TEST_INSTRUMENT_1


def test_script_repo_find(script_repo):
    """
    Test find on script repo
    :param script_repo: ScriptRepo fixture
    :return: None
    """
    found_scripts = script_repo.find(lambda s: s.script == "print('Script 1')")

    assert found_scripts[0] == TEST_SCRIPT
    assert len(found_scripts) == 1


def test_reduction_repo_find(reduction_repo):
    """
    Test find on reduction repo
    :param reduction_repo: reduction repo fixture
    :return: None
    """
    found_reductions = reduction_repo.find(lambda r: r.reduction_state == ReductionState.NOT_STARTED)
    assert found_reductions[0] == TEST_REDUCTION
    assert len(found_reductions) == 1


def test_run_repo_find(run_repo):
    """
    Test find on run repo
    :param run_repo: run repo fixture
    :return: None
    """
    found_runs = run_repo.find(lambda r: r.instrument.has(Instrument.instrument_name == "instrument 2"))
    assert found_runs[0] == TEST_RUN_3
    assert len(found_runs) == 1

    found_runs = run_repo.find(
        lambda r: r.instrument.has(Instrument.instrument_name == "instrument 1") & (r.title == "Test Run 2")
    )
    assert found_runs[0] == TEST_RUN_2
    assert len(found_runs) == 1


def test_run_repo_find_multiple_filters(run_repo):
    """
    Test find with multiple filter expression on run repo
    :param run_repo: run repo fixture
    :return: None
    """
    found_runs = run_repo.find(
        lambda r: r.instrument.has(Instrument.instrument_name == "instrument 1") & (r.users == "User1, User2")
    )
    assert len(found_runs) == 2
    assert TEST_RUN_1 in found_runs
    assert TEST_RUN_2 in found_runs

    found_runs = run_repo.find(
        lambda r: r.instrument.has(Instrument.instrument_name == "instrument 2") & (r.users == "User1, User2")
    )
    assert len(found_runs) == 1
    assert TEST_RUN_3 in found_runs


def test_run_repo_find_with_or(run_repo):
    """
    Test find with or on run repo
    :param run_repo: run repo fixture
    :return: None
    """
    found_runs = run_repo.find(
        lambda r: (r.instrument.has(Instrument.instrument_name == "instrument 1")) | (r.title == "Test Run 3")
    )
    assert len(found_runs) == 3
    assert TEST_RUN_1 in found_runs
    assert TEST_RUN_2 in found_runs
    assert TEST_RUN_3 in found_runs


def test_run_repo_find_with_reduction(run_repo):
    """
    Test find of run repo based on related reduction
    :param run_repo: run repo fixture
    :return: None
    """
    found_runs = run_repo.find(lambda r: r.reductions.any(Reduction.reduction_state == ReductionState.NOT_STARTED))
    assert len(found_runs) == 1
    assert TEST_RUN_1 in found_runs


def test_reduction_repo_find_with_run(reduction_repo):
    """
    test reduction repo find based on related instrument
    :param reduction_repo: reduction repo fixture
    :return: None
    """
    found_reductions = reduction_repo.find(
        lambda r: r.runs.any(Run.instrument.has(Instrument.instrument_name == "instrument 1"))
    )
    assert len(found_reductions) == 1
    assert TEST_REDUCTION in found_reductions
