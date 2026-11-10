from pathlib import Path
import pytest
from scripts.preflight import pinned_requirements


def test_includes_and_markers(tmp_path):
    (tmp_path / 'requirements.txt').write_text('# comment\n-r lock.txt\n')
    (tmp_path / 'lock.txt').write_text('pypdf==6.21.1\nuvloop==0.23.0; sys_platform == "never"\n')
    assert list(pinned_requirements(tmp_path / 'requirements.txt')) == [('pypdf', '6.21.1')]


def test_cyclic_and_unpinned_inputs_rejected(tmp_path):
    p = tmp_path / 'requirements.txt'
    p.write_text('-r requirements.txt\n')
    with pytest.raises(ValueError, match='Cyclic'):
        list(pinned_requirements(p))
    p.write_text('pypdf>=6\n')
    with pytest.raises(ValueError, match='exact'):
        list(pinned_requirements(p))


def test_deployment_entrypoint_can_be_checked():
    root = Path(__file__).resolve().parents[1]
    pins = dict(pinned_requirements(root / 'requirements.txt'))
    assert pins['pyarrow'] == '24.0.0'
    assert pins['streamlit'] == '1.66.0'
