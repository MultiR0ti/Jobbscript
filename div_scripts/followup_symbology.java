
// Variabler
var prio1 = ["Total","fjell","drt","pz","Cpt"];
var prim1 = ["pttotal","ptfjell","ptdrt","ptpz","ptcptu"];
var prio2 = ["Prøve","vb","enkel","dreie","ram"];
var prim2 = ["ptproves","ptvb","ptenkel","ptdreie","ptram"];
var posidx1 = 0;
var allkeys = Split($feature.Symbol, " ");

// Offset Y for symboler over hovedpunktet
function calcoffsetup(ptn, pri, symn) {
    // Offset markers
    if (pri != 0) {
        var offsety = 13 * pri;
        keys += ';po:' + ptn + '|OffsetY|' + offsety;
        keys += ";" + symn + ";po:" + ptn + '|Size|10';
    }
}

// Offset Y for symboler under hovedpunktet
function calcoffsetdown(ptn, pri, symn) {
    // Offset markers
    if (pri != 0) {
        var offsety = -13 * pri;
        keys += ';po:' + ptn + '|OffsetY|' + offsety;
        keys += ";" + symn + ";po:" + ptn + '|Size|10';
    }
}

// Finn antall piezometer
function findpzcount(listofsym) {
    var cnt = 0
    for (var k in listofsym) {
        if (listofsym[k]=="pz") {cnt += 1}
    }
    if (cnt >=6) {cnt = 6}
    return cnt
}

// Beregn X offset for piezometer
function calcoffsetpz(listofsym) {
    var npz = findpzcount(listofsym);
	var normalodd = [0,20,-20,40,-40];
    var normalpar = [10,-10,30,-30,50,-50];
    var smallodd = [0,14,-14,28,-28];
    var smallpar = [7,-7,21,-21,35,-35];

    if (npz % 2 == 0 && Find('ptpz|Size|10',keys)>0) {var offsetlist = smallpar;}
	else if (npz % 2 == 0) {var offsetlist = normalpar;} 
	else if (Find('ptpz|Size|10',keys)>0) {var offsetlist = smallodd;}
    else {var offsetlist = normalodd;}

    for (var i = 0; i < npz; i++) {
        if (i == 0) {keys += "pz;po:ptpz|OffsetX|"+offsetlist[i]+";";}
		else {
            keys += "pz"+i+";po:ptpz"+i+"|OffsetX|"+offsetlist[i]+";";
            if (Find('ptpz|Size|10',keys)>0) {keys += "pz"+i+";po:ptpz"+i+"|Size|10;";}
            if (Find('ptpz|OffsetY|',keys)>0) {
                var pzoffsety = Mid(keys,Find("pz;po:ptpz|OffsetY|",keys)+19,2)
                keys += "pz"+i+";po:ptpz"+i+"|OffsetY|"+pzoffsety+";";}
        }
	}    
}
// key for status
if (isempty($feature.Status)) {var keys = "status-udefinert;";} 
else {var keys = "status-" + $feature.Status + ';';}

// key for symbol/sondering
// Hvis det er Udefinert
if (isempty($feature.Symbol) || Find('udefinert', $feature.Symbol, 0)>=0) return keys + 'udefinert;';

// Eksisterer det et øvre hovedsymbol
if ((Find('Total', allkeys))>0 || Find('fjell', allkeys)>0 || Find('drt', allkeys)>0 || Find('pz', allkeys)>0 || Find('Cpt', allkeys)>0) {
    var posidx2 = 1;
}
else {
    var posidx2 = 0;
}

// Går igjennom øvre symboler
for (var key1 in prio1) {
    if (IndexOf(allkeys, prio1[key1]) >= 0) {
        if (posidx1 > 0) {
            keys += ";";
        }
        keys += prio1[key1];
        calcoffsetup(prim1[key1], posidx1, prio1[key1]);
        
        posidx1++;
    }
}

// Går igjennom nedre symboler
for (var key2 in prio2) {
    if (IndexOf(allkeys, prio2[key2]) >= 0) {
        if (posidx2 > 0) {
            keys += ";";
        }
        keys += prio2[key2];
        calcoffsetdown(prim2[key2], posidx2, prio2[key2]);
        posidx2++;
    }
}
keys += ";";

// Hvis det er Berg i dagen
if(Find('berg', $feature.Symbol, 0)>=0) {keys = keys + 'berg;';}
// Hvis det er Prøvegrop
if(Find('proveg', $feature.Symbol, 0)>=0) {keys = keys + 'proveg;';}
// Hvis det er Piezometer
if (Find('pz',allkeys)>1) {calcoffsetpz(allkeys)}

// Return string of keys.
return keys;
