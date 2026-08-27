import os
import json
from datetime import datetime

from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    request,
    flash,
    session,
    send_file
)

from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user
)

from werkzeug.utils import secure_filename

from PIL import Image, ImageDraw, ImageFont
from openpyxl import Workbook

from database import (
    db,
    Customer,
    Wishlist,
    Enquiry,
    Order,
    initialize_database
)

from werkzeug.security import generate_password_hash, check_password_hash

# ===================================================
# FLASK APP CONFIGURATION
# ===================================================

app = Flask(__name__)


# ===================================================
# SECRET KEY
# ===================================================

app.config["SECRET_KEY"] = "lokeshwari-secret-key"


# ===================================================
# DATABASE CONFIGURATION
# ===================================================

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///lokeshwari.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


# ===================================================
# SESSION SECURITY
# ===================================================

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"


# ===================================================
# LANGUAGE SUPPORT
# ===================================================

LANGUAGES = ["en", "te"]


def get_language():
    return session.get("lang", "en")


# ===================================================
# FOLDERS
# ===================================================

UPLOAD_FOLDER = os.path.join("static", "images")
VIDEO_FOLDER = os.path.join("static", "videos")
DATA_FOLDER = "data"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(VIDEO_FOLDER, exist_ok=True)
os.makedirs(DATA_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["VIDEO_FOLDER"] = VIDEO_FOLDER


# ===================================================
# JSON FILES
# ===================================================

DATA_FILE = os.path.join(DATA_FOLDER, "designs.json")
ENQUIRY_FILE = os.path.join(DATA_FOLDER, "enquiries.json")
ORDER_FILE = os.path.join(DATA_FOLDER, "orders.json")


# ===================================================
# ALLOWED FILE TYPES
# ===================================================

ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg"
}

ALLOWED_VIDEO_EXTENSIONS = {
    "mp4",
    "mov",
    "webm"
}


# ===================================================
# DATABASE INITIALIZATION
# ===================================================

db.init_app(app)


# ===================================================
# LOGIN MANAGER
# ===================================================

login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "customer_login"


# ===================================================
# ADMIN CREDENTIALS
# ===================================================

ADMIN_USERNAME = "lokeshwari"
ADMIN_PASSWORD = "admin123"


# ===================================================
# USER CLASS
# ===================================================

class User(UserMixin):

    def __init__(
        self,
        user_id,
        name="",
        email="",
        phone="",
        role="customer"
    ):

        self.id = str(user_id)
        self.name = name
        self.email = email
        self.phone = phone
        self.role = role


# ===================================================
# LOAD LOGGED-IN USER
# ===================================================


@login_manager.user_loader
def load_user(user_id):

    # -----------------------------------------------
    # CUSTOMER
    # -----------------------------------------------

    try:

        customer_id = int(user_id)

        customer = db.session.get(
            Customer,
            customer_id
        )

        if customer:
            return customer

    except (
        ValueError,
        TypeError
    ):

        pass


    # -----------------------------------------------
    # ADMIN
    # -----------------------------------------------

    if user_id == "admin":

        return User(
            user_id="admin",
            name="Administrator",
            email="",
            phone="",
            role="admin"
        )


    return None

# ===================================================
# HELPER FUNCTIONS
# ===================================================

def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


def allowed_video(filename):

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_VIDEO_EXTENSIONS
    )


# ===================================================
# LOAD DESIGNS
# ===================================================

def load_designs():

    if not os.path.exists(DATA_FILE):
        return []

    try:

        with open(
            DATA_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception:

        return []


# ===================================================
# SAVE DESIGNS
# ===================================================

def save_designs(designs):

    with open(
        DATA_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            designs,
            file,
            indent=4,
            ensure_ascii=False
        )


# ===================================================
# LOAD ENQUIRIES
# ===================================================

def load_enquiries():

    if not os.path.exists(ENQUIRY_FILE):
        return []

    try:

        with open(
            ENQUIRY_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception:

        return []


# ===================================================
# SAVE ENQUIRIES
# ===================================================

def save_enquiries(enquiries):

    with open(
        ENQUIRY_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            enquiries,
            file,
            indent=4,
            ensure_ascii=False
        )


# ===================================================
# LOAD ORDERS
# ===================================================

def load_orders():

    if not os.path.exists(ORDER_FILE):
        return []

    try:

        with open(
            ORDER_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception:

        return []


# ===================================================
# SAVE ORDERS
# ===================================================

def save_orders(orders):

    with open(
        ORDER_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            orders,
            file,
            indent=4,
            ensure_ascii=False
        )


# ===================================================
# WATERMARK FUNCTION
# ===================================================

def add_watermark(image_path, text):

    image = Image.open(
        image_path
    ).convert("RGBA")

    draw = ImageDraw.Draw(image)

    font_size = max(
        30,
        image.width // 18
    )

    try:

        font = ImageFont.truetype(
            "arial.ttf",
            font_size
        )

    except Exception:

        font = ImageFont.load_default()

    bbox = draw.textbbox(
        (0, 0),
        text,
        font=font
    )

    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = image.width - text_width - 20
    y = image.height - text_height - 20

    # Shadow

    draw.text(
        (x + 2, y + 2),
        text,
        fill=(0, 0, 0, 255),
        font=font
    )

    # Main text

    draw.text(
        (x, y),
        text,
        fill=(255, 255, 255, 255),
        font=font
    )

    image.convert("RGB").save(
        image_path,
        quality=95
    )


# ===================================================
# INITIALIZE JSON FILES
# ===================================================

if not os.path.exists(ENQUIRY_FILE):
    save_enquiries([])

if not os.path.exists(ORDER_FILE):
    save_orders([])


# ===================================================
# DEFAULT DESIGNS
# ===================================================

if not os.path.exists(DATA_FILE):

    default_designs = [

        {
            "code": "BL-101",
            "title": "Floral Bridal Blouse Design",
            "category": "Bridal",
            "description": (
                "Beautiful floral embroidery suitable "
                "for bridal blouses."
            ),
            "price_min": "0",
            "price_max": "0",
            "image": "images/BL-101.jpg",
            "video": ""
        },

        {
            "code": "BL-102",
            "title": "Elegant Neck Embroidery",
            "category": "Neck Design",
            "description": (
                "Elegant neck embroidery for "
                "party wear blouses."
            ),
            "price_min": "0",
            "price_max": "0",
            "image": "images/BL-102.jpg",
            "video": ""
        }

    ]

    save_designs(default_designs)


# ===================================================
# LANGUAGE SWITCH
# ===================================================

@app.route("/set-language/<lang>")
def set_language(lang):

    if lang in LANGUAGES:
        session["lang"] = lang

    return redirect(
        request.referrer
        or url_for("home")
    )


# ===================================================
# HOME PAGE
# ===================================================

@app.route("/")
def home():

    lang = get_language()

    designs = load_designs()

    featured_designs = designs[:6]

    if lang == "te":

        return render_template(
            "te/index.html",
            lang=lang,
            featured_designs=featured_designs
        )

    return render_template(
        "index.html",
        lang=lang,
        featured_designs=featured_designs
    )


# ===================================================
# CUSTOMER REGISTRATION
# ===================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if (
        current_user.is_authenticated
        and current_user.role == "customer"
    ):

        return redirect(
            url_for("customer_dashboard")
        )

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        # -------------------------------------------
        # VALIDATION
        # -------------------------------------------

        if not name:

            flash(
                "Please enter your name.",
                "danger"
            )

            return redirect(
                url_for("register")
            )

        if not email:

            flash(
                "Please enter your email.",
                "danger"
            )

            return redirect(
                url_for("register")
            )

        if not phone:

            flash(
                "Please enter your phone number.",
                "danger"
            )

            return redirect(
                url_for("register")
            )

        if len(phone) < 10:

            flash(
                "Please enter a valid phone number.",
                "danger"
            )

            return redirect(
                url_for("register")
            )

        if not password or len(password) < 6:

            flash(
                "Password must contain at least 6 characters.",
                "danger"
            )

            return redirect(
                url_for("register")
            )

        if password != confirm_password:

            flash(
                "Passwords do not match.",
                "danger"
            )

            return redirect(
                url_for("register")
            )

        # -------------------------------------------
        # CHECK EXISTING EMAIL
        # -------------------------------------------

        existing_email = Customer.query.filter_by(
            email=email
        ).first()

        if existing_email:

            flash(
                "An account already exists with this email. Please login.",
                "warning"
            )

            return redirect(
                url_for("customer_login")
            )

        # -------------------------------------------
        # CHECK EXISTING PHONE
        # -------------------------------------------

        existing_phone = Customer.query.filter_by(
            phone=phone
        ).first()

        if existing_phone:

            flash(
                "An account already exists with this phone number. Please login.",
                "warning"
            )

            return redirect(
                url_for("customer_login")
            )

        # -------------------------------------------
        # CREATE CUSTOMER
        # -------------------------------------------

        new_customer = Customer(
            name=name,
            email=email,
            phone=phone
        )

        # IMPORTANT:
        # Customer model uses password_hash.
        # Do not pass password= to Customer.

        new_customer.set_password(
            password
        )

        try:

            db.session.add(
                new_customer
            )

            db.session.commit()

        except Exception as error:

            db.session.rollback()

            flash(
                f"Registration failed: {str(error)}",
                "danger"
            )

            return redirect(
                url_for("register")
            )

        flash(
            "Registration successful! Please login.",
            "success"
        )

        return redirect(
            url_for("customer_login")
        )

    return render_template(
        "register.html"
    )


# ===================================================
# CUSTOMER LOGIN
# ===================================================

@app.route("/login", methods=["GET", "POST"])
def customer_login():

    # -----------------------------------------------
    # ALREADY LOGGED IN
    # -----------------------------------------------

    if current_user.is_authenticated:

        # Customer is already logged in
        if isinstance(current_user, Customer):
            return redirect(
                url_for("customer_dashboard")
            )

        # If your admin user has a role attribute
        if getattr(current_user, "role", None) == "admin":
            return redirect(
                url_for("admin_dashboard")
            )

        return redirect(
            url_for("home")
        )


    # -----------------------------------------------
    # LOGIN FORM SUBMISSION
    # -----------------------------------------------

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )


        # -------------------------------------------
        # VALIDATION
        # -------------------------------------------

        if not email or not password:

            flash(
                "Please enter your email and password.",
                "danger"
            )

            return redirect(
                url_for("customer_login")
            )


        # -------------------------------------------
        # FIND CUSTOMER
        # -------------------------------------------

        customer = Customer.query.filter_by(
            email=email
        ).first()


        if not customer:

            flash(
                "Invalid email or password.",
                "danger"
            )

            return redirect(
                url_for("customer_login")
            )


        # -------------------------------------------
        # CHECK PASSWORD
        # -------------------------------------------

        if not customer.check_password(password):

            flash(
                "Invalid email or password.",
                "danger"
            )

            return redirect(
                url_for("customer_login")
            )


        # -------------------------------------------
        # LOGIN CUSTOMER
        # IMPORTANT:
        # Customer itself is UserMixin
        # Do NOT create another User object
        # -------------------------------------------

        login_user(customer)


        flash(
            "Login successful!",
            "success"
        )


        return redirect(
            url_for("customer_dashboard")
        )


    # -----------------------------------------------
    # GET REQUEST
    # -----------------------------------------------

    return render_template(
        "login.html"
    )


# ===================================================
# CUSTOMER LOGOUT
# ===================================================

@app.route("/logout")
@login_required
def customer_logout():

    logout_user()


    flash(
        "You have been logged out successfully.",
        "success"
    )


    return redirect(
        url_for("home")
    )


# ===================================================
# CUSTOMER DASHBOARD
# ===================================================

@app.route("/dashboard")
@login_required
def customer_dashboard():

    # -----------------------------------------------
    # CURRENT LOGGED-IN CUSTOMER
    # -----------------------------------------------

    customer_id = current_user.id


    # -----------------------------------------------
    # CUSTOMER ENQUIRIES
    # -----------------------------------------------

    all_enquiries = load_enquiries()


    customer_enquiries = [

        enquiry

        for enquiry in all_enquiries

        if (

            str(
                enquiry.get(
                    "customer_id",
                    ""
                )
            )
            == str(customer_id)

        )

        or (

            str(
                enquiry.get(
                    "customer_email",
                    ""
                )
            ).strip().lower()

            ==

            str(
                current_user.email or ""
            ).strip().lower()

        )

        or (

            str(
                enquiry.get(
                    "phone",
                    ""
                )
            ).strip()

            ==

            str(
                current_user.phone or ""
            ).strip()

        )

    ]


    # -----------------------------------------------
    # CUSTOMER ENQUIRY IDS
    # -----------------------------------------------

    customer_enquiry_ids = [

        enquiry.get("id")

        for enquiry in customer_enquiries

    ]


    # -----------------------------------------------
    # CUSTOMER ORDERS
    # -----------------------------------------------

    all_orders = load_orders()


    customer_orders = [

        order

        for order in all_orders

        if (

            str(
                order.get(
                    "customer_id",
                    ""
                )
            )
            == str(customer_id)

        )

        or (

            order.get(
                "enquiry_id"
            )

            in

            customer_enquiry_ids

        )

        or (

            str(
                order.get(
                    "customer_email",
                    ""
                )
            ).strip().lower()

            ==

            str(
                current_user.email or ""
            ).strip().lower()

        )

        or (

            str(
                order.get(
                    "phone",
                    ""
                )
            ).strip()

            ==

            str(
                current_user.phone or ""
            ).strip()

        )

    ]


    # -----------------------------------------------
    # WISHLIST COUNT
    # -----------------------------------------------

    wishlist_count = Wishlist.query.filter_by(
        customer_id=customer_id
    ).count()


    # -----------------------------------------------
    # DELIVERED ORDERS
    # -----------------------------------------------

    delivered_count = len(

        [

            order

            for order in customer_orders

            if str(
                order.get(
                    "status",
                    ""
                )
            ).strip().lower()

            == "delivered"

        ]

    )


    # -----------------------------------------------
    # OPEN DASHBOARD
    # -----------------------------------------------

    return render_template(

        "customer/dashboard.html",

        enquiries=customer_enquiries,

        orders=customer_orders,

        wishlist_count=wishlist_count,

        delivered_count=delivered_count

    )

# ===================================================
# GALLERY
# ===================================================

@app.route("/gallery")
def gallery():

    designs = load_designs()

    search = request.args.get(
        "search",
        ""
    ).lower()

    category = request.args.get(
        "category",
        ""
    )

    if search:

        designs = [

            design

            for design in designs

            if (

                search
                in design.get(
                    "title",
                    ""
                ).lower()

                or

                search
                in design.get(
                    "description",
                    ""
                ).lower()

            )

        ]

    if category:

        designs = [

            design

            for design in designs

            if design.get("category")
            == category

        ]

    all_designs = load_designs()

    categories = sorted(
        list(
            set(

                design.get(
                    "category",
                    ""
                )

                for design in all_designs

            )
        )
    )

    return render_template(

        "gallery.html",

        designs=designs,

        categories=categories,

        search=search,

        selected_category=category

    )


# ===================================================
# DESIGN DETAIL
# ===================================================

@app.route("/design/<code>")
def design_detail(code):

    designs = load_designs()

    design = next(

        (

            design

            for design in designs

            if design.get("code")
            == code

        ),

        None

    )

    if design is None:

        return "Design not found", 404

    is_wishlisted = False

    if (
        current_user.is_authenticated
        and current_user.role == "customer"
    ):

        customer_id = int(
            current_user.id.replace(
                "customer_",
                ""
            )
        )

        is_wishlisted = Wishlist.query.filter_by(
            customer_id=customer_id,
            design_code=code
        ).first() is not None

    return render_template(

        "design_detail.html",

        design=design,

        is_wishlisted=is_wishlisted

    )


# ===================================================
# ADD TO WISHLIST
# ===================================================

@app.route("/wishlist/add/<code>")
@login_required
def add_to_wishlist(code):

    if current_user.role != "customer":

        flash(
            "Only customers can add designs to wishlist.",
            "danger"
        )

        return redirect(
            url_for("home")
        )

    designs = load_designs()

    design = next(
        (
            item
            for item in designs
            if item.get("code") == code
        ),
        None
    )

    if design is None:

        flash(
            "Design not found.",
            "danger"
        )

        return redirect(
            url_for("gallery")
        )

    customer_id = int(
        current_user.id.replace(
            "customer_",
            ""
        )
    )

    existing = Wishlist.query.filter_by(
        customer_id=customer_id,
        design_code=code
    ).first()

    if existing:

        flash(
            "This design is already in your wishlist.",
            "info"
        )

    else:

        wishlist_item = Wishlist(
            customer_id=customer_id,
            design_code=code
        )

        db.session.add(
            wishlist_item
        )

        db.session.commit()

        flash(
            "Design added to your wishlist!",
            "success"
        )

    return redirect(
        url_for(
            "design_detail",
            code=code
        )
    )


# ===================================================
# REMOVE FROM WISHLIST
# ===================================================

@app.route("/wishlist/remove/<code>")
@login_required
def remove_from_wishlist(code):

    if current_user.role != "customer":

        return redirect(
            url_for("home")
        )

    customer_id = int(
        current_user.id.replace(
            "customer_",
            ""
        )
    )

    wishlist_item = Wishlist.query.filter_by(
        customer_id=customer_id,
        design_code=code
    ).first()

    if wishlist_item:

        db.session.delete(
            wishlist_item
        )

        db.session.commit()

        flash(
            "Design removed from wishlist.",
            "success"
        )

    return redirect(
        url_for("wishlist")
    )


# ============================================
# CUSTOMER WISHLIST
# ============================================

@app.route("/wishlist")
@login_required
def wishlist():

    wishlist_items = Wishlist.query.filter_by(
        customer_id=current_user.id
    ).order_by(
        Wishlist.created_at.desc()
    ).all()

    return render_template(
        "customer/wishlist.html",
        wishlist_items=wishlist_items
    )


# ===================================================
# CONTACT PAGE
# ===================================================

@app.route("/contact")
def contact():

    return render_template(
        "contact.html"
    )


# ===================================================
# TRACK ORDER
# ===================================================

@app.route(
    "/track-order",
    methods=["GET", "POST"]
)
def track_order():

    enquiry = None
    order = None

    if request.method == "POST":

        enquiry_id = request.form.get(
            "enquiry_id",
            ""
        ).strip().upper()

        if enquiry_id.startswith("ENQ-"):

            enquiry_id = enquiry_id.replace(
                "ENQ-",
                ""
            )

        try:

            enquiry_id = int(enquiry_id)

        except ValueError:

            enquiry_id = None

        enquiries = load_enquiries()
        orders = load_orders()

        if enquiry_id is not None:

            enquiry = next(

                (
                    item
                    for item in enquiries
                    if item.get("id") == enquiry_id
                ),

                None

            )

            if enquiry:

                order = next(

                    (
                        item
                        for item in orders
                        if item.get("enquiry_id")
                        == enquiry.get("id")
                    ),

                    None

                )

    return render_template(

        "track_order.html",

        enquiry=enquiry,

        order=order

    )


# ===================================================
# CUSTOMER ENQUIRY
# ===================================================

@app.route(
    "/enquiry/<code>",
    methods=["GET", "POST"]
)
def enquiry(code):

    designs = load_designs()

    design = next(

        (
            item
            for item in designs
            if item.get("code") == code
        ),

        None

    )

    if design is None:

        return "Design not found", 404

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        message = request.form.get(
            "message",
            ""
        ).strip()

        customer_id = None
        customer_email = ""

        if (
            current_user.is_authenticated
            and current_user.role == "customer"
        ):

            name = current_user.name
            phone = current_user.phone
            customer_email = current_user.email

            try:

                customer_id = int(
                    current_user.id.replace(
                        "customer_",
                        ""
                    )
                )

            except Exception:

                customer_id = None

        enquiries = load_enquiries()

        new_id = max(

            [
                item.get("id", 0)
                for item in enquiries
            ],

            default=0

        ) + 1

        new_enquiry = {

            "id": new_id,

            "customer_id": customer_id,

            "customer_email": customer_email,

            "design_code": design.get("code"),

            "design_title": design.get("title"),

            "name": name,

            "phone": phone,

            "message": message,

            "status": "New",

            "created_at": datetime.now().strftime(
                "%d-%m-%Y %I:%M %p"
            )

        }

        enquiries.append(
            new_enquiry
        )

        save_enquiries(
            enquiries
        )

        if (
            current_user.is_authenticated
            and current_user.role == "customer"
        ):

            flash(
                "Enquiry submitted successfully! "
                "You can track it in My Dashboard.",
                "success"
            )

            return redirect(
                url_for(
                    "customer_dashboard"
                )
            )

        flash(
            f"Enquiry submitted successfully! "
            f"Your Enquiry ID is ENQ-{new_id:04d}",
            "success"
        )

        return redirect(
            url_for(
                "design_detail",
                code=code
            )
        )

    return render_template(
        "enquiry.html",
        design=design
    )


# ===================================================
# ADMIN LOGIN
# ===================================================

@app.route(
    "/admin/login",
    methods=["GET", "POST"]
)
def admin_login():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        )

        password = request.form.get(
            "password",
            ""
        )

        if (
            username == ADMIN_USERNAME
            and password == ADMIN_PASSWORD
        ):

            user = User(
                user_id="admin",
                name="Lokeshwari Admin",
                role="admin"
            )

            login_user(user)

            return redirect(
                url_for(
                    "admin_dashboard"
                )
            )

        flash(
            "Invalid username or password.",
            "danger"
        )

    return render_template(
        "admin/login.html"
    )


# ===================================================
# ADMIN LOGOUT
# ===================================================

@app.route("/admin/logout")
@login_required
def admin_logout():

    if current_user.role != "admin":

        return redirect(
            url_for("home")
        )

    logout_user()

    return redirect(
        url_for(
            "admin_login"
        )
    )


# ===================================================
# ADMIN DASHBOARD
# ===================================================

@app.route("/admin/dashboard")
@login_required
def admin_dashboard():

    if current_user.role != "admin":

        return redirect(
            url_for("customer_dashboard")
        )

    designs = load_designs()
    orders = load_orders()

    total_designs = len(
        designs
    )

    bridal_count = len([
        design
        for design in designs
        if design.get("category") == "Bridal"
    ])

    neck_count = len([
        design
        for design in designs
        if design.get("category") == "Neck Design"
    ])

    sleeve_count = len([
        design
        for design in designs
        if design.get("category") == "Sleeve Design"
    ])

    border_count = len([
        design
        for design in designs
        if design.get("category") == "Border Design"
    ])

    today = datetime.now().strftime(
        "%d-%m-%Y"
    )

    today_orders = len([
        order
        for order in orders
        if order.get(
            "created_at",
            ""
        ).startswith(today)
    ])

    delivered_orders = len([
        order
        for order in orders
        if order.get("status") == "Delivered"
    ])

    total_advance = sum([
        float(
            order.get(
                "advance_amount"
            ) or 0
        )
        for order in orders
    ])

    total_balance = sum([
        float(
            order.get(
                "balance_amount"
            ) or 0
        )
        for order in orders
    ])

    return render_template(

        "admin/dashboard.html",

        designs=designs,

        total_designs=total_designs,

        bridal_count=bridal_count,

        neck_count=neck_count,

        sleeve_count=sleeve_count,

        border_count=border_count,

        today_orders=today_orders,

        delivered_orders=delivered_orders,

        total_advance=total_advance,

        total_balance=total_balance

    )


# ===================================================
# ADMIN ENQUIRIES
# ===================================================

@app.route("/admin/enquiries")
@login_required
def admin_enquiries():

    if current_user.role != "admin":

        return redirect(
            url_for("home")
        )

    enquiries = load_enquiries()

    return render_template(
        "admin/enquiries.html",
        enquiries=enquiries
    )


# ===================================================
# UPDATE ENQUIRY STATUS
# ===================================================

@app.route(
    "/admin/enquiry-status/"
    "<int:enquiry_id>/<status>"
)
@login_required
def update_enquiry_status(
    enquiry_id,
    status
):

    if current_user.role != "admin":

        return redirect(
            url_for("home")
        )

    enquiries = load_enquiries()

    for item in enquiries:

        if item.get("id") == enquiry_id:

            item["status"] = status

            break

    save_enquiries(
        enquiries
    )

    flash(
        "Enquiry status updated!",
        "success"
    )

    return redirect(
        url_for(
            "admin_enquiries"
        )
    )


# ===================================================
# DELETE ENQUIRY
# ===================================================

@app.route(
    "/admin/delete-enquiry/"
    "<int:enquiry_id>"
)
@login_required
def delete_enquiry(enquiry_id):

    if current_user.role != "admin":

        return redirect(
            url_for("home")
        )

    enquiries = load_enquiries()

    updated_enquiries = [

        enquiry

        for enquiry in enquiries

        if enquiry.get("id")
        != enquiry_id

    ]

    save_enquiries(
        updated_enquiries
    )

    flash(
        "Enquiry deleted successfully!",
        "success"
    )

    return redirect(
        url_for(
            "admin_enquiries"
        )
    )


# ===================================================
# CREATE ORDER FROM ENQUIRY
# ===================================================

@app.route(
    "/admin/create-order/"
    "<int:enquiry_id>"
)
@login_required
def create_order(enquiry_id):

    if current_user.role != "admin":

        return redirect(
            url_for("home")
        )

    enquiries = load_enquiries()
    orders = load_orders()

    enquiry = next(

        (
            item
            for item in enquiries
            if item.get("id") == enquiry_id
        ),

        None

    )

    if enquiry is None:

        flash(
            "Enquiry not found.",
            "danger"
        )

        return redirect(
            url_for(
                "admin_enquiries"
            )
        )

    existing_order = next(

        (
            item
            for item in orders
            if item.get("enquiry_id")
            == enquiry_id
        ),

        None

    )

    if existing_order:

        flash(
            "Order already created for this enquiry.",
            "warning"
        )

        return redirect(
            url_for(
                "admin_orders"
            )
        )

    new_order_id = max(

        [
            item.get("id", 0)
            for item in orders
        ],

        default=0

    ) + 1

    new_order = {

        "id": new_order_id,

        "enquiry_id": enquiry_id,

        "customer_id": enquiry.get(
            "customer_id"
        ),

        "customer_email": enquiry.get(
            "customer_email",
            ""
        ),

        "name": enquiry.get("name"),

        "phone": enquiry.get("phone"),

        "design_code": enquiry.get(
            "design_code"
        ),

        "design_title": enquiry.get(
            "design_title"
        ),

        "blouse_size": "",

        "delivery_date": "",

        "advance_amount": "",

        "balance_amount": "",

        "status": "In Progress",

        "created_at": datetime.now().strftime(
            "%d-%m-%Y %I:%M %p"
        )

    }

    orders.append(
        new_order
    )

    save_orders(
        orders
    )

    enquiry["status"] = "Ordered"

    save_enquiries(
        enquiries
    )

    flash(
        "Order created successfully!",
        "success"
    )

    return redirect(
        url_for(
            "admin_orders"
        )
    )


# ===================================================
# ADMIN ORDERS
# ===================================================

@app.route("/admin/orders")
@login_required
def admin_orders():

    if current_user.role != "admin":

        return redirect(
            url_for("home")
        )

    orders = load_orders()

    search = request.args.get(
        "search",
        ""
    ).strip().lower()

    status = request.args.get(
        "status",
        ""
    ).strip()

    filtered_orders = orders

    if search:

        filtered_orders = [

            order

            for order in filtered_orders

            if (

                search
                in order.get(
                    "name",
                    ""
                ).lower()

                or

                search
                in order.get(
                    "phone",
                    ""
                ).lower()

                or

                search
                in order.get(
                    "design_code",
                    ""
                ).lower()

            )

        ]

    if status:

        filtered_orders = [

            order

            for order in filtered_orders

            if order.get("status")
            == status

        ]

    return render_template(

        "admin/orders.html",

        orders=filtered_orders,

        search=search,

        status=status

    )


# ===================================================
# UPDATE ORDER STATUS
# ===================================================

@app.route(
    "/admin/order-status/"
    "<int:order_id>/<status>"
)
@login_required
def update_order_status(
    order_id,
    status
):

    if current_user.role != "admin":

        return redirect(
            url_for("home")
        )

    orders = load_orders()

    for order in orders:

        if order.get("id") == order_id:

            order["status"] = status

            break

    save_orders(
        orders
    )

    flash(
        "Order status updated!",
        "success"
    )

    return redirect(
        url_for(
            "admin_orders"
        )
    )


# ===================================================
# EDIT ORDER
# ===================================================

@app.route(
    "/admin/edit-order/<int:order_id>",
    methods=["GET", "POST"]
)
@login_required
def edit_order(order_id):

    if current_user.role != "admin":

        return redirect(
            url_for("home")
        )

    orders = load_orders()

    order = next(

        (
            item
            for item in orders
            if item.get("id") == order_id
        ),

        None

    )

    if order is None:

        flash(
            "Order not found.",
            "danger"
        )

        return redirect(
            url_for("admin_orders")
        )

    if request.method == "POST":

        order["blouse_size"] = request.form.get(
            "blouse_size",
            ""
        ).strip()

        order["delivery_date"] = request.form.get(
            "delivery_date",
            ""
        ).strip()

        order["advance_amount"] = request.form.get(
            "advance_amount",
            ""
        ).strip()

        order["balance_amount"] = request.form.get(
            "balance_amount",
            ""
        ).strip()

        save_orders(
            orders
        )

        flash(
            "Order updated successfully!",
            "success"
        )

        return redirect(
            url_for("admin_orders")
        )

    return render_template(
        "admin/edit_order.html",
        order=order
    )


# ===================================================
# PRINT INVOICE
# ===================================================

@app.route(
    "/admin/invoice/<int:order_id>"
)
@login_required
def print_invoice(order_id):

    if current_user.role != "admin":

        return redirect(
            url_for("home")
        )

    orders = load_orders()

    order = next(

        (
            item
            for item in orders
            if item.get("id") == order_id
        ),

        None

    )

    if order is None:

        flash(
            "Order not found.",
            "danger"
        )

        return redirect(
            url_for("admin_orders")
        )

    return render_template(
        "admin/invoice.html",
        order=order
    )


# ===================================================
# DOWNLOAD ORDERS EXCEL
# ===================================================

@app.route("/admin/download-orders")
@login_required
def download_orders():

    if current_user.role != "admin":

        return redirect(
            url_for("home")
        )

    orders = load_orders()

    workbook = Workbook()

    worksheet = workbook.active

    worksheet.title = "Orders"

    headers = [

        "Order ID",
        "Date",
        "Customer",
        "Phone",
        "Design Code",
        "Design Title",
        "Size",
        "Delivery Date",
        "Advance Amount",
        "Balance Amount",
        "Status"

    ]

    worksheet.append(
        headers
    )

    for order in orders:

        worksheet.append([

            order.get("id"),

            order.get("created_at"),

            order.get("name"),

            order.get("phone"),

            order.get("design_code"),

            order.get("design_title"),

            order.get("blouse_size"),

            order.get("delivery_date"),

            order.get("advance_amount"),

            order.get("balance_amount"),

            order.get("status")

        ])

    for column in worksheet.columns:

        max_length = 0

        column_letter = column[0].column_letter

        for cell in column:

            value = (
                str(cell.value)
                if cell.value
                else ""
            )

            if len(value) > max_length:

                max_length = len(value)

        worksheet.column_dimensions[
            column_letter
        ].width = max_length + 4

    filename = "orders_report.xlsx"

    workbook.save(
        filename
    )

    return send_file(
        filename,
        as_attachment=True
    )


# ===================================================
# ADD DESIGN
# ===================================================

@app.route(
    "/admin/add-design",
    methods=["GET", "POST"]
)
@login_required
def add_design():

    if current_user.role != "admin":

        return redirect(
            url_for("home")
        )

    if request.method == "POST":

        code = request.form.get(
            "code",
            ""
        ).strip()

        title = request.form.get(
            "title",
            ""
        ).strip()

        category = request.form.get(
            "category",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        file = request.files.get(
            "image"
        )

        if not file or file.filename == "":

            flash(
                "Please select an image.",
                "danger"
            )

            return redirect(
                request.url
            )

        if not allowed_file(
            file.filename
        ):

            flash(
                "Only JPG, JPEG and PNG files are allowed.",
                "danger"
            )

            return redirect(
                request.url
            )

        designs = load_designs()

        existing = next(

            (
                design
                for design in designs
                if design.get("code") == code
            ),

            None

        )

        if existing:

            flash(
                "Design code already exists.",
                "danger"
            )

            return redirect(
                request.url
            )

        # -----------------------------------------------
        # SAVE IMAGE
        # -----------------------------------------------

        filename = secure_filename(
            file.filename
        )

        save_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            filename
        )

        file.save(
            save_path
        )

        watermark_text = (
            f"LOKESHWARI EMBROIDERY | {code}"
        )

        add_watermark(
            save_path,
            watermark_text
        )

        image_path = (
            f"images/{filename}"
        )

        # -----------------------------------------------
        # OPTIONAL VIDEO
        # -----------------------------------------------

        video_file = request.files.get(
            "video"
        )

        video_path = ""

        if (
            video_file
            and video_file.filename != ""
        ):

            if not allowed_video(
                video_file.filename
            ):

                flash(
                    "Only MP4, MOV and WEBM videos are allowed.",
                    "danger"
                )

                return redirect(
                    request.url
                )

            video_filename = secure_filename(
                video_file.filename
            )

            video_save_path = os.path.join(
                app.config["VIDEO_FOLDER"],
                video_filename
            )

            video_file.save(
                video_save_path
            )

            video_path = (
                f"videos/{video_filename}"
            )

        new_design = {

            "code": code,

            "title": title,

            "category": category,

            "description": description,

            "price_min": request.form.get(
                "price_min",
                "0"
            ),

            "price_max": request.form.get(
                "price_max",
                "0"
            ),

            "image": image_path,

            "video": video_path

        }

        designs.append(
            new_design
        )

        save_designs(
            designs
        )

        flash(
            "Service / Design added successfully!",
            "success"
        )

        return redirect(
            url_for(
                "admin_dashboard"
            )
        )

    return render_template(
        "admin/add_design.html"
    )


# ===================================================
# EDIT DESIGN
# ===================================================

@app.route(
    "/admin/edit-design/<code>",
    methods=["GET", "POST"]
)
@login_required
def edit_design(code):

    if current_user.role != "admin":

        return redirect(
            url_for("home")
        )

    designs = load_designs()

    design = next(

        (
            item
            for item in designs
            if item.get("code") == code
        ),

        None

    )

    if design is None:

        flash(
            "Design not found.",
            "danger"
        )

        return redirect(
            url_for("admin_dashboard")
        )

    if request.method == "POST":

        design["title"] = request.form.get(
            "title",
            ""
        ).strip()

        design["category"] = request.form.get(
            "category",
            ""
        ).strip()

        design["description"] = request.form.get(
            "description",
            ""
        ).strip()

        design["price_min"] = request.form.get(
            "price_min",
            "0"
        )

        design["price_max"] = request.form.get(
            "price_max",
            "0"
        )

        # -----------------------------------------------
        # UPDATE IMAGE
        # -----------------------------------------------

        file = request.files.get(
            "image"
        )

        if file and file.filename != "":

            if not allowed_file(
                file.filename
            ):

                flash(
                    "Only JPG, JPEG and PNG files are allowed.",
                    "danger"
                )

                return redirect(
                    request.url
                )

            old_image = design.get(
                "image",
                ""
            )

            if old_image:

                old_image_path = os.path.join(
                    "static",
                    old_image
                )

                if os.path.exists(
                    old_image_path
                ):

                    try:

                        os.remove(
                            old_image_path
                        )

                    except Exception:

                        pass

            filename = secure_filename(
                file.filename
            )

            save_path = os.path.join(
                app.config["UPLOAD_FOLDER"],
                filename
            )

            file.save(
                save_path
            )

            add_watermark(
                save_path,
                f"LOKESHWARI EMBROIDERY | {code}"
            )

            design["image"] = (
                f"images/{filename}"
            )

        # -----------------------------------------------
        # UPDATE VIDEO
        # -----------------------------------------------

        video_file = request.files.get(
            "video"
        )

        if (
            video_file
            and video_file.filename != ""
        ):

            if not allowed_video(
                video_file.filename
            ):

                flash(
                    "Only MP4, MOV and WEBM videos are allowed.",
                    "danger"
                )

                return redirect(
                    request.url
                )

            old_video = design.get(
                "video",
                ""
            )

            if old_video:

                old_video_path = os.path.join(
                    "static",
                    old_video
                )

                if os.path.exists(
                    old_video_path
                ):

                    try:

                        os.remove(
                            old_video_path
                        )

                    except Exception:

                        pass

            video_filename = secure_filename(
                video_file.filename
            )

            video_save_path = os.path.join(
                app.config["VIDEO_FOLDER"],
                video_filename
            )

            video_file.save(
                video_save_path
            )

            design["video"] = (
                f"videos/{video_filename}"
            )

        save_designs(
            designs
        )

        flash(
            "Design updated successfully!",
            "success"
        )

        return redirect(
            url_for("admin_dashboard")
        )

    return render_template(
        "admin/edit_design.html",
        design=design
    )


# ===================================================
# DELETE DESIGN
# ===================================================

@app.route(
    "/admin/delete-design/<code>"
)
@login_required
def delete_design(code):

    if current_user.role != "admin":

        return redirect(
            url_for("home")
        )

    designs = load_designs()

    design_to_delete = next(

        (
            item
            for item in designs
            if item.get("code") == code
        ),

        None

    )

    if design_to_delete is None:

        flash(
            "Design not found.",
            "danger"
        )

        return redirect(
            url_for("admin_dashboard")
        )

    # -----------------------------------------------
    # DELETE IMAGE
    # -----------------------------------------------

    image = design_to_delete.get(
        "image",
        ""
    )

    if image:

        image_path = os.path.join(
            "static",
            image
        )

        if os.path.exists(
            image_path
        ):

            try:

                os.remove(
                    image_path
                )

            except Exception:

                pass

    # -----------------------------------------------
    # DELETE VIDEO
    # -----------------------------------------------

    video = design_to_delete.get(
        "video",
        ""
    )

    if video:

        video_path = os.path.join(
            "static",
            video
        )

        if os.path.exists(
            video_path
        ):

            try:

                os.remove(
                    video_path
                )

            except Exception:

                pass

    updated_designs = [

        item

        for item in designs

        if item.get("code") != code

    ]

    save_designs(
        updated_designs
    )

    flash(
        "Design deleted successfully!",
        "success"
    )

    return redirect(
        url_for("admin_dashboard")
    )


# ===================================================
# INITIALIZE DATABASE TABLES
# ===================================================

with app.app_context():

    db.create_all()


# ===================================================
# RUN APPLICATION
# ===================================================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )