# DSW MCP Server

MCP server untuk aplikasi DSW (Kemenkeu) dengan session cookie persisten.

## Setup

```bash
cd dsw-mcp
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` dan isi kredensial:

```
DSW_USER=your_username
DSW_PASSWORD=your_password
```

## Menjalankan Server

```bash
python server.py
```

Server berjalan via stdio (default FastMCP).

## Konfigurasi Cursor

Tambahkan ke Cursor MCP settings:

```json
{
  "mcpServers": {
    "dsw": {
      "command": "python",
      "args": ["/absolute/path/to/dsw-mcp/server.py"],
      "cwd": "/absolute/path/to/dsw-mcp"
    }
  }
}
```

Ganti `/absolute/path/to/dsw-mcp` dengan path absolut ke direktori ini.

## Tools

### `login_dsw`

Login ke DSW menggunakan kredensial dari `.env`. Tidak memerlukan parameter.

Return value:

```json
{"success": true, "message": "Login berhasil"}
```

Cookie `ci_session` otomatis tersimpan di `requests.Session` dan dipakai ulang oleh tool berikutnya.

### `check_user_dsw`

Cek data user SatuDJA berdasarkan User ID. Auto-login dari `.env` jika session belum ada.

Parameter: `userid` (string)

Return value:

```json
{
  "success": true,
  "found": true,
  "userid": "527010",
  "unit": "527010 KANTOR PUSAT ...",
  "nama": "DENI HARYONO",
  "nip": "197812142000121001",
  "no_hp": "081352237779",
  "email": "user@kemenkeu.go.id",
  "login": "",
  "sugesti": "...",
  "password_asli": "..."
}
```

## SSL / Sertifikat

Server DSW memakai sertifikat Sectigo dengan intermediate CA yang mungkin belum ada di trust store sistem. MCP server otomatis membangun CA bundle dari **certifi** + **Sectigo OV R36** (`certs/sectigo-ov-r36.pem`) saat startup.

Override opsional via `.env`:

```env
# SSL_CA_BUNDLE=/path/to/custom-ca.pem
# SSL_VERIFY=false   # emergency only, tidak disarankan
```

### Troubleshooting SSL

Jika login gagal dengan `CERTIFICATE_VERIFY_FAILED`:

1. Pastikan file `certs/sectigo-ov-r36.pem` ada
2. Hapus cache bundle: `rm -f certs/dsw-ca-bundle.pem certs/.bundle-version` lalu restart server
3. Pastikan memakai Python dari venv: `.venv/bin/python3` (bukan system python)
4. Test koneksi HTTPS:
   ```bash
   python3 -c "from client.session import session; print(session.get('https://dsw.kemenkeu.go.id/', timeout=10).status_code)"
   ```

## Testing

```bash
pip install pytest
pytest tests/
```
