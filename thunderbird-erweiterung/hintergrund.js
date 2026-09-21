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
