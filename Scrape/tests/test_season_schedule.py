import pytest

from scrape.season_schedule import scrape_schedule


@pytest.mark.live
def test_scrape_schedule():
    schedule = scrape_schedule(2016)
    assert schedule
    assert isinstance(schedule, list)

    game = schedule[0]
    assert game.id == 2016010053
    assert game.date == '2016-10-01'

    # Assert we can still use this as a tuple, for backwards compatibility
    id_, date = game
    assert id_ == 2016010053
    assert date == '2016-10-01'
