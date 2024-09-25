-- Creates the history_modifications table
CREATE TABLE IF NOT EXISTS history_modifications (
    id SERIAL PRIMARY KEY,
    table_name TEXT NOT NULL,
    column_name TEXT NOT NULL,
    old_value TEXT,
    new_value TEXT,
    changed_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    operation_type TEXT NOT NULL,
    changed_by TEXT NOT NULL
);

-- Creates the audit_log table
CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    table_name TEXT NOT NULL,
    operation_type TEXT NOT NULL,
    affected_row_id TEXT NOT NULL,
    performed_by TEXT NOT NULL,
    performed_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
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
    column_name TEXT;
    old_value TEXT;
    new_value TEXT;
BEGIN

    SELECT current_user_name INTO username
    FROM user_context
    WHERE session_id = (SELECT current_setting('myapp.session_id'));

    IF username IS NULL THEN
        username := 'unknown';
    END IF;

    FOR column_name IN 
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = TG_TABLE_NAME AND column_name != 'id'
    LOOP
        EXECUTE format('SELECT ($1).%I::TEXT, ($2).%I::TEXT', column_name, column_name)
        INTO old_value, new_value
        USING OLD, NEW;

        IF old_value IS DISTINCT FROM new_value THEN
            INSERT INTO history_modifications(
                table_name,
                column_name,
                old_value,
                new_value,
                operation_type,
                changed_by,
                changed_at
            )
            VALUES (
                TG_TABLE_NAME,
                column_name,
                old_value,
                new_value,
                'UPDATE',
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
BEGIN

    SELECT current_user_name INTO username
    FROM user_context
    WHERE session_id = (SELECT current_setting('myapp.session_id'));

    IF username IS NULL THEN
        username := 'unknown';
    END IF;

    INSERT INTO audit_log(
        table_name,
        operation_type,
        affected_row_id,
        performed_by,
        performed_at
    )
    VALUES (
        TG_TABLE_NAME,
        'INSERT',
        NEW.id::TEXT,
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
BEGIN
    SELECT current_user_name INTO username
    FROM user_context
    WHERE session_id = (SELECT current_setting('myapp.session_id'));

    IF username IS NULL THEN
        username := 'unknown';
    END IF;

    INSERT INTO audit_log(
        table_name,
        operation_type,
        affected_row_id,
        performed_by,
        performed_at
    )
    VALUES (
        TG_TABLE_NAME,
        'DELETE',
        OLD.id::TEXT,
        username,
        CURRENT_TIMESTAMP
    );

    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

-- Creates the triggers on the items table
-- ITEMS
CREATE TRIGGER trigger_log_changes_items
AFTER UPDATE ON items
FOR EACH ROW
EXECUTE FUNCTION log_changes();

CREATE TRIGGER trigger_log_insert_items
AFTER INSERT ON items
FOR EACH ROW
EXECUTE FUNCTION log_insert();

CREATE TRIGGER trigger_log_delete_items
AFTER DELETE ON items
FOR EACH ROW
EXECUTE FUNCTION log_delete();
-- STOCK
CREATE TRIGGER trigger_log_changes_stock
AFTER UPDATE ON stock
FOR EACH ROW
EXECUTE FUNCTION log_changes();

CREATE TRIGGER trigger_log_insert_stock
AFTER INSERT ON stock
FOR EACH ROW
EXECUTE FUNCTION log_insert();

CREATE TRIGGER trigger_log_delete_stock
AFTER DELETE ON stock
FOR EACH ROW
EXECUTE FUNCTION log_delete();
-- GROUPS
CREATE TRIGGER trigger_log_changes_groups
AFTER UPDATE ON groups
FOR EACH ROW
EXECUTE FUNCTION log_changes();
-- PURCHASES
CREATE TRIGGER trigger_log_changes_purchases
AFTER UPDATE ON purchases
FOR EACH ROW
EXECUTE FUNCTION log_changes();

CREATE TRIGGER trigger_log_insert_purchases
AFTER INSERT ON purchases
FOR EACH ROW
EXECUTE FUNCTION log_insert();

CREATE TRIGGER trigger_log_delete_purchases
AFTER DELETE ON purchases
FOR EACH ROW
EXECUTE FUNCTION log_delete();
-- PURCHASE-GROUPS
CREATE TRIGGER trigger_log_changes_purchase_groups
AFTER UPDATE ON purchase_groups
FOR EACH ROW
EXECUTE FUNCTION log_changes();

CREATE TRIGGER trigger_log_insert_purchase_groups
AFTER INSERT ON purchase_groups
FOR EACH ROW
EXECUTE FUNCTION log_insert();

CREATE TRIGGER trigger_log_delete_purchase_groups
AFTER DELETE ON purchase_groups
FOR EACH ROW
EXECUTE FUNCTION log_delete();
