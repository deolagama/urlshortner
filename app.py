from flask import Flask, request, redirect, render_template, url_for, flash
from models import db, URL, Click
from utils import encode_base62
from config import Config
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="memory://"
)
limiter.init_app(app)

already_initialized = False
@app.before_request
def init_once():
    global already_initialized
    if not already_initialized:
        db.create_all()
        already_initialized = True

@app.route('/', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def index():
    if request.method == 'POST':
        original_url = request.form['url']
        new_url = URL(original=original_url, short="")  # Temporary value for short
        db.session.add(new_url)
        db.session.flush()  # This assigns new_url.id

        # Now generate and set the short URL
        new_url.short = encode_base62(new_url.id)

        db.session.commit()  # Commit with short filled in

        short_link = request.host_url + new_url.short
        return render_template("index.html", short_url=short_link)

    return render_template("index.html")


@app.route('/<short>')
def redirect_short(short):
    url = URL.query.filter_by(short=short).first_or_404()
    
    click = Click(url_id=url.id, ip_address=request.remote_addr)
    db.session.add(click)
    db.session.commit()

    return redirect(url.original)

if __name__ == "__main__":
    app.run(debug=True)
