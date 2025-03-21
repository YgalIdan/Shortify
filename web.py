from flask import Flask, render_template, request, jsonify, redirect
from datetime import datetime, timedelta, date
import random
import psycopg2
import yaml

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

app = Flask(__name__)

DB_CONFIG = {
    "dbname": config["DB"]["dbname"],
    "user": config["DB"]["user"],
    "password": config["DB"]["password"],
    "host": config["DB"]["host"],
    "port": config["DB"]["port"]
}

try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    print("✅ חיבור ל-PostgreSQL הצליח!")
except Exception as e:
    print("❌ שגיאה בחיבור ל-PostgreSQL:", str(e))


@app.route("/")
def index():
    today = date.today()
    max_date = today + timedelta(days=7)
    return render_template('index.html', today=today, max_date=max_date)


@app.route("/list_url")
def listUrl():
    try:
        cursor.execute("SELECT * FROM url WHERE created_at + INTERVAL '7 days' >\
                    NOW()")
        data = cursor.fetchall()
    except Exception as e:
        print("❌ שגיאה בחיבור ל-PostgreSQL:", str(e))
    return render_template('list_url.html', data=data)


def add_days(value, days):
    if isinstance(value, datetime):
        return value + timedelta(days=days)
    return value


def format_datetime(value, format='%d/%m/%Y'):
    if isinstance(value, datetime):
        return value.strftime(format)


app.jinja_env.filters['add_days'] = add_days
app.jinja_env.filters['format_datetime'] = format_datetime


@app.route("/<short_code>")
def connect(short_code):
    try:
        cursor.execute("SELECT created_at FROM url WHERE short_url=%s",
                    (short_code,))
        date = cursor.fetchone()
        cursor.execute("SELECT long_url FROM url WHERE short_url=%s",
                    (short_code,))
        url = cursor.fetchone()
    except Exception as e:
        print("❌ שגיאה בחיבור ל-PostgreSQL:", str(e))
    if url is None:
        return jsonify({"ERROR": "URL not found!"}), 400
    if date[0] + timedelta(days=7) < datetime.now():
        return jsonify({"ERROR": "URL Expired"}), 400
    return redirect(f"{url[0]}")


@app.route("/shorten", methods=['POST'])
def shorten():
    data = request.json
    url = data.get("url")
    expiry_date = data.get("expiry_date")
    if not url:
        return jsonify({"ERROR": "url missing!"}), 400
    urlShort = generateShortUrl(url)
    try:
        cursor.execute("SELECT short_url FROM url")
        shortURlInDB = cursor.fetchone()
        if shortURlInDB is not None or urlShort in shortURlInDB:
            insertDb(url, urlShort, expiry_date)
        return jsonify({"message": "URL shortened successfully!", "short_url":
                        urlShort}), 200
    except Exception as e:
        print("❌ שגיאה בחיבור ל-PostgreSQL:", str(e))
        return jsonify({"ERROR": str(e)}), 500


def insertDb(url, urlShort, expiry_date):
    if not expiry_date:
        insert_query = """
        INSERT INTO url (long_url, short_url, created_at)
        VALUES (%s, %s, NOW() + INTERVAL '7 days');
        """
        cursor.execute(insert_query, (url, urlShort))
    else:
        insert_query = """
        INSERT INTO url (long_url, short_url, created_at)
        VALUES (%s, %s, %s);
        """
        cursor.execute(insert_query, (url, urlShort, expiry_date))
    conn.commit()


def generateShortUrl(longUrl):
    opt = [chr(i) for i in range(48, 58)] + [chr(i) for i in range(65, 91)]\
    + [chr(i) for i in range(97, 123)]
    urlShort = ""
    for i in range(random.randrange(3, 6)):
        urlShort += random.choice(opt)
    return urlShort


@app.route("/health", methods=['GET'])
def health():
    try:
        cursor.execute("SELECT * FROM url")
        return jsonify({"STATUS": "DB healthy"}), 200
    except Exception as e:
        return jsonify({"ERROR": str(e)}), 500


if __name__ == "__main__":
    app.run(host=config["Flask"]["host"], port=config["Flask"]["port"],
            debug=config["Flask"]["debug"])
