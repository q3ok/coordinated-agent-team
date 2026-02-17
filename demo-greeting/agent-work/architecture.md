# Greeting Card Generator — Architektura

## 1. Przegląd

Greeting Card Generator to minimalna aplikacja front-endowa działająca wyłącznie w przeglądarce. Użytkownik wpisuje imię, wybiera jeden z trzech predefiniowanych kolorów tła, klika „Generuj" i widzi stylizowaną kartkę z powitaniem „Hello, {name}!". Aplikacja składa się z 3 plików (`index.html`, `app.js`, `styles.css`) w katalogu `demo-greeting/`, otwieranych bezpośrednio z systemu plików (`file://`). Brak backendu, frameworków, build toolingu i persystencji.

## 2. Mapowanie wymagań na komponenty

| Wymaganie | Odpowiedzialny element | Szczegóły |
|-----------|----------------------|-----------|
| FR-01: Pole imienia | `index.html` (markup) + `app.js` (walidacja) | `<input>` z `<label>`, walidacja `trim()` + empty check |
| FR-02: Wybór koloru | `index.html` (radio buttons) + `styles.css` (swatche) | 3x `<input type="radio">` z wizualnymi etykietami |
| FR-03: Przycisk „Generuj" | `index.html` (markup) + `app.js` (handler) | `<button type="button">` z event listenerem |
| FR-04: Wyświetlenie kartki | `app.js` (logika) + `styles.css` (styl kartki) | Dynamiczne ustawienie `textContent` i `style.backgroundColor` |
| FR-05: Re-generacja | `app.js` (aktualizacja istniejącego elementu) | Jeden element kartki aktualizowany in-place |

## 3. Moduły i odpowiedzialności

### 3.1 Struktura plików

```
demo-greeting/
  index.html      ← punkt wejścia, struktura HTML, ładuje CSS i JS
  app.js           ← cała logika aplikacji (ES Module)
  styles.css       ← style wizualne, custom properties, card styling
```

Struktura płaska (flat) — bez podkatalogów `public/`. Uzasadnienie: spec wymaga 3 plików w jednym katalogu; project nie potrzebuje testów, build toolingu ani skryptów. Decyzja udokumentowana w ADR-001.

### 3.2 `index.html`

**Odpowiedzialności:**
- Definiuje semantyczną strukturę strony (formularz + obszar wynikowy)
- Ładuje `styles.css` w `<head>` i `app.js` jako `<script type="module">` na końcu `<body>`
- Zapewnia dostępność: `<label>` dla każdego inputa, `aria-labelledby` na sekcjach, `aria-live="polite"` na obszarze kartki

**Struktura DOM:**
```
<body>
  <main>
    <h1>Greeting Card Generator</h1>
    <section#form-section aria-labelledby="form-heading">
      <h2#form-heading>Utwórz kartkę</h2>
      <label for="name-input">Twoje imię</label>
      <input#name-input type="text" placeholder="Wpisz imię…">
      <fieldset>
        <legend>Wybierz kolor</legend>
        <label><input type="radio" name="color" value="#FF6B6B" checked> Coral</label>
        <label><input type="radio" name="color" value="#4ECDC4"> Sky Blue</label>
        <label><input type="radio" name="color" value="#FFE66D"> Sunshine</label>
      </fieldset>
      <button#generate-btn type="button">Generuj</button>
      <p#error-msg class="error-msg" role="alert" hidden></p>
    </section>
    <section#card-section aria-labelledby="card-heading">
      <h2#card-heading class="sr-only">Podgląd kartki</h2>
      <div#card-output aria-live="polite"></div>
    </section>
  </main>
</body>
```

### 3.3 `app.js` (ES Module)

**Odpowiedzialności:**
- Inicjalizacja: pobranie referencji do elementów DOM przez `getElementById` / `querySelector`
- Obsługa zdarzenia kliknięcia „Generuj"
- Walidacja inputu: `trim()`, sprawdzenie pustego stringa
- Odczytanie wybranego koloru (`querySelector('input[name="color"]:checked')`)
- Renderowanie kartki: ustawienie `textContent` i `style.backgroundColor` na elemencie `#card-output`
- Wyświetlanie / ukrywanie komunikatu walidacji

**Eksportowane API (kontrakt):**

```js
// Stałe kolorów (referencyjne)
export const COLOR_PRESETS = [
  { value: '#FF6B6B', label: 'Coral' },
  { value: '#4ECDC4', label: 'Sky Blue' },
  { value: '#FFE66D', label: 'Sunshine' },
];

// Walidacja imienia — czysta funkcja
export function validateName(raw) {
  const trimmed = (raw ?? '').trim();
  if (trimmed.length === 0) {
    return { ok: false, error: 'Wpisz imię, aby wygenerować kartkę.' };
  }
  return { ok: true, name: trimmed };
}

// Generowanie tekstu powitania — czysta funkcja
export function greetingText(name) {
  return `Hello, ${name}!`;
}

// Inicjalizacja aplikacji (wywoływana z poziomu modułu)
export function initApp(doc = document) { ... }
```

**Wzorzec:** Czyste funkcje (`validateName`, `greetingText`) wydzielone dla testowalności. Funkcja `initApp` enkapsuluje DOM binding i handlery. Brak klas — wzorzec factory function / closure zgodny z konwencją repozytorium.

### 3.4 `styles.css`

**Odpowiedzialności:**
- Custom properties na `:root` dla palety kolorów i typografii
- Reset bazowy: `* { box-sizing: border-box; }`, `body { margin: 0; }`
- Layout: wycentrowany kontener z `max-width`
- Stylowanie formularza: `font: inherit` na form controls, spacing
- Stylowanie radio buttonów jako wizualnych swatchy (opcjonalnie)
- Klasa `.card` na elemencie wyjściowym: `border-radius`, `padding`, `box-shadow`, centrowany tekst
- Klasa `.error-msg`: kolor czerwony, komunikat walidacji
- Klasa `.sr-only` dla treści dostępnych tylko dla screen readerów
- Kontrast tekstu na kartce: biały tekst z cieniem lub czarny tekst — dobrany do czytelności na wszystkich 3 kolorach

## 4. Przepływ danych

1. **Ładowanie strony** → przeglądarka parsuje `index.html`, ładuje `styles.css`, wykonuje `app.js` jako moduł
2. **Inicjalizacja** → `initApp()` pobiera referencje DOM, binduje listener na `#generate-btn`
3. **Użytkownik wpisuje imię** → wartość pozostaje w `<input>`, nie jest przetwarzana do kliknięcia
4. **Użytkownik wybiera kolor** → radio button przechowuje stan natywnie w DOM
5. **Kliknięcie „Generuj"**:
   - `app.js` odczytuje `#name-input.value`
   - Wywołuje `validateName(value)`
   - Jeśli `ok === false` → wyświetla `#error-msg` z treścią błędu, ukrywa kartkę → STOP
   - Jeśli `ok === true` → ukrywa `#error-msg`
   - Odczytuje zaznaczony radio button → `selectedColor`
   - Ustawia `#card-output.textContent = greetingText(name)`
   - Ustawia `#card-output.style.backgroundColor = selectedColor`
   - Ustawia `#card-output.classList.add('card')` (jeśli jeszcze nie dodana)
6. **Re-generacja** → ten sam flow; element `#card-output` jest aktualizowany, nie tworzony na nowo

```
[User Input] → [validate] → OK? → [render card with textContent + backgroundColor]
                           ↓ NO
                     [show error msg]
```

## 5. Interfejsy i kontrakty

### 5.1 HTML → JS

| Element ID | Typ | Opis |
|-----------|-----|------|
| `name-input` | `<input type="text">` | Pole na imię użytkownika |
| `generate-btn` | `<button>` | Przycisk generuj |
| `card-output` | `<div>` | Kontener na wygenerowaną kartkę |
| `error-msg` | `<p>` | Komunikat walidacji (ukryty domyślnie) |
| `input[name="color"]:checked` | `<input type="radio">` | Aktywnie wybrany kolor |

### 5.2 JS → DOM (operacje zapisu)

| Operacja | Metoda | Uwaga |
|----------|--------|-------|
| Tekst kartki | `el.textContent = ...` | Nigdy `innerHTML` — ochrona przed XSS |
| Kolor tła kartki | `el.style.backgroundColor = selectedColor` | Wartość z atrybutu `value` radio buttona |
| Widoczność klasy | `el.classList.add('card')` | Dodanie stylu kartki |
| Komunikat błędu | `el.textContent = msg; el.hidden = false/true` | Wykorzystanie atrybutu `hidden` |

### 5.3 Czyste funkcje (testowalne bez DOM)

```
validateName(raw: string) → { ok: true, name: string } | { ok: false, error: string }
greetingText(name: string) → string
```

## 6. Strategia obsługi błędów

| Scenariusz | Obsługa |
|-----------|---------|
| Puste imię / tylko spacje | `validateName` zwraca `{ ok: false, error }` → wyświetlany komunikat inline |
| Brak zaznaczonego koloru | Niemożliwe — pierwszy radio jest `checked` domyślnie. Fallback: użyj `COLOR_PRESETS[0].value` |
| Znaki specjalne / HTML w imieniu | Bezpieczne — `textContent` eskejpuje HTML automatycznie |
| Bardzo długie imię | CSS `word-wrap: break-word` / `overflow-wrap` na kartce |
| JS wyłączony | `<noscript>` w HTML z komunikatem informacyjnym (nice-to-have) |

## 7. Strategia konfiguracji

Brak runtime konfiguracji. Wszystkie wartości (kolory, tekst, etykiety) są hardcoded w source:
- **Kolory**: zdefiniowane jako `value` atrybuty w radiach HTML i jako stała `COLOR_PRESETS` w `app.js`
- **Tekst powitania**: template `Hello, ${name}!` w funkcji `greetingText`
- **Etykiety UI**: inline w HTML (polski, zgodnie z konwencją repozytorium)
- **Wartości CSS**: custom properties w `:root`

## 8. Bezpieczeństwo

- **XSS**: Brak `innerHTML`, `eval()`, `new Function()`. Tekst użytkownika renderowany wyłącznie przez `textContent`.
- **Dane użytkownika**: Nie opuszczają przeglądarki — brak requestów sieciowych, brak storage.
- **CSP**: Nie wymagany (brak inline scripts, brak zewnętrznych zasobów), ale kompatybilny.
- **Walidacja**: Input sanityzowany przez `trim()` i sprawdzenie pustego stringa.

## 9. Strategia testowania (przegląd)

### 9.1 Testy jednostkowe (opcjonalne)

Czyste funkcje (`validateName`, `greetingText`) są testowalnie wydzielone i mogą być przetestowane za pomocą `node:test` + `node:assert/strict` bez DOM:

```js
import { validateName, greetingText } from '../app.js';
test('validateName trims and accepts valid name', () => { ... });
test('validateName rejects empty string', () => { ... });
test('greetingText formats correctly', () => { ... });
```

Jeśli QA zdecyduje o testach, wystarczy dodać `tests/app.test.js` i minimalny `package.json` z `"type": "module"` + `"test": "node --test"`.

### 9.2 Testy manualne

Wszystkie AC (AC-001 do AC-008) weryfikowane manualnie — otwarcie `index.html`, sprawdzenie formularza, generowanie kartki, edge cases.

### 9.3 Lint (opcjonalny)

Jeśli dodany, scanner sprawdza: brak `innerHTML=`, `eval(`, `new Function(` — wzorzec z `demo-pomidoro`.

## 10. Przyszłe rozszerzenia (poza scope)

Nie planowane, ale architektura nie blokuje:
- Dodanie eksportu kartki jako obrazka (Canvas API)
- Dodanie więcej kolorów lub custom color picker
- Dodanie persystencji (localStorage)
- Dodanie animacji generowania kartki (CSS transitions)
