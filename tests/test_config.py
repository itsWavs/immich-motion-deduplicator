import os

from immich_motion_deduplicator import config


def test_load_dotenv_reads_file_from_current_working_directory(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "IMMICH_API_URL=http://immich.local:2283\nMOTION_CANDIDATES_CSV=local.csv\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("IMMICH_API_URL", raising=False)
    monkeypatch.delenv("MOTION_CANDIDATES_CSV", raising=False)

    config.load_dotenv()

    assert os.environ["IMMICH_API_URL"] == "http://immich.local:2283"
    assert os.environ["MOTION_CANDIDATES_CSV"] == "local.csv"


def test_load_dotenv_does_not_override_existing_environment(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("IMMICH_API_KEY=from-file\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("IMMICH_API_KEY", "from-env")

    config.load_dotenv()

    assert os.environ["IMMICH_API_KEY"] == "from-env"


def test_get_immich_api_url_appends_api_suffix(monkeypatch):
    monkeypatch.setenv("IMMICH_API_URL", "http://immich.local:2283")

    assert config.get_immich_api_url() == "http://immich.local:2283/api"


def test_get_immich_api_url_preserves_existing_api_suffix(monkeypatch):
    monkeypatch.setenv("IMMICH_API_URL", "http://immich.local:2283/api")

    assert config.get_immich_api_url() == "http://immich.local:2283/api"
