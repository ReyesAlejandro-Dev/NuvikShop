"""
NuvikShop - Backend Flask
Tu propia tienda tipo Tebex
"""

from flask import Flask, render_template, request, jsonify, url_for
from mcrcon import MCRcon
from datetime import datetime
import os
import requests
import stripe

# Cargar variables de entorno
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='templates')

# ============================================
# CONFIGURACIÓN
# ============================================

# Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY')

# Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# Plugin
PLUGIN_SECRET_KEY = os.getenv('PLUGIN_SECRET_KEY', 'cambia-esta-clave')

# Cola de comandos pendientes
pending_commands = []

# Importar productos desde config.py
from config import PRODUCTS, SHOP_CONFIG

# ============================================
# UTILIDADES
# ============================================

def get_minecraft_uuid(username):
    """Obtiene el UUID de Mojang"""
    try:
        resp = requests.get(f'https://api.mojang.com/users/profiles/minecraft/{username}')
        if resp.status_code == 200:
            uuid_raw = resp.json().get('id', '')
            if len(uuid_raw) == 32:
                return f"{uuid_raw[:8]}-{uuid_raw[8:12]}-{uuid_raw[12:16]}-{uuid_raw[16:20]}-{uuid_raw[20:]}"
    except:
        pass
    return None

def add_command_to_queue(username, player_id, command, product_id):
    """Añade comando a la cola"""
    import uuid as uuid_lib
    entry = {
        'id': str(uuid_lib.uuid4())[:8],
        'username': username,
        'player_id': player_id,
        'command': command,
        'product_id': product_id,
        'created_at': datetime.now().isoformat()
    }
    pending_commands.append(entry)
    print(f"[QUEUE] Añadido: {entry['id']} - {command}")
    return entry['id']

def create_ticket(session_id, username, product_id, status, amount):
    """Crea ticket en Supabase"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return
    try:
        headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json'
        }
        data = {
            'id': f'TKT-{session_id[:8].upper()}',
            'username': username,
            'productId': product_id,
            'status': status,
            'total': amount/100,
            'createdAt': datetime.now().isoformat()
        }
        requests.post(f'{SUPABASE_URL}/rest/v1/tickets', headers=headers, json=data)
    except Exception as e:
        print(f"[TICKET] Error: {e}")

# ============================================
# RUTAS WEB
# ============================================

@app.route('/')
def index():
    return render_template('index.html', config=SHOP_CONFIG)

@app.route('/shop')
def shop():
    return render_template('shop.html', config=SHOP_CONFIG)

@app.route('/success')
def success():
    session_id = request.args.get('session_id')
    if session_id:
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            if session.payment_status == 'paid':
                username = session.metadata.get('minecraft_username')
                product_id = session.metadata.get('product_id')
                amount = session.amount_total or 0
                
                # Crear ticket
                create_ticket(session_id, username, product_id, 'completed', amount)
                
                # Obtener UUID y crear comando
                uuid = get_minecraft_uuid(username)
                player_id = uuid if uuid else username
                
                product = PRODUCTS.get(product_id)
                if product and 'command' in product:
                    cmd = product['command'].replace('{uuid}', player_id).replace('{username}', username)
                    add_command_to_queue(username, player_id, cmd, product_id)
                    
        except Exception as e:
            print(f"[ERROR] {e}")
    
    return render_template('success.html', config=SHOP_CONFIG)

@app.route('/cancel')
def cancel():
    return render_template('cancel.html', config=SHOP_CONFIG)

# ============================================
# API - STRIPE
# ============================================

@app.route('/api/create-checkout-session', methods=['POST'])
def create_checkout_session():
    data = request.json
    product_id = data.get('productId')
    username = data.get('username')
    
    product = PRODUCTS.get(product_id)
    if not product or not username:
        return jsonify(error='Producto no encontrado'), 400
    
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{'price': product['price_id'], 'quantity': 1}],
            mode=product.get('mode', 'payment'),
            success_url=url_for('success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('cancel', _external=True),
            metadata={'minecraft_username': username, 'product_id': product_id}
        )
        return jsonify({'id': session.id, 'url': session.url})
    except Exception as e:
        return jsonify(error=str(e)), 500

# ============================================
# API - PLUGIN
# ============================================

@app.route('/api/plugin/pending', methods=['GET'])
def get_pending():
    """El plugin consulta esto para obtener comandos"""
    if request.headers.get('X-Plugin-Secret') != PLUGIN_SECRET_KEY:
        return jsonify(error='Unauthorized'), 401
    return jsonify(success=True, commands=list(pending_commands))

@app.route('/api/plugin/confirm', methods=['POST'])
def confirm_command():
    """El plugin confirma que ejecutó un comando"""
    if request.headers.get('X-Plugin-Secret') != PLUGIN_SECRET_KEY:
        return jsonify(error='Unauthorized'), 401
    
    global pending_commands
    cmd_id = request.json.get('command_id')
    pending_commands = [c for c in pending_commands if c['id'] != cmd_id]
    return jsonify(success=True)

# ============================================
# MAIN
# ============================================

if __name__ == '__main__':
    port = int(os.getenv('PORT', 4242))
    debug = os.getenv('DEBUG', 'true').lower() == 'true'
    print(f"🛒 NuvikShop corriendo en http://localhost:{port}")
    app.run(debug=debug, port=port)
