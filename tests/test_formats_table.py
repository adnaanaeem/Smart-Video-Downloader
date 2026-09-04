# tests/test_formats_table.py
# Regression tests for _populate_formats_table / _add_format_row - the most bug-prone code in
# this app (three separate real bugs shipped here across one day: wrong yt-dlp binary masking
# real data, a None-abr crash, and the format/language pairing logic itself).

import pytest

from conftest import load_fixture


def test_single_merged_format_populates_without_raising(make_window):
    w = make_window()
    w.fetched_data = load_fixture("single_merged.json")
    w._populate_formats_table()  # must not raise
    assert w.formats_table.rowCount() >= 1  # the format row + the always-present MP3 row


def test_multi_resolution_multi_language_row_count_and_filters(make_window):
    w = make_window()
    w.fetched_data = load_fixture("multi_resolution_multi_language.json")
    w._populate_formats_table()

    # 3 video-only heights x 3 languages = 9 combined rows, + 1 pre-merged row,
    # + 1 MP3 row, + 3 audio-only rows = 14.
    assert w.formats_table.rowCount() == 14

    quality_items = [w.quality_filter.itemText(i) for i in range(w.quality_filter.count())]
    assert set(quality_items) == {"All", "1080p", "720p", "360p", "Audio"}

    language_items = {w.language_filter.itemText(i) for i in range(w.language_filter.count())}
    assert language_items == {"All", "English", "French", "Spanish"}


def test_language_filter_narrows_rows(make_window):
    w = make_window()
    w.fetched_data = load_fixture("multi_resolution_multi_language.json")
    w._populate_formats_table()

    idx = w.language_filter.findText("French")
    assert idx != -1
    w.language_filter.setCurrentIndex(idx)

    visible = sum(1 for i in range(w.formats_table.rowCount()) if not w.formats_table.isRowHidden(i))
    # 3 French combined rows + the standalone French audio-only row + the merged row and the MP3
    # row (both language-agnostic, so always visible regardless of the language filter)
    assert visible == 6


def test_audio_formats_with_none_abr_does_not_crash(make_window):
    """Regression test: .get('abr', 0) doesn't substitute a default when the key exists but is
    None, so max()/sorted() used to blow up comparing None to None. Fixed to .get('abr') or 0."""
    w = make_window()
    w.fetched_data = load_fixture("audio_none_abr.json")
    w._populate_formats_table()  # must not raise TypeError
    assert w.formats_table.rowCount() >= 1


@pytest.mark.parametrize("fixture_name", [
    "single_merged.json",
    "multi_resolution_multi_language.json",
    "audio_none_abr.json",
])
def test_all_fixtures_populate_without_raising(make_window, fixture_name):
    w = make_window()
    w.fetched_data = load_fixture(fixture_name)
    w._populate_formats_table()
