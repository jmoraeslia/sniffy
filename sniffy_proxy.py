import json
import sqlite3
import time

DB_FILE = "requests.db"
LOG_FILE = "requests.log"

def start():
    # Cria tabela se não existir
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            method TEXT,
            url TEXT,
            timestamp INTEGER,
            request_headers TEXT,
            request_body TEXT,
            response_status INTEGER,
            response_headers TEXT,
            response_body TEXT
        )
    """)
    conn.commit()
    conn.close()

start()

def response(flow):
    req = flow.request
    resp = flow.response

    method = req.method
    url = req.pretty_url
    timestamp = int(time.time())

    request_headers = json.dumps(dict(req.headers), indent=2)
    request_body = req.get_text()

    response_status = resp.status_code
    response_headers = json.dumps(dict(resp.headers), indent=2)
    response_body = resp.get_text()

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        INSERT INTO requests (
            method, url, timestamp,
            request_headers, request_body,
            response_status, response_headers, response_body
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        method, url, timestamp,
        request_headers, request_body,
        response_status, response_headers, response_body
    ))
    conn.commit()
    conn.close()

    # opcional: também logar em texto para live
    with open(LOG_FILE, "a") as f:
        log_entry = json.dumps({"method": method, "url": url})
        f.write(log_entry + "\n")
