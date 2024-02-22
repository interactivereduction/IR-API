"""
Inegration tests for data access.
Requires postgres running with user postgres and password password
Tests designed to test every specification with it's respective repo
with a live db connection
"""
import datetime

import pytest

from ir_api.core.exceptions import NonUniqueRecordError
from ir_api.core.model import Base, Script, Instrument, Reduction, ReductionState, Run
from ir_api.core.repositories import ENGINE, SESSION, Repo
from ir_api.core.specifications.reduction import ReductionSpecification
from ir_api.core.specifications.run import RunSpecification

# pylint: disable = redefined-outer-name

TEST_SCRIPT = Script(script="print('Script 1')")
TEST_REDUCTION = Reduction(
    reduction_start=datetime.datetime.now(datetime.UTC),
    reduction_state=ReductionState.NOT_STARTED,
    reduction_inputs={"input": "value"},
    script=TEST_SCRIPT,
)
TEST_REDUCTION_2 = Reduction(
    reduction_start=datetime.datetime.now(datetime.UTC),
    reduction_state=ReductionState.UNSUCCESSFUL,
    reduction_inputs={"input": "value"},
    script=TEST_SCRIPT,
)
TEST_REDUCTION_3 = Reduction(
    reduction_start=datetime.datetime.now(datetime.UTC),
    reduction_state=ReductionState.SUCCESSFUL,
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
    run_start=datetime.datetime.now(datetime.UTC),
    run_end=datetime.datetime.now(datetime.UTC),
    good_frames=200,
    raw_frames=200,
    instrument=TEST_INSTRUMENT_1,
)
TEST_RUN_1.reductions.append(TEST_REDUCTION_2)
TEST_RUN_2 = Run(
    filename="test_run",
    experiment_number=2,
    title="Test Run 2",
    users="User1, User2",
    run_start=datetime.datetime.now(datetime.UTC),
    run_end=datetime.datetime.now(datetime.UTC),
    good_frames=100,
    raw_frames=200,
    instrument=TEST_INSTRUMENT_1,
)
TEST_RUN_2.reductions.append(TEST_REDUCTION)
TEST_RUN_3 = Run(
    filename="test_run",
    experiment_number=3,
    title="Test Run 3",
    users="User1, User2",
    run_start=datetime.datetime.now(datetime.UTC),
    run_end=datetime.datetime.now(datetime.UTC),
    good_frames=100,
    raw_frames=200,
    instrument=TEST_INSTRUMENT_2,
)
TEST_REDUCTION_4 = Reduction(
    reduction_start=datetime.datetime.now(datetime.UTC),
    reduction_state=ReductionState.NOT_STARTED,
    reduction_inputs={"input": "value"},
    script=TEST_SCRIPT,
)
TEST_RUN_3.reductions.append(TEST_REDUCTION_4)


@pytest.fixture(scope="module", autouse=True)
def setup() -> None:
    """
    Set up the test database before module
    :return: None
    """
    Base.metadata.drop_all(ENGINE)
    Base.metadata.create_all(ENGINE)

    with SESSION() as session:
        session.add(TEST_SCRIPT)
        session.add(TEST_INSTRUMENT_1)
        session.add(TEST_INSTRUMENT_2)
        session.add(TEST_RUN_1)
        session.add(TEST_RUN_2)
        session.add(TEST_RUN_3)
        session.commit()
        session.refresh(TEST_SCRIPT)
        session.refresh(TEST_INSTRUMENT_1)
        session.refresh(TEST_INSTRUMENT_2)
        session.refresh(TEST_RUN_1)
        session.refresh(TEST_RUN_2)
        session.refresh(TEST_RUN_3)

    yield


@pytest.fixture()
def reduction_repo() -> Repo[Reduction]:
    """
    ReductionRepo fixture
    :return: ReductionRepo
    """
    return Repo()


@pytest.fixture()
def run_repo() -> Repo[Run]:
    """
    RunRepo fixture
    :return: RunRepo
    """
    return Repo()


def test_base_spec_all(run_repo):
    """Test all are in result"""
    result = run_repo.find(RunSpecification().all())
    assert TEST_RUN_3 in result
    assert TEST_RUN_2 in result
    assert TEST_RUN_1 in result


def test_base_spec_by_id(run_repo):
    """Test find by id"""
    result = run_repo.find_one(RunSpecification().by_id(1))
    assert result == TEST_RUN_1


def test_run_by_instrument(run_repo):
    """Test finding runs by instrument"""
    result = run_repo.find(RunSpecification().by_instrument("instrument 1"))
    assert result == [TEST_RUN_1, TEST_RUN_2]
    result = run_repo.find(
        RunSpecification().by_instrument(
            "instrument 1", limit=1, offset=1, order_by="good_frames", order_direction="desc"
        )
    )
    assert result == [TEST_RUN_2]


def test_run_by_instrument_raises_when_non_unique(run_repo):
    """Test correct exception raised when multiple runs exist"""
    with pytest.raises(NonUniqueRecordError):
        run_repo.find_one(RunSpecification().by_instrument("instrument 1"))


@pytest.mark.parametrize(
    ("order_field,expected_ascending"),
    [
        ("run_start", [TEST_REDUCTION_2, TEST_REDUCTION]),
        ("run_end", [TEST_REDUCTION_2, TEST_REDUCTION]),
        ("experiment_number", [TEST_REDUCTION_2, TEST_REDUCTION]),
        ("experiment_title", [TEST_REDUCTION_2, TEST_REDUCTION]),
    ],
)
def test_reductions_by_instrument_sort_by_run_field(reduction_repo, order_field, expected_ascending):
    """Test reductions by run fields"""
    expected = expected_ascending
    result = reduction_repo.find(
        ReductionSpecification().by_instrument("instrument 1", order_by=order_field, order_direction="asc")
    )
    assert expected == result
    result = reduction_repo.find(
        ReductionSpecification().by_instrument("instrument 1", order_by=order_field, order_direction="desc")
    )
    expected.reverse()
    assert expected == result


def test_reductions_by_instrument_sort_by_reduction_field(reduction_repo):
    """Test sorting by reduction field"""
    result = reduction_repo.find(
        ReductionSpecification().by_instrument("instrument 1", order_by="reduction_state", order_direction="asc")
    )
    expected = [TEST_REDUCTION_2, TEST_REDUCTION]
    assert result == expected

    result = reduction_repo.find(
        ReductionSpecification().by_instrument("instrument 1", order_by="reduction_state", order_direction="desc")
    )
    expected.reverse()
    assert result == expected
