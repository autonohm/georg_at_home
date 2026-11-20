from command_gate.gate import device_mode, is_open, read_mode_file


def test_open_only_when_device_and_profile_are_real():
    assert is_open("real", "real")
    for device, profile in [("sim", "real"), ("real", "sim"), ("", "real"),
                            ("real", ""), ("mock", "mock"), ("REAL", "real")]:
        assert not is_open(device, profile)


def test_missing_mode_file_is_empty(tmp_path):
    assert read_mode_file(str(tmp_path / "missing")) == ""


def test_mode_file_wins_over_env(tmp_path, monkeypatch):
    f = tmp_path / "mode"
    f.write_text("sim\n")
    monkeypatch.setenv("GEORG_MODE_FILE", str(f))
    monkeypatch.setenv("GEORG_DEVICE_MODE", "real")
    assert device_mode() == "sim"


def test_env_used_when_file_missing(tmp_path, monkeypatch):
    monkeypatch.setenv("GEORG_MODE_FILE", str(tmp_path / "missing"))
    monkeypatch.setenv("GEORG_DEVICE_MODE", "real")
    assert device_mode() == "real"
