"""Write output/howfast-calculator.html: the interactive version of the wage chart,
for the post as a Jekyll include. Every number comes from model.py; rerun this
after changing inputs so the calculator matches the static charts."""
import json
from pathlib import Path
from model import (VEHICLES, MEDIAN_WAGE, CAR_MILES_PER_YEAR, HOME_PARKING_PER_YEAR, NEW_CAR_ANNUAL_AT_15K,
                   NEW_CAR_PER_MILE, AAA_MILES, USED_CAR_5YR, USED_CAR_RUNNING_5YR, EDMUNDS_MILES,
                   STANDARD_DEDUCTION, FEDERAL_BRACKETS, FICA, STATE_TAX, HOURS_PER_YEAR,
                   door_to_door_mph, cost_per_mile, effective_mph)

HERE = Path(__file__).resolve().parent

def params():
    used_run = USED_CAR_RUNNING_5YR / 5 / EDMUNDS_MILES
    c, v = cost_per_mile(), door_to_door_mph()
    return {
        "median": MEDIAN_WAGE, "carMiles": CAR_MILES_PER_YEAR, "parking": HOME_PARKING_PER_YEAR,
        "cars": [{"name": "New car", "fixed": NEW_CAR_ANNUAL_AT_15K - NEW_CAR_PER_MILE * AAA_MILES,
                  "perMile": NEW_CAR_PER_MILE, "mph": v["New car"]},
                 {"name": "Used car", "fixed": USED_CAR_5YR / 5 - used_run * EDMUNDS_MILES,
                  "perMile": used_run, "mph": v["Used car"]}],
        "bikes": [{"name": "20 mph e-bike", "cost": c["E-bike, Class 2"], "mph": v["E-bike, Class 2"]},
                  {"name": "28 mph e-bike", "cost": c["E-bike, Class 3"], "mph": v["E-bike, Class 3"]}],
        "tax": {"deduction": STANDARD_DEDUCTION, "brackets": [[t if t != float("inf") else 1e12, r] for t, r in FEDERAL_BRACKETS],
                "fica": FICA, "state": STATE_TAX, "hours": HOURS_PER_YEAR},
    }

HTML = r"""<figure id="howfast-calc" markdown="0">
<style>
#howfast-calc{margin:2em 0;color:var(--text,#1c1c1c);--hf-ink:var(--text,#1c1c1c);--hf-accent:var(--accent,#b5763c);--hf-muted:var(--text-3,#8a8680);--hf-grid:var(--hairline,#dedad0)}
#howfast-calc .hf-label{font-family:var(--font-sans,inherit);font-size:15px;margin:0 0 6px}
#howfast-calc .hf-row{display:flex;align-items:center;gap:12px;margin:0 0 10px}
#howfast-calc input[type=range]{flex:1;accent-color:var(--hf-accent)}
#howfast-calc .hf-val{font-family:var(--font-sans,inherit);font-size:15px;min-width:4.5em;text-align:right;font-variant-numeric:tabular-nums}
#howfast-calc svg{width:100%;height:auto;display:block}
#howfast-calc svg text{font-family:var(--font-sans,inherit);fill:var(--hf-muted)}
#howfast-calc .hf-grid{stroke:var(--hf-grid);stroke-width:1}
#howfast-calc .hf-median{stroke:var(--hf-muted);stroke-dasharray:2 4}
#howfast-calc .hf-car{stroke:var(--hf-ink)}
#howfast-calc .hf-bike{stroke:var(--hf-accent)}
#howfast-calc text.hf-car{fill:var(--hf-ink);stroke:none}
#howfast-calc text.hf-bike{fill:var(--hf-accent);stroke:none}
#howfast-calc .hf-readout{font-family:var(--font-sans,inherit);font-size:15px;margin:8px 0 0}
#howfast-calc figcaption{font-family:var(--font-sans,inherit);font-size:13px;color:var(--hf-muted);margin-top:6px;line-height:1.45}
</style>
<label class="hf-label" for="hf-miles">Miles the car is driven a year</label>
<div class="hf-row"><input id="hf-miles" type="range" min="3000" max="20000" step="100"><span class="hf-val" id="hf-miles-out"></span></div>
<svg id="hf-svg" viewBox="0 0 400 380" role="img" aria-label="Effective speed in miles per hour by hourly wage for a new car, a used car and two e-bikes, on trips under 8 miles"></svg>
<div class="hf-readout" id="hf-readout" aria-live="polite"></div>
<figcaption>Miles per hour on trips under 8 miles, counting the after-tax hours worked to pay for each vehicle. The default is the US average of 10,900 miles a year.</figcaption>
<script>
(function(){
var P = __PARAMS__;
var W=400,H=380,L=40,R=98,T=12,B=44,X0=8,X1=80,Y1=14;
var NS="http://www.w3.org/2000/svg", svg=document.getElementById("hf-svg");
var slider=document.getElementById("hf-miles"), out=document.getElementById("hf-miles-out"), readout=document.getElementById("hf-readout");
function el(tag,a,txt){var e=document.createElementNS(NS,tag);for(var k in a)e.setAttribute(k,a[k]);if(txt!=null)e.textContent=txt;svg.appendChild(e);return e;}
function x(w){return L+(w-X0)/(X1-X0)*(W-L-R);}
function y(v){return T+(1-v/Y1)*(H-T-B);}
function range(a,b,step){var r=[];for(var v=a;!(v>b+1e-9);v+=step)r.push(v);return r;}
function fedTax(inc){var t=Math.max(inc-P.tax.deduction,0),tax=0,floor=0;P.tax.brackets.forEach(function(b){tax+=Math.max(Math.min(t,b[0])-floor,0)*b[1];floor=b[0];});return tax;}
function takeHome(w){var g=w*P.tax.hours;return (g-fedTax(g))/P.tax.hours-w*(P.tax.fica+P.tax.state);}
function series(miles){
  var s=P.cars.map(function(c){return {name:c.name,mph:c.mph,cost:(c.fixed+P.parking)/miles+c.perMile,cls:"hf-car"};});
  return s.concat(P.bikes.map(function(b){return {name:b.name,mph:b.mph,cost:b.cost,cls:"hf-bike"};}));
}
function eff(s,w){return 1/(1/s.mph+s.cost/takeHome(w));}
var dash={"New car":"","Used car":"9 5","20 mph e-bike":"9 5","28 mph e-bike":""};
function draw(){
  var miles=+slider.value; out.textContent=miles.toLocaleString();
  while(svg.firstChild)svg.removeChild(svg.firstChild);
  range(0,Y1,2).forEach(function(v){
    el("line",{x1:L,x2:W-R,y1:y(v),y2:y(v),"class":"hf-grid"});
    el("text",{x:L-8,y:y(v)+5,"text-anchor":"end","font-size":13},String(v));
  });
  el("text",{x:L+4,y:y(Y1)+5,"font-size":13},"mph");
  [20,40,60,80].forEach(function(w){el("text",{x:x(w),y:H-B+20,"text-anchor":"middle","font-size":13},"$"+w);});
  el("text",{x:(L+W-R)/2,y:H-6,"text-anchor":"middle","font-size":13},"Hourly wage, before tax");
  el("line",{x1:x(P.median),x2:x(P.median),y1:T,y2:H-B,"class":"hf-median"});
  el("text",{x:x(P.median)+5,y:H-B-8,"font-size":12},"Median wage");
  var S=series(miles), ends=[];
  S.forEach(function(s){
    var d=range(X0,X1,0.5).map(function(w,i){return (i?"L":"M")+x(w).toFixed(1)+","+y(Math.min(eff(s,w),Y1)).toFixed(1);}).join("");
    el("path",{d:d,fill:"none","class":s.cls,"stroke-width":3,"stroke-dasharray":dash[s.name],"stroke-linecap":"round"});
    ends.push({s:s,v:eff(s,X1)});
  });
  ends.sort(function(a,b){return a.v-b.v;});
  var last=null;
  ends.forEach(function(e){
    var py=y(Math.min(e.v,Y1));
    if(last!==null)py=Math.min(py,last-16);
    last=py;
    el("text",{x:W-R+6,y:py+4,"font-size":13,"class":e.s.cls},e.s.name);
  });
  var m=S.map(function(s){return s.name.charAt(0).toLowerCase()+s.name.slice(1)+" "+eff(s,P.median).toFixed(1);});
  readout.textContent="At the median wage ($"+P.median.toFixed(2)+"): "+m.join(", ")+" mph.";
}
slider.value=P.carMiles; slider.addEventListener("input",draw); draw();
})();
</script>
</figure>
"""

if __name__ == "__main__":
    p = params()
    html = HTML.replace("__PARAMS__", json.dumps(p))
    (HERE / "output").mkdir(exist_ok=True)
    (HERE / "output" / "howfast-calculator.html").write_text(html)
    print("Wrote output/howfast-calculator.html; median-wage check from model.py:")
    for v in VEHICLES:
        print(f"  {v:<16} {effective_mph(v, MEDIAN_WAGE):.1f} mph")
