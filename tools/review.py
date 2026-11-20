import json,re,sys
from pathlib import Path

def load(folder, table):
    path=Path(folder)/f'{table}.json'
    data = json.loads(path.read_text(encoding='utf-8')) if path.is_file() else {}
    return data.get('strings', data)

def brief(s):
    return s.replace('\r','').replace('\n',' / ')

if __name__ == '__main__':
    table=sys.argv[1]
    en,ja,th=(load(folder,table) for folder in ('source/en','source/ja','th'))
    pattern=re.compile(sys.argv[2] if len(sys.argv)>2 else '.',re.I)
    flags=sys.argv[3:]
    itemnames=load('source/en','item.'+{'20':'10','24':'10','25':'11','26':'12'}.get(table.split('.')[1],'0')) if table.startswith('item.') else {}
    seen=set()
    for k,e in en.items():
        t=th.get(k,'')
        name=itemnames.get(k,'')
        if ('missing' in flags and t) or ('existing' in flags and not t) or not pattern.search(' '.join((k,e,t,name))): continue
        if 'unique' in flags and (e,t) in seen: continue
        seen.add((e,t))
        print(k,name)
        print(brief(e))
        if 'ja' in flags: print(brief(ja.get(k,'')))
        if t: print(brief(t))
