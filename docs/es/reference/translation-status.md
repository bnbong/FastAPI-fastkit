# Estado de las traducciones

La documentación de FastAPI-fastkit se publica en varios idiomas, pero esas traducciones **no siempre tienen el mismo grado de avance**. Esta página es la referencia principal para saber qué está realmente traducido en cada idioma, qué se muestra cuando una página aún no se ha traducido y cómo colaborar.

## Fuente de verdad

> **El inglés (`en`) es la referencia principal.** Todo lo que la documentación explica sobre el producto, la CLI y la API se escribe primero en los archivos en inglés. Los demás idiomas son traducciones de esa base inglesa y pueden quedarse atrás respecto a una release o a páginas concretas.
>
> Si una página traducida no coincide con la página inglesa, **confía en la página inglesa** hasta que la traducción se actualice.

Los archivos en inglés viven en [`docs/en/`](https://github.com/bnbong/FastAPI-fastkit/tree/main/docs/en). Cualquier otro idioma (`docs/ko/`, `docs/ja/`, `docs/es/`, ...) es un destino de traducción.

El `CHANGELOG.md` de la raíz del repositorio también forma parte de esa referencia inglesa. Pueden existir páginas `changelog.md` específicas de cada idioma como páginas de acceso o páginas puente, pero reutilizan intencionadamente el historial de releases canónico en inglés en lugar de mantener copias traducidas.

## Completitud por idioma

Los números siguientes cuentan páginas Markdown presentes en el árbol de cada idioma respecto a la fuente inglesa. Reflejan lo que realmente está en el repositorio, no lo que aparece en el selector de idiomas (la siguiente sección explica la diferencia).

| Idioma | Estado | Páginas Markdown | Notas |
|---|---|---:|---|
| 🇬🇧 Inglés (`en`) | ✅ Fuente de verdad | 26 / 26 | Autoritativa. |
| 🇰🇷 Coreano (`ko`) | ✅ Completo | 26 / 26 | Todas las páginas del idioma están presentes. Phase 1: nivel superior + user-guide principal; Phase 2: user-guide restante + todos los tutorials; Phase 3: contributing + reference. `docs/ko/changelog.md` reutiliza intencionadamente el `CHANGELOG.md` canónico en inglés. |
| 🇯🇵 Japonés (`ja`) | ✅ Completo | 26 / 26 | Todas las páginas del idioma están presentes. Phase 1: nivel superior + user-guide principal; Phase 2: user-guide restante + todos los tutorials; Phase 3: contributing + reference. `docs/ja/changelog.md` reutiliza intencionadamente el `CHANGELOG.md` canónico en inglés. |
| 🇪🇸 Español (`es`) | ✅ Completo | 26 / 26 | Todas las páginas del idioma están presentes. Phase 1: nivel superior + user-guide principal; Phase 2: user-guide restante + todos los tutorials; Phase 3: contributing + reference. `docs/es/changelog.md` reutiliza intencionadamente el `CHANGELOG.md` canónico en inglés. |
| 🇨🇳 Chino (`zh`) | 🔴 Esqueleto | 0 / 26 | Solo está configurado como destino de compilación. Cada página muestra la versión en inglés. |
| 🇫🇷 Francés (`fr`) | ✅ Completo | 26 / 26 | Todas las páginas del idioma están presentes. Phase 1: nivel superior + núcleo del user-guide; Phase 2: resto del user-guide + todos los tutoriales; Phase 3: contributing + reference. `docs/fr/changelog.md` reutiliza intencionadamente el `CHANGELOG.md` canónico en inglés. |
| 🇩🇪 Alemán (`de`) | ✅ Completo | 26 / 26 | Todas las páginas del idioma están presentes. Phase 1: nivel superior + núcleo del user-guide; Phase 2: resto del user-guide + todos los tutoriales; Phase 3: contributing + reference. `docs/de/changelog.md` reutiliza intencionadamente el `CHANGELOG.md` canónico en inglés. |

*Verificado el 2026-05-17; la fila de `de` se volvió a contar para la rama actual tras completar Phase 3 (contributing + reference). El alemán ya tiene todas las páginas del idioma presentes, mientras que `docs/de/changelog.md` apunta al changelog canónico en inglés.* Esta cuenta se mantiene a mano; para volver a contar el estado actual desde la raíz del repositorio, ejecuta:

```console
$ for loc in en ko ja zh es fr de; do
    echo "$loc: $(find docs/$loc -name '*.md' 2>/dev/null | wc -l | tr -d ' ')"
  done
```

Si el recuento difiere de la tabla, la tabla está obsoleta — actualízala (o abre un PR / issue señalando el desfase).

Leyenda:

- ✅ **Fuente de verdad** — el idioma contra el que se escribe primero.
- 🟡 **Parcial** — hay algunas páginas traducidas; las que faltan muestran la versión en inglés.
- 🔴 **Esqueleto** — la entrada del selector de idiomas existe, pero todavía no hay páginas traducidas en el repositorio. El sitio renderiza contenido en inglés bajo las etiquetas de navegación traducidas.

## Cómo funciona el uso de la versión en inglés

El sitio de documentación usa [`mkdocs-static-i18n`](https://github.com/ultrabug/mkdocs-static-i18n) con `fallback_to_default: true`. Esto significa:

- Para cada idioma traducido, MkDocs solo escribe las páginas que existen en el directorio de ese idioma.
- Para cada página que **no** exista en un idioma, la compilación recurre a la versión inglesa de esa página.
- El selector global de idiomas siempre muestra todos los idiomas configurados, independientemente de cuántas páginas tenga cada uno, porque la compilación genera una URL accesible para cada caso (la página correspondiente o, si hace falta, su versión inglesa).

Por lo tanto, una entrada 🔴 Esqueleto en el selector **no** significa que la documentación ya esté traducida; solo indica que ese idioma está configurado como destino de compilación. Este comportamiento es intencionado (los colaboradores externos pueden traducir una página cada vez sin romper la estructura de enlaces), pero también hace que el selector de idiomas parezca más completo de lo que realmente está el contenido.

## Cómo leer el sitio

- **Por defecto, usa el inglés** si quieres la información más precisa y actualizada.
- **Usa un idioma traducido** solo después de comprobar su estado en esta página. Si aparece como 🟡 o 🔴 y llegas a un tema que aún no se ha traducido, en realidad estarás leyendo la página en inglés bajo una etiqueta de navegación traducida.

## Cómo ayudar

La estrategia actual es **un issue de seguimiento por idioma**, con el trabajo dividido en **fases**. Por ejemplo, `ko` se completó en Phase 1 (nivel superior + user-guide principal), Phase 2 (user-guide restante + todos los tutorials) y Phase 3 (contributing + reference). Cada fase se envía en su propio PR para que los revisores puedan aprobar una parte coherente sin tener que esperar a que todo el idioma esté terminado.

Si quieres colaborar:

1. Lee la [Guía de traducción](../contributing/translation-guide.md) para conocer el flujo, las herramientas y las convenciones de estilo.
2. **Comprueba o abre primero el issue de seguimiento del idioma.** Si un idioma ya tiene un issue de seguimiento abierto, reserva una fase (o una página concreta dentro de una fase) ahí para que el trabajo no se duplique. Si no hay issue de seguimiento para el idioma con el que quieres trabajar, abre uno que liste qué páginas pertenecen a cada fase y empieza por Phase 1.
3. **Lo ideal es un PR por fase.** Los PR pequeños del tipo "arregla esta única página" siguen siendo bienvenidos — sobre todo para corregir una traducción desincronizada — pero, al arrancar un idioma desde cero, agrupar por fase ayuda a mantener consistentes las decisiones de glosario y los textos de los enlaces cruzados dentro de ese bloque.
4. Abre el PR añadiendo archivos bajo `docs/<locale>/<misma ruta>`. Mantén los nombres de archivo idénticos a la fuente inglesa para que MkDocs los recoja automáticamente.
5. Trata las páginas changelog localizadas como páginas puente hacia el `CHANGELOG.md` canónico en inglés, salvo que la política del proyecto cambie de forma explícita.
6. Actualiza la tabla de esta página para reflejar el nuevo grado de traducción (usa el snippet de recuento de arriba) y actualiza la fecha de "Verificado" para que los revisores vean cuándo se revisó por última vez. Indica en la columna "Notas" qué fase se ha completado si el idioma sigue estando parcial.

Los reportes de errores sobre páginas traducidas que se hayan desincronizado respecto a la fuente inglesa son bienvenidos; enlaza la página inglesa y la traducida para que podamos revisarlas con rapidez.

## Por qué publicamos idiomas en 🔴 Esqueleto

Dos razones:

1. **Un espacio de URLs predecible.** Cada idioma tiene ya su subárbol `/<locale>/` accesible, así que en cuanto se añade una página traducida el enlace es estable desde el primer día, incluidos los enlaces publicados en esta guía.
2. **Menos fricción para quienes contribuyen.** Quien traduce una sola página no tiene que configurar además un nuevo idioma en la configuración de MkDocs; basta con añadir el archivo.

Si un idioma se queda en 🔴 Esqueleto sin actividad durante mucho tiempo, podemos replantearnos si dejar habilitado su destino de build. Esa decisión se rastrea por separado y **no** es algo que esta página de estado cambie silenciosamente.
