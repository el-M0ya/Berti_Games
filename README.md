# Berti Games

Catalogo web de juegos para **PS2, PS3, Xbox 360, PS4 y PS5**. Es un sitio
informativo: no tiene backend, no hay base de datos y no procesa pagos. Todo
son archivos estaticos que se pueden publicar en GitHub Pages gratis.

## Que tiene

- **Inicio** con las 6 consolas para elegir (PS2, PSP, PS3, Xbox 360, PS4,
  PS5), y mas abajo la seccion de contacto (movil, fijo, direccion y horario).
- **Catalogo por consola** con tarjetas: caratula de fondo y nombre abajo.
- **Ficha de cada juego**: al tocar una tarjeta, esa tarjeta se anima hacia la
  izquierda, el fondo se oscurece y aparece la descripcion a la derecha con
  dos etiquetas arriba: si es de 1 jugador o multijugador, y el genero.
- **Pirateo**: precios y versiones de los servicios de modificacion.

## Arrancar en local

```bash
npm install
npm run dev
```

Abre http://localhost:5173/Berti_Games/

Para probarlo como va a quedar en GitHub Pages (build de produccion):

```bash
npm run build      # genera dist/
npm run preview
```

## Editar los datos

Casi todo lo que tenes que tocar esta en `src/data/`:

| Archivo | Que editas |
| --- | --- |
| `site.js` | **Tu telefono, direccion y horario.** |
| `piracy.js` | La seccion Pirateo: servicios, versiones y precios. |
| `consoles.js` | Los textos de cada consola. |
| `games/ps2.js` ... `games/ps5.js` | Los juegos de cada consola. |

### Datos de contacto

`src/data/site.js`:

```js
contact: {
  mobile: '+54 9 11 5555 1234',
  mobileRaw: '5491155551234',   // sin +, para el link de WhatsApp
  landline: '+54 11 5555 9876',
},
address: { street: '...', city: '...', ... },
hours: [ { days: 'Lunes a Viernes', time: '10:00 - 20:00' }, ... ],
```

### Catalogo de juegos a mano

Cada juego se ve asi:

```js
{
  id: 'bloodborne',
  title: 'Bloodborne',
  year: 2015,
  cover: 'https://.../caratula.jpg',  // '' dibuja un placeholder
  players: ['1 jugador', 'Multijugador', 'Local 2-4'],
  genre: 'Accion-aventura',
  description: 'Texto de la sinopsis.',
}
```

Si `cover` esta vacio o la imagen no carga, la tarjeta muestra un placeholder
con las iniciales del juego y los colores de la consola. Asi el sitio nunca
se ve roto.

## Armar el catalogo con tus juegos (script)

Hay dos scripts de Python que se encargan de armar la lista de juegos por vos.
No hacen falta librerias externas: solo usan la libreria estandar.

### Paso 1: escanear tus carpetas

```bash
python tools/scan_games.py --root "D:\Juegos"
```

El script busca carpetas que se llamen `PS2`, `PS3`, `PS4`, `PS5`, `XBOX360`
(o como las tengas, con o sin espacios) y escribe `game_scan.json`.

Limpia los nombres tipicos: saca la extension, los codigos de producto entre
corchetes (`[SLUS-20958]`, `[BCUS30790]`, `[Guild01]`), las regiones y el
detalle de idiomas (`(USA)`, `(PAL)`, `(En,Fr,De,Es,It)`), los tags sueltos
(`_PS3`, `-USA`) y convierte ` - ` en `: ` para los subtitulos.

Si no encuentra ninguna carpeta de consola, renombra las tuyas o revisa que
esten dentro de `--root`.

Para probar sin tocar tus discos:

```bash
python tools/make_test_folders.py
python tools/scan_games.py --root "_test_juegos"
```

### Paso 2: buscar datos y caratulas

```bash
python tools/fetch_metadata.py --key TU_CLAVE_RAWG
```

Para procesar una consola a la vez y no esperar dos horas del tiron:

```bash
python tools/fetch_metadata.py --key TU_CLAVE_RAWG --merge games/*.json --only ps2
```

`--merge` junta varios JSON de escaneo y quita repetidos por id. Al unir, si
el mismo juego aparece en dos archivos, se queda con el que tenga caratula.

De donde saca la informacion:

1. **RAWG API** (recomendado). La clave gratuita se pide en
   https://rawg.io/apidocs. Trae el titulo oficial, el anio, la descripcion,
   los generos y la imagen de caratula. Filtra por plataforma, asi no te
   confunde la version de PS2 con la de PS5.
2. **Sin clave**: cae a Wikipedia en espanol para el texto. La caratula queda
   vacia y se dibuja el placeholder.

Sin clave de RAWG la cosa se pone lenta: Wikipedia corta las peticiones
gratuitas y cada reintento espera 3, 6 y 9 segundos. Para 5.000 juegos no es
viable. Pide la clave gratis antes de correr esto en serio.

Ojo con los IDs de plataforma de RAWG (`RAWG_PLATFORM` en el script): estan
puestos a mano y hay que confirmarlos con

```
GET https://api.rawg.io/api/platforms?key=TU_CLAVE
```

Si uno esta mal, la busqueda devuelve resultados de otra plataforma sin avisar.

Al terminar escribe `src/data/games/*.js` listos para la web y un
`game_review.json` con lo que conviene que revises a mano:

- juegos sin caratula (agrega la URL al `cover`)
- juegos donde no se pudo deducir si son de 1 jugador o multijugador
  (corrige el campo `players`)

Los resultados se guardan en `rawg_cache.json`, asi que si volves a correrlo
no consulta de nuevo lo que ya tiene. Para buscar todo de cero: `--no-cache`.

### PS5: la lista sale de superpsx.com

No tenias juegos de PS5 en el escaneo, asi que esa lista se baja de otro lado:

```bash
python tools/fetch_ps5_suppsx.py
```

Recorre las 37 paginas de la categoria de PS5 y escribe `games/ps5.json` con
el mismo formato que los demas, ya con caratula incluida. Como el sitio solo
pone "PS5" al final de cada titulo, el script limpia esa etiqueta y nada mas.

Despues se sigue el paso 2 normal:

```bash
python tools/fetch_metadata.py --key TU_CLAVE --scan games/ps5.json
```

Si preferis las imagenes en tu propio sitio en vez de enlazarlas:

```bash
python tools/fetch_ps5_suppsx.py --download-covers
```

Las baja a `public/covers/ps5/`. Es mas lento pero no depende de que el sitio
externo siga en pie.

### Opciones utiles

```bash
--out-dir otra/carpeta   # escribe los .js en otro lado (para probar)
--delay 2                # pausa entre consultas (default 1.1)
--no-cache               # ignora la cache
```

## Publicar en GitHub Pages

1. Subi el repo a GitHub.
2. Settings > Pages > Source: **GitHub Actions**.
3. Haciendolo, cada vez que pushes a `main` se publica solo.

El workflow `.github/workflows/deploy.yml` hace build y deploy. El prefijo de
la URL (`/Berti_Games/`) se detecta solo desde `GITHUB_REPOSITORY`, asi que no
hay que tocar `vite.config.js`.

Como GitHub Pages no reescribe URLs, `public/404.html` se encarga de que entrar
directo a `/consola/ps2` funcione igual.

## Estructura

```
src/
  data/            <- lo que editas
    site.js        contacto y horario
    piracy.js      seccion Pirateo
    consoles.js    datos de las consolas
    games/         catalogos (uno por consola)
  components/      Navbar, tarjetas, ficha del juego, contacto
  pages/           Home, ConsolePage, Piracy, NotFound
  styles/          un archivo de estilos por area
tools/             scripts de Python + tests
.github/workflows/ deploy automatico a Pages
```

## Comandos

```bash
npm run dev       # servidor de desarrollo
npm run build     # build de produccion en dist/
npm run preview   # ver el build

python tools/scan_games.py --root "..."   # escanear tus carpetas
python tools/fetch_ps5_suppsx.py          # bajar la lista de PS5 de superpsx
python tools/fetch_metadata.py --key ...  # buscar datos y caratulas
python tools/analyze_games.py             # resumen de games/ (duplicados, basura)
python tools/show_catalog.py games/ps5.json 20   # revisar una lista a ojo
python tools/seed_catalog.py              # regenerar los catalogos de ejemplo
python tools/check_text.py                # revisar que no haya caracteres raros

node tools/test_geometry.mjs              # tests de la animacion de la ficha
python tools/test_ps5_titles.py           # tests de limpieza de titulos
python tools/test_wiki_filter.py          # tests del filtro de Wikipedia
```

Los cuatro tests (`check_text.py` y los tres de test) corren en el workflow de
deploy, para no publicar nunca una web con texto roto ni con descripciones
equivocadas.

## Avisos importantes

**RAWG pide atribucion.** Sus terminos obligan a dar credito y enlazar a RAWG
en las paginas donde se usan sus datos o sus imagenes. El pie de pagina ya lo
hace. Si en algun momento cambias de fuente de imagenes, no hace falta.

**No redistribuyas los datos de RAWG.** Puedes usarlos para tu sitio, pero no
venderlos ni packaged como dataset para terceros.

**Los precios de "Pirateo" son de ejemplo** y se confirman por WhatsApp segun el
modelo de la consola. El sitio es informativo: no vende ni transacciona online.
