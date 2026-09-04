# tests/test_workers.py
# No subprocess or network calls in any test here - pure logic only.

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import workers


def test_bin_paths_resolve_under_bin_dir():
    bin_dir = workers.get_bin_dir()
    assert os.path.dirname(workers.YTDLP_PATH) == bin_dir
    assert os.path.dirname(workers.FFMPEG_PATH) == bin_dir


def test_exe_suffix_matches_platform():
    if workers.IS_MAC:
        assert workers.EXE_SUFFIX == ""
        assert not workers.YTDLP_PATH.endswith(".exe")
    else:
        assert workers.EXE_SUFFIX == ".exe"
        assert workers.YTDLP_PATH.endswith(".exe")
        assert workers.FFMPEG_PATH.endswith(".exe")


def test_create_no_window_is_always_defined():
    # Must never raise AttributeError on any platform.
    assert isinstance(workers.CREATE_NO_WINDOW, int)


def test_parse_flat_playlist_output_single_video():
    stdout = '{"id": "abc123", "title": "A Video", "url": "https://example.com/abc123"}\n'
    entries = workers.parse_flat_playlist_output(stdout)
    assert len(entries) == 1
    assert entries[0]["id"] == "abc123"


def test_parse_flat_playlist_output_multiple_entries():
    stdout = (
        '{"id": "a", "title": "Video A"}\n'
        '{"id": "b", "title": "Video B"}\n'
        '{"id": "c", "title": "Video C"}\n'
    )
    entries = workers.parse_flat_playlist_output(stdout)
    assert [e["id"] for e in entries] == ["a", "b", "c"]


def test_parse_flat_playlist_output_ignores_blank_lines_and_garbage():
    stdout = '{"id": "a"}\n\n   \nnot json\n{"id": "b"}\n'
    entries = workers.parse_flat_playlist_output(stdout)
    assert [e["id"] for e in entries] == ["a", "b"]


def test_parse_flat_playlist_output_empty_string():
    assert workers.parse_flat_playlist_output("") == []
