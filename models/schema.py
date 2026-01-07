# ================= TABLE NAMES =================
USERS = "users"
ORDERS = "orders"
ORDER_ITEMS = "order_items"
PRODUCTS = "products"
CART = "cart"

# ================= USERS COLUMNS =================
USER_ID = "id"
USER_NAME = "name"
USER_EMAIL = "email"
USER_ROLE = "role"

# ================= ORDERS COLUMNS =================
ORDER_ID = "id"
ORDER_BUYER_ID = "buyer_id"
ORDER_TOTAL = "total"
ORDER_STATUS = "status"
ORDER_ADDRESS = "address"
ORDER_CREATED_AT = "created_at"
ORDER_ESTIMATED_DELIVERY = "estimated_delivery"

# ================= ORDER STATUS VALUES =================
STATUS_PENDING = "pending"
STATUS_APPROVED = "approved"
STATUS_SHIPPED = "shipped"
STATUS_DELIVERED = "delivered"
STATUS_CANCELLED = "cancelled"

VALID_ORDER_STATUSES = {
    STATUS_PENDING,
    STATUS_APPROVED,
    STATUS_SHIPPED,
    STATUS_DELIVERED,
    STATUS_CANCELLED
}
