import json
from pathlib import Path

def test_registry_index_has_minimum_fields():
    data = json.loads(Path("registry_index.json").read_text())
    assert "version" in data
    assert "packs" in data
