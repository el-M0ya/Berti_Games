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

## Normalizar el catalogo (Fase 0)

Despues de llenar los catalogos con datos, hay que limpiarlos:

```bash
python tools/normalize_catalog.py            # aplica los cambios
python tools/normalize_catalog.py --dry-run  # solo el informe
```

Que hace, sobre los `.js` de `src/data/games/`:

| Campo | Que estaba | Que queda |
| --- | --- | --- |
| `genre` | `'Action, Shooter, Adventure'` en ingles | `genres: ['Accion', 'Disparadores', 'Aventura']` (20 valores limpio) |
| `players` | `1 jugador` en **todos** los juegos | `1 jugador` significa de verdad "solo un jugador" |
| `title` | `007-BLOOD STONE`, con notas de trabajo | `007 Blood Stone`, sin `(buscar)` ni `.rar` |
| `favorite` | no existia | `favorite: false` (lo editas tu) |
| `file` | rutas de tu disco | eliminado, no lo usaba nadie |
| `description` | entidades `&#39;`, espacios duros, vacias | texto limpio, o un texto generico si no hay |

Ademas descarta los juegos duplicados (mismo titulo con dos escrituras) y
avisa de cada uno para que revises.

**Orden importante**: si usas los scripts de Node de `games/`, el normalizador
va **siempre al final**:

```
node games/process_games.cjs
node games/fetch_game_data.cjs
node games/fetch_covers_igdb.cjs
node games/generate_final_js.cjs
python tools/normalize_catalog.py      <- ultimo paso
```

### Herramientas de la Fase 0

```bash
python tools/audit_catalog.py         # resumen: juegos, fotos, generos, favoritos
python tools/audit_descriptions.py    # descripciones que no corresponden al titulo
python tools/check_duplicates.py ps2  # que duplicados se van a descartar
python tools/list_title_notes.py      # que parentesis hay en los titulos
python tools/list_raw_genres.py       # los generos tal cual vienen de RAWG
python tools/fix_bad_descriptions.py  # corrige las descripciones equivocadas
```

### Marcar favoritos

Para que un juego salga primero en el catalogo hay que marcarlo. Con 7.800
juegos, se hace con un comando:

```bash
# 1. Ver que hay marcado ahora
python tools/mark_favorites.py --list

# 2. Buscar el juego y copied el id de la izquierda
python tools/mark_favorites.py --find "gta"

# 3. Marcar (acepta el id o el nombre)
python tools/mark_favorites.py --add gta-san-andreas
python tools/mark_favorites.py --add bloodborne --add "Shadow of the Colossus"

# 4. Sacar
python tools/mark_favorites.py --remove bloodborne
```

El comando **acepta un trozo del nombre**, pero si eso matchea varios juegos
se niega y te muestra la lista, para que no marques el equivocado:

```
  OJO: 'shadow' matchea 76 juegos:
         ps1       shadow-madness                               Shadow Madness
         ...
       No marco ninguno. Usa el id exacto de arriba.
```

En `src/data/generated/favorites.js` queda la lista que usa la web, pero ese
archivo se regenera en cada build: **nunca lo edites a mano**. Lo que manda
es `favorite: true` en `src/data/games/ps2.js` (y demas), que es lo que
modifica el comando.

Que aparezcan arriba: solo en el orden "Destacados", que es el de por
defecto. Si eliges "A-Z" o "Mas votados", el juego vuelve a su lugar por
nombre o por votos.

Solo lo edita el dueno de la web: los visitantes no pueden cambiarlo.

## Buscar y ordenar (en cada consola)

Cada pagina de consola tiene:

- **Buscador**: por nombre o anio. Ignora mayusculas y tildes, asi que
  `bloodborne`, `BLOODBORNE` y `resident evil` funcionan. Se pueden escribir
  varias palabras y se buscan en cualquier orden.
- **Filtro de jugadores**: Todos, 1 jugador, 2 jugadores, 4 jugadores.
- **Filtro de genero**: los 20 generos, con la cuenta de cada uno.
- **Orden**: Destacados (favoritos primero y luego A-Z, por defecto),
  A-Z, y Mas votados.

Las tarjetas se muestran de a 60 con un boton "Ver mas juegos", porque en
algunas consolas hay mas de 1.600.

### Votos

En la ficha de cada juego hay "Me gusta" / "No me gusta". Hay dos almacenes y
la web usa el primero que responda:

1. **Cloudflare D1** (`/api/votes`): compartido por todos los visitantes.
2. **`localStorage`**: solo la persona que vota. Es el respaldo automatico si
   la API no responde.

El codigo esta en `src/lib/votes.js`, que es la unica frontera con el
almacen. Cambiar de tecnologia mas adelante es modificar ese archivo.

#### Ponerlo en marcha (una sola vez)

Hace falta una cuenta gratuita de Cloudflare.

```bash
# 1. Instalar las herramientas de Cloudflare
npm install --save-dev wrangler

# 2. Entrar con tu cuenta
npx wrangler login

# 3. Crear la base de datos
npx wrangler d1 create berti-games-votos
```

El ultimo comando imprime algo asi:

```
[[d1_databases]]
binding = "VOTOS"
database_name = "berti-games-votos"
database_id = "8f3c...-...-..."
```

Copia ese `database_id` dentro de `wrangler.toml` y reemplazalo por
`PEGAR_AQUI_EL_DATABASE_ID`.

```bash
# 4. Crear las tablas
npx wrangler d1 execute berti-games-votos --file=schema.sql --remote
```

Ahora pon el dominio del sitio en `wrangler.toml`, para que nadie mas pueda
mandar votos desde su pagina:

```toml
[vars]
SITIO_ORIGIN = "https://TU-USUARIO.github.io"
```

#### Probarlo en local

```bash
npm run build
npx wrangler pages dev dist
```

Abre la direccion que indique y prueba a votar. Deberia decir
*"Tu voto se guarda y lo ven todos los visitantes"*.

#### Publicarlo

La funcion esta en `functions/api/votes.js` y Cloudflare Pages la sube sola.
Si el proyecto esta en Cloudflare Pages, los votos ya funcionan al publicar.

Si segues publicando solo en GitHub Pages, la funcion **no** se ejecuta y la
web cae sola a `localStorage`: todo sigue andando, pero los votos no se
comparten. En ese caso hay que crear un proyecto de Cloudflare Pages
apuntando al mismo repositorio.

#### Sobre el fraude

La tabla tiene una llave primaria `(game_id, client_id)`, asi que una persona
solo puede votar una vez por juego. El identificador del visitante es un
uuid aleatorio en su navegador, **no su IP**: no se guarda ningun dato
personal. Ademas la API rechaza peticiones que no vengan del dominio del
sitio.

Eso no impide que alguien con muchas cuentas vote de mas. Si algun dia pasa,
la solucion es una regla de Cloudflare WAF sobre `/api/votes`, no tocar la
web.

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
