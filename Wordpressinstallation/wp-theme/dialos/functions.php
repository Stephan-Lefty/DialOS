<?php
/**
 * DialOS Child-Theme (von "wlow").
 *
 * Laedt zuerst alle Stylesheets des Eltern-Themes, danach dieses
 * Child-Themes eigenes style.css - so bleiben Eltern-Updates unversehrt,
 * und eigene Regeln koennen sie gezielt ueberschreiben.
 */

add_action( 'wp_enqueue_scripts', 'dialos_child_enqueue_styles' );

function dialos_child_enqueue_styles() {
	$parent_style = 'wlow-style';

	wp_enqueue_style(
		$parent_style,
		get_template_directory_uri() . '/style.css'
	);

	wp_enqueue_style(
		'dialos-child-style',
		get_stylesheet_directory_uri() . '/style.css',
		array( $parent_style ),
		wp_get_theme()->get( 'Version' )
	);
}

/**
 * Die Cache-Marke der zweiten Einbindung unserer style.css richtigstellen
 * (Stephan, 2026-09-22 - gefunden, weil ein Fix am Handy wirkungslos blieb,
 * obwohl die Datei auf dem Server nachweislich richtig war).
 *
 * Das Eltern-Theme wlow meldet ein Stylesheet unter dem Handle "wlow-css"
 * an und verweist dabei auf get_stylesheet_uri(). Bei einem AKTIVEN
 * CHILD-THEME liefert diese Funktion aber nicht wlows eigene style.css,
 * sondern unsere. Unsere Datei wird dadurch zweimal geladen - das zweite
 * Mal ganz am Ende der Kette.
 *
 * DIE MARKE IST DIE WORDPRESS-KERNVERSION, nicht die von wlow. In
 * 1.6.13 stand hier das Falsche ("wlows Version 7.1.1"); wlow traegt
 * laut WordPress die 1.2.7. Richtig ist: Wer wp_enqueue_style() ohne
 * eigene Versionsangabe aufruft, bekommt von WordPress die Version des
 * KERNS als Marke angehaengt. Belegt am 2026-09-22 durch das Update von
 * WordPress 7.1.1 auf 7.1.2 - die Marke wanderte im selben Schritt von
 * ?ver=7.1.1 auf ?ver=7.1.2 mit, ohne dass an wlow oder an diesem Theme
 * irgendetwas geaendert wurde.
 *
 * Fuer die Wirkung aendert das nichts: Die Marke bewegt sich nur, wenn
 * WORDPRESS aktualisiert wird, nicht wenn sich unser Theme aendert. Ein
 * Besucher, der die Seite schon kennt, bekommt an dieser Stelle also die
 * alte Datei aus seinem Browserspeicher, und weil sie SPAETER geladen
 * wird als die richtige, gewinnen dort die alten Regeln. Genau daran ist
 * Fassung 1.6.12 gescheitert.
 *
 * UMGEBAUT IN 1.6.15 - die erste Fassung griff nachweislich nicht. Sie
 * hing an "wp_enqueue_scripts" mit Prioritaet 20 und suchte den Eintrag
 * im Register; nach dem Hochladen stand die Marke aber unveraendert auf
 * der Kernversion. Offenbar meldet wlow das Stylesheet erst spaeter an,
 * sodass zu diesem Zeitpunkt noch gar nichts zu finden war. Der Filter
 * "style_loader_src" laeuft dagegen beim Erzeugen JEDES Stylesheet-Links
 * und kennt keine Registrierungsreihenfolge.
 *
 * Bewusst nur die Versionsnummer korrigiert und die Einbindung NICHT
 * entfernt: An einem Handle koennen ueber wp_add_inline_style weitere
 * Angaben haengen, die sonst lautlos verschwinden wuerden. Doppelt
 * geladen kostet eine Anfrage - falsch zwischengespeichert kostet jede
 * kuenftige Aenderung.
 */
add_filter( 'style_loader_src', 'dialos_child_cache_marke_richtigstellen', 10, 2 );

function dialos_child_cache_marke_richtigstellen( $src, $handle ) {
	if ( 'wlow-css' !== $handle ) {
		return $src;
	}

	// Nur anfassen, wenn dort wirklich UNSERE Datei haengt - laedt wlow
	// eines Tages seine eigene, bleibt alles unberuehrt.
	if ( false === strpos( (string) $src, get_stylesheet() . '/style.css' ) ) {
		return $src;
	}

	return add_query_arg(
		'ver',
		wp_get_theme()->get( 'Version' ),
		remove_query_arg( 'ver', $src )
	);
}

/**
 * Seiten-Cache (WP Super Cache) bei jeder Aenderung an Seiten/
 * Beitraegen vollstaendig leeren (Stephan, 2026-08-25, beim Einrichten
 * des Cache-Plugins). Dessen eigene Einstellung dafuer
 * ("clear_cache_on_post_edit") liess sich ueber die Plugin-eigene
 * REST-API nicht setzen (mehrere Versuche, Ursache ohne Zugriff auf
 * den Plugin-Quelltext nicht zu klaeren) - ohne diesen Hook waeren
 * Inhalts-Aenderungen ueber die REST API, der uebliche Arbeitsweg
 * dieses Projekts, bis zu 10 Minuten lang nicht sichtbar gewesen
 * (siehe cache_time_interval). function_exists()-Absicherung, falls
 * das Plugin einmal deaktiviert wird.
 */
add_action( 'save_post', 'dialos_child_cache_leeren' );
// Zeitgesteuert veroeffentlichte Beitraege laufen nicht zwingend ueber
// save_post - ohne diese Zeile blieben die Bloecke mit den neuesten
// Beitraegen auf der Startseite stehen, bis irgendwer etwas anderes
// speichert (Stephan, 2026-09-17: "ein Automatismus, der prueft, ob es
// Neuigkeiten gibt"). Genau das ist er, nur ereignisgesteuert statt
// taeglich - und damit in Sekunden statt in bis zu 24 Stunden.
add_action( 'publish_future_post', 'dialos_child_cache_leeren' );

function dialos_child_cache_leeren() {
	if ( function_exists( 'wp_cache_clear_cache' ) ) {
		wp_cache_clear_cache();
	}
}

/**
 * Fusszeilen-Text anpassen (DialOS -> DialOS.org, Kontakt/Support-Mail).
 *
 * Bewusst per JavaScript nach dem Laden statt per footer.php-Override:
 * footer.php im Eltern-Theme "wlow" schliesst mehrere Wrapper-Divs und
 * ruft wp_footer() auf (Pflicht fuer Plugin-Skripte u.a.) - ein Override
 * ohne die exakte Originaldatei zu kennen, koennte das leicht kaputt
 * machen. Der reine Text-Tausch per JS ist dagegen ungefaehrlich.
 */
add_action( 'wp_footer', 'dialos_child_footer_text', 20 );

function dialos_child_footer_text() {
	$kontakt_label = dialos_child_ist_englisch() ? 'Contact' : 'Kontakt';
	?>
	<script>
	document.addEventListener('DOMContentLoaded', function () {
		var footerText = document.querySelector('.footer .col-md-6 p');
		if (footerText && footerText.textContent.indexOf('DialOS') !== -1) {
			footerText.innerHTML =
				'&copy; Copyright ' + new Date().getFullYear() + ' DialOS.org' +
				' &ndash; <?php echo esc_js( $kontakt_label ); ?>: <a href="mailto:kontakt@dialos.org">kontakt@dialos.org</a>' +
				' &ndash; Support: <a href="mailto:service@dialos.org">service@dialos.org</a>';
		}
	});
	</script>
	<?php
}

/**
 * "Nach oben"-Button: eigenes Element, direkt an <body> gehaengt statt
 * irgendwo im bestehenden Menue verschachtelt - dadurch unabhaengig von
 * dessen Aufbau/Zustand (anders als der vorherige Hamburger-Versuch,
 * der mit dem bestehenden Seiten-Menue kollidierte).
 */
add_action( 'wp_footer', 'dialos_child_to_top', 20 );

function dialos_child_to_top() {
	?>
	<script>
	document.addEventListener('DOMContentLoaded', function () {
		var btn = document.createElement('a');
		btn.href = '#';
		btn.className = 'dialos-to-top';
		btn.setAttribute('aria-label', 'Nach oben');
		btn.innerHTML = '&uarr;';
		btn.addEventListener('click', function (e) {
			e.preventDefault();
			window.scrollTo({ top: 0, behavior: 'smooth' });
		});
		document.body.appendChild(btn);

		var schwelle = 80;
		window.addEventListener('scroll', function () {
			var y = window.pageYOffset || document.documentElement.scrollTop;
			btn.classList.toggle('dialos-visible', y > schwelle);
		}, { passive: true });
	});
	</script>
	<?php
}

/**
 * Oberes Menue beim Scrollen ausblenden (Stephan, urspruenglich
 * 2026-08-23, beim Entfernen des Hamburger-Versuchs versehentlich mit
 * entfernt). Diesmal unproblematisch: der "Nach oben"-Button haengt
 * unabhaengig an <body>, nicht mehr im Menue verschachtelt wie beim
 * Hamburger - wird vom Ausblenden also nicht mehr beruehrt. Bewusst
 * "opacity" statt "transform" (transform auf einem Vorfahren wuerde
 * einen neuen Bezugsrahmen fuer "position: fixed"-Nachfahren erzeugen,
 * siehe der urspruengliche Hamburger-Bug).
 */
add_action( 'wp_footer', 'dialos_child_scroll_nav', 20 );

function dialos_child_scroll_nav() {
	?>
	<script>
	document.addEventListener('DOMContentLoaded', function () {
		var navbar = document.querySelector('.navbar');
		if (!navbar) return;
		var schwelle = 80;
		window.addEventListener('scroll', function () {
			var y = window.pageYOffset || document.documentElement.scrollTop;
			navbar.classList.toggle('dialos-nav-hidden', y > schwelle);
		}, { passive: true });
	});
	</script>
	<?php
}

/**
 * Seitenweite Suche + Barrierefrei-Umschalter im Menue, nebeneinander
 * in einem gemeinsamen <li> (Stephan, 2026-08-23). Impressum und die
 * Datenschutzerklaerungen sind dafuer aus dem Menue in die Fusszeile
 * gewandert (siehe dialos_child_footer_links()), damit hier Platz ist
 * und die "position: fixed"-Navbar nicht durch eine zusaetzliche Zeile
 * waechst (sonst rutscht der Seiteninhalt nicht mit, siehe Screenshot
 * vom 2026-08-23 - deshalb waren beide zwischenzeitlich in der
 * Fusszeile).
 */
add_action( 'wp_footer', 'dialos_child_search_and_a11y' );

function dialos_child_search_and_a11y() {
	$aktion = esc_url( home_url( '/' ) );
	if ( dialos_child_ist_englisch() ) {
		$text = array(
			'suchen_label'   => 'Search',
			'placeholder'    => 'Search …',
			'suche_starten'  => 'Start search',
			'a11y_aus'       => 'Accessibility Mode',
			'a11y_an'        => 'Accessibility Mode: On',
		);
	} else {
		$text = array(
			'suchen_label'   => 'Suchen',
			'placeholder'    => 'Suchen …',
			'suche_starten'  => 'Suche starten',
			'a11y_aus'       => 'Barrierefrei-Modus',
			'a11y_an'        => 'Barrierefrei-Modus: An',
		);
	}
	?>
	<script>
	document.addEventListener('DOMContentLoaded', function () {
		var menu = document.getElementById('menu-seiten');
		if (!menu) return;

		var li = document.createElement('li');
		li.className = 'dialos-search-a11y-item';

		var form = document.createElement('form');
		form.className = 'dialos-search-form';
		form.setAttribute('role', 'search');
		form.method = 'get';
		form.action = '<?php echo $aktion; ?>';
		form.innerHTML =
			'<label class="dialos-visually-hidden" for="dialos-search-input"><?php echo esc_js( $text['suchen_label'] ); ?></label>' +
			'<input type="search" id="dialos-search-input" name="s" placeholder="<?php echo esc_js( $text['placeholder'] ); ?>" />' +
			'<button type="submit" aria-label="<?php echo esc_js( $text['suche_starten'] ); ?>">&#128269;</button>';
		li.appendChild(form);

		var SCHLUESSEL = 'dialos-a11y-mode';
		var btn = document.createElement('button');
		btn.type = 'button';
		btn.id = 'dialos-a11y-button';
		btn.className = 'dialos-a11y-button';
		var istAn = localStorage.getItem(SCHLUESSEL) === '1';
		btn.setAttribute('aria-pressed', istAn ? 'true' : 'false');
		btn.textContent = istAn ? '<?php echo esc_js( $text['a11y_an'] ); ?>' : '<?php echo esc_js( $text['a11y_aus'] ); ?>';
		btn.addEventListener('click', function () {
			var an = !document.body.classList.contains('dialos-a11y-mode');
			localStorage.setItem(SCHLUESSEL, an ? '1' : '0');
			document.body.classList.toggle('dialos-a11y-mode', an);
			btn.setAttribute('aria-pressed', an ? 'true' : 'false');
			btn.textContent = an ? '<?php echo esc_js( $text['a11y_an'] ); ?>' : '<?php echo esc_js( $text['a11y_aus'] ); ?>';
		});
		li.appendChild(btn);

		menu.appendChild(li);

		document.body.classList.toggle('dialos-a11y-mode', istAn);
	});
	</script>
	<?php
}

/**
 * Impressum und Datenschutzerklaerungen in der Fusszeile statt im
 * oberen Menue (Stephan, 2026-08-23) - Menue-Eintraege dafuer per
 * REST API entfernt. Ersetzen dort den "Top"-Link, der seit dem
 * eigenen "Nach oben"-Button (dialos_child_to_top) ohnehin doppelt
 * war, statt eine zusaetzliche Fusszeilen-Zeile anzuhaengen.
 */
add_action( 'wp_footer', 'dialos_child_footer_links' );

function dialos_child_footer_links() {
	if ( dialos_child_ist_englisch() ) {
		$html = '<p class="dialos-footer-links">' .
			'<a href="https://dialos.org/en/legal-notice/">Legal Notice</a>' .
			'<a href="https://dialos.org/en/privacy-policy/">Privacy Policy (Website)</a>' .
			'<a href="https://dialos.org/en/dialos-mobil-privacy-policy/">Privacy Policy (App)</a>' .
			'</p>';
	} else {
		$html = '<p class="dialos-footer-links">' .
			'<a href="https://dialos.org/impressum/">Impressum</a>' .
			'<a href="https://dialos.org/datenschutzerklaerung/">Datenschutz (Website)</a>' .
			'<a href="https://dialos.org/dialos-mobil-datenschutz/">Datenschutz (App)</a>' .
			'</p>';
	}
	?>
	<script>
	document.addEventListener('DOMContentLoaded', function () {
		var ziel = document.querySelector('.footer .col-md-6:last-child');
		if (!ziel) return;
		ziel.innerHTML = <?php echo wp_json_encode( $html ); ?>;
	});
	</script>
	<?php
}

/**
 * lang-Attribut korrigieren.
 *
 * Alle Seiten/Beitraege liefern bisher lang="de", auch die englischen
 * (z.B. /en/idea/, /who-is-claude/) - die Site nutzt kein Mehrsprachen-
 * Plugin mit strukturierten Sprachdaten. Verlaesslichstes Signal, das
 * es gibt: Jede Seite/jeder Beitrag beginnt laut Konvention dieser
 * Website mit einem Sprachumschalter-Link ("Deutsch"/"English") zur
 * jeweils anderen Sprachversion - steht die deutsche Sprungmarke am
 * Anfang, ist die aktuelle Seite die englische.
 */
add_filter( 'language_attributes', 'dialos_child_language_attributes' );

function dialos_child_language_attributes( $output ) {
	if ( is_singular() ) {
		global $post;
		if ( $post && strpos( $post->post_content, '>Deutsch<' ) !== false ) {
			$output = str_replace( 'lang="de"', 'lang="en"', $output );
		}
	}
	return $output;
}

/**
 * Erkennt, ob die aktuelle Anfrage auf der englischen Seite liegt
 * (/en/ oder /en/irgendwas/). Gemeinsamer Helfer fuer Menue, Fusszeile
 * und Suche/Barrierefrei-Umschalter - so muss die Pfadpruefung nicht an
 * mehreren Stellen wiederholt werden.
 */
function dialos_child_ist_englisch() {
	$pfad = trim( (string) wp_parse_url( $_SERVER['REQUEST_URI'] ?? '', PHP_URL_PATH ), '/' );
	return ( 'en' === $pfad || 0 === strpos( $pfad, 'en/' ) );
}

/**
 * Englische Beitraege unter /en/ statt flach auf Root-Ebene (Stephan,
 * 2026-08-25). Seiten liegen dank WordPress' eingebauter Seiten-
 * Hierarchie schon sauber unter /en/ (z.B. /en/idea/) - Beitraege
 * kennen aber kein "parent" und lagen bisher alle flach unter
 * https://dialos.org/{slug}/, unabhaengig von der Sprache.
 *
 * Bewusst KEINE eigene add_rewrite_rule()+flush_rewrite_rules(): Eine
 * neue Regel mit Prioritaet "top" wuerde vor WordPress' eigener,
 * generischer Seiten-Regel geprueft und damit auch echte Seiten wie
 * /en/idea/ abfangen, bevor WordPress sie als Seite aufloesen kann -
 * das haette die vier bereits funktionierenden englischen Seiten
 * kaputt gemacht. Stattdessen ueber das "request"-Filter NACH der
 * normalen Aufloesung eingreifen: Nur wenn unter dem angefragten Pfad
 * KEINE Seite existiert, aber ein Beitrag mit passendem Slug, wird auf
 * diesen umgebogen - jede andere Anfrage bleibt unangetastet.
 *
 * Pfad bewusst selbst aus REQUEST_URI gelesen statt aus
 * $query_vars['pagename']: Testweise eingebauter Debug-Header (Version
 * 1.5.1) zeigte, dass WordPress /en/{beitrag}/ ueberraschend als
 * Anhang-URL aufloest (query_vars = ['attachment' => 'beitrag'], kein
 * 'pagename' dabei) - offenbar eine eingebaute, hoeher priorisierte
 * Regel fuer zweistufige Pfade nach dem Muster "elternseite/anhang".
 * /en/idea/ (eine echte Seite) landet dagegen bei 'pagename' - warum
 * genau dieselbe Pfadform je nach Ziel unterschiedliche eingebaute
 * Regeln trifft, war ohne Datenbank-/Dateisystem-Zugriff nicht weiter
 * aufzuloesen. Der eigene Pfad-Check umgeht das Problem vollstaendig,
 * unabhaengig davon, welche Query-Var WordPress selbst gewaehlt hat.
 */
add_filter( 'request', 'dialos_child_english_post_routing' );

function dialos_child_english_post_routing( $query_vars ) {
	$pfad = trim( (string) wp_parse_url( $_SERVER['REQUEST_URI'] ?? '', PHP_URL_PATH ), '/' );
	if ( ! preg_match( '#^en/([^/]+)$#', $pfad, $treffer ) ) {
		return $query_vars;
	}
	if ( get_page_by_path( $pfad ) ) {
		return $query_vars; // echte Seite existiert - unveraendert lassen
	}
	$beitrag = get_page_by_path( $treffer[1], OBJECT, 'post' );
	if ( $beitrag ) {
		return array(
			'name'      => $treffer[1],
			'post_type' => 'post',
		);
	}
	return $query_vars;
}

/**
 * "Vorheriger Beitrag" / "Naechster Beitrag" unterhalb des Kommentar-
 * bereichs jedes einzelnen Blogbeitrags (Stephan, 2026-08-25).
 * Navigiert bewusst nur innerhalb derselben Sprache (Erkennung wie
 * ueberall in dieser Datei ueber den ">Deutsch<"-Marker) - sonst
 * wuerde ein deutscher Leser unerwartet auf einen englischen Beitrag
 * springen.
 *
 * Ueber JS nach #comments eingefuegt statt per PHP-Hook
 * "comment_form_after": Bei zwei Beitraegen (186, 209) zeigte die
 * Live-Seite trotz comment_status=open weiterhin "Comments are
 * closed" - vermutlich ein serverseitiger Cache, der auf diese beiden
 * Felder nicht reagiert (Ursache ohne Datei-/Serverzugriff nicht
 * abschliessend zu klaeren). Der Kommentarbereich #comments ist aber
 * so oder so immer vorhanden, offen oder geschlossen - das Einfuegen
 * direkt danach macht die Platzierung unabhaengig von diesem Problem.
 */
add_action( 'wp_footer', 'dialos_child_post_navigation' );

function dialos_child_post_navigation() {
	if ( ! is_singular( 'post' ) ) {
		return;
	}

	global $post;
	$ist_englisch = ( strpos( $post->post_content, '>Deutsch<' ) !== false );

	$alle = get_posts(
		array(
			'post_type'      => 'post',
			'post_status'    => 'publish',
			'posts_per_page' => -1,
			'orderby'        => 'date',
			'order'          => 'ASC',
			'fields'         => 'all',
		)
	);

	$gleiche_sprache = array();
	foreach ( $alle as $p ) {
		$ist_p_englisch = ( strpos( $p->post_content, '>Deutsch<' ) !== false );
		if ( $ist_p_englisch === $ist_englisch ) {
			$gleiche_sprache[] = $p;
		}
	}

	$index = null;
	foreach ( $gleiche_sprache as $i => $p ) {
		if ( $p->ID === $post->ID ) {
			$index = $i;
			break;
		}
	}
	if ( null === $index ) {
		return;
	}

	$vorheriger = $index > 0 ? $gleiche_sprache[ $index - 1 ] : null;
	$naechster  = isset( $gleiche_sprache[ $index + 1 ] ) ? $gleiche_sprache[ $index + 1 ] : null;

	if ( ! $vorheriger && ! $naechster ) {
		return;
	}

	$vorheriger_titel = $ist_englisch ? 'Previous Post' : 'Vorheriger Beitrag';
	$naechster_titel  = $ist_englisch ? 'Next Post' : 'Nächster Beitrag';

	$html = '<div class="dialos-post-nav">';
	if ( $vorheriger ) {
		$html .= '<div class="dialos-post-nav-item"><h3>' . esc_html( $vorheriger_titel ) . '</h3><p><a href="' . esc_url( get_permalink( $vorheriger ) ) . '">' . esc_html( get_the_title( $vorheriger ) ) . '</a></p></div>';
	} else {
		$html .= '<div class="dialos-post-nav-item"></div>';
	}
	if ( $naechster ) {
		$html .= '<div class="dialos-post-nav-item dialos-post-nav-next"><h3>' . esc_html( $naechster_titel ) . '</h3><p><a href="' . esc_url( get_permalink( $naechster ) ) . '">' . esc_html( get_the_title( $naechster ) ) . '</a></p></div>';
	} else {
		$html .= '<div class="dialos-post-nav-item"></div>';
	}
	$html .= '</div>';
	?>
	<script>
	document.addEventListener('DOMContentLoaded', function () {
		var kommentare = document.getElementById('comments');
		var wrapper = document.createElement('div');
		wrapper.innerHTML = <?php echo wp_json_encode( $html ); ?>;
		var nav = wrapper.firstChild;
		if (kommentare && kommentare.parentNode) {
			kommentare.parentNode.insertBefore(nav, kommentare.nextSibling);
		} else {
			var artikel = document.querySelector('article') || document.getElementById('main');
			if (artikel) {
				artikel.appendChild(nav);
			}
		}
	});
	</script>
	<?php
}

/**
 * Zeigt fuer englische Beitraege die /en/-Adresse an (Permalink,
 * interne Verlinkungen, Feeds usw.), passend zu obiger Routing-
 * Aenderung. Erkennung ueber dieselbe Konvention wie beim lang-
 * Attribut: Beitrag beginnt mit einem "Deutsch"-Link -> englischer
 * Beitrag.
 */
add_filter( 'post_link', 'dialos_child_english_post_link', 10, 2 );

function dialos_child_english_post_link( $url, $post ) {
	if ( $post && 'post' === $post->post_type && strpos( $post->post_content, '>Deutsch<' ) !== false ) {
		$url = home_url( '/en/' . $post->post_name . '/' );
	}
	return $url;
}

/**
 * DE/EN-Umschalter im Menue, zwei Flaggen-Symbole nebeneinander direkt
 * vor dem Barrierefrei-Button (Stephan, 2026-08-25 - urspruenglich als
 * eigener Menuepunkt gebaut, dadurch landeten Suchfeld, Flaggen und
 * Barrierefrei-Button auf drei verschiedenen, teils weit auseinander-
 * gerissenen Zeilen; jetzt alle drei im selben Container wie Suche/
 * Barrierefrei-Umschalter, damit sie als eine zusammenhaengende Gruppe
 * direkt unter dem Suchfeld erscheinen). Sucht auf der aktuellen Seite
 * den bereits vorhandenen Sprachumschalter-Link ("Deutsch"/"English",
 * erste-Absatz-Konvention dieser Website) und verwendet dessen Ziel-
 * URL. Fuer Seiten ohne diesen Link (Impressum, Kontakt, Neuigkeiten)
 * faellt die andere Flagge auf die jeweilige Sprach-Startseite zurueck.
 * Prioritaet 16, also NACH dialos_child_search_and_a11y (Prioritaet
 * 10 = Standard) - deren <li> muss zuerst existieren, damit hier
 * hineingehaengt werden kann.
 */
add_action( 'wp_footer', 'dialos_child_language_switcher', 16 );

function dialos_child_language_switcher() {
	?>
	<script>
	document.addEventListener('DOMContentLoaded', function () {
		var a11yButton = document.getElementById('dialos-a11y-button');
		if (!a11yButton || !a11yButton.parentNode) return;

		var links = document.querySelectorAll('a');
		var partnerLink = null;
		for (var i = 0; i < links.length; i++) {
			var text = links[i].textContent.trim();
			if (text === 'English' || text === 'Deutsch') {
				partnerLink = links[i].getAttribute('href');
				break;
			}
		}

		var istEnglisch = window.location.pathname.indexOf('/en/') === 0;
		var deHref = istEnglisch ? (partnerLink || 'https://dialos.org/') : window.location.href;
		var enHref = istEnglisch ? window.location.href : (partnerLink || 'https://dialos.org/en/');

		var wrapper = document.createElement('span');
		wrapper.className = 'dialos-lang-switch';

		var de = document.createElement('a');
		de.href = deHref;
		de.innerHTML = '<span aria-hidden="true">🇩🇪</span><span class="dialos-visually-hidden">Deutsch</span>';
		if (!istEnglisch) {
			de.setAttribute('aria-current', 'page');
			de.classList.add('dialos-lang-active');
		}

		var en = document.createElement('a');
		en.href = enHref;
		en.innerHTML = '<span aria-hidden="true">🇬🇧</span><span class="dialos-visually-hidden">English</span>';
		if (istEnglisch) {
			en.setAttribute('aria-current', 'page');
			en.classList.add('dialos-lang-active');
		}

		wrapper.appendChild(de);
		wrapper.appendChild(en);
		a11yButton.parentNode.insertBefore(wrapper, a11yButton);
	});
	</script>
	<?php
}

/**
 * Menue ins Englische uebersetzen, wenn eine Seite/ein Beitrag unter
 * /en/ liegt (Stephan, 2026-08-25) - Folgeschritt zur URL-Struktur mit
 * /en/-Praefix: Wer auf einer englischen Seite landet, soll auch ein
 * englisches Menue sehen. Direkt an den Menue-Objekten geaendert
 * (server-seitig, "wp_nav_menu_objects"), nicht per JS-Textersetzung
 * wie bei anderen Anpassungen dieser Datei - robuster, weil es nicht
 * vom Zeitpunkt des Ladens oder exaktem sichtbarem Text abhaengt.
 * "Neuigkeiten" und "Kontakt" zeigen seit 2026-08-25 auf eigene
 * englische Seiten (/en/news/, /en/contact/) statt auf die deutschen.
 */
add_filter( 'wp_nav_menu_objects', 'dialos_child_translate_menu' );

function dialos_child_translate_menu( $items ) {
	if ( ! dialos_child_ist_englisch() ) {
		return $items;
	}

	$uebersetzungen = array(
		'Sprachsteuerung'               => array( 'Voice Control', 'https://dialos.org/en/idea/' ),
		'Idee'                           => array( 'Idea', 'https://dialos.org/en/idea/' ),
		'Sprachsteuerungen im Vergleich' => array( 'Voice Control Compared', 'https://dialos.org/en/in-comparison/' ),
		'Unterstützen'                   => array( 'Support', 'https://dialos.org/en/investors-sponsors/' ),
		'Investoren & Sponsoring'        => array( 'Investors & Sponsoring', 'https://dialos.org/en/investors-sponsors/' ),
		'Partner werden'                 => array( 'Become a Partner', 'https://dialos.org/en/become-a-partner/' ),
		'Neuigkeiten'                     => array( 'News', 'https://dialos.org/en/news/' ),
		'Kontakt'                         => array( 'Contact', 'https://dialos.org/en/contact/' ),
	);

	foreach ( $items as $item ) {
		if ( ! isset( $uebersetzungen[ $item->title ] ) ) {
			continue;
		}
		list( $neuer_titel, $neue_url ) = $uebersetzungen[ $item->title ];
		$item->title = $neuer_titel;
		if ( $neue_url ) {
			$item->url = $neue_url;
		}
	}

	return $items;
}

/**
 * "DIALOS"-Markenlink oben links zeigt auf englischen Seiten auf /en/
 * statt auf die deutsche Startseite (Stephan, 2026-08-25 - fiel auf,
 * weil ein Klick darauf komplett aus dem englischen Bereich heraus
 * fuehrte). Der Markenlink gehoert zum Kopfbereich des Eltern-Themes,
 * nicht zum per REST API verwalteten Menue - deshalb hier wie bei
 * anderen Kopf-/Fusszeilen-Anpassungen dieser Datei per JS geaendert.
 */
add_action( 'wp_footer', 'dialos_child_brand_link' );

function dialos_child_brand_link() {
	if ( ! dialos_child_ist_englisch() ) {
		return;
	}
	?>
	<script>
	document.addEventListener('DOMContentLoaded', function () {
		var marke = document.querySelector('.navbar-brand');
		if (marke) {
			marke.setAttribute('href', 'https://dialos.org/en/');
		}
	});
	</script>
	<?php
}

/**
 * "Zum Inhalt springen"-Link fuer Tastatur-/Screenreader-Nutzer.
 *
 * Per JS ganz an den Anfang von <body> gesetzt statt per header.php-
 * Override (gleiche Begruendung wie beim Fusszeilen-Text: das Original
 * nicht blind nachbauen). Optisch unsichtbar, erscheint nur bei
 * Tastatur-Fokus (siehe .dialos-skip-link in style.css).
 */
add_action( 'wp_footer', 'dialos_child_skip_link' );

function dialos_child_skip_link() {
	?>
	<script>
	document.addEventListener('DOMContentLoaded', function () {
		var ziel = document.getElementById('main');
		if (!ziel) return;
		if (!ziel.hasAttribute('tabindex')) {
			ziel.setAttribute('tabindex', '-1');
		}
		var link = document.createElement('a');
		link.href = '#main';
		link.className = 'dialos-skip-link';
		link.textContent = 'Zum Inhalt springen';
		link.addEventListener('click', function (e) {
			e.preventDefault();
			ziel.focus();
			ziel.scrollIntoView();
		});
		document.body.insertBefore(link, document.body.firstChild);
	});
	</script>
	<?php
}


/**
 * Englische Anfuehrungszeichen auf den englischen Seiten (Stephan,
 * 2026-09-17).
 *
 * WARUM: Die Installation laeuft auf Deutsch, und WordPress' wptexturize
 * macht aus geraden Anfuehrungszeichen deshalb deutsche - auf JEDER Seite,
 * auch auf den englischen. Im Quelltext der Beitraege stehen gerade Zeichen;
 * die deutschen entstehen erst beim Ausliefern. Eine Korrektur im Inhalt
 * bringt also nichts, sie muss hier passieren.
 *
 * Gefunden am 2026-09-17 bei einem Durchgang durch alle Seiten: 19 englische
 * Seiten und Beitraege waren betroffen, teils mit ueber 30 Vorkommen. Fuer
 * Muttersprachler liest sich das sofort nach Uebersetzung.
 *
 * Prioritaet 20, damit der Filter NACH wptexturize (10) laeuft. Frueher
 * angesetzt haette er nichts zu tun.
 *
 * wptexturize liefert die Zeichen als numerische Entities, deshalb werden
 * die zuerst vereinheitlicht. HTML-Attribute sind nicht betroffen: Die
 * enthalten gerade Anfuehrungszeichen, keine typografischen.
 */
add_filter( 'the_content', 'dialos_child_englische_anfuehrungszeichen', 20 );
add_filter( 'the_title', 'dialos_child_englische_anfuehrungszeichen', 20 );
add_filter( 'the_excerpt', 'dialos_child_englische_anfuehrungszeichen', 20 );
function dialos_child_englische_anfuehrungszeichen( $text ) {
	if ( ! dialos_child_ist_englisch() ) {
		return $text;
	}
	// Beide Schreibweisen: numerisch (so liefert wptexturize) UND benannt
	// (so steht es teilweise im Inhalt, geschrieben von der
	// Uebersetzungsroutine). Am 2026-09-17 blieben nach dem ersten Anlauf
	// genau vier Zeichen stehen, alle als &bdquo; auf /en/idea/ - der Filter
	// kannte nur die numerische Form.
	$text = str_replace(
		array( '&#8222;', '&#8220;', '&#8221;', '&#8218;', '&#8216;', '&#8217;',
			'&bdquo;', '&ldquo;', '&rdquo;', '&sbquo;', '&lsquo;', '&rsquo;' ),
		array( '„', '“', '”', '‚', '‘', '’',
			'„', '“', '”', '‚', '‘', '’' ),
		$text
	);
	// Deutsches Paar „...“ wird zum englischen “...”, ebenso die einfachen.
	$text = preg_replace( '/„([^„“]*)“/u', '“$1”', $text );
	$text = preg_replace( '/‚([^‚‘]*)‘/u', '‘$1’', $text );
	// Einzelgaenger ohne Partner - lieber ein oeffnendes englisches Zeichen
	// als ein deutsches, das dort ganz sicher falsch ist.
	$text = str_replace( array( '„', '‚' ), array( '“', '‘' ), $text );
	return $text;
}

/**
 * Die drei neuesten Beitraege als EIN Block in der rechten Spalte der
 * Startseite (Stephan, 2026-09-17, praezisiert am selben Abend).
 *
 * WARUM KEIN LAUFBAND: Stephan hatte zuerst nach einem Ticker gefragt und
 * die Idee selbst verworfen. Bewegter Text ist fuer diese Zielgruppe der
 * falsche Weg - ein Screenreader liest Inhalte vor, die sich unter ihm
 * wegbewegen, wer nur noch Umrisse erkennt kann wanderndem Text nicht
 * folgen, und die Richtlinien verlangen fuer Bewegung ueber fuenf Sekunden
 * einen Anhalteknopf. Ein ruhender Block leistet dasselbe.
 *
 * DREI KAESTEN, ABER GROESSER (Aenderung gegenueber 1.6.5): Stephans
 * Vorgabe war, dass ein Kasten so gross wird, wie die drei vorher zusammen
 * waren. Dafuer bekommt jeder Eintrag jetzt zusaetzlich den Textschnipsel
 * des Beitrags. Die Hoehe ergibt sich daraus - bewusst KEINE feste Hoehe
 * und kein min-height: Der Kasten soll so hoch sein, wie sein Inhalt es
 * verlangt, und in keinem Fall scrollen. Soll er groesser werden, wird der
 * Schnipsel laenger, nicht der Kasten gestreckt.
 *
 * OBERKANTE AUF HOEHE DER GRAFIK (Stephans Vorgabe): Der Kasten soll nicht
 * neben der Ueberschrift beginnen, sondern neben dem Bild darunter. Der
 * Abstand wird GEMESSEN, nicht geraten: Das Skript liest die tatsaechliche
 * Position des ersten Bildes im Hauptblock und setzt den oberen Abstand
 * danach. So stimmt es auch bei anderer Schriftgroesse, anderer Zoomstufe
 * und in jeder Sprache - eine feste Pixelzahl waere bei der naechsten
 * Textaenderung falsch, ohne dass es jemand merkt. Neu berechnet wird bei
 * Groessenaenderung und sobald das Bild geladen ist (vorher ist seine
 * Position noch null).
 *
 * WOHIN: Das Eltern-Theme legt neben main#main (col-md-9) bereits ein
 * leeres <aside id="sidebar" class="col-md-3"> an - am Layout war nichts
 * umzubauen. Unter 992 px schiebt Bootstrap die Spalte unter den
 * Hauptblock; dort entfaellt der gemessene Abstand wieder, sonst klaffte
 * eine Luecke.
 *
 * SPRACHE: Auf /en/ die drei neuesten englischen Beitraege, sonst die
 * deutschen, erkannt am Marker '>Deutsch<' - dieselbe Konvention wie in
 * dialos_child_english_post_link(). Wer sie aendert, muss beide Stellen
 * anfassen.
 */
add_action( 'wp_footer', 'dialos_child_neueste_beitraege', 22 );

function dialos_child_neueste_beitraege() {
	if ( ! is_page( array( 2, 135 ) ) ) {
		return;
	}
	$englisch = dialos_child_ist_englisch();
	$treffer  = array();

	foreach ( get_posts( array( 'numberposts' => 40, 'post_status' => 'publish' ) ) as $beitrag ) {
		$ist_englisch = ( false !== strpos( $beitrag->post_content, '>Deutsch<' ) );
		if ( $ist_englisch === $englisch ) {
			$treffer[] = $beitrag;
		}
		if ( count( $treffer ) === 3 ) {
			break;
		}
	}
	if ( ! $treffer ) {
		return;
	}

	// date_i18n folgt der Sprache der Installation, und die ist Deutsch.
	// Fuer /en/ deshalb uebersetzen - sonst stuende dort ein deutscher
	// Monatsname mitten im englischen Block.
	$monate_de = array( 'Januar', 'Februar', 'März', 'April', 'Mai', 'Juni',
		'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember' );
	$monate_en = array( 'January', 'February', 'March', 'April', 'May', 'June',
		'July', 'August', 'September', 'October', 'November', 'December' );

	$eintraege = array();
	foreach ( $treffer as $beitrag ) {
		$datum = $englisch
			? str_replace( $monate_de, $monate_en, date_i18n( 'j F Y', strtotime( $beitrag->post_date ) ) )
			: date_i18n( 'j. F Y', strtotime( $beitrag->post_date ) );

		// Achtzig Woerter, also reichlich. Wie viele davon stehenbleiben,
		// entscheidet erst der Browser: Dort laesst sich messen, wie hoch
		// die Kachel bei dieser Fensterbreite, Schriftgroesse und Titellaenge
		// tatsaechlich wird. Eine feste Wortzahl waere immer fuer genau einen
		// Fall richtig - bei einem langen Chronik-Titel zu viel, bei einem
		// kurzen zu wenig (Stephan am 2026-09-18: "den Block auch auffuellen,
		// wenn noch Platz ist").
		// Aus dem Beitrag muss alles heraus, was kein Fliesstext ist. Am
		// 2026-09-17 stand in JEDER deutschen Kachel "Diesen Beitrag
		// anhoeren - gesprochen von Anna" (die Beschriftung des
		// Audio-Blocks) und in jeder englischen "16 September 2026 General"
		// (die Datumszeile, die die Chronik-Routine fuer die englische
		// Anzeige einfuegt). Beides wurde erst am fertigen Auftritt
		// sichtbar, nicht im Code.
		//
		// Die Reihenfolge ist egal, die Vollstaendigkeit nicht:
		//   style/script - die eingebettete Datums-Korrektur
		//   .meta        - die Datums- und Kategoriezeile selbst
		//   lang-marker  - der per CSS versteckte Sprachumschalter
		//   figure       - Bildunterschriften UND der Audio-Block
		$roh = $beitrag->post_content;
		$roh = preg_replace( '#<style.*?</style>#s', ' ', $roh );
		$roh = preg_replace( '#<script.*?</script>#s', ' ', $roh );
		$roh = preg_replace( '#<p class="[^"]*dialos-lang-marker[^"]*".*?</p>#s', ' ', $roh );
		$roh = preg_replace( '#<p class="[^"]*\bmeta\b[^"]*".*?</p>#s', ' ', $roh );
		$roh = preg_replace( '#<figure.*?</figure>#s', ' ', $roh );
		$text = has_excerpt( $beitrag ) ? $beitrag->post_excerpt : $roh;
		// html_entity_decode, sonst steht woertlich "&ndash;" in der Kachel.
		// Am 2026-09-18 auf der Startseite gesehen: "gebuendelt auf zwei
		// Tage &ndash; dazwischen drei Wochen". wp_strip_all_tags() entfernt
		// nur Tags, keine Entitaeten - und weil der Text spaeter ueber
		// textContent gesetzt wird (richtig so, das schuetzt vor
		// eingeschleustem Code), erscheint die Entitaet dann als Text.
		$text = html_entity_decode( wp_strip_all_tags( $text ), ENT_QUOTES, 'UTF-8' );
		$text = wp_trim_words( $text, 80, '' );

		$eintraege[] = array(
			'titel' => get_the_title( $beitrag ),
			'url'   => get_permalink( $beitrag ),
			'datum' => $datum,
			'iso'   => mysql2date( 'Y-m-d', $beitrag->post_date ),
			'text'  => $text,
		);
	}

	$texte = array(
		'ueberschrift' => $englisch ? 'Latest posts' : 'Neueste Beiträge',
		'alle'         => $englisch ? 'All news' : 'Alle Neuigkeiten',
		'alle_url'     => $englisch ? home_url( '/en/news/' ) : home_url( '/neuigkeiten/' ),
	);
	?>
	<script>
	document.addEventListener('DOMContentLoaded', function () {
		var spalte = document.querySelector('#sidebar .content-sidebar');
		var haupt  = document.getElementById('main');
		if (!spalte || !haupt) return;

		var daten = <?php echo wp_json_encode( $eintraege ); ?>;
		var texte = <?php echo wp_json_encode( $texte ); ?>;

		var block = document.createElement('section');
		block.className = 'dialos-neueste';
		block.setAttribute('aria-labelledby', 'dialos-neueste-titel');

		var titel = document.createElement('h2');
		titel.id = 'dialos-neueste-titel';
		titel.className = 'dialos-neueste-titel';
		titel.textContent = texte.ueberschrift;
		block.appendChild(titel);

		daten.forEach(function (e) {
			var eintrag = document.createElement('article');
			eintrag.className = 'dialos-neueste-block';

			var h = document.createElement('h3');
			var link = document.createElement('a');
			link.href = e.url;
			link.textContent = e.titel;
			h.appendChild(link);
			eintrag.appendChild(h);

			var datum = document.createElement('time');
			datum.className = 'dialos-neueste-datum';
			datum.setAttribute('datetime', e.iso);
			datum.textContent = e.datum;
			eintrag.appendChild(datum);

			if (e.text) {
				var text = document.createElement('p');
				text.className = 'dialos-neueste-text';
				text.textContent = e.text;
				eintrag.appendChild(text);
				eintrag.dataset.text = e.text;
			}

			block.appendChild(eintrag);
		});

		var alle = document.createElement('p');
		alle.className = 'dialos-neueste-alle';
		var alleLink = document.createElement('a');
		alleLink.href = texte.alle_url;
		alleLink.textContent = texte.alle;
		alle.appendChild(alleLink);
		block.appendChild(alle);

		spalte.appendChild(block);

		// Oberkante auf Hoehe der Grafik im Hauptblock - gemessen, nicht
		// geraten. Unter 992 px stehen die Spalten untereinander, dort waere
		// ein Abstand eine Luecke.
		// Jede Kachel so weit fuellen, wie sie Platz hat, und keinen Deut
		// weiter. Gemessen wird die Hoehe gegen die Breite: Solange die
		// Kachel hoeher als breit ist, passt der Text nicht ins Quadrat und
		// es fliegen Woerter raus. Bewusst OHNE overflow:hidden - waere das
		// Skript einmal nicht da, wuerde der Text sonst lautlos abgeschnitten.
		// So waechst die Kachel im schlimmsten Fall sichtbar, statt etwas zu
		// verstecken, das niemand findet, der den Bildschirm nicht sieht.
		function fuellen() {
			if (window.innerWidth < 992) return;
			block.querySelectorAll('.dialos-neueste-block').forEach(function (kasten) {
				var absatz = kasten.querySelector('.dialos-neueste-text');
				if (!absatz || !kasten.dataset.text) return;
				var woerter = kasten.dataset.text.split(' ');
				var n = woerter.length;
				absatz.textContent = woerter.join(' ');
				// Schrittweise kuerzen. Erst grob, dann Wort fuer Wort, damit
				// es auch bei achtzig Woertern in wenigen Durchlaeufen sitzt.
				var schritt = 8;
				while (n > 6 && kasten.offsetHeight > kasten.offsetWidth + 1) {
					n -= schritt;
					if (n < 6) { n = 6; }
					absatz.textContent = woerter.slice(0, n).join(' ') + ' …';
					if (schritt > 1 && kasten.offsetHeight <= kasten.offsetWidth + 1) {
						n += schritt; schritt = 1;
						absatz.textContent = woerter.slice(0, n).join(' ') + ' …';
					}
				}
				if (n < woerter.length && absatz.textContent.slice(-1) !== '…') {
					absatz.textContent = absatz.textContent + ' …';
				}
			});
		}

		function ausrichten() {
			block.style.marginTop = '';
			if (window.innerWidth < 992) return;
			var bild = haupt.querySelector('figure img, img');
			if (!bild) return;
			var abstand = bild.getBoundingClientRect().top - spalte.getBoundingClientRect().top;
			if (abstand > 0) block.style.marginTop = Math.round(abstand) + 'px';
		}

		fuellen();
		ausrichten();
		window.addEventListener('load', function () { fuellen(); ausrichten(); });
		var bild = haupt.querySelector('figure img, img');
		if (bild && !bild.complete) bild.addEventListener('load', ausrichten);

		var warten;
		window.addEventListener('resize', function () {
			clearTimeout(warten);
			warten = setTimeout(function () { fuellen(); ausrichten(); }, 150);
		});
	});
	</script>
	<?php
}
