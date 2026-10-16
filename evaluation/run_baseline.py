from pathlib import Path
import json,re,time,platform
root=Path(__file__).resolve().parents[1]
cases=json.loads((root/'evaluation/sample_questions.json').read_text())
stop=set('a an the is are of for to what when who how many must be per in'.split())
def tokens(s):return set(re.findall(r'[a-z0-9]+',s.lower()))-stop
chunks=[]
for p in sorted((root/'data/sample').glob('*.txt')):
 for n,line in enumerate(p.read_text().splitlines(),1):
  if n>1:chunks.append((p.name,n,line))
results=[]
for c in cases:
 start=time.perf_counter()
 ranked=sorted(chunks,key=lambda x:-len(tokens(c['question'])&tokens(x[2])))[:3]
 elapsed=(time.perf_counter()-start)*1000
 hit=any(x[0]==c['source'] and x[1]==c['source_line'] for x in ranked) if c['type']=='answerable' else None
 results.append({'id':c['id'],'top3':[{'source':x[0],'line':x[1]} for x in ranked],'hit_at_3':hit,'retrieval_ms':elapsed})
eligible=[r for r in results if r['hit_at_3'] is not None]
out={'method':'Token overlap ranking, top 3, sorted file and line order for ties','dataset':'Synthetic authored fixture; not an independent or client benchmark','python':platform.python_version(),'answerable_count':len(eligible),'hits_at_3':sum(r['hit_at_3'] for r in eligible),'hit_rate_at_3':sum(r['hit_at_3'] for r in eligible)/len(eligible),'abstention':'Not implemented in this retrieval-only baseline','results':results}
(root/'evaluation/baseline_results.json').write_text(json.dumps(out,indent=2))
print(json.dumps({k:v for k,v in out.items() if k!='results'},indent=2))
