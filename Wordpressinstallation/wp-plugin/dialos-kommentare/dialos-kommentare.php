<?php
/**
 * Plugin Name:       DialOS – Kommentare
 * Description:       Deutsche Beiträge bekommen einen durchgehend deutschen Kommentarbereich (das Theme "wlow" lässt drei Texte auf Englisch stehen). Bei englischen Beiträgen wird der Kommentarbereich vollständig abgeschaltet. Unterbindet außerdem Selbst-Pingbacks zwischen den beiden Sprachfassungen eines Beitrags.
 * Version:           2.0.0
 * Requires at least: 6.0
 * Requires PHP:      7.4
 * Author:            Stephan Rösner
 * License:           Apache-2.0
 *
 * WARUM ES DIESES PLUGIN GIBT
 *
 * dialos.org ist zweisprachig, WordPress selbst aber nicht: Die Website
 * läuft auf de_DE, also stammen alle Texte, die WordPress beisteuert, aus
 * dem deutschen Sprachpaket - auch unter den englischen Beiträgen. Dort
 * stand "Schreibe einen Kommentar", "Deine E-Mail-Adresse wird nicht
 * veröffentlicht", "Antworten", "sagt:" und ein deutsch formatiertes Datum.
 *
 * Umgekehrt gibt das Theme "wlow" drei Texte fest auf Englisch aus -
 * "1 Response", "Submit Comment", "Comments RSS Feed" - die dann unter den
 * deutschen Beiträgen auffallen.
 *
 * Die Entscheidung (Stephan, 20.08.2026): deutsche Beiträge behalten die
 * Kommentarfunktion und bekommen sie vollständig auf Deutsch, englische
 * Beiträge bekommen gar keine. Das ist nicht nur der kürzere Weg, sondern
 * auch der ehrlichere - ein Kommentarbereich, den niemand betreut und der
 * in der falschen Sprache antwortet, lädt zu nichts ein.
 *
 * Der zuvor erwogene Weg, für englische Beiträge die gesamte WordPress-
 * Sprache auf en_US umzustellen, ist damit hinfällig. (Eine Liste einzeln
 * zu übersetzender Zeichenketten wäre ohnehin nie vollständig gewesen und
 * hätte beim nächsten WordPress-Update lautlos Lücken bekommen.)
 *
 * ZUR BARRIEREFREIHEIT
 *
 * Für Screenreader-Nutzer ist Sprachmischung kein Schönheitsfehler: Eine
 * deutsche Sprachausgabe, die "Submit Comment" vorliest, ist schwer zu
 * verstehen. Genau darum geht es bei DialOS - deshalb steht diese
 * Kleinigkeit hier.
 *
 * WIE EIN BEITRAG ALS ENGLISCH ERKANNT WIRD
 *
 * Über die Konvention, die auf dialos.org ohnehin gilt: Jede englische
 * Fassung verlinkt ganz oben auf ihre deutsche Entsprechung, und der
 * Linktext ist genau "Deutsch". Damit braucht es kein zusätzliches Feld,
 * das jemand pflegen und beim Anlegen neuer Beiträge vergessen könnte.
 * Wer die Konvention ändert, muss dialos_km_ist_englisch() nachziehen.
 *
 * @package DialOS
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit; // Kein direkter Aufruf.
}

/**
 * Ist der angefragte Beitrag die englische Fassung?
 *
 * @param int|WP_Post|null $post Beitrag; ohne Angabe der aktuelle.
 * @return bool
 */
function dialos_km_ist_englisch( $post = null ) {
	$post = get_post( $post );

	if ( ! $post || 'post' !== $post->post_type ) {
		return false;
	}

	// Sprachumschalter am Kopf des Beitrags: <a href="...">Deutsch</a>
	return 1 === preg_match(
		'#<a\s[^>]*href="[^"]*"[^>]*>\s*Deutsch\s*</a>#i',
		$post->post_content
	);
}

// ---------------------------------------------------------------------------
// Englische Beiträge: kein Kommentarbereich
// ---------------------------------------------------------------------------

/**
 * Kommentarformular abschalten.
 *
 * @param bool $offen   Bisheriger Zustand.
 * @param int  $post_id Beitrags-ID.
 * @return bool
 */
function dialos_km_kommentare_zu( $offen, $post_id ) {
	return dialos_km_ist_englisch( $post_id ) ? false : $offen;
}
add_filter( 'comments_open', 'dialos_km_kommentare_zu', 10, 2 );
add_filter( 'pings_open', 'dialos_km_kommentare_zu', 10, 2 );

/**
 * Vorhandene Kommentare und Pingbacks ausblenden.
 *
 * Nötig zusätzlich zu comments_open: Ein geschlossener Beitrag zeigt eine
 * bereits vorhandene Kommentarliste weiterhin an. Genau das ist hier der
 * Fall - die englischen Beiträge haben Selbst-Pingbacks abbekommen, bevor
 * dieses Plugin existierte.
 *
 * @param array $kommentare Geladene Kommentare.
 * @return array
 */
function dialos_km_keine_liste( $kommentare ) {
	return dialos_km_ist_englisch() ? array() : $kommentare;
}
add_filter( 'comments_array', 'dialos_km_keine_liste' );

/**
 * Zähler auf null setzen, damit keine Überschrift stehen bleibt.
 *
 * Ohne das zeigt das Theme weiter "1 Response" über einer leeren Liste.
 *
 * @param int|string $anzahl  Bisherige Anzahl.
 * @param int        $post_id Beitrags-ID.
 * @return int|string
 */
function dialos_km_kein_zaehler( $anzahl, $post_id ) {
	return dialos_km_ist_englisch( $post_id ) ? 0 : $anzahl;
}
add_filter( 'get_comments_number', 'dialos_km_kein_zaehler', 10, 2 );

// ---------------------------------------------------------------------------
// Deutsche Beiträge: die drei englischen Theme-Texte übersetzen
// ---------------------------------------------------------------------------

/**
 * Überschrift über der Kommentarliste.
 *
 * Das Theme ruft comments_number() mit englischen Vorgaben auf; dieser
 * Filter greift danach.
 *
 * @param string $ausgabe Fertiger Text, z. B. "1 Response".
 * @param int    $anzahl  Anzahl der Kommentare.
 * @return string
 */
function dialos_km_anzahl( $ausgabe, $anzahl ) {
	// Unter englischen Beiträgen nichts eindeutschen. Dort steht der Zähler
	// zwar ohnehin auf null, aber ob das Theme daraus eine Überschrift baut,
	// entscheidet das Theme - nicht dieses Plugin.
	if ( dialos_km_ist_englisch() ) {
		return $ausgabe;
	}

	$anzahl = (int) $anzahl;

	if ( 0 === $anzahl ) {
		return 'Keine Kommentare';
	}

	if ( 1 === $anzahl ) {
		return '1 Kommentar';
	}

	return sprintf( '%d Kommentare', $anzahl );
}
add_filter( 'comments_number', 'dialos_km_anzahl', 10, 2 );

/**
 * Beschriftung des Absende-Knopfes.
 *
 * @param array $vorgaben Vorgaben des Kommentarformulars.
 * @return array
 */
function dialos_km_knopf( $vorgaben ) {
	$vorgaben['label_submit'] = 'Kommentar abschicken';

	return $vorgaben;
}
add_filter( 'comment_form_defaults', 'dialos_km_knopf' );

/**
 * Link auf den Kommentar-Feed unter dem Formular.
 *
 * Das Theme gibt diesen Link auch dann aus, wenn Kommentare geschlossen
 * sind - bei den englischen Beiträgen stand deshalb weiterhin "Comments RSS
 * Feed" unter dem Artikel. Ein Feed für Kommentare, die es nicht geben
 * kann, ist sinnlos: Dort wird der Link ganz entfernt statt übersetzt.
 * (Würde er nur übersetzt, stünde plötzlich deutscher Text unter einem
 * englischen Beitrag - genau anders herum als beabsichtigt.)
 *
 * @param string $link     Fertiges <a>-Element.
 * @param int    $post_id  Beitrags-ID.
 * @param string $linktext Beschriftung, die das Theme übergeben hat.
 * @return string
 */
function dialos_km_feed_link( $link, $post_id, $linktext ) {
	if ( dialos_km_ist_englisch( $post_id ) ) {
		return '';
	}

	return str_replace( $linktext, 'Kommentare als RSS-Feed', $link );
}
add_filter( 'post_comments_feed_link_html', 'dialos_km_feed_link', 10, 3 );

/**
 * Auffangnetz, falls das Theme dieselben Texte über __() ausgibt.
 *
 * Kostet praktisch nichts und deckt den Fall mit ab, dass ein künftiges
 * Theme-Update die Zeichenketten übersetzbar macht, aber ohne deutsche
 * Übersetzung ausliefert.
 *
 * @param string $uebersetzt Übersetzter Text.
 * @param string $original   Originaltext.
 * @return string
 */
function dialos_km_ersatzuebersetzung( $uebersetzt, $original ) {
	static $tabelle = array(
		'Submit Comment'    => 'Kommentar abschicken',
		'Comments RSS Feed' => 'Kommentare als RSS-Feed',
		'1 Response'        => '1 Kommentar',
		'% Responses'       => '% Kommentare',
		'Leave a Reply'     => 'Schreibe einen Kommentar',
	);

	/*
	 * Die Reihenfolge ist Absicht: erst die billige Tabellenabfrage, dann
	 * erst die Sprachprüfung. Dieser Filter läuft bei JEDEM übersetzten Text
	 * - viele hundert Mal pro Seitenaufruf. dialos_km_ist_englisch() liest
	 * dabei den Beitrag und lässt einen regulären Ausdruck darüber laufen;
	 * das jedes Mal zu tun, wäre reine Verschwendung. So bleiben drei
	 * Aufrufe übrig statt hunderter.
	 */
	if ( ! isset( $tabelle[ $original ] ) ) {
		return $uebersetzt;
	}

	// Unter englischen Beiträgen bleibt Englisch stehen.
	return dialos_km_ist_englisch() ? $uebersetzt : $tabelle[ $original ];
}
add_filter( 'gettext', 'dialos_km_ersatzuebersetzung', 10, 2 );

// ---------------------------------------------------------------------------
// Keine Selbst-Pingbacks zwischen den eigenen Beiträgen
// ---------------------------------------------------------------------------

/**
 * Links auf die eigene Domain aus der Ping-Liste werfen.
 *
 * Jeder Beitrag auf dialos.org verlinkt oben auf seine anderssprachige
 * Fassung. WordPress macht daraus einen Kommentar ("DialOS Mobil sucht
 * Testerinnen und Tester sagt: [...] English [...]"), der unter dem Beitrag
 * steht und wie eine echte Wortmeldung aussieht. Für Lesende ist das
 * verwirrend, für Screenreader-Nutzer erst recht: Sie hören "1 Kommentar"
 * und bekommen dann einen sinnlosen Textschnipsel vorgelesen.
 *
 * Bereits vorhandene Pingbacks verschwinden dadurch NICHT - die müssen
 * einmalig von Hand weg (Kommentare > auswählen > Papierkorb).
 *
 * ACHTUNG: "pre_ping" ist trotz des Namens KEIN Filter, sondern eine Aktion
 * mit Referenzübergabe (do_action_ref_array). Ein zurückgegebener Wert wird
 * verworfen - die Liste muss über die Referenz geändert werden. Mit
 * add_filter und return sieht der Code richtig aus und tut nichts.
 *
 * @param array $links Zu pingende Adressen, per Referenz.
 * @return void
 */
function dialos_km_keine_selbstpings( &$links ) {
	$eigene = home_url();

	foreach ( $links as $index => $link ) {
		if ( 0 === strpos( $link, $eigene ) ) {
			unset( $links[ $index ] );
		}
	}
}
add_action( 'pre_ping', 'dialos_km_keine_selbstpings' );
