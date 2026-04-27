# Catálogo de riesgos IA

> **Catálogo v0.1.** Identificadores estables para riesgos típicos de
> IA referenciados desde `QUALITY_FRAMEWORK.md`, usados dentro de cada
> salida de auditoría para permitir agregación, seguimiento de
> recurrencia y análisis longitudinal.

## Cómo leer este catálogo

Cada entrada es una hipótesis: “es más probable que el código iOS
asistido por IA exhiba este patrón que el código escrito a mano”. El
catálogo es el vocabulario del plugin para esa hipótesis. Si un
riesgo concreto recurre en la práctica es algo que los datos de
auditoría contestan (ver `QUALITY_FRAMEWORK.md` Sección 7.3).

### Esquema de identificador

```
AI-3.X-NNN
```

- `3.X` — dimensión de calidad del modelo de calidad.
- `NNN` — índice secuencial con cero a la izquierda, por dimensión.

Los identificadores son estables. Nunca se reutilizan tras retirarse.
Un riesgo retirado se mantiene en este documento con
`status: retired` y una breve justificación.

### Valores de estado

- **`cited`** — al menos una fuente pública explícita describe el
  patrón como una desviación recurrente de la IA.
- **`common knowledge`** — ampliamente aceptado en la comunidad iOS,
  sin una fuente canónica única, pero observado de forma consistente.
- **`framework heuristic`** — introducido por este catálogo como una
  hipótesis testable. Será promovido, reformulado o retirado en
  función de los datos de auditoría acumulados.
- **`retired`** — ya no se usa. El ID se conserva para trazabilidad.

### Forma de cada entrada

Cada riesgo incluye:

- **ID, título, dimensión, estado.**
- **Descripción** — un párrafo en lenguaje claro con el riesgo.
- **Manifestación IA** — cómo tiende a introducirlo un copiloto de IA.
- **Ejemplo** — ilustración mínima (sin código completo, sin secretos
  reales).
- **Fuentes** — citas o punteros, cuando aplica.

---

## Dimensión 3.1 — Encaje de producto y límites

### AI-3.1-001 — Funcionalidad especulativa fuera del spec

- **Estado:** framework heuristic.
- **Descripción:** El codebase contiene rutas o feature flags para
  capacidades que nunca formaron parte de la especificación del
  producto, añadidas “por si acaso” o generadas por una IA que
  extrapoló más allá del prompt.
- **Manifestación IA:** un copiloto, al que se le pide “añadir
  login”, también añade reset de contraseña, login social y
  biométrico, ninguno de los cuales se solicitó ni diseñó.
- **Ejemplo:** un `enum AuthProvider { case email, google, apple,
  facebook }` sin dueño, con solo `email` realmente conectado a la UI.
- **Fuentes:** framework heuristic; informado por retrospectivas de
  trabajo asistido por IA.

---

## Dimensión 3.2 — Arquitectura y modularidad

### AI-3.2-001 — Capas plausibles pero inconsistentes

- **Estado:** framework heuristic.
- **Descripción:** El proyecto anuncia una arquitectura por capas
  (p. ej. MVVM + Coordinator + Repository) pero las capas filtran:
  las vistas hacen fetch a red, los view models persisten directamente,
  los repositorios contienen lógica de UI.
- **Manifestación IA:** la IA tiende a producir nombres que casan con
  un patrón aunque las responsabilidades no. La estructura parece
  correcta desde un listado de directorios y se rompe al inspeccionar.
- **Ejemplo:** un `HomeViewModel` que importa `URLSession` y decodifica
  JSON inline.
- **Fuentes:** framework heuristic; alineado con guías generales de
  arquitectura iOS por capas (Swift by Sundell — temas de arquitectura).

### AI-3.2-002 — Dependencias directas entre capas

- **Estado:** common knowledge.
- **Descripción:** un componente de mayor nivel (típicamente una
  vista) importa uno de menor nivel (red, persistencia) sin pasar
  por una abstracción.
- **Manifestación IA:** ante el prompt “añade un botón que cargue
  datos”, la IA frecuentemente inlinea la llamada de red en
  `.task { ... }` en lugar de pasar por un view model o repositorio.
- **Ejemplo:** `import Foundation` + `URLSession.shared.dataTask`
  dentro de la acción de un `Button { ... }`.
- **Fuentes:** common knowledge en la comunidad iOS; reforzado por
  contenido de Swift by Sundell sobre separación de responsabilidades.

---

## Dimensión 3.3 — Integridad del modelo de dominio

### AI-3.3-001 — Identificadores stringly-typed e invariantes débiles

- **Estado:** common knowledge.
- **Descripción:** los identificadores son `String` plano en todos
  lados; los enums se sustituyen por constantes string; los
  invariantes no se garantizan por el sistema de tipos.
- **Manifestación IA:** la IA gravita hacia `String` por ser el tipo
  más genérico que compila. Ante “user id”, produce `let id: String`
  en lugar de un `UserID` tipado.
- **Ejemplo:** `func loadUser(id: String)` y otro
  `func loadOrder(id: String)` aceptando el mismo tipo.
- **Fuentes:** common knowledge; reforzado por Swift by Sundell
  (typed identifiers y semántica valor).

---

## Dimensión 3.4 — Estado, concurrencia y data races

### AI-3.4-001 — Parches de concurrencia que ocultan problemas de aislamiento

- **Estado:** cited / common knowledge.
- **Descripción:** se salpican `@MainActor`, `DispatchQueue.main.async`
  o `Task { @MainActor in ... }` para silenciar warnings o resolver
  crashes observados, en lugar de diseñar las fronteras de actor.
- **Manifestación IA:** ante un warning de data race, la IA tiende a
  añadir la anotación más pequeña que compile, frecuentemente la
  equivocada (p. ej. `@MainActor` sobre una propiedad que no debería
  estar bound a UI).
- **Ejemplo:** una clase `Repository` declarada `@MainActor` porque
  una vista la usaba; ahora todo su trabajo bloquea el main thread.
- **Fuentes:** Donny Wals (contenido de Swift Concurrency);
  Antoine van der Lee (herramientas y artículos de migración a
  Swift 6).

### AI-3.4-002 — Tasks sin acotar o sin cancelación

- **Estado:** common knowledge.
- **Descripción:** bloques `Task { ... }` creados sin cancelación,
  observers de larga vida sin anclaje al ciclo de vida, fugas al
  cerrar vistas.
- **Manifestación IA:** la IA usa `Task { ... }` como primitiva
  fire-and-forget sin acoplar su vida a la de la vista que la posee.
- **Ejemplo:** `.onAppear { Task { await poll() } }` sin
  `.task { ... }` ni chequeo de `Task.isCancelled`.
- **Fuentes:** common knowledge; reforzado por la documentación
  oficial de Swift Concurrency.

---

## Dimensión 3.5 — Fiabilidad y manejo de errores

### AI-3.5-001 — Errores tragados en silencio

- **Estado:** cited.
- **Descripción:** se capturan errores y se ignoran, o se usa `try?`
  para tirar fallos, dejando al usuario mirando una pantalla en blanco.
- **Manifestación IA:** la IA prefiere código que compile limpio. El
  camino más corto es tragar el error: `try?`, `catch` vacío,
  `if let _ = try? ...`.
- **Ejemplo:** `let data = try? Data(contentsOf: url)`, con `data`
  silenciosamente `nil` ante cualquier error.
- **Fuentes:** Paul Hudson — *What to fix in AI-generated Swift code*
  (`hudson:281`).

### AI-3.5-002 — Lógica de retry/fallback plausible pero inefectiva

- **Estado:** framework heuristic.
- **Descripción:** código de retry que corre una vez sin backoff,
  fallbacks que no recuperan realmente, ramas “offline” que devuelven
  datos placeholder sin que el usuario lo sepa.
- **Manifestación IA:** la IA genera la forma de la robustez sin la
  sustancia: un `for _ in 0..<3` sin jitter, o un `catch` que devuelve
  `[]` y deja a la UI mostrando “sin elementos”.
- **Ejemplo:** `try await api.fetch()` envuelto en un loop de tres
  iteraciones con `try? await Task.sleep(for: .seconds(1))` y sin
  jitter.
- **Fuentes:** framework heuristic.

---

## Dimensión 3.6 — Seguridad y privacidad

### AI-3.6-001 — Secretos hardcodeados o almacenamiento inseguro

- **Estado:** common knowledge.
- **Descripción:** API keys, tokens o contraseñas aparecen en código
  fuente, en `UserDefaults`, en archivos plist o en constantes tipo
  entorno.
- **Manifestación IA:** la IA rellena placeholders de secretos para
  hacer ejecutable el código aislado; esos placeholders sobreviven a
  producción.
- **Ejemplo:** `let apiKey = "sk_live_abc123..."` en un `Constants.swift`.
- **Fuentes:** OWASP MASVS v2.1 — STORAGE; Apple App Review
  Guidelines — Safety/Legal.

### AI-3.6-002 — Relajaciones de App Transport Security

- **Estado:** common knowledge.
- **Descripción:** `NSAllowsArbitraryLoads` puesto a `true` o
  excepciones de dominio amplias, frecuentemente “para desarrollo”,
  que se quedan en el binario que se publica.
- **Manifestación IA:** la IA da la solución más amplia para que la
  request funcione, en lugar de añadir la excepción concreta o
  arreglar el certificado del lado servidor.
- **Ejemplo:** `NSAppTransportSecurity / NSAllowsArbitraryLoads = YES`
  en el `Info.plist` del target de producción.
- **Fuentes:** documentación de App Transport Security de Apple;
  OWASP MASVS v2.1 — NETWORK.

### AI-3.6-003 — Privacy manifest ausente o inexacto

- **Estado:** common knowledge.
- **Descripción:** `PrivacyInfo.xcprivacy` ausente, sin razones
  requeridas para APIs trackeadas o con dominios de tracking
  declarados que no coinciden con los que la app contacta.
- **Manifestación IA:** la IA no genera `PrivacyInfo.xcprivacy` salvo
  que se le pida; tampoco lo actualiza al añadir nuevos SDKs.
- **Ejemplo:** se integra un SDK nuevo de analítica; el privacy
  manifest no cambia.
- **Fuentes:** documentación de privacy manifest de Apple; App Review
  Guidelines — Privacy.

---

## Dimensión 3.7 — Observabilidad y telemetría

### AI-3.7-001 — `print` en lugar de logging estructurado

- **Estado:** cited.
- **Descripción:** el logging ocurre con `print(...)` en lugar de
  `OSLog` (`Logger`) con subsistema y categoría, dejando los logs
  sin filtrar en Console e Instruments.
- **Manifestación IA:** la IA va a `print` por defecto porque siempre
  funciona y no requiere setup.
- **Ejemplo:** `print("user logged in: \(user.email)")`.
- **Fuentes:** documentación oficial de OSLog; práctica común iOS.

### AI-3.7-002 — PII en logs

- **Estado:** framework heuristic.
- **Descripción:** los logs incluyen direcciones de email,
  identificadores de usuario, payloads completos u otros datos
  personales sin redacción ni clasificación de privacidad.
- **Manifestación IA:** la IA logea la variable más informativa para
  depurar, que suele ser el dato personal.
- **Ejemplo:** `Logger().info("loaded order for \(user.email)")`.
- **Fuentes:** OWASP MASVS v2.1 — PRIVACY; guías de privacidad de
  Apple.

---

## Dimensión 3.8 — Estrategia de testing

### AI-3.8-001 — Tests que verifican implementación, no comportamiento

- **Estado:** framework heuristic.
- **Descripción:** los tests verifican que se llamen funciones
  concretas, en orden concreto, sobre mocks concretos; se rompen en
  cada refactor y prueban poco del comportamiento de cara al usuario.
- **Manifestación IA:** la IA genera tests que reflejan la estructura
  del código bajo test, incluyendo sus pasos privados.
- **Ejemplo:** un test que verifica `mockRepository.fetchCalledTimes
  == 1` después de invocar una acción del view model, sin comprobar
  el estado de salida.
- **Fuentes:** framework heuristic; alineado con literatura general
  de testing.

### AI-3.8-002 — Tests con mock-everything sin aserción real

- **Estado:** framework heuristic.
- **Descripción:** todas las dependencias mockeadas, todos los
  retornos hardcodeados, y la única aserción es “no ha crasheado”.
- **Manifestación IA:** la IA satisface un prompt “escribe un test
  para X” con el scaffolding más pequeño que compila y corre.
- **Ejemplo:** un `func test_loadHome_doesNotCrash()` cuya única
  aserción es `#expect(true)`.
- **Fuentes:** framework heuristic.

---

## Dimensión 3.9 — CI/CD e ingeniería de release

### AI-3.9-001 — Gates obligatorios que en realidad no lo son

- **Estado:** common knowledge.
- **Descripción:** lint, tests o cobertura corren en CI pero no se
  aplican como gates de merge; los fallos se ven y se ignoran.
- **Manifestación IA:** la IA prepara workflows de CI que *ejecutan*
  los checks; si *bloquean* o no un merge es un paso de configuración
  separado que la IA rara vez marca.
- **Ejemplo:** un workflow de GitHub Actions que ejecuta `swiftlint`
  pero la branch protection no requiere su status check.
- **Fuentes:** common knowledge en práctica de CI/CD.

---

## Dimensión 3.10 — Experiencia de desarrollo (DX)

### AI-3.10-001 — Drift del README respecto al bootstrap real

- **Estado:** framework heuristic.
- **Descripción:** los pasos de setup en `README.md` ya no coinciden
  con lo necesario para que una máquina limpia compile y ejecute la
  app.
- **Manifestación IA:** la IA actualiza el código sin actualizar la
  documentación; las actualizaciones de documentación suelen producir
  instrucciones optimistas y no probadas.
- **Ejemplo:** el README dice `make bootstrap`; ese target se renombró
  hace tres meses.
- **Fuentes:** framework heuristic; informado por retrospectivas de
  equipo.

---

## Dimensión 3.11 — Localización e internacionalización

### AI-3.11-001 — Strings visibles hardcodeados

- **Estado:** common knowledge.
- **Descripción:** texto mostrado al usuario escrito directamente en
  vistas en lugar de pasar por `String(localized:)` o un string
  catalog.
- **Manifestación IA:** la IA escribe `Text("Save")` por ser la
  expresión correcta más corta para el prompt.
- **Ejemplo:** `Text("Continue")` en lugar de
  `Text(String(localized: "common.continue"))`.
- **Fuentes:** documentación oficial de localización de Apple.

### AI-3.11-002 — Formato sin conciencia de locale

- **Estado:** common knowledge.
- **Descripción:** números, fechas y monedas formateados por
  interpolación de strings o por un formatter sin locale explícito,
  produciendo salida incorrecta para locales no por defecto.
- **Manifestación IA:** la IA escribe `"\(price) €"` o
  `NumberFormatter()` sin setear `locale`.
- **Ejemplo:** `Text("$\(price)")` para un precio mostrado a un
  usuario francés.
- **Fuentes:** documentación oficial de localización de Apple.

---

## Dimensión 3.12 — Calidad UX y UI

### AI-3.12-001 — Vistas como computed properties en lugar de subvistas reales

- **Estado:** cited.
- **Descripción:** una pantalla SwiftUI compuesta enteramente de
  computed properties (`var header: some View { ... }`) en lugar de
  pequeños tipos reutilizables, llevando a tormentas de redibujado y
  pobre componibilidad.
- **Manifestación IA:** las computed properties son la forma de
  menor fricción para que la IA “separe una vista”; las produce por
  defecto.
- **Ejemplo:** una `HomeView` con ocho computed properties
  `var someSection: some View` y ningún tipo de subvista real.
- **Fuentes:** Paul Hudson — *What to fix in AI-generated Swift code*
  (`hudson:281`).

### AI-3.12-002 — Navegación incoherente con HIG

- **Estado:** common knowledge.
- **Descripción:** paradigmas de navegación mezclados (push + sheet +
  modal + full-screen cover) usados de forma inconsistente entre
  pantallas; los gestos atrás se rompen; las navigation bars se
  ocultan y reaparecen.
- **Manifestación IA:** la IA hace match del verbo del prompt
  (“muestra”, “abre”, “presenta”) con el modificador que más se le
  parezca, sin preservar la gramática de navegación de la app.
- **Ejemplo:** unos detalles hacen push, otros presentan un sheet,
  sin regla que explique cuándo.
- **Fuentes:** Apple Human Interface Guidelines — Navigation,
  Modality.

---

## Dimensión 3.13 — Accesibilidad

### AI-3.13-001 — Controles de solo icono sin etiqueta de accesibilidad

- **Estado:** common knowledge.
- **Descripción:** botones cuyo contenido es un SF Symbol sin
  etiqueta de accesibilidad, dejando a los usuarios de VoiceOver con
  “Botón” como única pista.
- **Manifestación IA:** la IA genera `Button { ... } label: { Image(systemName: "trash") }`
  sin `.accessibilityLabel`.
- **Ejemplo:** un botón de borrar con icono y sin nombre accesible.
- **Fuentes:** documentación de accesibilidad de Apple; Paul Hudson
  sobre accesibilidad en SwiftUI.

### AI-3.13-002 — Layouts que se rompen con Dynamic Type

- **Estado:** common knowledge.
- **Descripción:** alturas fijas, anchos fijos o textos en una sola
  línea que se truncan o cortan al activar tamaños de Dynamic Type
  más grandes.
- **Manifestación IA:** la IA usa `.frame(height: 44)` para botones o
  filas porque encaja con la altura “por defecto” de iOS; el layout
  colapsa en tamaños accesibles.
- **Ejemplo:** una fila con `.lineLimit(1)` y un frame de altura fija
  ocultando el texto del usuario en el ajuste de Dynamic Type más
  grande.
- **Fuentes:** documentación de accesibilidad de Apple; Paul Hudson
  sobre Dynamic Type.

---

## Dimensión 3.14 — Rendimiento y energía

### AI-3.14-001 — Trabajo pesado dentro de los `body` SwiftUI

- **Estado:** common knowledge.
- **Descripción:** cómputos, parsing o filtrado de colecciones
  grandes ocurren dentro de `body`, recalculándose en cada redibujado.
- **Manifestación IA:** la IA inlinea la transformación donde se
  consume el dato, por ser la expresión más directa de “muestra X
  filtrado por Y”.
- **Ejemplo:** `Text(items.filter { ... }.map { ... }.joined())`
  dentro del `body`.
- **Fuentes:** documentación de rendimiento SwiftUI de Apple.

### AI-3.14-002 — Decodificación síncrona de imágenes grandes en el main thread

- **Estado:** common knowledge.
- **Descripción:** imágenes grandes cargadas síncronamente,
  decodificadas en el main thread, o usadas a resolución completa
  donde una thumbnail bastaría, causando jank de scroll.
- **Manifestación IA:** la IA usa `Image(uiImage: UIImage(named:))`
  sin considerar tamaño ni hilo; o decodifica desde `Data` en el
  main actor.
- **Ejemplo:** una celda de lista que carga una imagen de 4 MB con
  `UIImage(contentsOfFile:)` en el main thread.
- **Fuentes:** documentación de imagen y rendimiento SwiftUI de Apple.

---

## Dimensión 3.15 — Frescura de APIs y deprecaciones

### AI-3.15-001 — `NavigationView` en lugar de `NavigationStack`

- **Estado:** cited.
- **Descripción:** código nuevo que usa `NavigationView`, que está
  deprecado, en lugar de `NavigationStack` / `NavigationSplitView`.
- **Manifestación IA:** los datos de entrenamiento de la IA siguen
  favoreciendo `NavigationView` por la abundancia de ejemplos.
- **Ejemplo:** una pantalla nueva scaffoldeada con
  `NavigationView { ... }` en un proyecto iOS 16+.
- **Fuentes:** Paul Hudson — *What to fix in AI-generated Swift code*
  (`hudson:281`).

### AI-3.15-002 — `ObservableObject` / `@StateObject` donde se prefiere `@Observable`

- **Estado:** cited.
- **Descripción:** view models nuevos adoptan el protocolo
  `ObservableObject` con propiedades `@Published` aunque el
  deployment target del proyecto soporte `@Observable`.
- **Manifestación IA:** mismo sesgo de los datos de entrenamiento
  hacia patrones más antiguos.
- **Ejemplo:** `final class HomeViewModel: ObservableObject` con
  `@Published var items: [Item] = []`, en un codebase iOS 17+.
- **Fuentes:** Paul Hudson — *What to fix in AI-generated Swift code*
  (`hudson:281`); documentación oficial del Observation framework.

### AI-3.15-003 — `.foregroundColor` en lugar de `.foregroundStyle`

- **Estado:** cited.
- **Descripción:** código nuevo que usa `.foregroundColor`, que está
  deprecado, en lugar de `.foregroundStyle`.
- **Manifestación IA:** sesgo de datos de entrenamiento.
- **Ejemplo:** `Text("Hello").foregroundColor(.red)` en un archivo
  nuevo.
- **Fuentes:** Paul Hudson — *What to fix in AI-generated Swift code*
  (`hudson:281`).

### AI-3.15-004 — API `tabItem` de `TabView` donde aplica el nuevo `Tab`

- **Estado:** cited.
- **Descripción:** en iOS 18+, la nueva API `Tab` /
  `TabView { Tab(...) }` es la preferida, pero la IA sigue produciendo
  el estilo antiguo `.tabItem { ... }`.
- **Manifestación IA:** sesgo de datos de entrenamiento.
- **Ejemplo:** `TabView { HomeView().tabItem { ... } }` en una app
  iOS 18 en lugar de
  `TabView { Tab("Home", systemImage: "house") { ... } }`.
- **Fuentes:** Paul Hudson — *What to fix in AI-generated Swift code*
  (`hudson:281`).

---

## Dimensión 3.16 — Salud del código y SOLID

### AI-3.16-001 — Comentarios narrativos que duplican el código

- **Estado:** common knowledge.
- **Descripción:** comentarios que repiten lo que la línea siguiente
  hace de forma obvia, añadiendo ruido sin aportar contexto.
- **Manifestación IA:** la IA tiende a comentar generosamente,
  explicando con frecuencia sus propias acciones aunque sean
  redundantes.
- **Ejemplo:** `// Increment counter` justo encima de `counter += 1`.
- **Fuentes:** common knowledge; reforzado por guías de estilo de la
  comunidad.

### AI-3.16-002 — Archivos-dios y crecimiento por append

- **Estado:** framework heuristic.
- **Descripción:** los archivos y tipos crecen por append: cada
  cambio asistido por IA añade un nuevo método o propiedad sin
  refactorizar, llegando a un único archivo que posee la mayor parte
  de una funcionalidad.
- **Manifestación IA:** sin instrucción explícita de refactorizar, la
  IA prefiere añadir al final de un archivo existente antes que
  introducir un tipo nuevo.
- **Ejemplo:** un `HomeViewModel.swift` de 1500+ líneas cubriendo
  loading, persistencia, formateo y analítica.
- **Fuentes:** framework heuristic.

---

## Changelog

- **v0.1** — Catálogo inicial. Alcance alineado con el modelo de
  calidad v0.1.
  Identificadores cubriendo dimensiones 3.1–3.16. Mezcla de `cited`
  (sobre todo Hudson 281), `common knowledge` y
  `framework heuristic`. Sin entradas retiradas todavía.
