from types import ModuleType

import pytest

from immich_motion_deduplicator import __main__


def test_delete_command_requires_execute_for_real_deletion():
    parser = __main__.build_parser()

    args = parser.parse_args(["delete"])

    assert args.command == "delete"
    assert args.execute is False


def test_all_command_supports_dry_run_flag():
    parser = __main__.build_parser()

    args = parser.parse_args(["all", "--dry-run"])

    assert args.command == "all"
    assert args.dry_run is True


def test_all_command_rejects_execute_flag():
    parser = __main__.build_parser()

    with pytest.raises(SystemExit):
        parser.parse_args(["all", "--execute"])


def test_main_runs_all_with_real_deletion_by_default(monkeypatch):
    calls = []
    scan_module = ModuleType("scan_library")
    ids_module = ModuleType("get_ids")
    delete_module = ModuleType("delete_assets")

    scan_module.run = lambda progress_every: calls.append(("scan", progress_every))
    ids_module.main = lambda: calls.append(("ids", None))
    delete_module.run = lambda dry_run: calls.append(("delete", dry_run))

    monkeypatch.setattr(__main__, "print_stage", lambda *args: None)
    monkeypatch.setattr(__main__, "error_console", ModuleType("error_console"))
    __main__.error_console.print = lambda *args, **kwargs: None
    monkeypatch.setitem(__import__("sys").modules, "immich_motion_deduplicator.scan_library", scan_module)
    monkeypatch.setitem(__import__("sys").modules, "immich_motion_deduplicator.get_ids", ids_module)
    monkeypatch.setitem(__import__("sys").modules, "immich_motion_deduplicator.delete_assets", delete_module)
    monkeypatch.setattr(__import__("sys"), "argv", ["immich-motion-deduplicator", "all"])

    __main__.main()

    assert calls == [("scan", 500), ("ids", None), ("delete", False)]


def test_main_runs_all_dry_run_when_requested(monkeypatch):
    calls = []
    scan_module = ModuleType("scan_library")
    ids_module = ModuleType("get_ids")
    delete_module = ModuleType("delete_assets")

    scan_module.run = lambda progress_every: calls.append(("scan", progress_every))
    ids_module.main = lambda: calls.append(("ids", None))
    delete_module.run = lambda dry_run: calls.append(("delete", dry_run))

    monkeypatch.setattr(__main__, "print_stage", lambda *args: None)
    monkeypatch.setattr(__main__, "error_console", ModuleType("error_console"))
    __main__.error_console.print = lambda *args, **kwargs: None
    monkeypatch.setitem(__import__("sys").modules, "immich_motion_deduplicator.scan_library", scan_module)
    monkeypatch.setitem(__import__("sys").modules, "immich_motion_deduplicator.get_ids", ids_module)
    monkeypatch.setitem(__import__("sys").modules, "immich_motion_deduplicator.delete_assets", delete_module)
    monkeypatch.setattr(
        __import__("sys"),
        "argv",
        ["immich-motion-deduplicator", "all", "--dry-run"],
    )

    __main__.main()

    assert calls == [("scan", 500), ("ids", None), ("delete", True)]
