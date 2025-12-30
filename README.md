# 🛒 NuvikShop

> Tu propia tienda para Minecraft estilo Tebex - **Gratis, Open Source y Sin Comisiones**

![Python](https://img.shields.io/badge/Python-3.9+-yellow?style=flat-square&logo=python)
![Minecraft](https://img.shields.io/badge/Minecraft-1.20+-blue?style=flat-square&logo=minecraft)
![Stripe](https://img.shields.io/badge/Stripe-Pagos-635bff?style=flat-square&logo=stripe)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

**NuvikShop** es un sistema completo para vender rangos, monedas y objetos en tu servidor de Minecraft usando tu propia página web.

## ✨ ¿Por qué usar esto?

| NuvikShop | Tebex / BuyCraft |
|-----------|------------------|
| ✅ **0% Comisiones** (tuyo es el 100%) | ❌ Comisiones altas |
| ✅ **Control Total** del código | ❌ Sistema cerrado |
| ✅ **Pagos Directos** a tu Stripe | ❌ Retención de fondos |
| ✅ **Diseño Moderno** y responsive | ❌ Plantillas genéricas |

---

## 🚀 Guía de Instalación Paso a Paso

Sigue estos pasos cuidadosamente. No necesitas ser experto en programación.

### PREREQUISITOS
- Una cuenta de **Stripe** (Gratis)
- Una cuenta de **Supabase** (Gratis)
- Python instalado en tu PC (para correr la web)
- Java/Maven (para compilar el plugin)

---

### PASO 1: Configurar la Base de Datos (Supabase)

1. Ve a [supabase.com](https://supabase.com) y crea una cuenta.
2. Crea un **Nuevo Proyecto**.
3. Ve a la sección **SQL Editor** (barra lateral izquierda).
4. Crea una **Nueva Query**, pega el contenido del archivo `db/schema.sql` y dale a **RUN**.
   - Esto creará las tablas necesarias (`products`, `tickets`).
5. Ve a **Settings** (engranaje) -> **API**.
6. Copia la `Project URL` y la `anon public key`. Las necesitarás luego.

---

### PASO 2: Configurar los Pagos (Stripe)

1. Ve a [dashboard.stripe.com](https://dashboard.stripe.com).
2. Clik en **Desarrolladores** -> **Claves de API**.
3. Copia tu `Clave publicable` (`pk_live_...`) y `Clave secreta` (`sk_live_...`).
4. Ve a **Productos** -> **Añadir producto**.
5. Crea tus rangos (ej: VIP, MVP). Ponles precio y guárdalos.
6. Al guardar, verás un **API ID** del precio (empieza por `price_...`). Copia esos IDs.

---

### PASO 3: Configurar la Página Web (Backend)

1. Entra a la carpeta `src/`.
2. Renombra el archivo `.env.example` a `.env` (sin .example).
3. Abre `.env` con un editor de texto (Notepad, VS Code) y rellena tus datos:

```ini
# Tus claves de Stripe (Paso 2)
STRIPE_SECRET_KEY=sk_live_xxxxxxxx...
STRIPE_PUBLIC_KEY=pk_live_xxxxxxxx...

# Tus claves de Supabase (Paso 1)
SUPABASE_URL=https://tuproyecto.supabase.co
SUPABASE_KEY=eyJxh...

# Inventa una clave secreta para comunicar la web con el plugin
PLUGIN_SECRET_KEY=mi-clave-secreta-super-segura
```

4. Abre `config.py` y configura tus productos:
   - Reemplaza los `STRIPE_PRICE_ID_HERE` con los IDs que copiaste en el Paso 2.
   - Configura los comandos que se ejecutarán en Minecraft.

```python
 PRODUCTS = {
     'vip': {
         'price_id': 'price_123456789', # Tu ID de Stripe
         'mode': 'payment',
         'command': 'lp user {uuid} parent set vip', # Comando para LuckPerms
     },
     ...
 }
```

5. Instala las dependencias y corre la web:
```bash
cd src
pip install -r requirements.txt
python app.py
```
¡Tu web ya debería estar funcionando en `http://localhost:4242`! 🎉

---

### PASO 4: Instalar el Plugin en Minecraft

1. Entra a la carpeta `plugin/`.
2. Compila el plugin usando Maven (o usa un IDE como IntelliJ/Eclipse):
```bash
mvn clean package
```
3. Toma el archivo `.jar` generado en la carpeta `target/` y ponlo en la carpeta `plugins/` de tu servidor.
4. Reinicia tu servidor.
5. Ve a `plugins/NuvikShop/config.yml` y edítalo:

```yaml
# URL donde está alojada tu web (si es local, usa http://localhost:4242)
api-url: "http://localhost:4242"

# La misma clave que pusiste en el archivo .env
secret-key: "mi-clave-secreta-super-segura"
```

6. Escribe `/nuvikshop reload` en la consola o reinicia.

---

## 🛠️ Personalización

### Cambiar el logo y colores
Edita `src/static/css/styles.css`. Al principio del archivo verás las variables de colores:
```css
:root {
    --accent: #3b82f6; /* Color principal (azul) */
    --bg-main: #09090b; /* Color de fondo */
}
```

### Cambiar textos de la web
Los textos principales están en `src/templates/index.html`. Puedes abrirlo y editar los títulos, descripciones y pies de página.

### Añadir más productos
Simplemente añade más entradas al diccionario `PRODUCTS` en `src/config.py`. No necesitas reiniciar la web, los cambios se aplican al recargar.

---

## ❓ Preguntas Frecuentes

**¿Es seguro?**
Sí. Las claves de Stripe y Supabase nunca se envían al navegador del usuario. Todo pasa por el servidor (backend).

**¿Qué pasa si el servidor está apagado?**
Si alguien compra mientras el servidor está off, la compra se guarda en la "cola". En cuanto el servidor prenda y el plugin conecte, se entregará el rango automáticamente.

**¿Puedo usarlo en hosting compartido?**
Sí, la parte web (src) la puedes subir a cualquier hosting Python (Render, Railway, Heroku, Vercel) y el plugin a tu host de Minecraft.

---

Hecho con ❤️ por **Nuvik**.
Si te sirvió, ¡dale una ⭐ al repo!
