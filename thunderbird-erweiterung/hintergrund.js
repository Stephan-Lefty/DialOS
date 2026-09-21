/* DialOS-Bruecke: Thunderbird tut, worum DialOS bittet - statt dass DialOS
 * an seinen Dateien vorbeischreibt.
 *
 * WARUM ES DIESE ERWEITERUNG GIBT (Stephans TODO vom 2026-09-18): DialOS hat
 * Entwuerfe in die mbox geschrieben, Kontakte in abook.sqlite und den Index
 * ueber die Postfachdateien gebaut. Jeder dieser drei Wege hat einen Fehler
 * erzeugt - CR LF, X-Mozilla-Status 0008, eine Warteschlange fuer den Fall,
 * dass Thunderbird laeuft. Dreimal dasselbe Muster: in fremde Dateiformate
 * schreiben, statt das Programm zu fragen, dem sie gehoeren.
 *
 * DIE MESSUNG IST DURCH, DER WEG IST PRODUKTIV (2026-09-21). Am Geraet belegt:
 * Kontakt anlegen und Entwurf ablegen gehen mit der offiziellen API, ohne
 * Experiment, und der Entwurf landet im Entwurfsordner des KONTOS - der wird
 * zum Server hochgeladen, anders als die lokalen Ordner. Der mbox-Weg in
 * dialos-mail-entwurf.py ist daraufhin geloescht worden, nicht stillgelegt.
 */

const NATIVER_NAME = "dialos_bruecke";

async function urspruengliche(bezug) {
  // Von der Message-ID zur Nachricht, die Thunderbird kennt.
  //
  // WOZU DER UMWEG: "bezug" ist die Message-ID aus dem Kopf der Mail
  // ("<abc@server>"), wie sie im Suchindex steht. Thunderbird spricht intern
  // ueber eigene Nummern. Ohne diese Zuordnung kann es eine Antwort nicht als
  // Antwort erkennen.
  if (!bezug) return null;
  const sauber = String(bezug).replace(/^<|>$/g, "");
  try {
    const treffer = await browser.messages.query({ headerMessageId: sauber });
    const liste = treffer && treffer.messages ? treffer.messages : [];
    return liste.length ? liste[0] : null;
  } catch (fehler) {
    return null;
  }
}

async function entwurfAblegen({ an, betreff, text, bezug }) {
  // compose.beginNew oeffnet ein Verfassen-Fenster; saveMessage legt es als
  // Entwurf ab und schliesst es. Beides ist offizielle MailExtension-API.
  //
  // BEI EINER ANTWORT IST beginReply PFLICHT, NICHT KOSMETIK (2026-09-21):
  // Nur so setzt Thunderbird "In-Reply-To" und "References". Fehlen die, ist
  // die Antwort beim Empfaenger kein Teil des Gespraechsfadens mehr, sondern
  // eine neue Mail mit aehnlichem Betreff - und in einem langen Verlauf sucht
  // er den Bezug vergeblich. Der alte mbox-Weg konnte das; es hier
  // wegzulassen waere ein Rueckschritt gewesen.
  //
  // Der DIKTIERTE Text ersetzt anschliessend den Rumpf: Das Zitat hat DialOS
  // schon angehaengt, Thunderbirds eigenes waere ein zweites.
  const koerper = (text || "").replace(/\n/g, "<br>");
  const bezugs_mail = await urspruengliche(bezug);
  let tab = null;
  if (bezugs_mail) {
    try {
      tab = await browser.compose.beginReply(bezugs_mail.id, "replyToSender");
      await browser.compose.setComposeDetails(tab.id, {
        to: an ? [an] : [],
        subject: betreff || "(ohne Betreff)",
        body: koerper,
      });
    } catch (fehler) {
      tab = null;
    }
  }
  if (!tab) {
    tab = await browser.compose.beginNew({
      to: an ? [an] : [],
      subject: betreff || "(ohne Betreff)",
      body: koerper,
    });
  }
  await browser.compose.saveMessage(tab.id, { mode: "draft" });
  try {
    await browser.tabs.remove(tab.id);
  } catch (fehler) {
    /* Das Fenster schliesst sich nach dem Speichern oft selbst. */
  }
  return { ok: true, was: "entwurf", an, betreff,
           antwort_auf: bezugs_mail ? bezugs_mail.id : null };
}

async function mailSenden({ an, betreff, text }) {
  // Senden ist die einzige Sache hier, die sich NICHT rueckgaengig machen
  // laesst - deshalb steht die Bestaetigung nicht in dieser Datei, sondern
  // dort, wo der Nutzer spricht (dialos-mail-schreiben.py). Diese Funktion
  // fragt nichts und prueft nichts; sie wird nur gerufen, wenn der Mensch
  // "ja" gesagt hat.
  //
  // "compose.send" ist eine EIGENE Berechtigung, getrennt von "compose" und
  // "compose.save" - dieselbe Falle wie am 2026-09-21 beim Speichern, wo
  // "browser.compose.saveMessage is not a function" nach einem Programmfehler
  // aussah und in Wahrheit eine fehlende Zeile im Manifest war.
  const tab = await browser.compose.beginNew({
    to: an ? [an] : [],
    subject: betreff || "(ohne Betreff)",
    body: (text || "").replace(/\n/g, "<br>"),
  });
  try {
    await browser.compose.sendMessage(tab.id, { mode: "sendNow" });
  } catch (fehler) {
    // NICHT WEGWERFEN, WENN DAS SENDEN SCHEITERT (kein Netz, Server sagt
    // nein): Der Text ist diktiert und waere sonst verloren. Er kommt als
    // Entwurf in Sicherheit, und DialOS sagt es.
    try {
      await browser.compose.saveMessage(tab.id, { mode: "draft" });
    } catch (zweiter) {
      /* dann bleibt das Fenster offen stehen - immer noch besser als weg */
    }
    return { ok: false, was: "senden", fehler: String(fehler),
             entwurf: true };
  }
  return { ok: true, was: "senden", an, betreff };
}

async function schreibfenster() {
  // Welche Schreibfenster stehen offen - und was steht darin?
  //
  // WOZU: DialOS schliesst Thunderbird auf Zuruf. Am 2026-09-21 gemessen:
  // Auf SIGTERM geht Thunderbird nach EINER Sekunde zu und fragt nicht nach -
  // ein angefangenes Schreibfenster ist danach lautlos weg. Wer den Bildschirm
  // nicht sieht, merkt davon nichts. Also fragt DialOS vorher.
  const tabs = await browser.tabs.query({ type: "messageCompose" });
  const offen = [];
  for (const tab of tabs) {
    try {
      const d = await browser.compose.getComposeDetails(tab.id);
      offen.push({
        id: tab.id,
        an: (d.to || []).join(", "),
        betreff: d.subject || "",
      });
    } catch (fehler) {
      offen.push({ id: tab.id, an: "", betreff: "" });
    }
  }
  return { ok: true, was: "schreibfenster", anzahl: offen.length, offen };
}

async function schreibfensterSichern() {
  // Jedes offene Schreibfenster als Entwurf ablegen - und NICHT schliessen.
  //
  // NICHT SCHLIESSEN IST ABSICHT: Sitzt ein sehender Helfer davor und tippt,
  // waere ein Fenster, das unter den Haenden verschwindet, schlimmer als das
  // Problem. Gespeichert ist gespeichert; ob das Fenster zugeht, entscheidet
  // gleich Thunderbird selbst beim Beenden.
  const tabs = await browser.tabs.query({ type: "messageCompose" });
  let gesichert = 0;
  const fehler = [];
  for (const tab of tabs) {
    try {
      await browser.compose.saveMessage(tab.id, { mode: "draft" });
      gesichert += 1;
    } catch (f) {
      fehler.push(String(f));
    }
  }
  return { ok: fehler.length === 0, was: "schreibfenster sichern",
           gesichert, fehler };
}

async function kontaktAnlegen({ name, mail, firma }) {
  const buecher = await browser.addressBooks.list();
  const ziel = buecher.find((b) => !b.readOnly);
  if (!ziel) {
    return { ok: false, fehler: "kein beschreibbares Adressbuch" };
  }
  const id = await browser.contacts.create(ziel.id, {
    DisplayName: name || mail,
    PrimaryEmail: mail || "",
    Company: firma || "",
  });
  return { ok: true, was: "kontakt", id, buch: ziel.name };
}

async function ausfuehren(bitte) {
  try {
    if (bitte.befehl === "entwurf") return await entwurfAblegen(bitte);
    if (bitte.befehl === "senden") return await mailSenden(bitte);
    if (bitte.befehl === "schreibfenster") return await schreibfenster();
    if (bitte.befehl === "schreibfenster sichern") return await schreibfensterSichern();
    if (bitte.befehl === "kontakt") return await kontaktAnlegen(bitte);
    if (bitte.befehl === "hallo") {
      const konten = await browser.accounts.list();
      return {
        ok: true,
        was: "hallo",
        thunderbird: (await browser.runtime.getBrowserInfo?.())?.version,
        konten: konten.map((k) => k.name),
      };
    }
    return { ok: false, fehler: `unbekannter Befehl: ${bitte.befehl}` };
  } catch (fehler) {
    // JEDER FEHLER GEHT ZURUECK, nie ins Leere: DialOS muss dem Nutzer sagen
    // koennen, was schiefging - er sieht keinen Bildschirm.
    return { ok: false, fehler: String(fehler && fehler.message ? fehler.message : fehler) };
  }
}

let verbindung = null;

function verbinden() {
  verbindung = browser.runtime.connectNative(NATIVER_NAME);
  verbindung.onMessage.addListener(async (bitte) => {
    const antwort = await ausfuehren(bitte);
    antwort.nummer = bitte.nummer;
    verbindung.postMessage(antwort);
  });
  verbindung.onDisconnect.addListener(() => {
    verbindung = null;
    // Neu verbinden, aber nicht im Sekundentakt - die Bruecke kann auch
    // absichtlich beendet worden sein.
    setTimeout(verbinden, 5000);
  });
}

verbinden();
