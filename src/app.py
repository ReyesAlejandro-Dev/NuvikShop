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
import uuid as uuid_lib

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

# Importar productos desde config.py
from config import PRODUCTS, SHOP_CONFIG

# ============================================
# INTERACCIÓN CON SUPABASE
# ============================================

def supabase_request(method, endpoint, data=None):
    """Helper para hacer peticiones a Supabase"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("[ERROR] Faltan credenciales de Supabase")
        return None
        
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=representation'
    }
    
    url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
    
    try:
        if method == 'GET':
            resp = requests.get(url, headers=headers, params=data)
        elif method == 'POST':
            resp = requests.post(url, headers=headers, json=data)
        elif method == 'PATCH':
            resp = requests.patch(url, headers=headers, json=data)
        elif method == 'DELETE':
            resp = requests.delete(url, headers=headers)
            
        return resp.json() if resp.text else None
    except Exception as e:
        print(f"[SUPABASE ERROR] {e}")
        return None

def add_command_to_queue(username, player_id, command, product_id):
    """Añade comando a la tabla pending_commands en Supabase"""
    data = {
        'id': str(uuid_lib.uuid4())[:8],
        'username': username,
        'player_id': player_id,
        'command': command,
        'product_id': product_id,
        'status': 'pending',
        'created_at': datetime.now().isoformat()
    }
    supabase_request('POST', 'pending_commands', data)
    print(f"[QUEUE] Comando guardado en DB: {data['id']}")
    return data['id']

def get_pending_commands_from_db():
    """Obtiene comandos pendientes de la DB"""
    # select=*&status=eq.pending
    params = {'select': '*', 'status': 'eq.pending'}
    return supabase_request('GET', 'pending_commands', params) or []

def mark_command_as_executed(command_id):
    """Marca un comando como ejecutado o lo borra"""
    # Opción A: Borrarlo (para no llenar la DB)
    params = {'id': f'eq.{command_id}'}
    # supabase_request('DELETE', f'pending_commands?id=eq.{command_id}')
    
    # Opción B: Marcarlo como executed
    supabase_request('PATCH', f'pending_commands?id=eq.{command_id}', {'status': 'executed'})

def create_ticket(session_id, username, product_id, status, amount):
    """Crea ticket en Supabase"""
    data = {
        'id': f'TKT-{session_id[:8].upper()}',
        'username': username,
        'productId': product_id,
        'status': status,
        'total': amount/100,
        'stripeSessionId': session_id,
        'createdAt': datetime.now().isoformat()
    }
    supabase_request('POST', 'tickets', data)

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
    
    # Leer desde la DB en lugar de memoria
    commands = get_pending_commands_from_db() or []
    return jsonify(success=True, commands=commands)

@app.route('/api/plugin/confirm', methods=['POST'])
def confirm_command():
    """El plugin confirma que ejecutó un comando"""
    if request.headers.get('X-Plugin-Secret') != PLUGIN_SECRET_KEY:
        return jsonify(error='Unauthorized'), 401
    
    cmd_id = request.json.get('command_id')
    if cmd_id:
        mark_command_as_executed(cmd_id)
        
    return jsonify(success=True)

# ============================================
# MAIN
# ============================================

if __name__ == '__main__':
    port = int(os.getenv('PORT', 4242))
    debug = os.getenv('DEBUG', 'true').lower() == 'true'
    print(f"🛒 NuvikShop corriendo en http://localhost:{port}")
    app.run(debug=debug, port=port)
