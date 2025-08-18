# αρχείο: install_el_en_models.py
import argostranslate.package as pkg
import argostranslate.translate as tr

print("Updating package index...")
pkg.update_package_index()
available = pkg.get_available_packages()

pairs = [("el","en"), ("en","el")]
for fr,to in pairs:
    try:
        p = next(p for p in available if p.from_code == fr and p.to_code == to)
    except StopIteration:
        print(f"Package {fr}->{to} not found in index.")
        continue
    print(f"Downloading {fr}->{to}...")
    path = p.download()
    print(f"Installing {fr}->{to} from {path}...")
    pkg.install_from_path(path)

# Έλεγχος εγκατάστασης (συμβατό με νεότερες εκδόσεις)
installed = tr.get_installed_languages()
summary = []
for lang in installed:
    try:
        targets = [t.to_lang.code for t in lang.get_translations()]
    except AttributeError:
        # fallback για πολύ παλιές εκδόσεις (σπάνιο)
        targets = []
    summary.append((lang.code, targets))

print("Installed languages:", summary)
print("Done.")
