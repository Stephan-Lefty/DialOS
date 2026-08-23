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
	?>
	<script>
	document.addEventListener('DOMContentLoaded', function () {
		var footerText = document.querySelector('.footer .col-md-6 p');
		if (footerText && footerText.textContent.indexOf('DialOS') !== -1) {
			footerText.innerHTML =
				'&copy; Copyright ' + new Date().getFullYear() + ' DialOS.org' +
				' &ndash; Kontakt: <a href="mailto:kontakt@dialos.org">kontakt@dialos.org</a>' +
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
 * Seitenweite Suche als letzten Menuepunkt anhaengen.
 *
 * WordPress' eingebaute Suche funktioniert bereits (Aufruf ueber
 * ?s=...), das Theme zeigt bisher nur kein Formular dafuer an. Als
 * <li> ans bestehende Menue "menu-seiten" angehaengt statt eigenes
 * Markup irgendwo einzuschieben - erscheint dadurch automatisch auch
 * im mobilen Seiten-Menue mit, ohne eigene Positionierung noetig.
 */
add_action( 'wp_footer', 'dialos_child_search' );

function dialos_child_search() {
	$aktion = esc_url( home_url( '/' ) );
	?>
	<script>
	document.addEventListener('DOMContentLoaded', function () {
		var menu = document.getElementById('menu-seiten');
		if (!menu) return;
		var li = document.createElement('li');
		li.className = 'dialos-search-item';
		li.innerHTML =
			'<form class="dialos-search-form" role="search" method="get" action="<?php echo $aktion; ?>">' +
			'<label class="dialos-visually-hidden" for="dialos-search-input">Suchen</label>' +
			'<input type="search" id="dialos-search-input" name="s" placeholder="Suchen …" />' +
			'<button type="submit" aria-label="Suche starten">&#128269;</button>' +
			'</form>';
		menu.appendChild(li);
	});
	</script>
	<?php
}
