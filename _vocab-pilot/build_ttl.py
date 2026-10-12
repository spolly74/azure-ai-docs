import os,re,sys,datetime
sys.path.insert(0,os.path.expanduser('~/kw')); from concepts import C
try:
    from concepts import NOTES
except ImportError:
    NOTES={}
corpus=sys.argv[1]; out=sys.argv[2]
NS="https://vocab.example.org/azure-ml/"
docs=[]
for r,d,f in os.walk(corpus):
    for fn in f:
        if fn.endswith('.md'):
            t=open(os.path.join(r,fn),encoding='utf-8',errors='ignore').read()
            t=re.sub(r'```.*?```','',t,flags=re.S); docs.append(t)
ids={c[0] for c in C}
for c in C:
    for ref in ([c[4]] if c[4] else [])+c[5]: assert ref in ids, (c[0],ref)
def esc(s): return s.replace('\\','\\\\').replace('"','\\"')
def count(labels):
    pats=[re.compile(r'(?<![\w-])'+re.escape(l).replace(r'\ ',r'[\s-]')+r's?(?![\w-])',re.I) for l in labels]
    return sum(1 for t in docs if any(p.search(t) for p in pats))
narrow={}
for c in C:
    if c[4]: narrow.setdefault(c[4],[]).append(c[0])
rel={c[0]:list(c[5]) for c in C}
for c in C:
    for r in c[5]:
        if c[0] not in rel[r]: rel[r].append(c[0])
today=datetime.date.today().isoformat()
L=[f"@prefix skos: <http://www.w3.org/2004/02/skos/core#> .",f"@prefix dct: <http://purl.org/dc/terms/> .",f"@prefix : <{NS}> .","",
 ":scheme a skos:ConceptScheme ;",'  skos:prefLabel "Azure Machine Learning documentation vocabulary (pilot)"@en ;',
 f'  dct:created "{today}" ;',
 '  skos:editorialNote "Draft generated from term extraction of articles/machine-learning in azure-ai-docs. All concepts need review."@en ;']
tops=[c[0] for c in C if not c[4]]
L.append('  skos:hasTopConcept '+', '.join(':'+t for t in tops)+' .'); L.append('')
rows=[]
for cid,pref,alts,hidden,broader,related,note in C:
    group = note and note.startswith('Grouping concept')
    n=None if group else count([pref]+alts+hidden)
    p=[f":{cid} a skos:Concept",f"  skos:inScheme :scheme",f'  skos:prefLabel "{esc(pref)}"@en']
    p+= [f'  skos:altLabel "{esc(a)}"@en' for a in alts]
    p+= [f'  skos:hiddenLabel "{esc(h)}"@en' for h in hidden]
    if broader: p.append(f"  skos:broader :{broader}")
    else: p.append("  skos:topConceptOf :scheme")
    p+= [f"  skos:narrower :{x}" for x in narrow.get(cid,[])]
    p+= [f"  skos:related :{x}" for x in rel[cid]]
    if n is not None: p.append(f'  skos:editorialNote "Pilot count: appears in {n} of {len(docs)} articles in articles/machine-learning (any label)."@en')
    if note: p.append(f'  skos:editorialNote "{esc(note)}"@en')
    for k,v in NOTES.get(cid,{}).items(): p.append(f'  skos:{k} "{esc(v)}"@en')
    L.append(' ;\n'.join(p)+' .\n'); rows.append((pref,n))
open(out,'w').write('\n'.join(L))
print(len(C),'concepts;',len(tops),'top concepts')
for pref,n in rows: print(n,pref)
