import streamlit as st

# ================================
# 🏦 OOP: BankAccount Class
# ================================
class BankAccount:
    def __init__(self, owner, account_type):
        self.owner = owner
        self.account_type = account_type  # 'Savings' or 'Current'
        self.balance = 0.0

    def deposit(self, amount):
        if amount <= 0:
            return "❌ Deposit must be greater than ₦0"
        self.balance += amount
        return f"✅ ₦{amount:,.2f} deposited to your {self.account_type} account."

    def withdraw(self, amount):
        if amount <= 0:
            return "❌ Withdrawal must be greater than ₦0"
        if amount > self.balance:
            return "❌ Insufficient balance"
        self.balance -= amount
        return f"💸 ₦{amount:,.2f} withdrawn from your {self.account_type} account."

    def get_balance(self):
        return f"💼 Your {self.account_type} account balance is ₦{self.balance:,.2f}"

# ================================
# 🖥️ Streamlit UI
# ================================
st.set_page_config(page_title="UnionEdge Bank", page_icon="🏦")
st.title("🏦 UnionEdge Bank")
st.markdown("#### 💳 Digital Banking for You — Secure, Smart & Simple")

# Keep account in session
if 'account' not in st.session_state:
    st.session_state.account = None

# Step 1: Account Creation
st.header("🧾 Open a Bank Account")
name = st.text_input("👤 Enter your full name:")
account_type = st.selectbox("🏷️ Choose account type:", ["Savings", "Current"])

if st.button("🆕 Create Account"):
    if name.strip() == "":
        st.error("Please enter your name.")
    else:
        st.session_state.account = BankAccount(name, account_type)
        st.success(f"🎉 Account created for **{name}** ({account_type})")

# Step 2: Transactions
if st.session_state.account:
    st.divider()
    st.header("💰 Manage Your Account")
    st.markdown(f"👋 Hello **{st.session_state.account.owner}** | Account Type: **{st.session_state.account.account_type}**")

    amount = st.number_input("Enter amount (₦)", min_value=0.0, step=100.0)

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("➕ Deposit"):
            msg = st.session_state.account.deposit(amount)
            st.success(msg)

    with col2:
        if st.button("➖ Withdraw"):
            msg = st.session_state.account.withdraw(amount)
            st.warning(msg)

    with col3:
        if st.button("📊 Check Balance"):
            msg = st.session_state.account.get_balance()
            st.info(msg)

    st.caption("🔐 Secured by UnionEdge Bank | Built with 💙 and Python 🐍")
