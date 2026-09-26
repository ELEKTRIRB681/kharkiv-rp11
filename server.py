#!/usr/bin/env python3
"""
Simple static file server + ranks API using only standard library.

Endpoints:
- GET  /api/ranks           -> returns all records from data.json
- GET  /api/ranks?nick=NAME -> returns matching records
- POST /api/ranks           -> saves { nickname, rank, faction, verified, expires_on }
- PUT  /api/ranks           -> updates an existing record by identifier nickname

Serves static files from working directory.
"""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
import shutil
from urllib.parse import urlparse, parse_qs
import threading
import queue
import time
import unicodedata
from datetime import date

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data.json')
LICENSE_FACTION = 'Ліцензія на зброю'
VALID_FACTIONS = {'ДБР', 'СБС', 'Суд', 'Прокуратура', LICENSE_FACTION}
BACKUP_FILE = DATA_FILE + '.bak'
LOCK = threading.RLock()
SUBSCRIBERS = []
SUB_LOCK = threading.Lock()


def normalize_faction(value):
    return unicodedata.normalize('NFC', str(value or '')).strip()


def canonical_faction(value):
    normalized = normalize_faction(value)
    key = normalized.casefold()
    return next((faction for faction in VALID_FACTIONS if faction.casefold() == key), '')


def atomic_write(data):
    temporary_file = DATA_FILE + '.tmp'
    with open(temporary_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())
    if os.path.exists(DATA_FILE):
        os.replace(DATA_FILE, BACKUP_FILE)
    os.replace(temporary_file, DATA_FILE)
    if not os.path.exists(BACKUP_FILE):
        shutil.copyfile(DATA_FILE, BACKUP_FILE)


def read_records():
    if not os.path.exists(DATA_FILE):
        return []
    with LOCK:
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if not isinstance(data, list):
                raise json.JSONDecodeError('records must be a list', '', 0)
        except (OSError, json.JSONDecodeError):
            if not os.path.exists(BACKUP_FILE):
                raise
            with open(BACKUP_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            atomic_write(data)
        today = date.today().isoformat()
        active = [
            record for record in data
            if not (record.get('faction') == LICENSE_FACTION and record.get('expires_on', '') < today)
        ]
        if len(active) != len(data):
            atomic_write(active)
        return active


def write_records(data):
    with LOCK:
        atomic_write(data)
    # notify live subscribers about the update
    try:
        payload = json.dumps({'type': 'update', 'ts': int(time.time())}, ensure_ascii=False)
        with SUB_LOCK:
            for q in list(SUBSCRIBERS):
                try:
                    q.put(payload, block=False)
                except Exception:
                    # ignore queue issues; handler will clean up
                    pass
    except Exception:
        pass


class Handler(SimpleHTTPRequestHandler):
    def _set_headers(self, status=200, ctype='application/json'):
        self.send_response(status)
        self.send_header('Content-type', ctype)
        # allow simple cross-origin access when using ngrok or remote testing
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        # Server-Sent Events endpoint for live updates
        if parsed.path == '/api/stream':
            q = queue.Queue()
            with SUB_LOCK:
                SUBSCRIBERS.append(q)
            try:
                self.send_response(200)
                self.send_header('Content-Type', 'text/event-stream')
                self.send_header('Cache-Control', 'no-cache')
                self.send_header('Connection', 'keep-alive')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                # send an initial comment to establish connection
                self.wfile.write(b": connected\n\n")
                self.wfile.flush()
                while True:
                    try:
                        data = q.get(timeout=15)
                        msg = f"event: update\ndata: {data}\n\n".encode('utf-8')
                        self.wfile.write(msg)
                        self.wfile.flush()
                    except queue.Empty:
                        # send a keepalive comment
                        try:
                            self.wfile.write(b": keepalive\n\n")
                            self.wfile.flush()
                        except Exception:
                            break
            except Exception:
                pass
            finally:
                # remove subscriber
                with SUB_LOCK:
                    try:
                        SUBSCRIBERS.remove(q)
                    except ValueError:
                        pass
            return
        if parsed.path == '/api/ranks':
            qs = parse_qs(parsed.query)
            nick = qs.get('nick', [None])[0]
            data = read_records()
            if nick:
                key = nick.strip().lower()
                matches = [r for r in data if r.get('nickname','').lower() == key]
                self._set_headers(200)
                self.wfile.write(json.dumps(matches, ensure_ascii=False).encode('utf-8'))
                return
            self._set_headers(200)
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
            return

        # fall back to static file serving
        return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == '/api/ranks':
            length = int(self.headers.get('Content-Length', 0))
            raw = self.rfile.read(length)
            try:
                payload = json.loads(raw.decode('utf-8'))
            except Exception:
                self._set_headers(400)
                self.wfile.write(json.dumps({'error': 'invalid json'}).encode('utf-8'))
                return

            # expected fields: nickname, rank, faction, verified, expires_on
            nick = payload.get('nickname')
            if not nick:
                self._set_headers(400)
                self.wfile.write(json.dumps({'error': 'nickname required'}).encode('utf-8'))
                return

            nickname = str(nick).strip()
            rank = str(payload.get('rank','')).strip()
            faction = canonical_faction(payload.get('faction'))
            verified = bool(payload.get('verified', False))
            expires_on = str(payload.get('expires_on', '')).strip()

            if faction not in VALID_FACTIONS:
                self._set_headers(400)
                self.wfile.write(json.dumps({'error': 'invalid faction'}, ensure_ascii=False).encode('utf-8'))
                return
            if faction == LICENSE_FACTION:
                try:
                    expiry = date.fromisoformat(expires_on)
                except ValueError:
                    self._set_headers(400)
                    self.wfile.write(json.dumps({'error': 'license expiration date required'}, ensure_ascii=False).encode('utf-8'))
                    return
                if expiry < date.today():
                    self._set_headers(400)
                    self.wfile.write(json.dumps({'error': 'license expiration date has passed'}, ensure_ascii=False).encode('utf-8'))
                    return
            else:
                expires_on = ''

            data = read_records()
            # find existing
            key = nickname.lower()
            updated = False
            for r in data:
                if r.get('nickname','').lower() == key:
                    r['nickname'] = nickname
                    r['rank'] = rank
                    r['faction'] = faction
                    r['verified'] = verified
                    r['expires_on'] = expires_on
                    updated = True
                    break
            if not updated:
                data.append({'nickname': nickname, 'rank': rank, 'faction': faction, 'verified': verified, 'expires_on': expires_on})

            try:
                write_records(data)
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({'error': 'failed to write data', 'details': str(e)}).encode('utf-8'))
                return

            self._set_headers(200)
            self.wfile.write(json.dumps({'ok': True}).encode('utf-8'))
            return

        # otherwise 404
        self._set_headers(404)
        self.wfile.write(json.dumps({'error': 'not found'}).encode('utf-8'))

    def do_PUT(self):
        parsed = urlparse(self.path)
        if parsed.path != '/api/ranks':
            self._set_headers(404)
            self.wfile.write(json.dumps({'error': 'not found'}).encode('utf-8'))
            return

        length = int(self.headers.get('Content-Length', 0))
        try:
            payload = json.loads(self.rfile.read(length).decode('utf-8'))
        except Exception:
            self._set_headers(400)
            self.wfile.write(json.dumps({'error': 'invalid json'}).encode('utf-8'))
            return

        identifier = str(payload.get('identifier', '')).strip()
        nickname = str(payload.get('nickname', '')).strip()
        faction = canonical_faction(payload.get('faction'))
        rank = str(payload.get('rank', '')).strip()
        expires_on = str(payload.get('expires_on', '')).strip()
        verified = bool(payload.get('verified', False))

        if not identifier or not nickname:
            self._set_headers(400)
            self.wfile.write(json.dumps({'error': 'identifier and nickname required'}).encode('utf-8'))
            return
        if faction not in VALID_FACTIONS:
            self._set_headers(400)
            self.wfile.write(json.dumps({'error': 'invalid faction'}, ensure_ascii=False).encode('utf-8'))
            return
        if faction == LICENSE_FACTION:
            try:
                expiry = date.fromisoformat(expires_on)
            except ValueError:
                self._set_headers(400)
                self.wfile.write(json.dumps({'error': 'license expiration date required'}, ensure_ascii=False).encode('utf-8'))
                return
            if expiry < date.today():
                self._set_headers(400)
                self.wfile.write(json.dumps({'error': 'license expiration date has passed'}, ensure_ascii=False).encode('utf-8'))
                return
        else:
            expires_on = ''

        data = read_records()
        identifier_key = identifier.casefold()
        matches = [record for record in data if str(record.get('nickname', '')).strip().casefold() == identifier_key]
        if not matches:
            self._set_headers(404)
            self.wfile.write(json.dumps({'error': 'record not found'}, ensure_ascii=False).encode('utf-8'))
            return

        updated = matches[0]
        updated.update({
            'nickname': nickname,
            'rank': rank,
            'faction': faction,
            'verified': verified,
            'expires_on': expires_on
        })
        # Collapse any historical duplicates for the same identifier.
        result = []
        replaced = False
        for record in data:
            if str(record.get('nickname', '')).strip().casefold() == identifier_key:
                if not replaced:
                    result.append(updated)
                    replaced = True
            else:
                result.append(record)

        try:
            write_records(result)
        except Exception as error:
            self._set_headers(500)
            self.wfile.write(json.dumps({'error': 'failed to write data', 'details': str(error)}).encode('utf-8'))
            return

        self._set_headers(200)
        self.wfile.write(json.dumps({'ok': True, 'record': updated}, ensure_ascii=False).encode('utf-8'))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Serve static files and ranks API')
    parser.add_argument('--port', '-p', type=int, default=3000)
    args = parser.parse_args()

    os.chdir(os.path.dirname(__file__) or '.')
    server = ThreadingHTTPServer(('0.0.0.0', args.port), Handler)
    print(f'Serving on http://0.0.0.0:{args.port} (Ctrl-C to stop)')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nShutting down')
        server.server_close()
