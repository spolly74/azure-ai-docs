"""Generate a Vale substitution rule from a SKOS vocabulary.

Convention: skos:hiddenLabel = a form to flag (misspelling, casing error, retired name).
            skos:altLabel    = an acceptable synonym; not flagged.
Usage: python3 vocab_to_vale.py <vocabulary.ttl> <output Terms.yml>
"""
import re, sys
import rdflib
from rdflib.namespace import SKOS, RDF

def sentence_case_only(variant, pref):
    # "Workspace" vs "workspace": the term at the start of a sentence, not an error
    return variant != pref and variant[:1].lower() + variant[1:] == pref

def main(src, out):
    g = rdflib.Graph(); g.parse(src, format="turtle")
    swap, skipped = {}, []
    for c in sorted(g.subjects(RDF.type, SKOS.Concept)):
        notes = [str(s) for s in g.objects(c, SKOS.scopeNote)]
        if any(n.startswith("Grouping concept") for n in notes):
            continue
        pref = str(next(g.objects(c, SKOS.prefLabel)))
        alts = [str(a) for a in g.objects(c, SKOS.altLabel)]
        norm = lambda t: t.lower().replace("-", " ")
        for lab in sorted(str(l) for l in g.objects(c, SKOS.hiddenLabel)):
            # A casing or hyphen variant of an acceptable label gets that label
            # as its suggestion; anything else gets the preferred label.
            target = next((a for a in [pref] + alts if norm(a) == norm(lab)), pref)
            if sentence_case_only(lab, target):
                skipped.append(lab); continue
            key = re.escape(lab).replace("\\ ", " ").replace("\\-", "-")
            swap[key] = target
    lines = [
        "# Generated from the controlled vocabulary. Do not edit by hand;",
        "# change the vocabulary in VocBench, export it, and regenerate.",
        f"# Source: {src.split('/')[-1]}",
        "extends: substitution",
        "message: \"Use '%s' instead of '%s'.\"",
        "level: warning",
        "ignorecase: false",
        "action:",
        "  name: replace",
        "swap:",
    ] + [f'  "{k}": "{v}"' for k, v in sorted(swap.items(), key=lambda kv: kv[0].lower())]
    open(out, "w").write("\n".join(lines) + "\n")
    print(f"{len(swap)} substitutions written; {len(skipped)} sentence-case variants skipped")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
