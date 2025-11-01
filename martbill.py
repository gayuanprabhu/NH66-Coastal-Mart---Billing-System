import tkinter as tk
from tkinter import ttk, messagebox
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime
import webbrowser, os

# -----------------------------
# NH66 Coastal Mart Billing App
# -----------------------------

PRODUCTS = {
    "Groceries 🥦": {
        "Rice (1kg)": (60, 0.05),
        "Wheat Flour (1kg)": (45, 0.05),
        "Pulses (1kg)": (80, 0.05),
        "Cooking Oil (1L)": (150, 0.05),
        "Sugar (1kg)": (50, 0.05),
        "Salt (1kg)": (20, 0.05),
    },
    "Snacks 🍪": {
        "Chips Pack": (25, 0.12),
        "Biscuits": (30, 0.12),
        "Namkeen": (50, 0.12),
        "Chocolate Bar": (40, 0.12),
    },
    "Beverages ☕": {
        "Tea Pack": (120, 0.18),
        "Coffee Pack": (200, 0.18),
        "Soft Drink (1L)": (60, 0.18),
        "Juice Pack": (90, 0.18),
    },
    "Cosmetics 💄": {
        "Soap": (40, 0.18),
        "Shampoo": (120, 0.18),
        "Face Cream": (180, 0.18),
        "Toothpaste": (60, 0.18),
    },
    "Cleaning 🧴": {
        "Detergent": (90, 0.12),
        "Floor Cleaner": (150, 0.12),
        "Toilet Cleaner": (120, 0.12),
        "Dishwash Liquid": (80, 0.12),
    },
    "Dairy & Bakery 🧈": {
        "Milk (1L)": (60, 0.05),
        "Bread": (40, 0.05),
        "Butter": (120, 0.05),
        "Cheese": (150, 0.05),
    }
}


class BillingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NH66 Coastal Mart 🛒")
        self.root.geometry("1200x700")
        self.root.configure(bg="#ECFDF5")

        self.last_bill = None

        # ---------------- HEADER ----------------
        header = tk.Label(root, text="NH66 Coastal Mart Billing System 🧾",
                          font=("Arial Rounded MT Bold", 22, "bold"), bg="#A7F3D0", fg="#065F46", pady=12)
        header.pack(fill=tk.X)

        # ---------------- CUSTOMER FRAME ----------------
        cust_frame = tk.Frame(root, bg="#D1FAE5", pady=8)
        cust_frame.pack(fill=tk.X, padx=10, pady=(10, 0))

        tk.Label(cust_frame, text="Customer Name:", font=("Arial", 12), bg="#D1FAE5").grid(row=0, column=0)
        self.customer_name = tk.Entry(cust_frame, width=25)
        self.customer_name.grid(row=0, column=1, padx=5)

        tk.Label(cust_frame, text="Phone:", font=("Arial", 12), bg="#D1FAE5").grid(row=0, column=2)
        self.phone = tk.Entry(cust_frame, width=20)
        self.phone.grid(row=0, column=3, padx=5)

        tk.Label(cust_frame, text="Points:", font=("Arial", 12), bg="#D1FAE5").grid(row=0, column=4)
        self.points = tk.Entry(cust_frame, width=10)
        self.points.insert(0, "0")
        self.points.grid(row=0, column=5, padx=5)

        # ---------------- MAIN FRAME ----------------
        container = tk.Frame(root, bg="#ECFDF5")
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Bill area
        self.bill_frame = tk.Frame(container, bg="#CCFBF1", bd=2, relief=tk.RIDGE)
        self.bill_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        tk.Label(self.bill_frame, text="🧾 Bill Preview",
                 font=("Arial Rounded MT Bold", 14), bg="#99F6E4", fg="#065F46", pady=5).pack(fill=tk.X)

        self.bill_text = tk.Text(self.bill_frame, width=45, height=28,
                                 font=("Courier New", 10), bg="#ECFEFF", fg="#064E3B", wrap=tk.WORD)
        self.bill_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.scroll_bill = ttk.Scrollbar(self.bill_frame, command=self.bill_text.yview)
        self.scroll_bill.pack(side=tk.RIGHT, fill=tk.Y)
        self.bill_text.config(yscrollcommand=self.scroll_bill.set)

        # Product list area (scrollable)
        prod_canvas = tk.Canvas(container, bg="#ECFDF5", highlightthickness=0)
        prod_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y = ttk.Scrollbar(container, orient="vertical", command=prod_canvas.yview)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        prod_canvas.configure(yscrollcommand=scroll_y.set)

        self.prod_frame = tk.Frame(prod_canvas, bg="#ECFDF5")
        prod_canvas.create_window((0, 0), window=self.prod_frame, anchor="nw")
        self.prod_frame.bind("<Configure>", lambda e: prod_canvas.configure(scrollregion=prod_canvas.bbox("all")))

        self.quantity_vars = {}
        self.display_products()

        # ---------------- FIXED BUTTONS ----------------
        bottom = tk.Frame(root, bg="#D1FAE5", height=60)
        bottom.pack(side=tk.BOTTOM, fill=tk.X)

        style_btn = dict(font=("Arial Rounded MT Bold", 12), padx=12, pady=6, relief="flat", cursor="hand2")

        tk.Button(bottom, text="🧹 Clear", bg="#6EE7B7", fg="#064E3B",
                  command=self.clear_fields, **style_btn).pack(side=tk.LEFT, padx=10)

        tk.Button(bottom, text="🧾 Total", bg="#34D399", fg="white",
                  command=self.total_bill, **style_btn).pack(side=tk.LEFT, padx=10)

        tk.Button(bottom, text="💾 Save PDF", bg="#2DD4BF", fg="white",
                  command=self.save_pdf, **style_btn).pack(side=tk.LEFT, padx=10)

        tk.Button(bottom, text="🖨️ Print", bg="#14B8A6", fg="white",
                  command=self.save_pdf, **style_btn).pack(side=tk.LEFT, padx=10)

        tk.Button(bottom, text="❌ Exit", bg="#F87171", fg="white",
                  command=root.destroy, **style_btn).pack(side=tk.RIGHT, padx=10)

    # ---------------- FUNCTIONS ----------------
    def display_products(self):
        col, row = 0, 0
        for category, items in PRODUCTS.items():
            cat_frame = tk.LabelFrame(self.prod_frame, text=category,
                                      bg="#A7F3D0", fg="#064E3B", font=("Arial Rounded MT Bold", 12),
                                      labelanchor="n", padx=10, pady=10)
            cat_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

            for product, (price, tax) in items.items():
                frame = tk.Frame(cat_frame, bg="#ECFDF5")
                frame.pack(fill=tk.X, pady=2)
                tk.Label(frame, text=product, font=("Arial", 11), bg="#ECFDF5", width=20, anchor="w").pack(side=tk.LEFT)
                tk.Label(frame, text=f"₹{price}", font=("Arial", 11), bg="#ECFDF5", width=8).pack(side=tk.LEFT)
                q_var = tk.StringVar(value="0")
                self.quantity_vars[product] = (q_var, price, tax)
                tk.Entry(frame, textvariable=q_var, width=5, justify="center").pack(side=tk.LEFT)

            col += 1
            if col > 1:
                col = 0
                row += 1

    def clear_fields(self):
        self.customer_name.delete(0, tk.END)
        self.phone.delete(0, tk.END)
        self.points.delete(0, tk.END)
        self.points.insert(0, "0")
        self.bill_text.delete("1.0", tk.END)
        for var, _, _ in self.quantity_vars.values():
            var.set("0")

    def total_bill(self):
        name = self.customer_name.get().strip()
        phone = self.phone.get().strip()
        if not name or not phone:
            messagebox.showwarning("Missing Info", "Please enter customer name and phone number.")
            return

        purchased, subtotal, total_gst = [], 0, 0

        for product, (q_var, price, tax_rate) in self.quantity_vars.items():
            try:
                qty = int(q_var.get())
            except ValueError:
                qty = 0
            if qty > 0:
                item_total = price * qty
                gst_amount = item_total * tax_rate
                purchased.append((product, qty, price, tax_rate, item_total + gst_amount))
                subtotal += item_total
                total_gst += gst_amount

        if not purchased:
            messagebox.showinfo("No Items", "No items selected.")
            return

        grand_total = subtotal + total_gst
        self.last_bill = {
            "purchased": purchased,
            "subtotal": subtotal,
            "gst": total_gst,
            "grand_total": grand_total,
            "customer": name,
            "phone": phone,
            "datetime": datetime.now().strftime("%d-%b-%Y %I:%M %p")
        }

        self.bill_text.delete("1.0", tk.END)
        self.bill_text.insert(tk.END, f"NH66 Coastal Mart 🛍️\nDate: {self.last_bill['datetime']}\n")
        self.bill_text.insert(tk.END, f"Customer: {name}\nPhone: {phone}\n{'-'*40}\n")
        for p, q, price, tax, total in purchased:
            self.bill_text.insert(tk.END, f"{p[:18]:18} x{q:<2} ₹{total:>7.2f}\n")
        self.bill_text.insert(tk.END, f"\n{'-'*40}\n")
        self.bill_text.insert(tk.END, f"Subtotal: ₹{subtotal:.2f}\nGST: ₹{total_gst:.2f}\nTotal: ₹{grand_total:.2f}\n")
        self.bill_text.insert(tk.END, f"{'-'*40}\nThank you for shopping 🌊\n")

    def save_pdf(self):
        if not self.last_bill:
            messagebox.showwarning("No Bill", "Please generate a bill first.")
            return

        bill = self.last_bill
        os.makedirs("bills", exist_ok=True)
        file_name = f"bills/Bill_{bill['customer'].replace(' ', '')}{bill['phone'][-4:]}.pdf"
        pdf = canvas.Canvas(file_name, pagesize=A4)
        pdf.setFont("Helvetica-Bold", 18)
        pdf.drawString(180, 800, "NH66 Coastal Mart 🛍️")
        pdf.setFont("Helvetica", 11)
        pdf.drawString(50, 780, f"Date & Time: {bill['datetime']}")
        pdf.drawString(50, 765, f"Customer: {bill['customer']} | Phone: {bill['phone']}")
        pdf.line(50, 755, 550, 755)

        y = 735
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(50, y, "Product")
        pdf.drawString(250, y, "Qty")
        pdf.drawString(300, y, "Price")
        pdf.drawString(370, y, "GST")
        pdf.drawString(430, y, "Total")
        pdf.line(50, y - 5, 550, y - 5)
        y -= 20

        pdf.setFont("Helvetica", 11)
        for p, q, price, tax, total in bill["purchased"]:
            pdf.drawString(50, y, p[:20])
            pdf.drawString(260, y, str(q))
            pdf.drawString(310, y, f"{price}")
            pdf.drawString(380, y, f"{int(tax*100)}%")
            pdf.drawString(440, y, f"₹{round(total, 2)}")
            y -= 20

        pdf.line(50, y, 550, y)
        y -= 20
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(50, y, f"Subtotal: ₹{bill['subtotal']:.2f}")
        y -= 20
        pdf.drawString(50, y, f"Total GST: ₹{bill['gst']:.2f}")
        y -= 20
        pdf.drawString(50, y, f"Grand Total: ₹{bill['grand_total']:.2f}")
        y -= 40
        pdf.setFont("Helvetica-Oblique", 11)
        pdf.drawString(50, y, "Thank you for shopping with NH66 Coastal Mart 🌊")
        pdf.save()

        webbrowser.open_new_tab(f"file://{os.path.abspath(file_name)}")
        messagebox.showinfo("Saved", f"Bill saved as {file_name}")


# ---------------- RUN ----------------
if __name__ == "__main__":
    root = tk.Tk()
    app = BillingApp(root)
    root.mainloop()