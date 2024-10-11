-- Creates the history_modifications table
CREATE TABLE IF NOT EXISTS history_modifications (
    id SERIAL PRIMARY KEY,
    table_name TEXT NOT NULL,
    column_name TEXT NOT NULL,
    row_id TEXT NOT NULL,
    old_value TEXT,
    new_value TEXT,
    changed_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    changed_by TEXT NOT NULL
);

-- Creates the audit_log table
CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    table_name TEXT NOT NULL,
    operation_type TEXT NOT NULL,
    affected_row_id TEXT NOT NULL,
    related_id TEXT,
    performed_by TEXT NOT NULL,
    performed_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

--Creates the deleted _item table
CREATE TABLE IF NOT EXISTS deleted_items (
    id SERIAL PRIMARY KEY,
    item_id INTEGER,  
    status_id INTEGER,
    part_number_id INTEGER,
    serial_number TEXT,
    deleted_by TEXT NOT NULL, 
    deleted_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP  
);

-- Creates the user_context table
CREATE TABLE user_context (
    session_id TEXT PRIMARY KEY,
    current_user_name TEXT
);

-- Creates the triggers functions
-- UPDATE
CREATE OR REPLACE FUNCTION log_update() RETURNS TRIGGER AS $$
DECLARE
    username TEXT;
    col_name TEXT;
    old_value TEXT;
    new_value TEXT;
    row_id TEXT;
BEGIN

    SELECT current_user_name INTO username
    FROM user_context
    WHERE session_id = (SELECT current_setting('myapp.session_id'));

    IF username IS NULL THEN
        username := 'unknown';
    END IF;

    row_id := OLD.id::TEXT;

    FOR col_name IN 
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = TG_TABLE_NAME AND column_name != 'id' AND column_name != 'updated_at'
    LOOP
        EXECUTE format('SELECT ($1).%I::TEXT, ($2).%I::TEXT', col_name, col_name)
        INTO old_value, new_value
        USING OLD, NEW;

        IF old_value IS DISTINCT FROM new_value THEN
            INSERT INTO history_modifications(
                table_name,
                column_name,
                row_id,
                old_value,
                new_value,
                changed_by,
                changed_at
            )
            VALUES (
                TG_TABLE_NAME,
                col_name,
                row_id,
                old_value,
                new_value,
                username,
                CURRENT_TIMESTAMP
            );
        END IF;
    END LOOP;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- INSERT
CREATE OR REPLACE FUNCTION log_insert() RETURNS TRIGGER AS $$
DECLARE
    username TEXT;
    related_id_value TEXT;
BEGIN

    SELECT current_user_name INTO username
    FROM user_context
    WHERE session_id = (SELECT current_setting('myapp.session_id'));

    IF username IS NULL THEN
        username := 'unknown';
    END IF;

    RAISE NOTICE 'El registro completo de NEW es: %', row_to_json(NEW);

    IF TG_TABLE_NAME = 'stocks' THEN
        related_id_value := NEW.item_id::TEXT;
    ELSIF TG_TABLE_NAME = 'items' THEN
        related_id_value := NEW.part_number_id::TEXT;
    ELSE
        related_id_value := NULL;
    END IF;

    INSERT INTO audit_log(
        table_name,
        operation_type,
        affected_row_id,
        related_id,
        performed_by,
        performed_at
    )
    VALUES (
        TG_TABLE_NAME,
        'INSERT',
        NEW.id::TEXT,
        related_id_value,
        username,
        CURRENT_TIMESTAMP
    );

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- DELETE
CREATE OR REPLACE FUNCTION log_delete() RETURNS TRIGGER AS $$
DECLARE
    username TEXT;
    related_id_value TEXT;
BEGIN
    SELECT current_user_name INTO username
    FROM user_context
    WHERE session_id = (SELECT current_setting('myapp.session_id'));

    IF username IS NULL THEN
        username := 'unknown';
    END IF;

    IF TG_TABLE_NAME = 'stocks' THEN
        related_id_value := OLD.item_id::TEXT;
    ELSIF TG_TABLE_NAME = 'items' THEN
        related_id_value := OLD.part_number_id::TEXT;
    ELSE
        related_id_value := NULL;
    END IF;

    INSERT INTO audit_log(
        table_name,
        operation_type,
        affected_row_id,
        related_id,
        performed_by,
        performed_at
    )
    VALUES (
        TG_TABLE_NAME,
        'DELETE',
        OLD.id::TEXT,
        related_id_value,
        username,
        CURRENT_TIMESTAMP
    );

    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION log_deleted_item() RETURNS TRIGGER AS $$
DECLARE
    username TEXT;
BEGIN
    SELECT current_user_name INTO username
    FROM user_context
    WHERE session_id = (SELECT current_setting('myapp.session_id'));

    IF username IS NULL THEN
        username := 'unknown';
    END IF;

    INSERT INTO deleted_items (
        item_id, 
        status_id, 
        part_number_id, 
        serial_number, 
        deleted_by, 
        deleted_at
    )
    VALUES (
        OLD.id, 
        OLD.status_id, 
        OLD.part_number_id, 
        OLD.serial_number, 
        username, 
        CURRENT_TIMESTAMP
    );

    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

-- Creates the triggers on the items table
-- ITEMS
CREATE TRIGGER trigger_log_update_items
AFTER UPDATE ON items
FOR EACH ROW
EXECUTE FUNCTION log_update();

CREATE TRIGGER trigger_log_insert_items
AFTER INSERT ON items
FOR EACH ROW
EXECUTE FUNCTION log_insert();

CREATE TRIGGER trigger_log_delete_items
AFTER DELETE ON items
FOR EACH ROW
EXECUTE FUNCTION log_delete();

CREATE TRIGGER trigger_log_deleted_item
AFTER DELETE ON items
FOR EACH ROW
EXECUTE FUNCTION log_deleted_item();
-- STOCK
CREATE TRIGGER trigger_log_update_stock
AFTER UPDATE ON stocks
FOR EACH ROW
EXECUTE FUNCTION log_update();

CREATE TRIGGER trigger_log_insert_stock
AFTER INSERT ON stocks
FOR EACH ROW
EXECUTE FUNCTION log_insert();

CREATE TRIGGER trigger_log_delete_stock
AFTER DELETE ON stocks
FOR EACH ROW
EXECUTE FUNCTION log_delete();
-- GROUPS
CREATE TRIGGER trigger_log_update_groups
AFTER UPDATE ON groups
FOR EACH ROW
EXECUTE FUNCTION log_update();
-- PURCHASES
CREATE TRIGGER trigger_log_update_purchases
AFTER UPDATE ON purchases
FOR EACH ROW
EXECUTE FUNCTION log_update();

CREATE TRIGGER trigger_log_insert_purchases
AFTER INSERT ON purchases
FOR EACH ROW
EXECUTE FUNCTION log_insert();

CREATE TRIGGER trigger_log_delete_purchases
AFTER DELETE ON purchases
FOR EACH ROW
EXECUTE FUNCTION log_delete();
-- PURCHASE-GROUPS
CREATE TRIGGER trigger_log_update_purchase_groups
AFTER UPDATE ON purchase_groups
FOR EACH ROW
EXECUTE FUNCTION log_update();

CREATE TRIGGER trigger_log_insert_purchase_groups
AFTER INSERT ON purchase_groups
FOR EACH ROW
EXECUTE FUNCTION log_insert();

CREATE TRIGGER trigger_log_delete_purchase_groups
AFTER DELETE ON purchase_groups
FOR EACH ROW
EXECUTE FUNCTION log_delete();

-- INDEXES
DROP INDEX IF EXISTS unique_item_stock;
CREATE UNIQUE INDEX unique_item_stock ON stocks (item_id, stock_type_id);

 DROP INDEX IF EXISTS unique_item_code;
-- CREATE UNIQUE INDEX unique_item_code ON items (code)
-- WHERE code IS NOT NULL AND code != '';

DROP INDEX IF EXISTS unique_item_serial_number;
-- CREATE UNIQUE INDEX unique_item_serial_number ON items (serial_number)
-- WHERE serial_number IS NOT NULL AND serial_number != '';

DROP INDEX IF EXISTS unique_purchase_group_order;
CREATE UNIQUE INDEX unique_purchase_group_order ON purchase_groups (order_number)
WHERE order_number IS NOT NULL AND order_number != '';