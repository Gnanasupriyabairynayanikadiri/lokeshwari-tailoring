# ============================================================
# FILE: database.py
# ============================================================

from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)


# ============================================================
# DATABASE INSTANCE
# ============================================================

db = SQLAlchemy()


# ============================================================
# CUSTOMER MODEL
# ============================================================

class Customer(UserMixin, db.Model):

    __tablename__ = "customers"

    # --------------------------------------------------------
    # PRIMARY KEY
    # --------------------------------------------------------

    id = db.Column(
        db.Integer,
        primary_key=True
    )


    # --------------------------------------------------------
    # CUSTOMER INFORMATION
    # --------------------------------------------------------

    name = db.Column(
        db.String(100),
        nullable=False
    )


    phone = db.Column(
        db.String(20),
        unique=True,
        nullable=False
    )


    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )


    # --------------------------------------------------------
    # PASSWORD
    # --------------------------------------------------------

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )


    # --------------------------------------------------------
    # CREATED DATE
    # --------------------------------------------------------

    created_at = db.Column(
        db.DateTime,
        default=datetime.now,
        nullable=False
    )


    # ========================================================
    # PASSWORD METHODS
    # ========================================================

    def set_password(self, password):

        self.password_hash = generate_password_hash(
            password
        )


    def check_password(self, password):

        return check_password_hash(
            self.password_hash,
            password
        )


    # ========================================================
    # DISPLAY CUSTOMER
    # ========================================================

    def __repr__(self):

        return (
            f"<Customer "
            f"id={self.id} "
            f"name={self.name}>"
        )


# ============================================================
# WISHLIST MODEL
# ============================================================

class Wishlist(db.Model):

    __tablename__ = "wishlists"


    # --------------------------------------------------------
    # PRIMARY KEY
    # --------------------------------------------------------

    id = db.Column(
        db.Integer,
        primary_key=True
    )


    # --------------------------------------------------------
    # CUSTOMER
    # --------------------------------------------------------

    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("customers.id"),
        nullable=False
    )


    # --------------------------------------------------------
    # DESIGN
    # --------------------------------------------------------

    design_code = db.Column(
        db.String(50),
        nullable=False
    )


    # --------------------------------------------------------
    # CREATED DATE
    # --------------------------------------------------------

    created_at = db.Column(
        db.DateTime,
        default=datetime.now,
        nullable=False
    )


    # ========================================================
    # RELATIONSHIP
    # ========================================================

    customer = db.relationship(
        "Customer",
        backref=db.backref(
            "wishlist_items",
            lazy=True,
            cascade="all, delete-orphan"
        )
    )


    # ========================================================
    # DISPLAY WISHLIST
    # ========================================================

    def __repr__(self):

        return (
            f"<Wishlist "
            f"id={self.id} "
            f"customer_id={self.customer_id} "
            f"design={self.design_code}>"
        )


# ============================================================
# ENQUIRY MODEL
# ============================================================

class Enquiry(db.Model):

    __tablename__ = "enquiries"


    # --------------------------------------------------------
    # PRIMARY KEY
    # --------------------------------------------------------

    id = db.Column(
        db.Integer,
        primary_key=True
    )


    # --------------------------------------------------------
    # CUSTOMER
    # --------------------------------------------------------

    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("customers.id"),
        nullable=False
    )


    # --------------------------------------------------------
    # DESIGN INFORMATION
    # --------------------------------------------------------

    design_code = db.Column(
        db.String(50),
        nullable=False
    )


    design_title = db.Column(
        db.String(200),
        nullable=True
    )


    # --------------------------------------------------------
    # CUSTOMER INFORMATION
    # --------------------------------------------------------

    customer_name = db.Column(
        db.String(100),
        nullable=True
    )


    phone = db.Column(
        db.String(20),
        nullable=True
    )


    # --------------------------------------------------------
    # ENQUIRY MESSAGE
    # --------------------------------------------------------

    message = db.Column(
        db.Text,
        nullable=True
    )


    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    status = db.Column(
        db.String(50),
        default="New",
        nullable=False
    )


    # --------------------------------------------------------
    # CREATED DATE
    # --------------------------------------------------------

    created_at = db.Column(
        db.DateTime,
        default=datetime.now,
        nullable=False
    )


    # ========================================================
    # CUSTOMER RELATIONSHIP
    # ========================================================

    customer = db.relationship(
        "Customer",
        backref=db.backref(
            "enquiries",
            lazy=True,
            cascade="all, delete-orphan"
        )
    )


    # ========================================================
    # DISPLAY ENQUIRY
    # ========================================================

    def __repr__(self):

        return (
            f"<Enquiry "
            f"id={self.id} "
            f"customer_id={self.customer_id} "
            f"design={self.design_code} "
            f"status={self.status}>"
        )


# ============================================================
# ORDER MODEL
# ============================================================

class Order(db.Model):

    __tablename__ = "orders"


    # --------------------------------------------------------
    # PRIMARY KEY
    # --------------------------------------------------------

    id = db.Column(
        db.Integer,
        primary_key=True
    )


    # --------------------------------------------------------
    # CUSTOMER
    # --------------------------------------------------------

    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("customers.id"),
        nullable=False
    )


    # --------------------------------------------------------
    # RELATED ENQUIRY
    # --------------------------------------------------------

    enquiry_id = db.Column(
        db.Integer,
        db.ForeignKey("enquiries.id"),
        nullable=True
    )


    # --------------------------------------------------------
    # DESIGN INFORMATION
    # --------------------------------------------------------

    design_code = db.Column(
        db.String(50),
        nullable=False
    )


    design_title = db.Column(
        db.String(200),
        nullable=True
    )


    # --------------------------------------------------------
    # ORDER STATUS
    # --------------------------------------------------------

    status = db.Column(
        db.String(50),
        default="In Progress",
        nullable=False
    )


    # --------------------------------------------------------
    # DATES
    # --------------------------------------------------------

    order_date = db.Column(
        db.DateTime,
        default=datetime.now,
        nullable=False
    )


    delivery_date = db.Column(
        db.Date,
        nullable=True
    )


    # --------------------------------------------------------
    # PAYMENT INFORMATION
    # --------------------------------------------------------

    total_amount = db.Column(
        db.Float,
        default=0.0,
        nullable=False
    )


    advance_amount = db.Column(
        db.Float,
        default=0.0,
        nullable=False
    )


    balance_amount = db.Column(
        db.Float,
        default=0.0,
        nullable=False
    )


    # --------------------------------------------------------
    # NOTES
    # --------------------------------------------------------

    notes = db.Column(
        db.Text,
        nullable=True
    )


    # ========================================================
    # CUSTOMER RELATIONSHIP
    # ========================================================

    customer = db.relationship(
        "Customer",
        backref=db.backref(
            "orders",
            lazy=True,
            cascade="all, delete-orphan"
        )
    )


    # ========================================================
    # ENQUIRY RELATIONSHIP
    # ========================================================

    enquiry = db.relationship(
        "Enquiry",
        backref=db.backref(
            "orders",
            lazy=True
        )
    )


    # ========================================================
    # DISPLAY ORDER
    # ========================================================

    def __repr__(self):

        return (
            f"<Order "
            f"id={self.id} "
            f"customer_id={self.customer_id} "
            f"design={self.design_code} "
            f"status={self.status}>"
        )


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def initialize_database(app):

    with app.app_context():

        db.create_all()

        print("===================================")
        print("Database initialized successfully!")
        print("===================================")