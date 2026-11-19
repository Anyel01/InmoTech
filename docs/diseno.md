# Diseño

Decisiones visuales de InmoTech, especificación de los componentes de fotos y resultado de la revisión de accesibilidad y de textos.

## 1. Identidad visual

El sitio tiene una identidad definida en `app/static/css/theme.css`, y los componentes nuevos la respetan en vez de inventar otra:

| Elemento | Valor | Uso |
|---|---|---|
| Verde profundo `--primary` | `#183c3a` | Barra superior, botones principales, fondo del carrusel |
| Terracota `--accent` | `#b5472f` | Acciones destacadas, enlaces, etiquetas, miniatura activa, anillo de foco. Cumple el contraste AA con texto blanco y sobre crema |
| Terracota oscuro `--accent-hover` | `#963a28` | Estado al pasar el mouse sobre botones de acento |
| Crema `--bg-card` / `--bg-main` | `#fffdf8` / `#f3f0e8` | Tarjetas y fondo |
| Gris verdoso `--text-muted` | `#687571` | Texto secundario |
| Ocre | `#e5d78e` | Detalles de la barra y el pie |
| Titulares | Georgia (serif) | Títulos de sección, precios |
| Texto | Aptos / Segoe UI | Todo lo demás |
| Esquinas | `6px 26px 6px 26px` (alternadas) | Tarjetas, galería, zona de fotos: es la firma del sitio |
| Sombras | `--shadow-sm`, `--shadow-md`, `--shadow-lg` | Elevación de tarjetas, galería y ventanas |

Los iconos son archivos SVG propios (`app/static/img/icons/`) que toman el color del texto que los rodea. Se piden con `ico('nombre')` desde las plantillas.

## 2. Ilustraciones de los inmuebles

Los inmuebles de prueba necesitaban fotos y no se podían usar fotografías con derechos. En su lugar hay **26 ilustraciones** (`app/static/img/inmuebles/`, 1600 x 1000, SVG) hechas con la paleta del sitio:

- Formas planas, sin degradados fotográficos, con un grano muy suave que recuerda a la impresión en papel.
- Tres atmósferas de luz (alba, día y atardecer) para que no se vean todas iguales.
- Cada inmueble cuenta una historia distinta: fachada, interior, terraza o plano. El lote incluye un **plano con medidas** (40 x 30 m = 1.200 m²), que es información real y no solo decoración.
- Los textos que aparecen en las ilustraciones son mínimos (medidas y norte del plano).

El script que las genera está en `tools/generar_ilustraciones.py`; sirve para ajustar colores o agregar escenas:

```bash
python tools/generar_ilustraciones.py app/static/img/inmuebles
```

Las fotos que suban los vendedores reemplazan a estas en cada inmueble; las ilustraciones solo son los datos de ejemplo.

## 3. Componentes de fotos

Estilos en `app/static/css/galeria.css`, comportamiento en `app/static/js/carrusel.js` y `subida-fotos.js`.

### 3.1 Carrusel (detalle del inmueble)

| Parte | Detalle |
|---|---|
| Proporción | 16:10, esquinas `6px 26px`, fondo verde mientras carga |
| Pie | Barra inferior con el texto de la foto (izquierda) y el contador `2 / 4` (derecha) |
| Flechas | Círculos de 46 px sobre los lados; dan la vuelta (de la última pasa a la primera) |
| Ampliar | Botón de 44 px arriba a la derecha; también se abre con un clic en la foto |
| Miniaturas | Fila de 96 x 60 px bajo la foto, con desplazamiento horizontal. La activa lleva borde terracota |
| Movimiento | Desplazamiento de 380 ms al cambiar de foto. **No hay avance automático** |

**Estados**

| Situación | Comportamiento |
|---|---|
| Sin fotos | No se dibuja; el detalle muestra el icono de la categoría (como antes) |
| Una sola foto | Se ocultan flechas, miniaturas y contador |
| Varias fotos | Todo visible; las diapositivas fuera de vista quedan `inert` (sin foco ni lectura) |
| Con `prefers-reduced-motion` | Sin animaciones; el cambio es instantáneo |
| Móvil (menos de 760 px) | Miniaturas de 76 px y esquinas más pequeñas; se puede deslizar con el dedo |

**Teclado y lector de pantalla**

| Entrada | Efecto |
|---|---|
| **←** / **→** (con el foco dentro del carrusel) | Foto anterior / siguiente |
| **Inicio** / **Fin** | Primera / última foto |
| **Tab** | Recorre expandir, flechas y miniaturas |
| Cambio de foto | Una región `aria-live="polite"` anuncia "Foto 2 de 4: Sala con chimenea" |

Roles: la sección es un `region` con `aria-roledescription="carrusel"`; cada foto es un `group` con `aria-roledescription="diapositiva"` y etiqueta "2 de 4".

### 3.2 Vista ampliada

Ventana modal (`<dialog>`) a pantalla completa con fondo verde casi negro. Foto centrada sin recortar (`object-fit: contain`), texto y contador abajo, flechas a los lados y cerrar arriba a la derecha.

- Se cierra con **Esc**, el botón de cerrar o un clic en el fondo.
- Al cerrar, el foco vuelve al botón que la abrió y el carrusel queda en la foto donde se dejó el visor.
- Mientras está abierta la página de atrás no se desplaza.
- Precarga la foto anterior y la siguiente.

### 3.3 Vista rápida (catálogo e inicio)

Ventana modal de hasta 1020 px: carrusel a la izquierda y datos a la derecha (etiquetas, título, precio, ubicación, características, descripción de hasta 5 líneas y dos botones: **Ver detalle completo** y **Cerrar**). En móvil se apila y deja libre la esquina del botón de cerrar.

| Estado | Qué se ve |
|---|---|
| Cargando | "Cargando el inmueble…" |
| Error de red | "No pudimos cargar la vista rápida. Revisa tu conexión o abre el detalle completo." con un botón al detalle |
| Sin fotos | "Este inmueble todavía no tiene fotos." junto a los datos |

El título de la ventana (`aria-labelledby`) es el del inmueble. Los datos vienen de `GET /api/inmuebles/<id>` y se guardan en memoria, así que abrir el mismo inmueble otra vez es instantáneo.

### 3.4 Tarjeta con foto

La foto de portada ocupa toda la cabecera de la tarjeta, con un degradado oscuro arriba y abajo para que se lean las etiquetas (operación, categoría), el botón **Vista rápida** (abajo a la izquierda) y el número de fotos (abajo a la derecha). Sin foto, la tarjeta conserva el diseño anterior con el icono de la categoría.

### 3.5 Carrusel de tarjetas (inicio)

"Hallazgos recientes" es una fila que se desplaza con `scroll-snap`: cada tarjeta se detiene alineada al borde. Las flechas del encabezado mueven 85 % del ancho visible y se desactivan en los extremos. También se desplaza con la rueda, el trackpad o el dedo. Tarjetas de 360 px (86 % del ancho en móvil).

### 3.6 Zona de fotos y vista previa (publicar y editar)

| Parte | Detalle |
|---|---|
| Zona | Borde punteado; se resalta en terracota al arrastrar. El campo de archivos real está oculto y la etiqueta "Elegir fotos" hace de botón (tiene anillo de foco) |
| Miniaturas | Rejilla de tarjetas de 150 px con nombre, peso y acciones. La primera lleva la marca **Portada** |
| Acciones de una foto nueva | Ampliar (clic en la imagen), **Usar de portada**, **Quitar** |
| Fotos actuales (edición) | Selector de portada y casilla **Quitar**; la foto marcada se atenúa |
| Errores | Debajo de la zona, en rojo, con `role="alert"`. Dicen cuál foto falla y por qué |
| Vista previa | Tarjeta real del catálogo junto al formulario (fija en pantallas de 1100 px o más). Se actualiza con cada cambio de título, precio, ubicación, características y portada |

## 4. Revisión de diseño

**Qué funciona bien**

- La identidad es coherente: el verde profundo y el terracota se repiten en todas las pantallas y las esquinas asimétricas le dan carácter.
- La jerarquía del detalle es clara: título, foto, cifras clave, descripción, y a la derecha el precio con una sola acción principal.
- Los estados vacíos del panel del vendedor invitan a actuar.

**Oportunidades** (no se cambiaron, para no alterar la identidad sin decisión del equipo)

| Hallazgo | Severidad | Recomendación |
|---|---|---|
| Hay mucho estilo escrito directamente en las plantillas (`style="..."`) con colores del tema anterior (`#f8fafc`, `#e0f2fe`, `#0284c7`) que no pertenecen a la paleta actual | Media | Pasarlos a clases en `theme.css` con las variables de color |
| `styles.css` y `theme.css` definen los mismos componentes dos veces (`theme.css` sobrescribe) | Media | Unificarlos en un solo archivo de estilos |
| Los botones y títulos mezclan "Title Case" y "Sentence case" ("Publicar Nuevo Inmueble", "Ver detalle") | Baja | Elegir una (se recomienda minúscula después de la primera palabra) |
| La combinación crema, titulares con serifa y terracota es muy común en sitios actuales | Baja | Si se quiere un rasgo más propio, las ilustraciones y la forma de las esquinas son el camino; los colores pueden quedarse |

## 5. Revisión de accesibilidad (WCAG 2.1 AA)

**Resuelto en esta revisión**

| Problema | Criterio | Solución |
|---|---|---|
| Las etiquetas de los filtros del catálogo no estaban asociadas a sus campos (los lectores de pantalla leían "cuadro combinado" sin nombre) | 1.3.1, 3.3.2, 4.1.2 | Cada `label` ahora tiene `for` y su campo `id` |
| El campo precio rechazaba valores redondos como 540.000.000 (`min="1" step="1000"` solo acepta 1, 1001, 2001...) | 3.3.1 | `min="1000" step="1000"` |
| Las fotos nuevas necesitan texto alternativo | 1.1.1 | Cada foto tiene descripción; si falta se usa "Foto N de <título>" |
| El carrusel debe poder usarse sin mouse | 2.1.1 | Teclas, botones reales y foco visible |
| Los avisos de cambio de foto deben llegar a lectores de pantalla | 4.1.3 | Región `aria-live` |
| Los diálogos deben atrapar el foco y devolverlo | 2.4.3 | `<dialog>` modal nativo |
| Movimiento innecesario | 2.3.3 | Sin avance automático y respeta `prefers-reduced-motion` |
| Tamaño de los controles táctiles | 2.5.5 | Flechas y botones de 44 px o más |

**Verificado automáticamente** en inicio, catálogo, detalle, publicar, editar y mis inmuebles: ninguna imagen sin `alt`, ningún botón sin nombre, ningún campo sin etiqueta y ningún `id` repetido.

**Contraste**

| Elemento | Relación | Mínimo | Resultado |
|---|---|---|---|
| Texto blanco sobre el terracota (`#b5472f`): botones de acento, etiquetas de categoría y de rol, chip "Portada" | 5,4 : 1 | 4,5 | Cumple |
| Terracota como texto sobre crema (precios, enlaces, "Ver disponibles") | 5,3 : 1 | 4,5 | Cumple |
| Terracota como texto sobre el fondo general `#f3f0e8` | 4,7 : 1 | 4,5 | Cumple |
| Botón "Vista rápida" (verde sobre crema) | 11,8 : 1 | 4,5 | Cumple |
| Texto secundario `--text-muted` sobre crema | 4,7 : 1 | 4,5 | Cumple |
| Borde de la miniatura activa (terracota sobre el fondo crema que la rodea) | 5,3 : 1 | 3 | Cumple |

**Corregido.** El terracota original (`#d26045`) daba 3,8 : 1 con texto blanco y sobre crema, por debajo del 4,5 mínimo para texto pequeño. Se cambió `--accent` a `#b5472f` (un poco más oscuro) y `--accent-hover` a `#963a28`; el cambio se hizo una sola vez en `theme.css` y se aplica a botones, etiquetas, enlaces, precios y al logo. Las ilustraciones de los inmuebles conservan el terracota original porque son arte, no texto.

Pendientes menores: añadir un enlace "Saltar al contenido" al inicio de cada página y revisar el orden de los títulos de sección en las páginas que no se tocaron.

## 6. Criterios de redacción

Los textos de la interfaz siguen estas reglas, para que una misma acción se llame igual en todas partes:

- Los botones empiezan con un verbo y dicen lo que pasa: "Publicar inmueble", "Guardar cambios", "Ver detalle completo".
- Un mensaje de error dice **qué pasó y qué hacer**: «sala.png pesa 5,2 MB. Cada foto puede pesar hasta 4 MB.»
- Los estados vacíos explican por qué está vacío y cómo seguir: "Ningún inmueble coincide con estos filtros. Prueba con otra ciudad o amplía el rango de precio."
- Se usa "quitar" para sacar algo de una lista (filtros, fotos) y "cancelar" solo para visitas.
- Las cantidades concuerdan en número: "1 foto", "2 fotos"; "1 inmueble disponible", "7 inmuebles disponibles".

Cambios hechos en esta revisión: "Mostrando N inmueble(s) disponible(s)" pasó a "N inmuebles disponibles"; "Limpiar Filtros" y "Restablecer Búsqueda" pasaron a "Quitar filtros"; "Aplicar Filtros" pasó a "Filtrar"; "Ver Detalle" y "Ver Detalle Completo" quedaron como "Ver detalle" en las tarjetas.

## 7. Panel de administración

Mismas fuentes, colores y esquinas que el resto del sitio. Lo propio del panel es el menú lateral (se vuelve una fila deslizable en móvil) y el resumen, que se diseñó con estas decisiones:

**Qué forma tiene cada dato**

| Dato | Forma | Por qué |
|---|---|---|
| Inmuebles disponibles | Cifra principal (72 px, fuente sans, una sola en la pantalla) | Es el número con el que se abre el panel |
| Usuarios, visitas pendientes, sin fotos, bloqueadas | Fichas con etiqueta, valor y una línea de contexto | Un solo valor actual: una barra de una sola barra sería peor que el número |
| Inmuebles por categoría y por ciudad | Barras horizontales ordenadas, una sola tinta, con el valor en la punta | Es magnitud sobre categorías sin orden natural: un solo color, sin rampa |
| Visitas por estado | Una barra segmentada de 28 px con leyenda de nombres | Es un todo dividido en cuatro partes, para leer de un vistazo |
| Usuarios por rol | Barras horizontales | Compara tres cantidades |

**Reglas de gráficos que se respetaron:** barras de 16 px de grosor con la punta redondeada de 4 px y la base recta; 2 px de separación entre segmentos; línea base de un píxel muy tenue (sin cuadrícula); ningún eje doble; texto en el color de texto del sitio, no en el color de la serie; cada gráfico con sus valores escritos y, el de segmentos, con una **tabla alternativa** ("Ver como tabla") para quien no distingue los colores o usa lector de pantalla.

**Colores de la barra de visitas** (`pendiente #8f6317`, `confirmada #4f8fa6`, `realizada #183c3a`, `cancelada #b5472f`). Los cuatro colores de estado originales del tema eran demasiado parecidos entre sí (el verde y el azul verdoso daban una diferencia de 6,8 sobre 100, por debajo del mínimo de 15). Se validaron los nuevos con el validador de paletas: separación entre vecinos para visión normal ≥ 19, separación para daltonismo ≥ 14 y contraste con la superficie ≥ 3:1. La luminosidad del verde profundo queda fuera de la banda de las paletas categóricas porque es el color de marca; no se usa para distinguir series sino partes de un mismo todo, rotuladas con su nombre y su porcentaje. El texto dentro de cada segmento es blanco o casi negro según el contraste (≥ 4,6 : 1).

**Accesibilidad del panel:** todos los campos tienen su etiqueta; los botones de icono tienen nombre; los selectores de las tablas llevan una etiqueta oculta que dice a qué fila pertenecen; la página actual del menú y del paginador se marca con `aria-current`; ninguna información depende solo del color (las insignias llevan texto). Revisado automáticamente en las ocho pantallas del panel: sin campos sin etiqueta, sin botones sin nombre, sin `id` repetidos y un solo `h1` por página.

