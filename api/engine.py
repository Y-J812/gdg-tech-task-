import re
from collections import Counter
DEFAULT_TOPICS=[
{"name":"Spectroscopy","keywords":["spectroscopy","beer lambert","lambert beer","colorimetry","uv-vis","uv vis","nmr","mass spectroscopy"],"difficulty":3},
{"name":"Chromatography","keywords":["chromatography","thin layer","tlc"],"difficulty":3},
{"name":"Thermodynamics","keywords":["thermodynamics","enthalpy","internal energy","steady flow","control volume","first law"],"difficulty":4},
{"name":"Semiconductors","keywords":["semiconductor","pn junction","zener","diode","rectifier","clipper","clamper","led"],"difficulty":3},
{"name":"Engineering Materials","keywords":["polymer","cement","glass","refractory","nanomaterial"],"difficulty":2},
{"name":"Manufacturing Processes","keywords":["casting","forging","rolling","extrusion","welding","metal forming"],"difficulty":3},
{"name":"Communication Skills","keywords":["communication","barriers","precis","comprehension","non-verbal"],"difficulty":2}]
def parse_syllabus(text):
 out=[]
 for line in text.splitlines():
  p=[x.strip() for x in re.split(r"\s*\|\s*",line.strip())]
  if len(p)>=2 and p[0] and p[1]:
   m=re.search(r"\d+",p[2]) if len(p)>2 else None
   out.append({"name":p[0],"keywords":[x.strip().lower() for x in p[1].split(",") if x.strip()],"difficulty":max(1,min(5,int(m.group()))) if m else 3})
 return out or DEFAULT_TOPICS
def parse_questions(text):
 out=[]
 for line in text.splitlines():
  line=line.strip()
  if len(line)<8 or line.lower().startswith(("question paper","subject:","semester:","year:")): continue
  y=re.search(r"\b(20\d{2})\b",line); m=re.search(r"\b(\d{1,2})\s*(?:marks?|m)\b",line,re.I)
  out.append({"text":line,"year":int(y.group(1)) if y else None,"marks":max(1,min(30,int(m.group(1)))) if m else 5})
 return out
def analyse(question_text,syllabus_text="",hours=10):
 topics=parse_syllabus(syllabus_text); qs=parse_questions(question_text)
 if not qs: raise ValueError("No question lines found. Paste one question per line.")
 stats={t["name"]:{"frequency":0,"marks":0,"years":Counter(),"difficulty":t["difficulty"]} for t in topics}; unmatched=0
 for q in qs:
  ranked=[]
  for t in topics:
   hits=sum(1 for k in t["keywords"] if k and k in q["text"].lower())
   if hits: ranked.append((hits,t))
  if not ranked: unmatched+=1; continue
  ranked.sort(key=lambda x:x[0],reverse=True); s=stats[ranked[0][1]["name"]]
  s["frequency"]+=1;s["marks"]+=q["marks"]
  if q["year"]: s["years"][q["year"]]+=1
 maxf=max([x["frequency"] for x in stats.values()]+[1]); maxm=max([x["marks"] for x in stats.values()]+[1])
 years=sorted({y for s in stats.values() for y in s["years"]}); results=[]
 for name,s in stats.items():
  score=round(100*(.45*s["frequency"]/maxf+.35*s["marks"]/maxm+.15*(len(s["years"])/max(1,len(years)) if years else 0)+.05*s["difficulty"]/5),1)
  ys=sorted(s["years"]); conf="Low" if not s["frequency"] else ("High" if s["frequency"]>=3 and len(ys)>=2 else "Medium")
  results.append({"topic":name,"frequency":s["frequency"],"marks":s["marks"],"years":", ".join(map(str,ys)) or "Not specified","priority":score,"confidence":conf})
 results.sort(key=lambda x:x["priority"],reverse=True); active=[x for x in results if x["frequency"]] or results
 total=sum(max(1,x["priority"]) for x in active) or 1; mins=[{"topic":x["topic"],"minutes":max(20,round((max(1,x["priority"])/total)*int(hours)*6)),"priority":x["priority"]} for x in active]
 while sum(x["minutes"] for x in mins)>int(hours)*60:
  big=max(mins,key=lambda x:x["minutes"])
  if big["minutes"]<=20: break
  big["minutes"]-=10
 return {"results":results,"plan":mins,"questions_read":len(qs),"matched_questions":len(qs)-unmatched,"unmatched_questions":unmatched,"method":"Priority = 45% frequency + 35% marks + 15% year coverage + 5% topic difficulty. Heuristic only, not an exam prediction."}
