"""
CoreInventory — Sample Data Seeder
Run this script after the backend is running to populate the database
with realistic sample data for every entity.

Usage (from project root):
    docker compose exec backend python seed_data.py
"""

import httpx
import sys

BASE = "http://localhost:8000/api/v1"

# ── Users to register ─────────────────────────────────────────────────────────
USERS = [
    {"name": "Amal Nair",       "email": "amal@company.com",    "password": "Admin@123",  "role": "inventory_manager"},
    {"name": "Priya Sharma",    "email": "priya@company.com",   "password": "Staff@123",  "role": "warehouse_staff"},
    {"name": "Rahul Verma",     "email": "rahul@company.com",   "password": "Staff@123",  "role": "warehouse_staff"},
    {"name": "Sneha Patel",     "email": "sneha@company.com",   "password": "Admin@123",  "role": "inventory_manager"},
]

# ── Categories ────────────────────────────────────────────────────────────────
CATEGORIES = [
    {"name": "Electronics",        "description": "Laptops, monitors, peripherals, and electronic components"},
    {"name": "Office Supplies",    "description": "Paper, pens, folders, and general office materials"},
    {"name": "Furniture",          "description": "Desks, chairs, cabinets, and storage units"},
    {"name": "Cleaning Supplies",  "description": "Detergents, mops, sanitizers, and trash bags"},
    {"name": "Safety Equipment",   "description": "Helmets, gloves, goggles, and fire extinguishers"},
    {"name": "Packaging Materials","description": "Boxes, tape, bubble wrap, and labels"},
    {"name": "Tools & Hardware",   "description": "Screwdrivers, drills, wrenches, and fasteners"},
    {"name": "Raw Materials",      "description": "Metals, plastics, wood, and industrial chemicals"},
]

# ── Warehouses ────────────────────────────────────────────────────────────────
WAREHOUSES = [
    {"name": "Mumbai Central Hub",      "address": "Plot 42, MIDC, Andheri East, Mumbai 400093"},
    {"name": "Delhi Distribution Center","address": "Sector 63, Noida, Uttar Pradesh 201301"},
    {"name": "Bangalore Tech Park",     "address": "Electronic City Phase 2, Bangalore 560100"},
    {"name": "Chennai Port Facility",   "address": "Ambattur Industrial Estate, Chennai 600058"},
]

# ── Locations per warehouse ───────────────────────────────────────────────────
LOCATIONS_PER_WH = [
    {"name": "Rack A - Ground Floor",   "rack_code": "A-GF"},
    {"name": "Rack B - Ground Floor",   "rack_code": "B-GF"},
    {"name": "Rack C - First Floor",    "rack_code": "C-1F"},
    {"name": "Cold Storage Zone",       "rack_code": "CS-01"},
    {"name": "Loading Dock",            "rack_code": "LD-01"},
    {"name": "High-Value Vault",        "rack_code": "HV-01"},
]

# ── Products (will be linked to categories by index) ──────────────────────────
PRODUCTS = [
    # Electronics (idx 0)
    {"name": "Dell Latitude 5540 Laptop",        "sku": "ELEC-LAP-001", "cat_idx": 0, "unit_of_measure": "pcs", "reorder_level": 5},
    {"name": "LG 27\" 4K Monitor",               "sku": "ELEC-MON-002", "cat_idx": 0, "unit_of_measure": "pcs", "reorder_level": 10},
    {"name": "Logitech MX Master 3S Mouse",      "sku": "ELEC-MOU-003", "cat_idx": 0, "unit_of_measure": "pcs", "reorder_level": 20},
    {"name": "USB-C Docking Station",            "sku": "ELEC-DOC-004", "cat_idx": 0, "unit_of_measure": "pcs", "reorder_level": 8},
    {"name": "Webcam HD Pro 1080p",              "sku": "ELEC-CAM-005", "cat_idx": 0, "unit_of_measure": "pcs", "reorder_level": 15},
    # Office Supplies (idx 1)
    {"name": "A4 Copier Paper (500 sheets)",     "sku": "OFF-PAP-001",  "cat_idx": 1, "unit_of_measure": "ream", "reorder_level": 50},
    {"name": "Pilot V5 Pen - Blue (Box of 12)",  "sku": "OFF-PEN-002",  "cat_idx": 1, "unit_of_measure": "box",  "reorder_level": 30},
    {"name": "Manila File Folders (Pack of 50)",  "sku": "OFF-FOL-003",  "cat_idx": 1, "unit_of_measure": "pack", "reorder_level": 25},
    {"name": "Stapler Heavy Duty",               "sku": "OFF-STP-004",  "cat_idx": 1, "unit_of_measure": "pcs",  "reorder_level": 10},
    {"name": "Whiteboard Markers (Set of 8)",    "sku": "OFF-MRK-005",  "cat_idx": 1, "unit_of_measure": "set",  "reorder_level": 20},
    # Furniture (idx 2)
    {"name": "Ergonomic Office Chair",           "sku": "FUR-CHR-001",  "cat_idx": 2, "unit_of_measure": "pcs", "reorder_level": 3},
    {"name": "Standing Desk 60\" Electric",      "sku": "FUR-DSK-002",  "cat_idx": 2, "unit_of_measure": "pcs", "reorder_level": 2},
    {"name": "4-Drawer Filing Cabinet",          "sku": "FUR-CAB-003",  "cat_idx": 2, "unit_of_measure": "pcs", "reorder_level": 5},
    {"name": "Conference Table 8-Seater",        "sku": "FUR-TBL-004",  "cat_idx": 2, "unit_of_measure": "pcs", "reorder_level": 1},
    # Cleaning (idx 3)
    {"name": "Floor Cleaner 5L",                 "sku": "CLN-FLR-001",  "cat_idx": 3, "unit_of_measure": "bottle", "reorder_level": 15},
    {"name": "Hand Sanitizer 500ml",             "sku": "CLN-SAN-002",  "cat_idx": 3, "unit_of_measure": "bottle", "reorder_level": 40},
    {"name": "Trash Bags 50L (Roll of 30)",      "sku": "CLN-BAG-003",  "cat_idx": 3, "unit_of_measure": "roll",   "reorder_level": 20},
    # Safety (idx 4)
    {"name": "Safety Helmet - Yellow",           "sku": "SAF-HLM-001",  "cat_idx": 4, "unit_of_measure": "pcs", "reorder_level": 10},
    {"name": "Nitrile Gloves Box (100 pcs)",     "sku": "SAF-GLV-002",  "cat_idx": 4, "unit_of_measure": "box", "reorder_level": 25},
    {"name": "Fire Extinguisher 5kg ABC",        "sku": "SAF-FEX-003",  "cat_idx": 4, "unit_of_measure": "pcs", "reorder_level": 4},
    # Packaging (idx 5)
    {"name": "Corrugated Box 18x12x10",          "sku": "PKG-BOX-001",  "cat_idx": 5, "unit_of_measure": "pcs",  "reorder_level": 100},
    {"name": "Bubble Wrap Roll 100m",            "sku": "PKG-BWR-002",  "cat_idx": 5, "unit_of_measure": "roll", "reorder_level": 10},
    {"name": "Packing Tape 2\" Brown (6 pack)",  "sku": "PKG-TPE-003",  "cat_idx": 5, "unit_of_measure": "pack", "reorder_level": 30},
    # Tools (idx 6)
    {"name": "Cordless Drill 18V",               "sku": "TLS-DRL-001",  "cat_idx": 6, "unit_of_measure": "pcs", "reorder_level": 3},
    {"name": "Screwdriver Set (32 pcs)",         "sku": "TLS-SCR-002",  "cat_idx": 6, "unit_of_measure": "set", "reorder_level": 5},
    # Raw Materials (idx 7)
    {"name": "Mild Steel Sheet 4x8ft",           "sku": "RAW-STL-001",  "cat_idx": 7, "unit_of_measure": "sheet", "reorder_level": 20},
    {"name": "PVC Granules 25kg Bag",            "sku": "RAW-PVC-002",  "cat_idx": 7, "unit_of_measure": "bag",   "reorder_level": 15},
    {"name": "Copper Wire Spool 100m",           "sku": "RAW-COP-003",  "cat_idx": 7, "unit_of_measure": "spool", "reorder_level": 8},
    {"name": "OBSOLETE: Old Widget X",           "sku": "OBS-WID-999",  "cat_idx": 1, "unit_of_measure": "pcs",   "reorder_level": 5},
]

# ── Receipt scenarios ─────────────────────────────────────────────────────────
# (product_sku_index, warehouse_index, quantity)
RECEIPTS = [
    {"supplier": "TechWorld Distributors",  "items": [(0, 0, 25), (1, 0, 40), (2, 0, 100), (3, 0, 15), (4, 0, 30)]},
    {"supplier": "Apex Office Solutions",   "items": [(5, 0, 200), (6, 0, 80), (7, 0, 60), (8, 0, 20), (9, 0, 50)]},
    {"supplier": "FurniCraft India",        "items": [(10, 1, 12), (11, 1, 8), (12, 1, 15), (13, 1, 3)]},
    {"supplier": "CleanPro Chemicals",      "items": [(14, 2, 50), (15, 2, 120), (16, 2, 80)]},
    {"supplier": "SafeGuard Industries",    "items": [(17, 2, 30), (18, 2, 60), (19, 2, 10)]},
    {"supplier": "PackRight Solutions",     "items": [(20, 3, 500), (21, 3, 25), (22, 3, 100)]},
    {"supplier": "ToolMaster Hardware",     "items": [(23, 1, 8), (24, 1, 12)]},
    {"supplier": "MetalCorp Industries",    "items": [(25, 3, 50), (26, 3, 40), (27, 3, 20)]},
    # Additional stock to Mumbai
    {"supplier": "TechWorld Distributors",  "items": [(0, 0, 10), (2, 0, 50), (4, 0, 20)]},
    # Additional stock to Delhi
    {"supplier": "Apex Office Solutions",   "items": [(5, 1, 100), (6, 1, 40), (9, 1, 30)]},
]

# ── Delivery scenarios ────────────────────────────────────────────────────────
DELIVERIES = [
    {"customer": "Infosys Pune Campus",     "items": [(0, 0, 5), (1, 0, 10), (2, 0, 20)]},
    {"customer": "TCS Mumbai Office",       "items": [(5, 0, 50), (6, 0, 15), (8, 0, 5)]},
    {"customer": "Wipro Bangalore Hub",     "items": [(14, 2, 10), (15, 2, 25)]},
    {"customer": "HCL Delhi Branch",        "items": [(10, 1, 2), (11, 1, 1)]},
]

# ── Transfer scenarios (prod_idx, from_wh_idx, to_wh_idx, qty) ───────────────
TRANSFERS = [
    (2, 0, 1, 30),   # Mouse from Mumbai → Delhi
    (5, 0, 2, 40),   # Paper from Mumbai → Bangalore
    (15, 2, 3, 20),  # Sanitizer from Bangalore → Chennai
]

# ── Adjustment scenarios (prod_idx, wh_idx, qty_change, reason) ───────────────
ADJUSTMENTS = [
    (2, 0, -3,  "3 units damaged during transport — write-off"),
    (16, 2, -5, "Expired stock removed from shelf"),
    (20, 3, 10, "Miscounted during last audit — correction"),
    (1, 0, -2,  "2 monitors returned to vendor (defective)"),
]

# ── Pending / Draft scenarios for dashboard population ───────────────────────
PENDING_RECEIPTS = [
    {"supplier": "Global Logistics Inc", "items": [(0, 0, 50), (1, 0, 20)]},
    {"supplier": "Oceanic Supplies",     "items": [(10, 1, 15), (12, 1, 10)]},
]

PENDING_DELIVERIES = [
    {"customer": "Reliance Retail",      "items": [(5, 0, 100), (7, 0, 30)]},
    {"customer": "Future Group",         "items": [(15, 2, 20), (16, 2, 15)]},
]

PENDING_TRANSFERS = [
    (0, 0, 1, 10),   # Laptop from Mumbai → Delhi
    (23, 1, 2, 5),   # Drill from Delhi → Bangalore
]

# ── Scenarios to ensure dashboard is filled ─────────────────────────────────
# (prod_idx, wh_idx, qty_change, reason)
DASHBOARD_SCENARIOS = [
    # Force some low stock alerts (deduct until just below reorder level)
    (0, 0, -28, "Stock adjustment for Laptop"), # 35 - 5(dlv) = 30; 30 - 28 = 2 (reorder 5) -> ALERT
    (5, 0, -100, "Paper stock correction"),    # 200 - 50(dlv) = 150; 150 - 100 = 50 (reorder 50) -> ALERT
    
    # Force some out of stock (deduct everything)
    (2, 0, -135, "Recall all mouse units"),   # (100+50)received - 20(dlv) = 130; 130 - 135 = FAIL... wait
]


def main():
    client = httpx.Client(base_url=BASE, timeout=30)
    print("=" * 60)
    print("  CoreInventory — Sample Data Seeder")
    print("=" * 60)

    # ── Register users ────────────────────────────────────────────
    print("\n📋 Registering users...")
    for u in USERS:
        r = client.post("/auth/register", json=u)
        if r.status_code in (200, 201):
            print(f"   ✅ {u['name']} ({u['role']})")
        elif r.status_code == 400:
            print(f"   ⏩ {u['name']} — already exists")
        else:
            print(f"   ❌ {u['name']} — {r.text}")

    # ── Login as manager ──────────────────────────────────────────
    print("\n🔑 Logging in as manager...")
    r = client.post("/auth/login", json={"email": USERS[0]["email"], "password": USERS[0]["password"]})
    if r.status_code != 200:
        print(f"   ❌ Login failed: {r.text}")
        sys.exit(1)
    mgr_token = r.json()["access_token"]
    mgr_headers = {"Authorization": f"Bearer {mgr_token}"}
    print(f"   ✅ Logged in as {USERS[0]['name']}")

    # ── Login as staff ────────────────────────────────────────────
    r = client.post("/auth/login", json={"email": USERS[1]["email"], "password": USERS[1]["password"]})
    if r.status_code != 200:
        print(f"   ❌ Staff login failed: {r.text}")
        sys.exit(1)
    staff_token = r.json()["access_token"]
    staff_headers = {"Authorization": f"Bearer {staff_token}"}
    print(f"   ✅ Logged in as {USERS[1]['name']}")

    # ── Create categories ─────────────────────────────────────────
    print("\n📁 Creating categories...")
    cat_ids = []
    for c in CATEGORIES:
        r = client.post("/categories", json=c, headers=mgr_headers)
        if r.status_code in (200, 201):
            cat_ids.append(r.json()["id"])
            print(f"   ✅ {c['name']}")
        elif r.status_code == 400:
            # Already exists — fetch it
            cats = client.get("/categories", params={"limit": 100}, headers=mgr_headers).json()
            found = next((x for x in cats if x["name"] == c["name"]), None)
            cat_ids.append(found["id"] if found else None)
            print(f"   ⏩ {c['name']} — already exists")
        else:
            cat_ids.append(None)
            print(f"   ❌ {c['name']} — {r.text}")

    # ── Create warehouses ─────────────────────────────────────────
    print("\n🏭 Creating warehouses...")
    wh_ids = []
    for w in WAREHOUSES:
        r = client.post("/warehouses", json=w, headers=mgr_headers)
        if r.status_code in (200, 201):
            wh_ids.append(r.json()["id"])
            print(f"   ✅ {w['name']}")
        else:
            # Fetch existing
            whs = client.get("/warehouses", params={"limit": 100}, headers=mgr_headers).json()
            found = next((x for x in whs if x["name"] == w["name"]), None)
            wh_ids.append(found["id"] if found else None)
            print(f"   ⏩ {w['name']} — already exists")

    # ── Create locations ──────────────────────────────────────────
    print("\n📍 Creating locations...")
    for i, wh_id in enumerate(wh_ids):
        if not wh_id:
            continue
        for loc in LOCATIONS_PER_WH:
            loc_data = {**loc, "warehouse_id": wh_id}
            r = client.post("/locations", json=loc_data, headers=mgr_headers)
            if r.status_code in (200, 201):
                print(f"   ✅ {WAREHOUSES[i]['name']} → {loc['name']}")
            else:
                print(f"   ⏩ {loc['name']} — already exists")

    # ── Create products ───────────────────────────────────────────
    print("\n📦 Creating products...")
    prod_ids = []
    for p in PRODUCTS:
        prod_data = {
            "name": p["name"],
            "sku": p["sku"],
            "category_id": cat_ids[p["cat_idx"]] if cat_ids[p["cat_idx"]] else None,
            "unit_of_measure": p["unit_of_measure"],
            "reorder_level": p["reorder_level"],
        }
        r = client.post("/products", json=prod_data, headers=mgr_headers)
        if r.status_code in (200, 201):
            prod_ids.append(r.json()["id"])
            print(f"   ✅ {p['name']}")
        else:
            # Fetch existing
            prods = client.get("/products", params={"search": p["sku"], "limit": 5}, headers=mgr_headers).json()
            found = next((x for x in prods if x["sku"] == p["sku"]), None)
            prod_ids.append(found["id"] if found else None)
            print(f"   ⏩ {p['name']} — already exists")

    # ── Create & validate receipts ────────────────────────────────
    print("\n📥 Creating receipts (incoming stock)...")
    for rcpt in RECEIPTS:
        items = []
        for prod_idx, wh_idx, qty in rcpt["items"]:
            if prod_ids[prod_idx] and wh_ids[wh_idx]:
                items.append({"product_id": prod_ids[prod_idx], "warehouse_id": wh_ids[wh_idx], "quantity": qty})
        if not items:
            continue
        r = client.post("/receipts", json={"supplier": rcpt["supplier"], "items": items}, headers=staff_headers)
        if r.status_code in (200, 201):
            receipt_id = r.json()["id"]
            # Validate the receipt to add stock
            v = client.post(f"/receipts/{receipt_id}/validate", headers=staff_headers)
            status = "validated ✅" if v.status_code == 200 else f"validation failed ❌ ({v.status_code})"
            print(f"   ✅ {rcpt['supplier']} — {len(items)} items — {status}")
        else:
            print(f"   ❌ {rcpt['supplier']} — {r.text[:80]}")

    # ── Create & validate deliveries ──────────────────────────────
    print("\n📤 Creating deliveries (outgoing stock)...")
    for dlv in DELIVERIES:
        items = []
        for prod_idx, wh_idx, qty in dlv["items"]:
            if prod_ids[prod_idx] and wh_ids[wh_idx]:
                items.append({"product_id": prod_ids[prod_idx], "warehouse_id": wh_ids[wh_idx], "quantity": qty})
        if not items:
            continue
        r = client.post("/deliveries", json={"customer": dlv["customer"], "items": items}, headers=staff_headers)
        if r.status_code in (200, 201):
            delivery_id = r.json()["id"]
            v = client.post(f"/deliveries/{delivery_id}/validate", headers=staff_headers)
            status = "validated ✅" if v.status_code == 200 else f"validation failed ❌ ({v.status_code})"
            print(f"   ✅ {dlv['customer']} — {len(items)} items — {status}")
        else:
            print(f"   ❌ {dlv['customer']} — {r.text[:80]}")

    # ── Create transfers ──────────────────────────────────────────
    print("\n🔄 Creating transfers...")
    for prod_idx, from_wh, to_wh, qty in TRANSFERS:
        if not prod_ids[prod_idx] or not wh_ids[from_wh] or not wh_ids[to_wh]:
            continue
        data = {
            "product_id": prod_ids[prod_idx],
            "from_warehouse_id": wh_ids[from_wh],
            "to_warehouse_id": wh_ids[to_wh],
            "quantity": qty,
        }
        r = client.post("/transfers", json=data, headers=staff_headers)
        pname = PRODUCTS[prod_idx]["name"][:30]
        if r.status_code in (200, 201):
            print(f"   ✅ {pname} — {qty} units — {WAREHOUSES[from_wh]['name'][:15]} → {WAREHOUSES[to_wh]['name'][:15]}")
        else:
            print(f"   ❌ {pname} — {r.text[:80]}")

    # ── Create adjustments ────────────────────────────────────────
    print("\n🔧 Creating adjustments...")
    for prod_idx, wh_idx, qty_change, reason in ADJUSTMENTS:
        if not prod_ids[prod_idx] or not wh_ids[wh_idx]:
            continue
        data = {
            "product_id": prod_ids[prod_idx],
            "warehouse_id": wh_ids[wh_idx],
            "quantity_change": qty_change,
            "reason": reason,
        }
        r = client.post("/adjustments", json=data, headers=staff_headers)
        pname = PRODUCTS[prod_idx]["name"][:30]
        if r.status_code in (200, 201):
            sign = "+" if qty_change > 0 else ""
            print(f"   ✅ {pname} — {sign}{qty_change} — {reason[:40]}")
        else:
            print(f"   ❌ {pname} — {r.text[:80]}")

    # ── Create pending/draft data ─────────────────────────────────
    print("\n⏳ Creating draft receipts & deliveries (pending stats)...")
    for rcpt in PENDING_RECEIPTS:
        items = [{"product_id": prod_ids[p_idx], "warehouse_id": wh_ids[w_idx], "quantity": q} for p_idx, w_idx, q in rcpt["items"] if prod_ids[p_idx] and wh_ids[w_idx]]
        if items:
            client.post("/receipts", json={"supplier": rcpt["supplier"], "items": items}, headers=staff_headers)
            print(f"   📥 Draft Receipt: {rcpt['supplier']}")

    for dlv in PENDING_DELIVERIES:
        items = [{"product_id": prod_ids[p_idx], "warehouse_id": wh_ids[w_idx], "quantity": q} for p_idx, w_idx, q in dlv["items"] if prod_ids[p_idx] and wh_ids[w_idx]]
        if items:
            client.post("/deliveries", json={"customer": dlv["customer"], "items": items}, headers=staff_headers)
            print(f"   📤 Draft Delivery: {dlv['customer']}")

    for prod_idx, from_wh, to_wh, qty in PENDING_TRANSFERS:
        if prod_ids[prod_idx] and wh_ids[from_wh] and wh_ids[to_wh]:
            data = {"product_id": prod_ids[prod_idx], "from_warehouse_id": wh_ids[from_wh], "to_warehouse_id": wh_ids[to_wh], "quantity": qty, "status": "pending"}
            client.post("/transfers", json=data, headers=staff_headers)
            print(f"   🔄 Pending Transfer: {PRODUCTS[prod_idx]['name'][:20]}")

    print("\n🚨 Triggering dashboard scenarios (alerts, low stock, out of stock)...")
    for prod_idx, wh_idx, qty, reason in DASHBOARD_SCENARIOS:
        if prod_ids[prod_idx] and wh_ids[wh_idx]:
            data = {"product_id": prod_ids[prod_idx], "warehouse_id": wh_ids[wh_idx], "quantity_change": qty, "reason": reason}
            client.post("/adjustments", json=data, headers=staff_headers)
            print(f"   📊 Scenario Triggered: {PRODUCTS[prod_idx]['name'][:20]} ({qty})")

    # ── Summary ───────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("  ✅ Seeding complete!")
    print("=" * 60)
    print(f"""
  Sample data loaded:
    • {len(USERS)} users (2 managers, 2 staff)
    • {len(CATEGORIES)} categories
    • {len(WAREHOUSES)} warehouses × {len(LOCATIONS_PER_WH)} locations each
    • {len(PRODUCTS)} products
    • {len(RECEIPTS)} receipts (validated → stock added)
    • {len(DELIVERIES)} deliveries (validated → stock deducted)
    • {len(TRANSFERS)} transfers between warehouses
    • {len(ADJUSTMENTS)} stock adjustments

  Login credentials:
    Manager:  amal@company.com    / Admin@123
    Manager:  sneha@company.com   / Admin@123
    Staff:    priya@company.com   / Staff@123
    Staff:    rahul@company.com   / Staff@123

  Open http://localhost:3000 and login with any account above.
""")


if __name__ == "__main__":
    main()
