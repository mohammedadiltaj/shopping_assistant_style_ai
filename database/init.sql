-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create schemas following Oracle RDM conventions
CREATE SCHEMA IF NOT EXISTS retail;

-- Product Hierarchy (Category, Department, Class, Subclass)
CREATE TABLE IF NOT EXISTS retail.product_hierarchy (
    hierarchy_id SERIAL PRIMARY KEY,
    hierarchy_level VARCHAR(50) NOT NULL,
    hierarchy_name VARCHAR(200) NOT NULL,
    parent_hierarchy_id INTEGER REFERENCES retail.product_hierarchy(hierarchy_id),
    hierarchy_path VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Product (Master Product)
CREATE TABLE IF NOT EXISTS retail.product (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(500) NOT NULL,
    product_description TEXT,
    brand_name VARCHAR(200),
    hierarchy_id INTEGER REFERENCES retail.product_hierarchy(hierarchy_id),
    product_type VARCHAR(100),
    gender VARCHAR(50),
    season VARCHAR(50),
    year INTEGER,
    status VARCHAR(50) DEFAULT 'ACTIVE',
    embedding vector(1536), -- OpenAI ada-002 dimensions
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Product Variant (Color, Size variations)
CREATE TABLE IF NOT EXISTS retail.product_variant (
    variant_id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES retail.product(product_id) ON DELETE CASCADE,
    variant_name VARCHAR(200),
    color VARCHAR(100),
    size VARCHAR(50),
    material VARCHAR(200),
    pattern VARCHAR(100),
    variant_attributes JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- SKU (Stock Keeping Unit)
CREATE TABLE IF NOT EXISTS retail.sku (
    sku_id SERIAL PRIMARY KEY,
    variant_id INTEGER NOT NULL REFERENCES retail.product_variant(variant_id) ON DELETE CASCADE,
    sku_code VARCHAR(100) UNIQUE NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    cost DECIMAL(10, 2),
    currency VARCHAR(3) DEFAULT 'USD',
    inventory_quantity INTEGER DEFAULT 0,
    reorder_point INTEGER DEFAULT 10,
    status VARCHAR(50) DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Customer
CREATE TABLE IF NOT EXISTS retail.customer (
    customer_id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone VARCHAR(20),
    date_of_birth DATE,
    gender VARCHAR(50),
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(100) DEFAULT 'USA',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Style Profile (Customer preferences)
CREATE TABLE IF NOT EXISTS retail.style_profile (
    profile_id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES retail.customer(customer_id) ON DELETE CASCADE,
    style_preferences JSONB,
    favorite_colors TEXT[],
    size_preferences JSONB,
    price_range_min DECIMAL(10, 2),
    price_range_max DECIMAL(10, 2),
    brand_preferences TEXT[],
    occasion_preferences TEXT[],
    embedding vector(1536),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Event Profile (Special occasions)
CREATE TABLE IF NOT EXISTS retail.event_profile (
    event_id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES retail.customer(customer_id) ON DELETE CASCADE,
    event_type VARCHAR(100),
    event_date DATE,
    dress_code VARCHAR(100),
    venue_type VARCHAR(100),
    guest_count INTEGER,
    preferences JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Review
CREATE TABLE IF NOT EXISTS retail.review (
    review_id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES retail.product(product_id) ON DELETE CASCADE,
    customer_id INTEGER REFERENCES retail.customer(customer_id),
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    review_title VARCHAR(200),
    review_text TEXT,
    verified_purchase BOOLEAN DEFAULT FALSE,
    helpful_count INTEGER DEFAULT 0,
    embedding vector(1536),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Order
CREATE TABLE IF NOT EXISTS retail.order (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES retail.customer(customer_id),
    order_number VARCHAR(100) UNIQUE NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    order_status VARCHAR(50) DEFAULT 'PENDING',
    subtotal DECIMAL(10, 2) NOT NULL,
    tax_amount DECIMAL(10, 2) DEFAULT 0,
    shipping_amount DECIMAL(10, 2) DEFAULT 0,
    discount_amount DECIMAL(10, 2) DEFAULT 0,
    total_amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    shipping_address JSONB,
    billing_address JSONB,
    payment_method VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Order Line Item
CREATE TABLE IF NOT EXISTS retail.order_line_item (
    line_item_id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES retail.order(order_id) ON DELETE CASCADE,
    sku_id INTEGER NOT NULL REFERENCES retail.sku(sku_id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10, 2) NOT NULL,
    discount_amount DECIMAL(10, 2) DEFAULT 0,
    line_total DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Return Request
CREATE TABLE IF NOT EXISTS retail.return_request (
    return_id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES retail.order(order_id),
    line_item_id INTEGER REFERENCES retail.order_line_item(line_item_id),
    return_reason VARCHAR(200),
    return_status VARCHAR(50) DEFAULT 'PENDING',
    requested_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_date TIMESTAMP,
    refund_amount DECIMAL(10, 2),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_product_hierarchy ON retail.product(hierarchy_id);
CREATE INDEX IF NOT EXISTS idx_product_embedding ON retail.product USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_sku_variant ON retail.sku(variant_id);
CREATE INDEX IF NOT EXISTS idx_variant_product ON retail.product_variant(product_id);
CREATE INDEX IF NOT EXISTS idx_review_product ON retail.review(product_id);
CREATE INDEX IF NOT EXISTS idx_review_embedding ON retail.review USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_order_customer ON retail.order(customer_id);
CREATE INDEX IF NOT EXISTS idx_order_date ON retail.order(order_date);
CREATE INDEX IF NOT EXISTS idx_style_profile_customer ON retail.style_profile(customer_id);
CREATE INDEX IF NOT EXISTS idx_style_profile_embedding ON retail.style_profile USING ivfflat (embedding vector_cosine_ops);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_product_updated_at BEFORE UPDATE ON retail.product
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sku_updated_at BEFORE UPDATE ON retail.sku
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_customer_updated_at BEFORE UPDATE ON retail.customer
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_order_updated_at BEFORE UPDATE ON retail.order
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

