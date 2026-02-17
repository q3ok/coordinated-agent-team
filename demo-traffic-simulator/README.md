# Traffic Simulator Demo

Minimalna statyczna aplikacja symulująca ruch pojazdów na prostym skrzyżowaniu.

## Uruchomienie lokalne

1. Otwórz folder `demo-traffic-simulator`.
2. Uruchom prosty serwer statyczny (zalecane), np.:
   - `python -m http.server 8080`
3. Otwórz `http://localhost:8080`.

Alternatywnie możesz otworzyć `index.html` bez serwera (`file://`), ale część przeglądarek ogranicza ładowanie modułów ES w tym trybie.

## Tryb offline

- Po udostępnieniu plików lokalnie aplikacja nie wymaga połączenia z internetem do działania symulacji.
- Demo nie korzysta z backendu ani zewnętrznych usług runtime.

## Kompatybilność z GitHub Pages

- Aplikacja jest statyczna (HTML/CSS/JS), więc jest zgodna z hostingiem GitHub Pages.
- Utrzymuj ścieżki względne do zasobów (`public/...`) i publikuj zawartość katalogu `demo-traffic-simulator`.
- `localStorage` (jeśli dostępny w przeglądarce) przechowuje tylko lokalne ustawienia użytkownika.

## Funkcje

- Widoczna mapa dróg/siatka i pojazdy na `canvas`.
- Ruch po pasach z prostą logiką hamowania i bez nakładania pojazdów na tym samym pasie.
- Sterowanie: natężenie ruchu, mnożnik prędkości, tryb sygnalizacji, gęstość pasa, pauza/wznów, reset.
- Statystyki live: aktywne pojazdy, średnia prędkość, przepustowość, zatrzymane pojazdy.
- Zapisywanie ustawień do `localStorage` (bez danych wrażliwych).

## Struktura

- `index.html` — layout i semantyczna struktura UI
- `public/styles.css` — minimalne style responsywne
- `public/app.js` — bootstrap i połączenie modułów
- `public/state.js` — stan globalny i normalizacja ustawień
- `public/simulation.js` — pętla fixed timestep
- `public/traffic-model.js` — spawn, sygnalizacja, logika ruchu
- `public/renderer-canvas.js` — render mapy i pojazdów
- `public/controls.js` — obsługa wejść użytkownika
- `public/metrics.js` — metryki runtime
- `public/ui.js` — aktualizacja tekstów UI
- `public/storage.js` — trwałość ustawień
