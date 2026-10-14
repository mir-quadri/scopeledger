"""Build the downloadable source kit, excluding hosted identity, caches and this zip."""
from pathlib import Path
import zipfile
root=Path(__file__).resolve().parents[1]
out=root/'dist'/'scopeledger-source.zip'
exclude={'node_modules','__pycache__','.git','.openai'}
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED) as z:
 for p in sorted(root.rglob('*')):
  rel=p.relative_to(root)
  if not p.is_file() or any(part in exclude for part in rel.parts) or p==out:continue
  if p.name.startswith('.env') or p.suffix in {'.pyc','.sqlite3','.gz'}:continue
  z.write(p,'scopeledger/'+str(rel))
print(out)
