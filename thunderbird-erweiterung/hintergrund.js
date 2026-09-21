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
 * ERSTER SCHRITT IST EINE MESSUNG, KEIN UMBAU: Diese Fassung kann genau zwei
 * Dinge - einen Entwurf ablegen und einen Kontakt anlegen - und meldet, ob die
 * offizielle API dafuer reicht. Erst wenn das steht, wird der mbox-Weg abgeloest.
 */

const NATIVER_NAME = "dialos_bruecke";

async function entwurfAblegen({ an, betreff, text }) {
  // compose.beginNew oeffnet ein Verfassen-Fenster; saveMessage legt es als
  // Entwurf ab und schliesst es. Beides ist offizielle MailExtension-API -
  // genau das ist hier die Frage.
  const tab = await browser.compose.beginNew({
    to: an ? [an] : [],
    subject: betreff || "(ohne Betreff)",
    body: (text || "").replace(/\n/g, "<br>"),
  });
  await browser.compose.saveMessage(tab.id, { mode: "draft" });
  try {
    await browser.tabs.remove(tab.id);
  } catch (fehler) {
    /* Das Fenster schliesst sich nach dem Speichern oft selbst. */
  }
  return { ok: true, was: "entwurf", an, betreff };
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
