#!/usr/bin/env python3
"""Build /<lang>/index.html (localized link-preview tags) from index.html. Run from the repo root after any edit to index.html."""
import os,re,html,sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from lang_cards import CARDS
src=open('index.html',encoding='utf-8').read()
e=lambda x:html.escape(x,quote=True)
def one(pat,new,s):
    s2,n=re.subn(pat,lambda m:new,s,count=1,flags=re.S)
    assert n==1,pat
    return s2
import json
def grab(s):
    g=lambda pat:html.unescape(re.search(pat,s,re.S).group(1))
    return {'t':g(r'<title>(.*?)</title>'),'d':g(r'<meta name="description" content="(.*?)">'),'u':g(r'<link rel="canonical" href="(.*?)">'),'ot':g(r'<meta property="og:title" content="(.*?)">'),'od':g(r'<meta property="og:description" content="(.*?)">'),'oi':g(r'<meta property="og:image" content="(.*?)">'),'oa':g(r'<meta property="og:image:alt" content="(.*?)">'),'tt':g(r'<meta name="twitter:title" content="(.*?)">'),'td':g(r'<meta name="twitter:description" content="(.*?)">'),'ti':g(r'<meta name="twitter:image" content="(.*?)">')}
CD={'en':grab(src)}
for code,(hl,loc,name,tag,stats,title,ogt,desc,rtl) in CARDS.items():
    d=f'https://visiblebible.org/{code}/'; img=f'https://visiblebible.org/og-{code}.png'
    s=src
    s=one(r'<html lang="en">',f'<html lang="{hl}" dir="{"rtl" if rtl else "ltr"}" data-lang="{code}" data-base="../">',s)
    s=one(r'<title>.*?</title>',f'<title>{e(title)}</title>',s)
    s=one(r'<meta name="description" content=".*?">',f'<meta name="description" content="{e(desc)}">',s)
    s=one(r'<link rel="canonical" href=".*?">',f'<link rel="canonical" href="{d}">',s)
    s=one(r'<meta property="og:site_name" content=".*?">',f'<meta property="og:site_name" content="{e(name)}">\n<meta property="og:locale" content="{loc}">',s)
    s=one(r'<meta property="og:title" content=".*?">',f'<meta property="og:title" content="{e(ogt)}">',s)
    s=one(r'<meta property="og:description" content=".*?">',f'<meta property="og:description" content="{e(desc)}">',s)
    s=one(r'<meta property="og:url" content=".*?">',f'<meta property="og:url" content="{d}">',s)
    s=one(r'<meta property="og:image" content=".*?">',f'<meta property="og:image" content="{img}">',s)
    s=one(r'<meta property="og:image:alt" content=".*?">',f'<meta property="og:image:alt" content="{e(name+": "+tag+". "+stats.replace("  "," "))}">',s)
    s=one(r'<meta name="twitter:image" content=".*?">',f'<meta name="twitter:image" content="{img}">',s)
    s=one(r'<meta name="twitter:title" content=".*?">',f'<meta name="twitter:title" content="{e(ogt)}">',s)
    s=one(r'<meta name="twitter:description" content=".*?">',f'<meta name="twitter:description" content="{e(desc)}">',s)
    s=s.replace('url(fonts/','url(../fonts/')
    os.makedirs(code,exist_ok=True)
    open(f'{code}/index.html','w',encoding='utf-8').write(s)
    CD[code]=grab(s)
open('data/cards.json','w',encoding='utf-8').write(json.dumps(CD,ensure_ascii=False,separators=(',',':')))
# sitemap
urls=['','feedback.html']+[c+'/' for c in CARDS]
alts=''.join(f'<xhtml:link rel="alternate" hreflang="{h}" href="https://visiblebible.org/{p}"/>' for h,p in [('en',''),('x-default','')]+[({'zh':'zh-Hans','zht':'zh-Hant'}.get(c,c),c+'/') for c in CARDS])
out='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
for u in urls:
    out+=f'<url><loc>https://visiblebible.org/{u}</loc>'+(alts if u=='' or u.endswith('/') else '')+'</url>\n'
out+='</urlset>\n'
open('sitemap.xml','w',encoding='utf-8').write(out)
print('built',len(CARDS),'pages')
