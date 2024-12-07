import psycopg2
import select
from testapp.tasks import run_selenium_bot 

"""
This script listens for database changes in the `mysafir` PostgreSQL database 
and triggers a Celery task when a change occurs.

Key Functionality:
- Subscribes to the `db_changes` channel in PostgreSQL.
- Listens for notifications sent by a trigger on the `testapp_createorder` table.
- When a notification is received, it extracts details (`table`, `record_id`, 
  `operation`) and triggers the `run_selenium_bot` Celery task asynchronously.

Setup:
1. Define the trigger function in PostgreSQL
2. Attach the trigger to the table:

Usage:
Run this script to listen for database changes:
   $ python listen_to_changes.py
"""

def listen_to_changes():
    try:
        # Connect to PostgreSQL database
        conn = psycopg2.connect(
            dbname="mysafir",
            user="postgres",
            password="postgres",
            host="localhost",  
            port=5432       
        )
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Listen to the 'db_changes' channel
        cursor.execute("LISTEN db_changes;")
        print("Listening to database changes...")

        # Infinite loop to wait for notifications
        while True:
            if select.select([conn], [], [], None):  # Wait for notifications
                conn.poll()
                while conn.notifies:
                    notify = conn.notifies.pop(0)
                    print(f"Received notification: {notify.payload}")

                    # Parse the notification payload
                    payload = eval(notify.payload)  # Parse the JSON-like string into a Python dict
                    table = payload.get('table')
                    record_id = payload.get('id')
                    operation = payload.get('operation')

                    # Trigger the Celery task
                    run_selenium_bot.delay(table, record_id, operation)

    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    listen_to_changes()



"""
I run this  into mysafir database
CREATE OR REPLACE FUNCTION notify_change()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM pg_notify(
        'db_changes',
        json_build_object(
            'table', TG_TABLE_NAME,
            'operation', TG_OP,
            'id', NEW.id
        )::text
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;




run this:
CREATE TRIGGER notify_order_change
AFTER INSERT OR UPDATE OR DELETE ON testapp_createorder
FOR EACH ROW
EXECUTE FUNCTION notify_change();

"""