from mandible.cumulus.ingest.granule import unversion_filename


def test_unversion_filename_noop():
    assert unversion_filename("foobar.txt") == "foobar.txt"
    assert unversion_filename(
        "foobar.20241208T001155999",
    ) == "foobar.20241208T001155999"
    assert unversion_filename(
        "foobar.txt.20241208T001155999",
    ) == "foobar.txt.20241208T001155999"
    assert unversion_filename(
        "foobar.v20241208T00115599",
    ) == "foobar.v20241208T00115599"
    assert unversion_filename(
        "foobar.txt.v99999999T999999999",
    ) == "foobar.txt.v99999999T999999999"


def test_unversion_filename():
    assert unversion_filename(
        "foobar.txt.v20241208T001155999",
    ) == "foobar.txt"
    assert unversion_filename(
        "foobar.txt.v00000101T000000000",
    ) == "foobar.txt"
    assert unversion_filename(
        "foobar.txt.v99991231T235959999",
    ) == "foobar.txt"
