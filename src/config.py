# ============================================
# NUVIKSHOP - Configuración de Productos
# ============================================
# Edita este archivo para personalizar tu tienda

PRODUCTS = {
    # =====================
    # RANGOS PERMANENTES
    # =====================
    'vip': {
        'price_id': 'STRIPE_PRICE_ID_HERE',
        'mode': 'payment',
        'command': 'lp user {uuid} parent set vip',
    },
    'mvp': {
        'price_id': 'STRIPE_PRICE_ID_HERE',
        'mode': 'payment',
        'command': 'lp user {uuid} parent set mvp',
    },
    
    # =====================
    # RANGOS TEMPORALES
    # =====================
    'vip-30dias': {
        'price_id': 'STRIPE_PRICE_ID_HERE',
        'mode': 'payment',
        'command': 'lp user {uuid} parent addtemp vip 30d',
    },
    
    # =====================
    # MONEDAS
    # =====================
    'coins-50k': {
        'price_id': 'STRIPE_PRICE_ID_HERE',
        'mode': 'payment',
        'command': 'eco give {username} 50000',
    },
    
    # =====================
    # COMANDOS
    # =====================
    'cmd-fly': {
        'price_id': 'STRIPE_PRICE_ID_HERE',
        'mode': 'payment',
        'command': 'lp user {uuid} permission set essentials.fly true',
    },
}

# Configuración de la tienda
SHOP_CONFIG = {
    'name': 'Mi Servidor',
    'currency': 'USD',
    'currency_symbol': '$',
    'discord_url': 'https://discord.gg/tu-servidor',
}
