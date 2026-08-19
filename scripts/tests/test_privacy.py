"""The privacy gate that stands between this repository and a public push.

These cases were previously asserted through `marketplace export`'s wrapper.
That wrapper is gone, but the scanner outlived it -- it now backs
`marketplace scan`, the prek pre-push hook, and the `check` merge gate -- so the
behaviour is pinned directly against the scanner instead.

The hard/soft split is the load-bearing part: a hard error blocks a push, while
a soft warning is reported and allowed through. Promoting a warning to an error
would block every push over an ordinary email address; demoting an error would
let a machine path or a credential ship.
"""

from __future__ import annotations

from pathlib import Path

from marketplace.privacy import scan_file, scan_paths, scan_tree


def _write(tmp_path: Path, name: str, content: str) -> Path:
    path = tmp_path / name
    path.write_text(content, encoding="utf-8")
    return path


def test_absolute_home_path_is_a_hard_error(tmp_path: Path) -> None:
    hard, _ = scan_file(_write(tmp_path, "a.md", "See /Users/someone/Projects/thing\n"))

    assert len(hard) == 1
    assert "Absolute home path" in hard[0]


def test_linux_home_path_is_a_hard_error(tmp_path: Path) -> None:
    hard, _ = scan_file(_write(tmp_path, "a.md", "cd /home/someone/src\n"))

    assert len(hard) == 1
    assert "Absolute home path" in hard[0]


def test_secret_shaped_assignment_is_a_hard_error(tmp_path: Path) -> None:
    hard, _ = scan_file(
        _write(tmp_path, "cfg.sh", 'api_key = "sk-abcdef0123456789abcdef0123456789"\n')
    )

    assert len(hard) == 1
    assert "Secret-ish value" in hard[0]


def test_vault_name_warns_but_does_not_block(tmp_path: Path) -> None:
    # The vault name is an intentional configurable default in several plugins;
    # treating it as an error would block every push.
    hard, soft = scan_file(_write(tmp_path, "a.md", "Notes live in ~/Loose Ends/\n"))

    assert hard == []
    assert len(soft) == 1
    assert "Vault name mention" in soft[0]


def test_email_address_warns_but_does_not_block(tmp_path: Path) -> None:
    hard, soft = scan_file(_write(tmp_path, "a.md", "Contact jacob@jdh.onl\n"))

    assert hard == []
    assert any("Email address" in warning for warning in soft)


def test_clean_file_produces_nothing(tmp_path: Path) -> None:
    assert scan_file(_write(tmp_path, "a.md", "# Title\n\nOrdinary prose.\n")) == ([], [])


def test_binary_file_is_skipped_rather_than_crashing(tmp_path: Path) -> None:
    path = tmp_path / "blob.bin"
    path.write_bytes(b"\xff\xfe\x00\x01binary\x00")

    assert scan_file(path) == ([], [])


def test_scan_paths_ignores_entries_that_are_not_files(tmp_path: Path) -> None:
    offender = _write(tmp_path, "bad.md", "/Users/someone/x\n")
    missing = tmp_path / "gone.md"
    directory = tmp_path / "sub"
    directory.mkdir()

    hard, _ = scan_paths([offender, missing, directory])

    assert len(hard) == 1


def test_scan_tree_skips_vendor_and_vcs_directories(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    _write(tmp_path, ".git/config", "/Users/someone/x\n")
    _write(tmp_path, "real.md", "/Users/someone/y\n")

    hard, _ = scan_tree(tmp_path)

    assert len(hard) == 1, "only the tracked file should be scanned"
    assert "real.md" in hard[0]
