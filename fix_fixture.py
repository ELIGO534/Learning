# fix_fixture.py
with open("datadump.json", "rb") as f:
    raw = f.read()

# Remove BOM if present
if raw.startswith(b'\xef\xbb\xbf'):
    raw = raw[3:]

with open("datadump_clean.json", "wb") as f:
    f.write(raw)
