import argparse, hashlib
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument("--directory",required=True)
a=p.parse_args()
base=Path(a.directory)
lines=[]
for file in sorted(x for x in base.rglob("*") if x.is_file() and x.name!="model.sha256"):
    digest=hashlib.sha256(file.read_bytes()).hexdigest()
    lines.append(f"{digest}  {file.relative_to(base).as_posix()}")
out=base/"model.sha256"
out.write_text("\n".join(lines)+"\n",encoding="utf-8")
print(f"wrote {out} with {len(lines)} file checksums")
