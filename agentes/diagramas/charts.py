import json, collections, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt, numpy as np
from matplotlib.patches import FancyBboxPatch
RED='#C8310E'; NAVY='#1A3A5C'; GREEN='#1E7B34'; ORG='#E39B2D'; BLUE='#2E75B6'; GRAY='#8C8C8C'
# ---- espectro de autonomía ----
fig,ax=plt.subplots(figsize=(12,4.3)); ax.set_xlim(0,12); ax.set_ylim(0,4.6); ax.axis('off')
nivs=[('LLM aumentado','Una llamada al modelo\n(con búsqueda o\nherramientas puntuales)','Explicar un error'),
      ('Flujo de trabajo','Pasos fijos definidos\npor el programador\n(cadena, router)','Historia → criterios\n→ pruebas (Lab 09)'),
      ('Agente','El LLM decide los pasos\nen un bucle con\nherramientas','Resolver un issue\n(este laboratorio)'),
      ('Multiagente','Varios agentes con roles\ny permisos distintos\nque colaboran','Planificar, ejecutar\ny revisar un PR')]
for i,(t,d,e) in enumerate(nivs):
    x=0.15+i*2.98; c=plt.cm.Reds(0.35+i*0.18)
    ax.add_patch(FancyBboxPatch((x,1.25),2.75,2.35,boxstyle="round,pad=0.02,rounding_size=0.1",fc=c,ec='white'))
    fc='white' if i>0 else '#222'
    ax.text(x+1.37,3.3,t,ha='center',va='center',fontsize=12.5,weight='bold',color=fc)
    ax.text(x+1.37,2.3,d,ha='center',va='center',fontsize=9.6,color=fc)
    ax.text(x+1.37,0.85,e,ha='center',va='center',fontsize=9,color='#333',style='italic')
ax.annotate('',xy=(11.9,4.1),xytext=(0.15,4.1),arrowprops=dict(arrowstyle='-|>',color=RED,lw=1.6))
ax.text(6,4.3,'Más autonomía y flexibilidad  →  más costo, latencia, riesgo y dificultad para probar',ha='center',fontsize=10.5,color=RED,weight='bold')
ax.text(6,0.2,'Regla práctica: use la opción más simple que resuelva el problema (Anthropic, 2024).',ha='center',fontsize=10,color=NAVY)
plt.savefig('img/espectro.png',dpi=200,bbox_inches='tight'); plt.close()
# ---- métricas reales de las trazas (dos rondas actor-crítico) ----
import pathlib
grupos=[('ejecutor','Ejecutor\nronda 1'),('revisor','Revisor\nronda 1'),('ejecutor_r2','Ejecutor\nronda 2'),('revisor_r2','Revisor\nronda 2')]
ev={k:[json.loads(l) for l in open(f'ej/trazas/{k}.jsonl',encoding='utf-8')] for k,_ in grupos}
perm=[sum(1 for e in ev[k] if e['tipo']=='accion' and not e['bloqueada']) for k,_ in grupos]
bloq=[sum(1 for e in ev[k] if e['tipo']=='accion' and e['bloqueada']) for k,_ in grupos]
ctx=[]
herr=collections.Counter(e['accion'] for k,_ in grupos for e in ev[k] if e['tipo']=='accion')
fig,axs=plt.subplots(1,2,figsize=(12.5,4.2),gridspec_kw={'width_ratios':[1.2,1.2]})
ax=axs[0]; x=np.arange(4)
ax.bar(x,perm,color=GREEN,label='Acciones permitidas')
ax.bar(x,bloq,bottom=perm,color=RED,label='Bloqueadas por la política')
for i_ in range(4): ax.text(i_,perm[i_]+bloq[i_]+0.15,f'{perm[i_]+bloq[i_]}',ha='center',fontsize=10,weight='bold')
ax.set_xticks(x); ax.set_xticklabels([g for _,g in grupos],fontsize=9.5); ax.set_ylabel('Número de acciones'); ax.set_ylim(0,10.5)
ax.axvline(1.5,color='#BBBBBB',ls='--',lw=1)
ax.legend(frameon=False,fontsize=9,loc='upper right'); ax.set_title('Acciones por agente y ronda',fontsize=12,weight='bold',color=NAVY)
ax=axs[1]; it=herr.most_common()
ax.barh([k for k,_ in it][::-1],[v for _,v in it][::-1],color=BLUE)
for i_,(k,v) in enumerate(it[::-1]): ax.text(v+0.05,i_,str(v),va='center',fontsize=10)
ax.set_title('Uso de herramientas (todas las rondas)',fontsize=12,weight='bold',color=NAVY); ax.set_xlabel('Llamadas'); ax.set_xlim(0,max(herr.values())+0.8)
for a_ in axs:
    for s_ in ['top','right']: a_.spines[s_].set_visible(False)
plt.tight_layout(); plt.savefig('img/metricas.png',dpi=200,bbox_inches='tight'); plt.close()
print(perm,bloq,dict(herr))
# ---- ruta de la unidad III ----
fig,ax=plt.subplots(figsize=(12,2.9)); ax.set_xlim(0,12.5); ax.set_ylim(0,3); ax.axis('off')
labs=[('Lab 09','Tema 12','Prompt\nEngineering',False),('Lab 10','Tema 13','Sistemas\nagénticos',True),('Lab 11','Tema 14','Protocolos y\ncontexto (MCP)',False),
      ('Lab 12','Tema 15','Desarrollo\nasistido por IA',False),('Lab 13','Tema 16','Pruebas, seguridad\ny evaluación',False)]
for i_,(l1,l2,l3,act) in enumerate(labs):
    x0=0.1+i_*2.5
    ax.add_patch(FancyBboxPatch((x0,0.35),2.25,2.2,boxstyle="round,pad=0.02,rounding_size=0.12",fc=RED if act else '#EEF2F8',ec=RED if act else NAVY,lw=1.4))
    c='white' if act else NAVY
    ax.text(x0+1.12,2.15,l1,ha='center',fontsize=12.5,weight='bold',color=c)
    ax.text(x0+1.12,1.8,l2,ha='center',fontsize=9.5,color=c)
    ax.text(x0+1.12,1.05,l3,ha='center',va='center',fontsize=10.5,color=c,weight='bold' if act else 'normal')
    if i_<4: ax.annotate('',xy=(x0+2.5,1.45),xytext=(x0+2.27,1.45),arrowprops=dict(arrowstyle='-|>',color=GRAY))
ax.text(6.25,0.05,'Unidad III — Capítulo IV: IA en la Ingeniería de Software. Este laboratorio introduce lo que los siguientes profundizan.',ha='center',fontsize=9.5,color='#444',style='italic')
plt.savefig('img/ruta.png',dpi=200,bbox_inches='tight'); plt.close()
# ---- semana ----
fig,ax=plt.subplots(figsize=(11,3.6))
dias=['Lun 16/11','Mar 17/11','Mié 18/11','Jue 19/11','Vie 20/11','Sáb 21/11']
tasks=[('Lectura previa',0,1,BLUE),('Sesión presencial de 100 min (según grupo)',1,5,RED),('Trabajo autónomo: E4–E8',1,5.6,'#7F9CC4'),('',5.6,6,GREEN)]
for i,(t,s,e,c) in enumerate(tasks[::-1]):
    ax.barh(i,e-s,left=s,color=c,edgecolor='white',height=0.6); ax.text(s+0.08,i,t,va='center',color='white',fontsize=10,weight='bold')
ax.text(5.55,0,'Entrega 23:59 (tag v1.0-agentes)',ha='right',va='center',fontsize=10,weight='bold',color=GREEN)
for x_,lab in [(1.5,'G1 Mar\n11:30'),(2.5,'G2 Mié\n18:30'),(4.5,'G3 Vie\n14:00')]: ax.text(x_,3.52,lab,ha='center',va='bottom',fontsize=8.5,color=RED)
ax.set_xticks([i+0.5 for i in range(6)]); ax.set_xticklabels(dias,fontsize=10); ax.set_xlim(0,6); ax.set_yticks([]); ax.set_ylim(-0.6,4.1)
for s in ['top','right','left']: ax.spines[s].set_visible(False)
for i in range(7): ax.axvline(i,color='#DDDDDD',lw=0.8,zorder=0)
ax.set_title('Plan de la semana 13: 16/11/2026 – 21/11/2026',fontsize=13,weight='bold',color=NAVY,pad=22)
plt.savefig('img/semana.png',dpi=200,bbox_inches='tight'); plt.close()
