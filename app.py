import os
import json
from datetime import datetime

from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    request,
    flash
)

from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user
)

from werkzeug.utils import secure_filename

from PIL import Image, ImageDraw, ImageFont
from openpyxl import Workbook
from flask import send_file


# ===================================================
# FLASK APP CONFIGURATION
# ===================================================

app = Flask(__name__)

app.config['SECRET_KEY'] = 'lokeshwari-secret-key'

app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

UPLOAD_FOLDER = os.path.join('static', 'images')

DATA_FILE = os.path.join('data', 'designs.json')
ENQUIRY_FILE = os.path.join('data', 'enquiries.json')
ORDER_FILE = os.path.join('data', 'orders.json')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('data', exist_ok=True)


# ===================================================
# LOGIN MANAGER
# ===================================================

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'


# ===================================================
# ADMIN CREDENTIALS
# ===================================================

ADMIN_USERNAME = 'lokeshwari'
ADMIN_PASSWORD = 'admin123'


# ===================================================
# USER CLASS
# ===================================================

class User(UserMixin):

    def __init__(self, user_id):
        self.id = user_id


@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


# ===================================================
# HELPER FUNCTIONS
# ===================================================

def allowed_file(filename):

    return (
        '.' in filename and
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def load_designs():

    if not os.path.exists(DATA_FILE):
        return []

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_designs(designs):

    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(designs, f, indent=4, ensure_ascii=False)


# ===================================================
# WATERMARK FUNCTION
# ===================================================

def add_watermark(image_path, text):

    image = Image.open(image_path).convert('RGBA')

    draw = ImageDraw.Draw(image)

    font_size = max(30, image.width // 18)

    try:
        font = ImageFont.truetype('arial.ttf', font_size)
    except:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)

    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = image.width - text_width - 20
    y = image.height - text_height - 20

    draw.text((x+2, y+2), text, fill=(0, 0, 0, 255), font=font)

    draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)

    image.convert('RGB').save(image_path, quality=95)


# ===================================================
# ENQUIRY HELPERS
# ===================================================

if not os.path.exists(ENQUIRY_FILE):

    with open(ENQUIRY_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f)


def load_enquiries():

    with open(ENQUIRY_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_enquiries(enquiries):

    with open(ENQUIRY_FILE, 'w', encoding='utf-8') as f:
        json.dump(enquiries, f, indent=4, ensure_ascii=False)


# ===================================================
# ORDER HELPERS
# ===================================================

if not os.path.exists(ORDER_FILE):

    with open(ORDER_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f)


def load_orders():

    with open(ORDER_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_orders(orders):

    with open(ORDER_FILE, 'w', encoding='utf-8') as f:
        json.dump(orders, f, indent=4, ensure_ascii=False)


# ===================================================
# DEFAULT DESIGNS
# ===================================================

if not os.path.exists(DATA_FILE):

    default_designs = [
        {
            'code': 'BL-101',
            'title': 'Floral Bridal Blouse Design',
            'category': 'Bridal',
            'description': 'Beautiful floral embroidery suitable for bridal blouses.',
            'image': 'images/BL-101.jpg'
        },
        {
            'code': 'BL-102',
            'title': 'Elegant Neck Embroidery',
            'category': 'Neck Design',
            'description': 'Elegant neck embroidery for party wear blouses.',
            'image': 'images/BL-102.jpg'
        }
    ]

    save_designs(default_designs)


# ===================================================
# PUBLIC ROUTES
# ===================================================

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/gallery')
def gallery():

    designs = load_designs()

    return render_template('gallery.html', designs=designs)


@app.route('/design/<code>')
def design_detail(code):

    designs = load_designs()

    design = next((d for d in designs if d['code'] == code), None)

    if design is None:
        return 'Design not found', 404

    return render_template('design_detail.html', design=design)


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/wishlist')
def wishlist():
    return render_template('wishlist.html')

# ===================================================
# CUSTOMER ENQUIRY
# ===================================================

@app.route('/enquiry/<code>', methods=['GET', 'POST'])
def enquiry(code):

    designs = load_designs()

    design = next((d for d in designs if d['code'] == code), None)

    if design is None:
        return 'Design not found', 404

    if request.method == 'POST':

        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        message = request.form.get('message', '').strip()

        enquiries = load_enquiries()

        new_id = max([e.get('id', 0) for e in enquiries], default=0) + 1

        enquiries.append({
            'id': new_id,
            'design_code': design['code'],
            'design_title': design['title'],
            'name': name,
            'phone': phone,
            'message': message,
            'status': 'New',
            'created_at': datetime.now().strftime('%d-%m-%Y %I:%M %p')
        })

        save_enquiries(enquiries)

        flash('Enquiry submitted successfully!', 'success')

        return redirect(url_for('design_detail', code=code))

    return render_template('enquiry.html', design=design)


# ===================================================
# ADMIN LOGIN
# ===================================================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():

    if request.method == 'POST':

        username = request.form.get('username')
        password = request.form.get('password')

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:

            user = User(username)

            login_user(user)

            return redirect(url_for('admin_dashboard'))

        flash('Invalid username or password', 'danger')

    return render_template('admin/login.html')


@app.route('/admin/logout')
@login_required
def admin_logout():

    logout_user()

    return redirect(url_for('admin_login'))


# ===================================================
# ADMIN DASHBOARD
# ===================================================

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():

    designs = load_designs()
    orders = load_orders()

    total_designs = len(designs)

    bridal_count = len([d for d in designs if d['category'] == 'Bridal'])
    neck_count = len([d for d in designs if d['category'] == 'Neck Design'])
    sleeve_count = len([d for d in designs if d['category'] == 'Sleeve Design'])
    border_count = len([d for d in designs if d['category'] == 'Border Design'])

    # ---------------------------
    # Order Statistics
    # ---------------------------

    today = datetime.now().strftime('%d-%m-%Y')

    today_orders = len([
        o for o in orders
        if o.get('created_at', '').startswith(today)
    ])

    delivered_orders = len([
        o for o in orders
        if o.get('status') == 'Delivered'
    ])

    total_advance = sum([
        float(o.get('advance_amount') or 0)
        for o in orders
    ])

    total_balance = sum([
        float(o.get('balance_amount') or 0)
        for o in orders
    ])

    return render_template(
        'admin/dashboard.html',

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

@app.route('/admin/enquiries')
@login_required
def admin_enquiries():

    enquiries = load_enquiries()

    return render_template('admin/enquiries.html', enquiries=enquiries)


# ===================================================
# ADMIN ORDERS
# ===================================================

@app.route('/admin/orders')
@login_required
def admin_orders():

    orders = load_orders()

    search = request.args.get('search', '').strip().lower()
    status = request.args.get('status', '').strip()

    filtered_orders = orders

    # Search by name, phone, or design code
    if search:
        filtered_orders = [
            o for o in filtered_orders
            if search in o.get('name', '').lower()
            or search in o.get('phone', '').lower()
            or search in o.get('design_code', '').lower()
        ]

    # Filter by status
    if status:
        filtered_orders = [
            o for o in filtered_orders
            if o.get('status') == status
        ]

    return render_template(
        'admin/orders.html',
        orders=filtered_orders,
        search=search,
        status=status
    )

# ===================================================
# UPDATE ENQUIRY STATUS
# ===================================================

@app.route('/admin/enquiry-status/<int:enquiry_id>/<status>')
@login_required
def update_enquiry_status(enquiry_id, status):

    enquiries = load_enquiries()

    for enquiry in enquiries:

        if enquiry.get('id') == enquiry_id:
            enquiry['status'] = status
            break

    save_enquiries(enquiries)

    flash('Enquiry status updated!', 'success')

    return redirect(url_for('admin_enquiries'))


# ===================================================
# DELETE ENQUIRY
# ===================================================

@app.route('/admin/delete-enquiry/<int:enquiry_id>')
@login_required
def delete_enquiry(enquiry_id):

    enquiries = load_enquiries()

    updated = [e for e in enquiries if e.get('id') != enquiry_id]

    save_enquiries(updated)

    flash('Enquiry deleted successfully!', 'success')

    return redirect(url_for('admin_enquiries'))


# ===================================================
# CREATE ORDER FROM ENQUIRY
# ===================================================

@app.route('/admin/create-order/<int:enquiry_id>')
@login_required
def create_order(enquiry_id):

    enquiries = load_enquiries()
    orders = load_orders()

    enquiry = next((e for e in enquiries if e.get('id') == enquiry_id), None)

    if enquiry is None:
        flash('Enquiry not found', 'danger')
        return redirect(url_for('admin_enquiries'))

    existing_order = next(
        (o for o in orders if o.get('enquiry_id') == enquiry_id),
        None
    )

    if existing_order:
        flash('Order already created for this enquiry', 'warning')
        return redirect(url_for('admin_orders'))

    new_order = {
        'id': len(orders) + 1,
        'enquiry_id': enquiry_id,
        'name': enquiry['name'],
        'phone': enquiry['phone'],
        'design_code': enquiry['design_code'],
        'design_title': enquiry['design_title'],
        'status': 'In Progress',
        'created_at': datetime.now().strftime('%d-%m-%Y %I:%M %p')
    }

    orders.append(new_order)

    save_orders(orders)

    enquiry['status'] = 'Ordered'

    save_enquiries(enquiries)

    flash('Order created successfully!', 'success')

    return redirect(url_for('admin_orders'))


# ===================================================
# UPDATE ORDER STATUS
# ===================================================

@app.route('/admin/order-status/<int:order_id>/<status>')
@login_required
def update_order_status(order_id, status):

    orders = load_orders()

    for order in orders:

        if order.get('id') == order_id:
            order['status'] = status
            break

    save_orders(orders)

    flash('Order status updated!', 'success')

    return redirect(url_for('admin_orders'))

# ===================================================
# EDIT ORDER DETAILS
# ===================================================

@app.route('/admin/edit-order/<int:order_id>', methods=['GET', 'POST'])
@login_required
def edit_order(order_id):

    orders = load_orders()

    order = next((o for o in orders if o.get('id') == order_id), None)

    if order is None:
        flash('Order not found', 'danger')
        return redirect(url_for('admin_orders'))

    if request.method == 'POST':

        order['blouse_size'] = request.form.get('blouse_size', '').strip()
        order['delivery_date'] = request.form.get('delivery_date', '').strip()
        order['advance_amount'] = request.form.get('advance_amount', '').strip()
        order['balance_amount'] = request.form.get('balance_amount', '').strip()

        save_orders(orders)

        flash('Order updated successfully!', 'success')

        return redirect(url_for('admin_orders'))

    return render_template('admin/edit_order.html', order=order)

# ===================================================
# PRINT ORDER INVOICE
# ===================================================

@app.route('/admin/invoice/<int:order_id>')
@login_required
def print_invoice(order_id):

    orders = load_orders()

    order = next((o for o in orders if o.get('id') == order_id), None)

    if order is None:
        flash('Order not found', 'danger')
        return redirect(url_for('admin_orders'))

    return render_template('admin/invoice.html', order=order)


# ===================================================
# DOWNLOAD ORDERS EXCEL REPORT
# ===================================================

@app.route('/admin/download-orders')
@login_required
def download_orders():

    orders = load_orders()

    wb = Workbook()
    ws = wb.active
    ws.title = 'Orders'

    # Header Row
    headers = [
        'Order ID',
        'Date',
        'Customer',
        'Phone',
        'Design Code',
        'Design Title',
        'Size',
        'Delivery Date',
        'Advance Amount',
        'Balance Amount',
        'Status'
    ]

    ws.append(headers)

    # Data Rows
    for order in orders:

        ws.append([
            order.get('id'),
            order.get('created_at'),
            order.get('name'),
            order.get('phone'),
            order.get('design_code'),
            order.get('design_title'),
            order.get('blouse_size'),
            order.get('delivery_date'),
            order.get('advance_amount'),
            order.get('balance_amount'),
            order.get('status')
        ])

    # Auto column width
    for column in ws.columns:

        max_length = 0
        column_letter = column[0].column_letter

        for cell in column:

            value = str(cell.value) if cell.value else ''

            if len(value) > max_length:
                max_length = len(value)

        ws.column_dimensions[column_letter].width = max_length + 4

    filename = 'orders_report.xlsx'
    wb.save(filename)

    return send_file(
        filename,
        as_attachment=True
    )


# ===================================================
# ADD DESIGN
# ===================================================

@app.route('/admin/add-design', methods=['GET', 'POST'])
@login_required
def add_design():

    if request.method == 'POST':

        code = request.form.get('code', '').strip()
        title = request.form.get('title', '').strip()
        category = request.form.get('category', '').strip()
        description = request.form.get('description', '').strip()

        file = request.files.get('image')

        if not file or file.filename == '':
            flash('Please select an image', 'danger')
            return redirect(request.url)

        if not allowed_file(file.filename):
            flash('Only JPG, JPEG, and PNG files are allowed', 'danger')
            return redirect(request.url)

        designs = load_designs()

        existing = next((d for d in designs if d['code'] == code), None)

        if existing:
            flash('Design code already exists', 'danger')
            return redirect(request.url)

        filename = secure_filename(file.filename)

        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        file.save(save_path)

        watermark_text = f'LOKESHWARI TAILORING | {code}'
        add_watermark(save_path, watermark_text)

        # Correct image path
        image_path = f'images/{filename}'

        new_design = {
            'code': code,
            'title': title,
            'category': category,
            'description': description,
            'price_min': request.form.get('price_min', '0'),
            'price_max': request.form.get('price_max', '0'),
            'image': image_path
        }

        designs.append(new_design)

        save_designs(designs)

        flash('Service / Design added successfully!', 'success')

        return redirect(url_for('admin_dashboard'))

    return render_template('admin/add_design.html')


# ===================================================
# EDIT DESIGN
# ===================================================

@app.route('/admin/edit-design/<code>', methods=['GET', 'POST'])
@login_required
def edit_design(code):

    designs = load_designs()

    design = next((d for d in designs if d['code'] == code), None)

    if design is None:
        flash('Design not found', 'danger')
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':

        design['title'] = request.form.get('title', '').strip()
        design['category'] = request.form.get('category', '').strip()
        design['description'] = request.form.get('description', '').strip()
        design['price_min'] = request.form.get('price_min', '0')
        design['price_max'] = request.form.get('price_max', '0')

        file = request.files.get('image')

        if file and file.filename != '':

            if not allowed_file(file.filename):
                flash('Only JPG, JPEG, and PNG files are allowed', 'danger')
                return redirect(request.url)

            old_image_path = os.path.join('static', design['image'])

            if os.path.exists(old_image_path):

                try:
                    os.remove(old_image_path)
                except Exception:
                    pass

            filename = secure_filename(file.filename)

            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            file.save(save_path)

            watermark_text = f'LOKESHWARI EMBROIDERY | {code}'
            add_watermark(save_path, watermark_text)

            design['image'] = f'images/{filename}'

        save_designs(designs)

        flash('Design updated successfully!', 'success')

        return redirect(url_for('admin_dashboard'))

    return render_template('admin/edit_design.html', design=design)


# ===================================================
# DELETE DESIGN
# ===================================================

@app.route('/admin/delete-design/<code>')
@login_required
def delete_design(code):

    designs = load_designs()

    design_to_delete = next(
        (d for d in designs if d['code'] == code),
        None
    )

    if design_to_delete is None:
        flash('Design not found', 'danger')
        return redirect(url_for('admin_dashboard'))

    image_path = os.path.join('static', design_to_delete['image'])

    if os.path.exists(image_path):

        try:
            os.remove(image_path)
        except Exception:
            pass

    updated_designs = [
        d for d in designs
        if d['code'] != code
    ]

    save_designs(updated_designs)

    flash('Design deleted successfully!', 'success')

    return redirect(url_for('admin_dashboard'))


# ===================================================
# RUN APPLICATION
# ===================================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)