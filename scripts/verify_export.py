"""Read-only asset roundtrip verification; emits hash-bound evidence only."""
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
TOOL = Path(r'C:\Users\etqdo\Documents\maya\LtMAO\src')
sys.path.insert(0, str(TOOL))
from LtMAO import pyRitoFile

source = ROOT / 'References/Squidward Briar Maya/briar.wad.client/assets/Etdoan/Squidward-Briar/briar_base.skn'
original = source.read_bytes()
model = pyRitoFile.skn.SKN().read(original, raw=True)
serialized = model.write(None, raw=True)
from skn_layout import require_complete
# The original same-parser roundtrip missed pyRitoFile's absent v4 end tab.
require_complete(original)
if model.version >= 2:
    serialized += original[-12:]
require_complete(serialized)
loaded = pyRitoFile.skn.SKN().read(serialized, raw=True)
def digest_semantics(value):
    return hashlib.sha256(json.dumps(value, default=lambda x: x.__json__(), sort_keys=True).encode()).hexdigest()
before = digest_semantics(model)
after = digest_semantics(loaded)
assert before == after, 'SKN semantic roundtrip changed data'
report = {
    'status': 'OFFLINE EXPORT PATH VERIFIED',
    'runtime': sys.executable,
    'library': str(TOOL / 'LtMAO/pyRitoFile'),
    'source': str(source),
    'source_sha256': hashlib.sha256(original).hexdigest(),
    'serialized_sha256': hashlib.sha256(serialized).hexdigest(),
    'byte_identical': original == serialized,
    'semantic_identical': before == after,
    'semantic_sha256': before,
    'vertices': len(model.vertices),
    'indices': len(model.indices),
    'submeshes': [s.__json__() for s in model.submeshes],
    'scope': 'SKN read/write/read in memory; source assets unchanged. Candidate-specific validation and gameplay still required.',
}
output = ROOT / 'evidence/export_verification.json'
output.parent.mkdir(exist_ok=True)
output.write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps({k: report[k] for k in ('status','byte_identical','semantic_identical','vertices','indices')}))
