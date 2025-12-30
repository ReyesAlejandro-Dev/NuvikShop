-- ============================================
-- NUVIKSHOP - Esquema de Base de Datos
-- ============================================
-- Ejecuta este SQL en tu proyecto de Supabase

-- Tabla de productos
CREATE TABLE IF NOT EXISTS products (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT,
    price NUMERIC NOT NULL,
    image TEXT,
    icon TEXT,
    description TEXT,
    features JSONB,
    featured BOOLEAN DEFAULT false,
    outOfStock BOOLEAN DEFAULT false,
    createdAt TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla de tickets (compras)
CREATE TABLE IF NOT EXISTS tickets (
    id TEXT PRIMARY KEY,
    username TEXT NOT NULL,
    productId TEXT,
    product JSONB,
    status TEXT DEFAULT 'pending',
    paymentMethod TEXT,
    stripeSessionId TEXT,
    createdAt TIMESTAMPTZ DEFAULT NOW(),
    updatedAt TIMESTAMPTZ,
    coupon TEXT,
    discount NUMERIC DEFAULT 0,
    total NUMERIC
);

-- Índices para mejor rendimiento
CREATE INDEX IF NOT EXISTS idx_tickets_username ON tickets (username);

CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets (status);

CREATE INDEX IF NOT EXISTS idx_products_category ON products (category);