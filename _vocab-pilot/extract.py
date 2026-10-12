import os,re,sys,collections,json
root=sys.argv[1]
STOP=set("""a an the and or of to in on for with by from at as is are be been being this that these those it its you your we our can will may must should would could not no do does did if then than so such into over under about after before between through using use used via all any each more most other some only also how what when where which who why new see following example examples step steps learn article information see note tip important warning following create get set run make need want lets let use one two first next value values file files name names type types list data""".split())
def clean(t):
    t=re.sub(r'^---\n.*?\n---\n','',t,flags=re.S)
    t=re.sub(r'```.*?```','',t,flags=re.S)
    t=re.sub(r'`[^`]*`',' | ',t)
    t=re.sub(r'\[!INCLUDE[^\]]*\]\([^)]*\)','',t)
    t=re.sub(r'!\[[^\]]*\]\([^)]*\)','',t)
    t=re.sub(r'\[([^\]]*)\]\([^)]*\)',r'\1',t)
    t=re.sub(r'<[^>]+>',' ',t)
    t=re.sub(r'https?://\S+',' ',t)
    return t
df=collections.Counter(); tf=collections.Counter(); head=collections.Counter(); forms=collections.defaultdict(collections.Counter)
N=0
for r,d,f in os.walk(root):
    for fn in f:
        if not fn.endswith('.md'): continue
        raw=open(os.path.join(r,fn),encoding='utf-8',errors='ignore').read()
        fm=re.match(r'---\n(.*?)\n---',raw,re.S)
        title=''
        if fm:
            m=re.search(r'^title:\s*(.*)$',fm.group(1),re.M); title=m.group(1) if m else ''
        t=clean(raw); N+=1
        heads=' | '.join(re.findall(r'^#{1,4}\s+(.*)$',t,re.M)+[title])
        seen=set()
        for src,text in (('body',t),('head',heads)):
            for seg in re.split(r'[.,;:!?()\[\]|"“”\n*_>#/=]+',text):
                w=re.findall(r"[A-Za-z][A-Za-z0-9+\-']*",seg)
                for n in range(1,5):
                    for i in range(len(w)-n+1):
                        g=w[i:i+n]
                        if g[0].lower() in STOP or g[-1].lower() in STOP: continue
                        if n==1 and (len(g[0])<4): continue
                        surf=' '.join(g); key=re.sub(r'[-\s]+',' ',surf.lower())
                        if src=='head': head[key]+=1; continue
                        tf[key]+=1; forms[key][surf]+=1; seen.add(key)
        for k in seen: df[k]+=1
out=[]
for k,c in df.items():
    if c<8: continue
    nw=len(k.split())
    out.append((k,c,tf[k],head[k],nw,forms[k].most_common(4)))
json.dump({'N':N,'terms':out},open(os.path.expanduser('~/kw/ml_terms.json'),'w'))
print(N,len(out))
