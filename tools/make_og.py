#!/usr/bin/env python3
"""Make og-<lang>.png (1200x630) from og.png: keeps the book bars, redraws the text in each language. Run from the repo root."""
import os,sys,html,base64
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from lang_cards import CARDS
from playwright.sync_api import sync_playwright
bg=base64.b64encode(open('og.png','rb').read()).decode()
SERIF="'DejaVu Serif','Noto Serif CJK SC','Noto Serif CJK JP','Noto Serif CJK KR','Noto Serif CJK TC','FreeSerif',serif"
SANS="'DejaVu Sans','Noto Sans CJK SC','Noto Sans CJK JP','Noto Sans CJK KR','Noto Sans CJK TC','FreeSans',sans-serif"
CJK={'zh':'SC','zht':'TC','ja':'JP','ko':'KR'}
def page(code,name,tag,stats,rtl):
    ser=SERIF; san=SANS
    if code in CJK:
        f=f"'Noto Serif CJK {CJK[code]}'"; ser=f+','+SERIF; san=f"'Noto Sans CJK {CJK[code]}',"+SANS
    al='right' if rtl else 'left'; d='rtl' if rtl else 'ltr'
    box=lambda top,h,fs,color,wt,fam,txt:f'<div class="fit" style="top:{top}px;height:{h}px;font-size:{fs}px;color:{color};font-weight:{wt};font-family:{fam};line-height:{h}px">{html.escape(txt)}</div>'
    return f'''<html><body style="margin:0;width:1200px;height:630px;position:relative;overflow:hidden;background:#0e1424 url(data:image/png;base64,{bg})">
<style>.fit{{position:absolute;left:70px;width:1060px;white-space:nowrap;text-align:{al};direction:{d}}}.cv{{position:absolute;left:0;width:1200px;background:#0e1424}}</style>
<div class="cv" style="top:50px;height:225px"></div><div class="cv" style="top:515px;height:115px"></div>
{box(65,120,100,'#e8e6df',700,ser,name)}{box(190,56,38,'#b9bfd3',400,ser,tag)}
{box(525,56,38,'#df8a1d',700,san,stats)}{box(587,36,26,'#8f97b0',400,san,'visiblebible.org/'+code)}
</body></html>'''
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':1200,'height':630})
    for code,c in CARDS.items():
        name,tag,stats,rtl=c[2],c[3],c[4],c[8]
        pg.set_content(page(code,name,tag,stats,rtl))
        pg.evaluate('''()=>document.querySelectorAll('.fit').forEach(e=>{let s=parseFloat(e.style.fontSize);while(e.scrollWidth>1060&&s>14){s-=1;e.style.fontSize=s+'px'}})''')
        pg.screenshot(path=f'og-{code}.png')
    b.close()
print('ok')
