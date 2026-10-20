#!/usr/bin/env python3
"""Write guides-src/ref-vin-decoder.json, the spec for the VIN decoder page.

The letter tables below are the single source for both the in-browser decoder (embedded as JSON
in the page) and the static "how it's decoded" tables, so the two can't drift apart.
Source of the data: Aston_Guru/references/vin-decoding.md (NHTSA vPIC Part 565 filings plus
real VINs). Then build the page as usual:

    python3 scripts/build_vin_spec.py && python3 scripts/build_guides.py
"""
import html, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
US, REAL, BOTH = "US filing", "real VIN", "US filing + real VINs"

YEARS = {**{str(d): 2000 + d for d in range(5, 10)}, **{c: 2010 + i for i, c in enumerate("ABCDEFGHJK")}}

RESTRAINT = {
    "old": {"A": ("VH1 seat (DB9, DBS) · 3-point belts with pyro pretensioners", BOTH),
            "B": ("VH2 seat (Vantage) · 3-point belts with pyro pretensioners", BOTH)},
    "new": {"E": ("Front belts with pretensioners, side airbags in the seats (two-seaters)", BOTH),
            "F": ("Adds rear 3-point belts and door curtain airbags (2+2 cars)", BOTH),
            "H": ("Curtain airbags for both rows, rear pretensioners (Rapide)", BOTH)},
}

# gearbox letter -> (meaning, source), per era; first matching era wins
GEARBOX = [
    (2005, 2009, {"B": ("Manual (Graziano 6-speed)", BOTH), "D": ("Automatic (ZF 6HP26 Touchtronic)", BOTH),
                  "F": ("Sportshift automated manual (V8 Vantage, from 2007)", BOTH),
                  "C": ("Automatic (ZF 6HP26 Touchtronic), UK/EU code", REAL)}),
    (2010, 2012, {"B": ("Manual (Graziano 6-speed)", US), "D": ("Automatic (ZF 6HP26 Touchtronic)", BOTH),
                  "F": ("Sportshift automated manual", US), "C": ("Automatic (ZF 6HP26 Touchtronic), UK/EU code", REAL)}),
    (2013, 2014, {"B": ("6-speed manual", US), "D": ("6-speed automatic (ZF 6HP26 Touchtronic)", US),
                  "K": ("7-speed automated manual (Sportshift II / III)", US),
                  "C": ("Automatic (ZF 6HP26 Touchtronic), UK/EU code", REAL)}),
    (2015, 2016, {"B": ("6-speed manual", US), "D": ("6-speed automatic (ZF 6HP26 Touchtronic)", US),
                  "K": ("7-speed automated manual (Sportshift II / III)", US),
                  "M": ("8-speed automatic (ZF Touchtronic III)", US)}),
    (2017, 2019, {"B": ("6-speed manual", US), "S": ("7-speed manual (V12 Vantage S dog-leg, AMSHIFT)", BOTH),
                  "K": ("7-speed Sportshift automated manual", US), "M": ("8-speed automatic (ZF Touchtronic III)", BOTH)}),
]

MODEL = {
    "old": {"01": ("DB9", "Coupé"), "02": ("DB9", "Volante"), "03": ("V8 Vantage", "Coupé"),
            "04": ("V8 Vantage", "Roadster"), "05": ("DBS", "Coupé")},
    "new": {"AA": ("DB9", "Coupé"), "AB": ("DB9", "Volante"), "AC": ("DB9", "Coupé"), "AD": ("DB9", "Volante"),
            "AE": ("DB9", "Coupé"), "AF": ("DB9", "Volante"), "AG": ("DB9", "Coupé"), "AH": ("DB9", "Volante"),
            "BA": ("V8 Vantage", "Coupé"), "BD": ("V8 Vantage", "Coupé"), "BB": ("V8 Vantage", "Roadster"),
            "BE": ("V8 Vantage", "Roadster"), "BC": ("V12 Vantage", "Coupé"), "BF": ("V12 Vantage", "Roadster"),
            "CA": ("DBS", "Coupé"), "CB": ("DBS", "Coupé"), "CC": ("DBS", "Volante"),
            "CE": ("Vanquish", "Coupé"), "CF": ("Vanquish", "Coupé"), "CG": ("Vanquish", "Volante"),
            "CH": ("Vanquish", "Volante"), "DA": ("Rapide", "Four-door"), "DB": ("Rapide", "Four-door"),
            "DH": ("Rapide", "Four-door (2019, Rapide AMR)"), "EA": ("Virage", "Coupé"), "EC": ("Virage", "Coupé"),
            "EB": ("Virage", "Volante"), "ED": ("Virage", "Volante")},
}
PLATFORM = {"A": "DB9 (VH1)", "B": "Vantage (VH2)", "C": "DBS, then Vanquish from 2014 (VH3)", "D": "Rapide (VH4)",
            "E": "Virage (VH1)"}

# engine letter -> (code, description, bhp, years, source)
ENGINE = {
    "old": {"A": ("AM04", "5.9 V12 (DB9)", 450, "2005–09", BOTH),
            "B": ("AM05", "4.3 V8 (V8 Vantage)", 380, "2006–08", BOTH),
            "C": ("AM07", "4.7 V8 (V8 Vantage)", 420, "2009", REAL),
            "D": ("AM08", "5.9 V12 (DBS)", 510, "2009", US),
            "E": ("AM09", "5.9 V12 (DB9)", 470, "2009", REAL),
            "G": ("GAM05", "4.3 V8, N400 spec (V8 Vantage N400)", 400, "2008", REAL)},
    "new": {"C": ("AM07", "4.7 V8 (V8 Vantage)", 420, "2010", US),
            "D": ("AM08", "5.9 V12 (DBS)", 510, "2010–12", US),
            "E": ("AM09", "5.9 V12 (DB9)", 470, "2010–12", BOTH),
            "F": ("AM10", "5.9 V12 (V12 Vantage)", 510, "2011–13", US),
            "J": ("AM16", "5.9 V12 (Rapide)", 470, "2010–12", US),
            "K": ("AM14", "4.7 V8 (V8 Vantage)", 420, "2011–18", US),
            "L": ("AM15", "4.7 V8, S spec (V8 Vantage S)", 430, "2012–18", US),
            "M": ("AM11", "5.9 V12, DB9 tune", 510, "2013–16", BOTH),
            "N": ("AM25", "5.9 V12 (Virage)", 490, "2012", US),
            "P": ("AM11", "5.9 V12, Vanquish tune", 565, "2014", US),
            "T": ("AM11", "5.9 V12, Rapide S tune", 550, "2014", US),
            "R": ("AM28", "5.9 V12 (V12 Vantage S)", 565, "2015–18", BOTH),
            "S": ("AM29", "5.9 V12, Rapide S tune", 552, "2015–18", BOTH),
            "U": ("AM29", "5.9 V12, Vanquish tune", 568, "2015–17", US),
            "Z": ("AM27", "5.9 V12 (Vanquish S)", 595, "2018–19", US)},
}
NOT_VH = {"V": "AE31 5.2 twin-turbo V12 (DB11 generation)", "W": "AMG 4.0 twin-turbo V8 (DB11 generation)"}

PLANT = {"G": ("Gaydon, Warwickshire", BOTH), "A": ("Graz, Austria (Magna Steyr; early Rapides)", US)}
SERIES = {"A": ("DB9 coupé", BOTH), "B": ("DB9 Volante", BOTH), "C": ("Vantage", BOTH), "E": ("DBS", US),
          "F": ("Rapide (seen on a 2017 car)", REAL), "S": ("V12 Vantage S Roadster (seen on a 2017 car)", REAL)}

EXAMPLE = "SCFAD01A35GA01906"   # Steve McEvoy's 2005 DB9, published on aston1936.com

DATA = {"years": YEARS, "restraint": RESTRAINT, "gearbox": GEARBOX, "model": MODEL, "platform": PLATFORM,
        "engine": ENGINE, "notVH": NOT_VH, "plant": PLANT, "series": SERIES, "example": EXAMPLE}


def tag(src):
    cls = "tag-expected" if src != REAL else "tag-sympathy"
    return f'<span class="tag {cls}">{src}</span>'


WIDGET = r"""<style>
  .vin-box { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 22px 24px; margin: 8px 0 24px; }
  .vin-row { display: flex; gap: 10px; flex-wrap: wrap; }
  .vin-row input { flex: 1 1 320px; min-width: 0; background: var(--bg); border: 1px solid var(--border); border-radius: 6px; color: var(--text);
    font-family: 'DM Mono', monospace; font-size: 17px; letter-spacing: 0.12em; padding: 12px 14px; text-transform: uppercase; }
  .vin-row input:focus { outline: none; border-color: var(--accent); }
  .vin-row button { background: var(--accent); color: var(--bg); border: 0; border-radius: 6px; font-family: 'DM Mono', monospace; font-size: 12px;
    letter-spacing: 0.12em; text-transform: uppercase; padding: 12px 18px; cursor: pointer; }
  .vin-row button.alt { background: transparent; color: var(--text-muted); border: 1px solid var(--border); }
  .vin-note { font-family: 'DM Mono', monospace; font-size: 10px; color: var(--text-dim); letter-spacing: 0.08em; text-transform: uppercase; margin-top: 10px; }
  .vin-summary { font-family: 'DM Serif Display', serif; font-size: 24px; color: var(--accent); margin: 18px 0 4px; }
  .vin-msg { margin-top: 14px; }
  .vin-chars { font-family: 'DM Mono', monospace; color: var(--accent); white-space: nowrap; }
</style>
<div class="vin-box">
  <form id="vin-form" class="vin-row" autocomplete="off">
    <input id="vin-in" maxlength="25" placeholder="SCF…  17 characters" aria-label="VIN" spellcheck="false">
    <button type="submit">Decode</button>
    <button type="button" class="alt" id="vin-eg">Try an example</button>
  </form>
  <div class="vin-note">Decoded in your browser · your VIN isn't sent anywhere</div>
  <div id="vin-out"></div>
</div>
<noscript><p>The decoder needs JavaScript. The tables further down this page decode a VIN by hand.</p></noscript>
<script>
(function(){
var D=__DATA__;
var W=[8,7,6,5,4,3,2,10,0,9,8,7,6,5,4,3,2], T={};
"0123456789".split("").forEach(function(c,i){T[c]=i;});
"ABCDEFGH".split("").forEach(function(c,i){T[c]=i+1;});
"JKLMN".split("").forEach(function(c,i){T[c]=i+1;}); T.P=7; T.R=9;
"STUVWXYZ".split("").forEach(function(c,i){T[c]=i+2;});
function el(t,cls,txt){var e=document.createElement(t); if(cls)e.className=cls; if(txt!=null)e.textContent=txt; return e;}
function tagEl(src){return el("span","tag "+(src==="real VIN"?"tag-sympathy":"tag-expected"),src);}
function unk(){return el("span","tag tag-derived","not yet confirmed");}
function check(v){var s=0; for(var i=0;i<17;i++)s+=T[v[i]]*W[i]; s%=11; return s===10?"X":String(s);}
function decode(raw){
  var out=document.getElementById("vin-out"); out.textContent="";
  var v=raw.toUpperCase().replace(/[\s-]/g,"");
  function msg(cls,txt){var m=el("div",cls+" vin-msg",txt); out.appendChild(m);}
  if(!v){return;}
  if(/[IOQ]/.test(v)){msg("warn-box","⚠ VINs never use the letters I, O or Q. Check for a 1 or a 0 instead.");return;}
  if(!/^[A-Z0-9]+$/.test(v)){msg("warn-box","⚠ A VIN only contains letters and numbers.");return;}
  if(v.length!==17){msg("warn-box","⚠ That's "+v.length+" characters. A VIN has exactly 17.");return;}
  if(v.slice(0,3)!=="SCF"){msg("warn-box","⚠ An Aston Martin VIN from this era starts with SCF. This one starts with "+v.slice(0,3)+".");return;}
  var yr=D.years[v[9]];
  if(!yr){msg("warn-box","⚠ Character 10 ("+v[9]+") isn't a 2005–2019 model-year code, so this isn't a VH-era car.");return;}
  var lay=yr<=2009?"old":"new", rows=[], summary={};
  function row(pos,chars,meaning,src){rows.push([pos,chars,meaning,src]);}
  row("1–3",v.slice(0,3),"Aston Martin Lagonda, UK (manufacturer code)","US filing + real VINs");
  var r=D.restraint[lay][v[3]]; row("4",v[3],r?r[0]:"Restraint / seat type",r?r[1]:null);
  var gb=null; D.gearbox.forEach(function(e){if(!gb&&yr>=e[0]&&yr<=e[1])gb=e[2];});
  var g=gb&&gb[v[4]]; row("5",v[4],g?"Gearbox: "+g[0]:"Gearbox",g?g[1]:null); if(g)summary.gearbox=g[0];
  var mk=v.slice(5,7), m=D.model[lay][mk];
  var mtxt=m?m[0]+" "+m[1]:(lay==="new"&&D.platform[v[5]]?"Platform "+D.platform[v[5]]+", body code "+v[6]:"Model and body");
  row("6–7",mk,mtxt,m?"US filing":null); if(m)summary.model=m;
  var e=D.engine[lay][v[7]];
  if(e){row("8",v[7],"Engine "+e[0]+": "+e[1]+", "+e[2]+" bhp",e[4]); summary.engine=e;}
  else if(lay==="new"&&D.notVH[v[7]]){row("8",v[7],"Engine: "+D.notVH[v[7]]+". Not a VH engine",null);}
  else row("8",v[7],"Engine",null);
  var cd=check(v), cdok=cd===v[8];
  row("9",v[8],cdok?"Check digit: correct":"Check digit: should be "+cd,cdok?"calculated":"error");
  row("10",v[9],"Model year "+yr,"US filing + real VINs");
  var p=D.plant[v[10]]; row("11",v[10],p?"Built in "+p[0]:"Plant",p?p[1]:null);
  var s=D.series[v[11]]; row("12",v[11],s?"Chassis series: "+s[0]:"Chassis series letter",s?s[1]:null);
  row("13–17",v.slice(12),"Serial number","US filing + real VINs");
  if(!cdok)msg("warn-box","⚠ The check digit doesn't match. Every real Aston VIN we've tested, UK and US, has a valid one, so this is most likely a typo. Check each character against the V5C or the windscreen plate.");
  var head=(summary.model?summary.model[0]+" "+summary.model[1]:"Aston Martin")+" · "+yr;
  out.appendChild(el("div","vin-summary",head));
  var bits=[]; if(summary.engine)bits.push(summary.engine[0]+" "+summary.engine[1]+", "+summary.engine[2]+" bhp"); if(summary.gearbox)bits.push(summary.gearbox);
  if(bits.length)out.appendChild(el("p",null,bits.join(" · ")));
  var wrap=el("div","table-wrap"), tb=el("table","mapping-table"), th=el("thead"), hr=el("tr");
  ["Position","Characters","Meaning","Source"].forEach(function(h){hr.appendChild(el("th",null,h));}); th.appendChild(hr); tb.appendChild(th);
  var body=el("tbody");
  rows.forEach(function(x){var tr=el("tr"); tr.appendChild(el("td",null,x[0])); tr.appendChild(el("td","vin-chars",x[1])); tr.appendChild(el("td",null,x[2]));
    var td=el("td"); if(x[3]==="error")td.appendChild(el("span","tag tag-real","mismatch")); else if(x[3]==="calculated")td.appendChild(el("span","tag tag-expected","calculated")); else if(x[3])td.appendChild(tagEl(x[3])); else td.appendChild(unk()); tr.appendChild(td); body.appendChild(tr);});
  tb.appendChild(body); wrap.appendChild(tb); out.appendChild(wrap);
  var links=[];
  if(summary.engine&&/V12/.test(summary.engine[1]))links.push(["ref-cylinder-numbering.html","V12 cylinder numbering and the twin engine ECUs"]);
  if(summary.gearbox&&/6HP26/.test(summary.gearbox))links.push(["ref-gearbox-service.html","ZF 6HP26 gearbox service"]);
  if(summary.model&&summary.model[0]==="DB9")links.push(["db9.html","More about the DB9"]);
  if(links.length){var ul=el("ul","plain-list"); links.forEach(function(l){var li=el("li"); var a=el("a",null,l[1]); a.href=l[0]; li.appendChild(a); ul.appendChild(li);});
    out.appendChild(el("h3",null,"Related on this site")); out.appendChild(ul);}
  if(rows.some(function(x){return !x[3];}))msg("info-box","ℹ \"Not yet confirmed\" means that letter isn't in Aston's US filing and hasn't turned up on a real VIN we've checked. It isn't an error. UK and European cars use a few letters that were never filed in the US.");
}
var f=document.getElementById("vin-form"), inp=document.getElementById("vin-in");
f.addEventListener("submit",function(ev){ev.preventDefault(); decode(inp.value);});
document.getElementById("vin-eg").addEventListener("click",function(){inp.value=D.example; decode(D.example);});
})();
</script>"""


def table(head, rows, title=None):
    b = {"table": {"head": head, "rows": rows}}
    if title:
        b["table"]["title"] = title
    return b


def main():
    e = html.escape
    eng_rows = []
    for lay, label in (("old", "2005–09"), ("new", "2010–18")):
        for k, (code, desc, bhp, yrs, src) in ENGINE[lay].items():
            eng_rows.append([label, f'<span class="code">{k}</span>', code, e(desc), f"{bhp} bhp", yrs, tag(src)])
    gb_rows = []
    for lo, hi, m in GEARBOX:
        for k, (txt, src) in m.items():
            gb_rows.append([f"{lo}–{hi if hi < 2019 else 2018}", f'<span class="code">{k}</span>', e(txt), tag(src)])
    old_models = [[f'<span class="code">{k}</span>', m, b] for k, (m, b) in MODEL["old"].items()]
    new_models = [[f'<span class="code">{k}</span>', m, e(b)] for k, (m, b) in MODEL["new"].items()]

    blocks = [
        {"p": ["Paste a VIN from a 2005–2018 Gaydon-era Aston Martin (DB9, V8 or V12 Vantage, DBS, Virage, Rapide or the 2012–18 Vanquish). "
               "It tells you the model and body, model year, gearbox, the engine's derivative code and power, where the car was built, "
               "and whether the check digit is right. The VIN is on the V5C, the plate at the base of the windscreen and the label in the door shut."]},
        {"raw": WIDGET.replace("__DATA__", json.dumps(DATA, ensure_ascii=False, separators=(",", ":")))},
        {"h2": "Why the VIN matters on these cars"},
        {"p": ["The engine number is stamped on the block, and on a V12 in a DB9 you won't see it without taking things apart. "
               "The 8th character of the VIN gives the same derivative code (AM04, AM09, AM11 and so on), and that decides which parts, "
               "software and settings apply. The 5th character tells you the gearbox, which settles questions such as whether a Vantage has "
               "the manual or the Sportshift, or whether a 2017 V12 Vantage S is a dog-leg car."]},
        {"h2": "How the VIN is decoded"},
        {"p": ["Every manufacturer selling cars in the US has to file its VIN scheme with the US safety regulator, NHTSA (under 49 CFR Part 565). "
               "These tables come from Aston Martin's own filings, read out of NHTSA's public decoder one character at a time, "
               "and checked against real VINs from UK, European and US cars. The power figures in the filing match Aston's published "
               "outputs for each engine, which is a good sign the letters mean what they say."],
         },
        {"warn": "The US filing has gaps. It misses letters used only on UK and European cars (for example the N400's engine letter G), "
                 "and it misses two letters used on every 2009 car: C for the 4.7 V8 Vantage and E for the DB9's AM09. Those come from real VINs. "
                 "Where this page says <em>real VIN</em>, the letter is confirmed from actual cars rather than the filing."},
        table(["Position", "What it means", "Example (2005 DB9)"], [
            ["1–3", "Manufacturer: <span class=\"code\">SCF</span> = Aston Martin Lagonda, UK", "SCF"],
            ["4", "Restraint system / seat type", "A = VH1 seat"],
            ["5", "Gearbox", "D = automatic"],
            ["6–7", "Model and body (2010 on: 6 = platform, 7 = body)", "01 = DB9 coupé"],
            ["8", "<strong>Engine derivative code</strong>", "A = AM04"],
            ["9", "Check digit, calculated from the other 16", "3"],
            ["10", "Model year: 5–9 = 2005–09, A = 2010 … J = 2018", "5 = 2005"],
            ["11", "Factory: G = Gaydon, A = Graz (Austria)", "G = Gaydon"],
            ["12", "Chassis series letter, as used in service bulletins", "A = DB9 coupé"],
            ["13–17", "Serial number", "01906"],
        ], "The 17 positions"),
        {"p": ["The example is Steve McEvoy's 2005 DB9, published on his <a href=\"https://aston1936.com/\">aston1936.com</a> blog. "
               "The layout changed for 2010: positions 6 and 7 became a platform letter and a body letter instead of a two-digit model number."]},
        table(["Years", "Letter", "Engine", "Description", "Power", "Filed / seen", "Source"], eng_rows, "Position 8: engine"),
        {"p": ["The same derivative can appear under more than one letter when it was tuned differently: AM11 is M (DB9, 510 bhp), "
               "P (Vanquish, 565 bhp) or T (Rapide S, 550 bhp), and AM29 is S (Rapide S) or U (Vanquish). "
               "Letters V and W also appear in the filing for 2017 on; they're the DB11 generation's 5.2 V12 and AMG V8, not VH engines."]},
        table(["Years", "Letter", "Gearbox", "Source"], gb_rows, "Position 5: gearbox"),
        table(["Code", "Model", "Body"], old_models, "Positions 6–7, 2005–2009"),
        table(["Code", "Model", "Body"], new_models, "Positions 6–7, 2010–2018"),
        {"p": ["From 2010, position 6 is the platform: " + ", ".join(f'<span class="code">{k}</span> {e(v)}' for k, v in PLATFORM.items()) + "."]},
        table(["Letter", "Meaning", "Source"],
              [[f'<span class="code">{k}</span>', e(v[0]), tag(v[1])] for k, v in SERIES.items()], "Position 12: chassis series"),
        {"p": ["The series letter is the one in the chassis numbers that Aston's service bulletins quote, for example "
               "\"DB9 up to A12418, V8 Vantage up to C13358, DBS up to E01351\"."]},
        {"h3": "The check digit"},
        {"p": ["Position 9 is calculated from the other 16 characters using the standard ISO 3779 weighting, so a single wrong character "
               "almost always shows up. Every real Aston VIN we've tested has a valid check digit, UK and European cars included, "
               "so if the decoder says it doesn't match, look for a typo first."]},
        {"h2": "What it can't tell you"},
        {"ul": ["History, ownership, finance or theft status. Use an HPI-type check for that.",
                "Options and colour. Those are in the build sheet, which the Aston Martin Heritage Trust can supply from the VIN.",
                "Special editions (N400, Carbon Black and so on) don't have their own model code; the engine letter sometimes gives them away, as with the N400's G.",
                "Cars never sold in the US (One-77, V12 Zagato, Lagonda Taraf, DB10) aren't in the filing."]},
        {"h2": "Sources"},
        {"ul": ["NHTSA vPIC decoder and Aston Martin's 49 CFR Part 565 VIN filings: <a href=\"https://vpic.nhtsa.dot.gov/\">vpic.nhtsa.dot.gov</a>",
                "Real VINs from UK, European and US cars, including this one (2009 DB9) and a numbered N400 from "
                "<a href=\"https://www.aston-martin-forum.de/viewtopic.php?t=3808\">aston-martin-forum.de</a>",
                "Power figures and model history cross-checked against <a href=\"https://astonmartins.com/\">astonmartins.com</a>",
                "Chassis series letters cross-checked against Aston Martin service bulletin SB-11-0300"]},
    ]

    spec = {
        "slug": "ref-vin-decoder",
        "title": "Aston Martin VIN Decoder: DB9, Vantage, DBS, Rapide",
        "description": "Free Aston Martin VIN decoder for 2005–2018 Gaydon cars: DB9, Vantage, DBS, Rapide, Vanquish. "
                       "Engine, gearbox, model year and factory from the VIN.",
        "h1": "Aston Martin VIN Decoder",
        "chip_title": "VIN Decoder — Engine, Gearbox &amp; Model from the VIN",
        "chip_note": "Every Gaydon-era model · 2005–2018",
        "meta": ["DB9 · Vantage · DBS · Virage · Rapide · Vanquish", "From Aston's own VIN filings · October 2026"],
        "og_image": "photos/hero.jpg",
        "published": "2026-10-20",
        "blocks": blocks,
    }
    path = os.path.join(ROOT, "guides-src", "ref-vin-decoder.json")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(spec, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("wrote", os.path.relpath(path, ROOT))


if __name__ == "__main__":
    main()
