import pytest

from scrape import shared


@pytest.mark.parametrize('value,result', (
    ('-16:0-', 1200),
    ('20:00', 1200),
    ('00:00', 0),
    ('11:22', 682),
))
def test_convert_to_seconds(value, result):
    assert shared.convert_to_seconds(value) == result


@pytest.mark.parametrize('name,result', (
    ('joe SCHMOE random PLAYER', 'joe SCHMOE random PLAYER'),
    ('zachary sanford', 'zachary sanford'),
    ('ZACHARY SANFORD', 'ZACH SANFORD'),
))
def test_fix_name(name, result):
    assert shared.fix_name(name) == result
