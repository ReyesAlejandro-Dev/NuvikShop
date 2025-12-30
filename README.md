# 🛒 NuvikShop

> Tu propia tienda tipo Tebex - 100% Configurable y Open Source

![License](https://img.shields.io/badge/license-MIT-green)
![Minecraft](https://img.shields.io/badge/Minecraft-1.20+-blue)
![Python](https://img.shields.io/badge/Python-3.9+-yellow)

## ✨ ¿Qué es NuvikShop?

NuvikShop es una **alternativa gratuita y open-source a Tebex/BuyCraft** que te permite tener tu propia tienda web para vender rangos, items, comandos y cualquier cosa en tu servidor de Minecraft.

### Ventajas

- **0% comisiones** - Solo pagas Stripe (~2.9%)
- **Control total** - El código es tuyo, modifícalo como quieras
- **Sin límites** - Productos ilimitados
- **Panel Admin** - Gestiona productos y ventas
- **Múltiples monedas** - USD, EUR, MXN, etc.

## 🏗️ Arquitectura

```
┌─────────────┐     ┌───────────┐     ┌─────────────┐
│   TIENDA    │────▶│  STRIPE   │────▶│   FLASK     │
│    WEB      │     │  (Pagos)  │     │  (Backend)  │
└─────────────┘     └───────────┘     └──────┬──────┘
                                              │
┌─────────────┐     ┌───────────┐     ┌──────▼──────┐
│  MINECRAFT  │◀────│  PLUGIN   │◀────│    COLA     │
│  (Servidor) │     │ (Polling) │     │ (Comandos)  │
└─────────────┘     └───────────┘     └─────────────┘
```

El plugin consulta la API cada X segundos buscando comandos pendientes y los ejecuta automáticamente.

## 🚀 Instalación

### Paso 1: Clonar repositorio

```bash
git clone https://github.com/tu-usuario/nuvikshop
cd nuvikshop
```

### Paso 2: Configurar Backend

```bash
cd src
pip install -r requirements.txt
cp .env.example .env
# Edita .env con tus claves
python app.py
```

### Paso 3: Configurar Stripe

1. Crea cuenta en [stripe.com](https://stripe.com)
2. Ve a **Products** → **Add Product**
3. Copia el `price_id` de cada producto
4. Pégalos en `config.py`

### Paso 4: Configurar Base de Datos

1. Crea proyecto en [supabase.com](https://supabase.com)
2. Crea las tablas (ver `db/schema.sql`)
3. Copia URL y API Key a `.env`

### Paso 5: Instalar Plugin

```bash
cd plugin
mvn clean package
# Copia target/NuvikShop-1.0.0.jar a plugins/
```

Configura `plugins/NuvikShop/config.yml`:
```yaml
api-url: "https://tu-dominio.com"
secret-key: "tu-clave-secreta"
check-interval-seconds: 10
```

## 📁 Estructura

```
nuvikshop/
├── src/                        # Backend Flask
│   ├── app.py                  # Servidor principal
│   ├── config.py               # Configuración de productos
│   ├── .env.example            # Variables de entorno
│   ├── requirements.txt        # Dependencias Python
│   ├── templates/              # Páginas HTML
│   └── static/                 # CSS, JS, imágenes
│
├── plugin/                     # Plugin de Minecraft
│   ├── pom.xml                 # Maven build
│   └── src/main/
│       ├── java/               # Código Java
│       └── resources/          # plugin.yml, config.yml
│
└── db/                         # Base de datos
    └── schema.sql              # Esquema de tablas
```

## ⚙️ Configuración

### Añadir productos

Edita `config.py`:

```python
PRODUCTS = {
    'mi-rango': {
        'price_id': 'price_xxx',  # De Stripe
        'mode': 'payment',
        'command': 'lp user {uuid} parent set mi-rango',
    },
}
```

### Comandos disponibles

En los comandos puedes usar:
- `{uuid}` - UUID del jugador
- `{username}` - Nombre del jugador

## 🔒 Seguridad

- Las claves de API nunca se exponen al frontend
- Los comandos se autentican con secret-key
- Los pagos se verifican con Stripe

## 📄 Licencia

MIT License - Usa este código como quieras.

## 💬 Soporte

- Discord: [discord.gg/tu-servidor](https://discord.gg/tu-servidor)
- Issues: Usa GitHub Issues

---

⭐ **Si te gusta el proyecto, déjanos una estrella!** ⭐
