from flask import Flask, render_template, request, redirect, url_for, session
from authlib.integrations.flask_client import OAuth
import os

app = Flask(__name__)

app.secret_key = "omakase-uwu-secret-key"

oauth = OAuth(app)

google = oauth.register(
    name="google",

    client_id=os.environ.get("GOOGLE_CLIENT_ID"),

    client_secret=os.environ.get("GOOGLE_CLIENT_SECRET"),

    server_metadata_url=
    "https://accounts.google.com/.well-known/openid-configuration",

    client_kwargs={
        "scope": "openid email profile"
    }
)


# =========================
# หน้าแรก
# =========================

@app.route("/")
def home():

    if "user" in session:
        return redirect(url_for("booking"))

    return render_template("index.html")


# =========================
# เลือก Email / Google
# =========================

@app.route("/login-method", methods=["POST"])
def login_method():

    method = request.form.get("method")

    if method == "email":

        return redirect(url_for("email_login"))

    elif method == "google":

        redirect_uri = url_for(
            "google_callback",
            _external=True
        )

        return google.authorize_redirect(
            redirect_uri
        )

    else:

        return "กรุณาเลือกวิธีเข้าสู่ระบบ"


# =========================
# Email
# =========================

@app.route("/email")
def email_login():

    return render_template("email.html")


@app.route("/email-login", methods=["POST"])
def email_login_process():

    email = request.form.get("email")
    password = request.form.get("password")

    if email == "":

        return render_template(
            "email.html",
            error="กรุณากรอก Email"
        )

    elif password == "":

        return render_template(
            "email.html",
            error="กรุณากรอกรหัสผ่าน"
        )

    else:

        session["user"] = email

        return redirect(
            url_for("booking")
        )


# =========================
# Google
# =========================

@app.route("/google/callback")
def google_callback():

    try:

        token = google.authorize_access_token()

        user_info = token.get("userinfo")

        if user_info:

            session["user"] = user_info["email"]

            return redirect(
                url_for("booking")
            )

        elif user_info is None:

            return "ไม่สามารถรับข้อมูลจาก Google ได้"

        else:

            return "Google Login ไม่สำเร็จ"

    except Exception as error:

        return f"Google Login ไม่สำเร็จ: {error}"


# =========================
# หน้าจอง
# =========================

@app.route("/booking")
def booking():

    if "user" not in session:

        return redirect(
            url_for("home")
        )

    return render_template(
        "booking.html",
        user=session["user"]
    )


# =========================
# ยืนยันการจอง
# =========================

@app.route("/confirm-booking", methods=["POST"])
def confirm_booking():

    if "user" not in session:

        return redirect(
            url_for("home")
        )

    name = request.form.get("name")
    date = request.form.get("date")
    time = request.form.get("time")
    people = request.form.get("people")

    if name == "":

        return render_template(
            "booking.html",
            error="กรุณากรอกชื่อผู้จอง",
            user=session["user"]
        )

    elif date == "":

        return render_template(
            "booking.html",
            error="กรุณากรอกวันที่",
            user=session["user"]
        )

    elif time == "":

        return render_template(
            "booking.html",
            error="กรุณากรอกเวลา",
            user=session["user"]
        )

    elif people == "":

        return render_template(
            "booking.html",
            error="กรุณากรอกจำนวนคน",
            user=session["user"]
        )

    elif int(people) <= 0:

        return render_template(
            "booking.html",
            error="จำนวนคนต้องมากกว่า 0 คน",
            user=session["user"]
        )

    elif int(people) > 20:

        return render_template(
            "booking.html",
            error="จองได้สูงสุด 20 คน",
            user=session["user"]
        )

    else:

        booking_data = {
            "name": name,
            "date": date,
            "time": time,
            "people": people,
            "email": session["user"]
        }

        return render_template(
            "success.html",
            booking=booking_data
        )


# =========================
# Logout
# =========================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("home")
    )


if __name__ == "__main__":

    app.run(debug=True)