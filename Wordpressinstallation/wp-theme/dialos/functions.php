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
			'<a href="https://dialos.org/impressum/">Legal Notice</a>' .
			'<a href="https://dialos.org/datenschutzerklaerung/">Privacy Policy (Website)</a>' .
			'<a href="https://dialos.org/dialos-mobil-datenschutz/">Privacy Policy (App)</a>' .
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
 */
add_filter( 'request', 'dialos_child_english_post_routing' );

function dialos_child_english_post_routing( $query_vars ) {
	if ( isset( $_GET['dialos_debug'] ) ) {
		header( 'X-Dialos-QueryVars: ' . wp_json_encode( $query_vars ) );
		header( 'X-Dialos-RequestUri: ' . ( $_SERVER['REQUEST_URI'] ?? '' ) );
	}
	if ( empty( $query_vars['pagename'] ) ) {
		return $query_vars;
	}
	if ( ! preg_match( '#^en/([^/]+)$#', $query_vars['pagename'], $treffer ) ) {
		return $query_vars;
	}
	if ( get_page_by_path( $query_vars['pagename'] ) ) {
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
 * "Kontakt" hat keine englische Entsprechung - dort wird nur die
 * Beschriftung uebersetzt, das Ziel bleibt deutsch. "Neuigkeiten"
 * zeigt seit 2026-08-25 auf die eigene englische Uebersicht /en/news/.
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
		'Kontakt'                         => array( 'Contact', null ),
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

