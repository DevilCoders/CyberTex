from pathlib import Path

from sapl.environment import create_virtual_environment, load_required_config


def test_load_required_config_reads_manifest(tmp_path):
    data = load_required_config()
    assert "runtime" in data
    assert any(item.startswith("python") for item in data["runtime"])


def test_create_virtual_environment_copies_manifest(tmp_path):
    env_dir = tmp_path / "env"
    create_virtual_environment(env_dir)
    assert (env_dir / "pyvenv.cfg").exists()
    manifest_path = env_dir / "sapl-required.yaml"
    assert manifest_path.exists()
    manifest = load_required_config(manifest_path)
    assert "tooling" in manifest
