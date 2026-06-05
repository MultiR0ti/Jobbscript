
// Variabler
var prio1 = ["Total","Fjell","DrT","PZ","Cpt"];
var prim1 = ["ptTotal","ptFjell","ptDrT","ptPZ","ptCpt"];
var prio2 = ["Prøve","Vb","Enkel","Dreie","Ram"];
var prim2 = ["ptPrøve","ptVb","ptEnkel","ptDreie","ptRam"];
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
function findPZcount(listofsym) {
    var cnt = 0
    for (var k in listofsym) {
        if (listofsym[k]=="PZ") {cnt += 1}
    }
    if (cnt >=6) {cnt = 6}
    return cnt
}

// Beregn X offset for piezometer
function calcoffsetPZ(listofsym) {
    var nPZ = findPZcount(listofsym);
	var normalodd = [0,20,-20,40,-40];
    var normalpar = [10,-10,30,-30,50,-50];
    var smallodd = [0,14,-14,28,-28];
    var smallpar = [7,-7,21,-21,35,-35];

    if (nPZ % 2 == 0 && Find('ptPZ|Size|10',keys)>0) {var offsetlist = smallpar;}
	else if (nPZ % 2 == 0) {var offsetlist = normalpar;} 
	else if (Find('ptPZ|Size|10',keys)>0) {var offsetlist = smallodd;}
    else {var offsetlist = normalodd;}

    for (var i = 0; i < nPZ; i++) {
        if (i == 0) {keys += "PZ;po:ptPZ|OffsetX|"+offsetlist[i]+";";}
		else {
            keys += "PZ"+i+";po:ptPZ"+i+"|OffsetX|"+offsetlist[i]+";";
            if (Find('ptPZ|Size|10',keys)>0) {keys += "PZ"+i+";po:ptPZ"+i+"|Size|10;";}
            if (Find('ptPZ|OffsetY|',keys)>0) {
                var PZoffsety = Mid(keys,Find("PZ;po:ptPZ|OffsetY|",keys)+19,2)
                keys += "PZ"+i+";po:ptPZ"+i+"|OffsetY|"+PZoffsety+";";}
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
if ((Find('Total', allkeys))>0 || Find('Fjell', allkeys)>0 || Find('DrT', allkeys)>0 || Find('PZ', allkeys)>0 || Find('Cpt', allkeys)>0) {
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
if (Find('PZ',allkeys)>1) {calcoffsetPZ(allkeys)}

// Return string of keys.
return keys;
