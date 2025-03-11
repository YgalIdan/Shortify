from flask import Flask, render_template, request, jsonify, redirect
import random, psycopg2

app = Flask(__name__)

DB_CONFIG = {
    "dbname": "shortURL",
    "user": "admin",
    "password": "admin",
    "host": "127.0.0.1",
    "port": 5432
}

try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    print("✅ חיבור ל-PostgreSQL הצליח!")
except Exception as e:
    print("❌ שגיאה בחיבור ל-PostgreSQL:", str(e))

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/<short_code>")
def connect(short_code):
    cursor.execute(f"SELECT long_url FROM url WHERE short_url=%s",(short_code,))
    url = cursor.fetchone()
    if url is None:
        return jsonify({"ERROR": "URL not found!"}), 400
    return redirect(f"{url[0]}")


@app.route("/shorten", methods=['POST'])
def shorten():
    data = request.json
    url = data.get("url")
    expiry_date = data.get("expiry_date")
    if not url:
        return jsonify({"ERROR": "url missing!"}), 400
    
    urlShort = generateShortUrl(url)
    cursor.execute("SELECT short_url FROM url")
    shortURlInDB = cursor.fetchone()
    if shortURlInDB is None or urlShort in shortURlInDB:
        insertDb(url, urlShort, expiry_date)
    return jsonify({"message": "URL shortened successfully!", "short_url": urlShort}), 200

def insertDb(url, urlShort, expiry_date):
    if not expiry_date:
        insert_query = """
        INSERT INTO url (long_url, short_url, created_at) 
        VALUES (%s, %s, NOW() + INTERVAL '7 days');
        """
        cursor.execute(insert_query,(url, urlShort))
    else:    
        insert_query = """
        INSERT INTO url (long_url, short_url, created_at) 
        VALUES (%s, %s, %s);
        """
        cursor.execute(insert_query,(url, urlShort, expiry_date))
    conn.commit()

def generateShortUrl(longUrl):
    opt = [chr(i) for i in range(48, 58)] + [chr(i) for i in range(65, 91)] + [chr(i) for i in range(97, 123)]
    urlShort = ""
    for i in range(random.randrange(3, 6)):
        urlShort += random.choice(opt)
    return urlShort

@app.route("/health", methods=['GET'])
def health():
    try:
        cursor.execute("SELECT * FROM url")
        return jsonify({"STATUS":"DB healthy"}), 200
    except Exception as e:
        return jsonify({"ERROR":str(e)}), 500
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port="6789", debug=True)