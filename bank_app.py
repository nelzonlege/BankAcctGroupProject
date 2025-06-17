import streamlit as st
from datetime import datetime
import json


class Account:
    """Base Account class"""

    def _init_(self, account_number, account_holder, initial_balance=0):
        self.account_number = account_number
        self.account_holder = account_holder
        self.balance = initial_balance
        self.transaction_history = []
        self.created_date = datetime.now()

    def get_balance(self):
        return self.balance

    def add_transaction(self, transaction_type, amount, description=""):
        transaction = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": transaction_type,
            "amount": amount,
            "balance": self.balance,
            "description": description
        }
        self.transaction_history.append(transaction)


class SavingsAccount(Account):
    """Savings Account with withdrawal limit"""

    def _init_(self, account_number, account_holder, initial_balance=0, withdrawal_limit=5000):
        super()._init_(account_number, account_holder, initial_balance)
        self.account_type = "Savings"
        self.withdrawal_limit = withdrawal_limit

    def deposit(self, amount):
        """Deposit method for savings account"""
        if amount <= 0:
            return False, "Deposit amount must be positive"

        self.balance += amount
        self.add_transaction("DEPOSIT", amount, "Deposit to savings account")
        return True, f"Successfully deposited ${amount:.2f}. New balance: ${self.balance:.2f}"

    def withdraw(self, amount):
        """Withdrawal method with limit for savings account"""
        if amount <= 0:
            return False, "Withdrawal amount must be positive"

        if amount > self.withdrawal_limit:
            return False, f"Withdrawal amount exceeds limit of ${self.withdrawal_limit:.2f}"

        if amount > self.balance:
            return False, "Insufficient funds"

        self.balance -= amount
        self.add_transaction("WITHDRAWAL", amount, "Withdrawal from savings account")
        return True, f"Successfully withdrew ${amount:.2f}. New balance: ${self.balance:.2f}"


class CurrentAccount(Account):
    """Current Account with overdraft facility"""

    def _init_(self, account_number, account_holder, initial_balance=0, overdraft_limit=1000):
        super()._init_(account_number, account_holder, initial_balance)
        self.account_type = "Current"
        self.overdraft_limit = overdraft_limit

    def deposit(self, amount):
        """Deposit method for current account"""
        if amount <= 0:
            return False, "Deposit amount must be positive"

        self.balance += amount
        self.add_transaction("DEPOSIT", amount, "Deposit to current account")
        return True, f"Successfully deposited ${amount:.2f}. New balance: ${self.balance:.2f}"

    def withdraw(self, amount):
        """Withdrawal method for current account with overdraft"""
        if amount <= 0:
            return False, "Withdrawal amount must be positive"

        available_balance = self.balance + self.overdraft_limit
        

        if amount > available_balance:
            return False, f"Insufficient funds. Available balance (including overdraft): ${available_balance:.2f}"

        self.balance -= amount
        self.add_transaction("WITHDRAWAL", amount, "Withdrawal from current account")
        return True, f"Successfully withdrew ${amount:.2f}. New balance: ${self.balance:.2f}"


# Initialize session state
if 'accounts' not in st.session_state:
    st.session_state.accounts = {}
if 'current_account' not in st.session_state:
    st.session_state.current_account = None


def main():
    st.set_page_config(page_title="Banking System", page_icon="🏦", layout="wide")

    # Header
    st.title("🏦 Banking System")
    st.markdown("---")

    # Sidebar for account selection
    with st.sidebar:
        st.header("Account Management")

        # Create new account
        with st.expander("Create New Account"):
            account_type = st.selectbox("Account Type", ["Savings", "Current"])
            account_holder = st.text_input("Account Holder Name")
            initial_balance = st.number_input("Initial Balance", min_value=0.0, value=100.0, step=10.0)

            if account_type == "Savings":
                withdrawal_limit = st.number_input("Withdrawal Limit", min_value=1000.0, value=5000.0, step=500.0)
            else:
                overdraft_limit = st.number_input("Overdraft Limit", min_value=0.0, value=1000.0, step=100.0)

            if st.button("Create Account"):
                if account_holder:
                    account_number = f"{account_type.upper()}{len(st.session_state.accounts) + 1:04d}"

                    if account_type == "Savings":
                        account = SavingsAccount(account_number, account_holder, initial_balance, withdrawal_limit)
                    else:
                        account = CurrentAccount(account_number, account_holder, initial_balance, overdraft_limit)

                    st.session_state.accounts[account_number] = account
                    st.success(f"Account {account_number} created successfully!")
                else:
                    st.error("Please enter account holder name")

        # Select existing account
        if st.session_state.accounts:
            st.markdown("### Select Account")
            account_options = [f"{acc_num} - {acc.account_holder} ({acc.account_type})"
                               for acc_num, acc in st.session_state.accounts.items()]

            selected_option = st.selectbox("Choose Account", [""] + account_options)

            if selected_option:
                account_number = selected_option.split(" - ")[0]
                st.session_state.current_account = st.session_state.accounts[account_number]

  # Main content area
    if st.session_state.current_account is None:
        st.info("👈 Please create or select an account from the sidebar to get started.")

        # Show overview of all accounts if any exist
        if st.session_state.accounts:
            st.subheader("All Accounts Overview")

            for acc_num, account in st.session_state.accounts.items():
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Account", acc_num)
                with col2:
                    st.metric("Holder", account.account_holder)
                with col3:
                    st.metric("Type", account.account_type)
                with col4:
                    st.metric("Balance", f"${account.balance:.2f}")
                st.markdown("---")

    else:
        account = st.session_state.current_account

        # Account information
        col1, col2 = st.columns(2)

        with col1:
            st.subheader(f"Account Details")
            st.write(f"**Account Number:** {account.account_number}")
            st.write(f"**Account Holder:** {account.account_holder}")
            st.write(f"**Account Type:** {account.account_type}")
            st.write(f"**Current Balance:** ${account.balance:.2f}")

            if hasattr(account, 'withdrawal_limit'):
                st.write(f"**Withdrawal Limit:** ${account.withdrawal_limit:.2f}")
            if hasattr(account, 'overdraft_limit'):
                st.write(f"**Overdraft Limit:** ${account.overdraft_limit:.2f}")

        with col2:
            st.subheader("Quick Stats")
            total_deposits = sum([t['amount'] for t in account.transaction_history if t['type'] == 'DEPOSIT'])
            total_withdrawals = sum([t['amount'] for t in account.transaction_history if t['type'] == 'WITHDRAWAL'])

            st.metric("Total Deposits", f"${total_deposits:.2f}")
            st.metric("Total Withdrawals", f"${total_withdrawals:.2f}")
            st.metric("Transaction Count", len(account.transaction_history))

        st.markdown("---")

 # Transaction operations
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("💰 Deposit")
            deposit_amount = st.number_input("Deposit Amount", min_value=0.01, value=100.0, step=10.0, key="deposit")

            if st.button("Make Deposit", type="primary"):
                success, message = account.deposit(deposit_amount)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

        with col2:
            st.subheader("💸 Withdrawal")
            withdraw_amount = st.number_input("Withdrawal Amount", min_value=0.01, value=50.0, step=10.0,
                                              key="withdraw")

            # Show withdrawal limit warning for savings accounts
            if hasattr(account, 'withdrawal_limit'):
                if withdraw_amount > account.withdrawal_limit:
                    st.warning(f"⚠ Amount exceeds withdrawal limit of ${account.withdrawal_limit:.2f}")

            if st.button("Make Withdrawal", type="secondary"):
                success, message = account.withdraw(withdraw_amount)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

        st.markdown("---")

        # Transaction history
        st.subheader("📊 Transaction History")

        if account.transaction_history:
            # Show recent transactions
            recent_transactions = account.transaction_history[-10:]  # Last 10 transactions

            for transaction in reversed(recent_transactions):
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

                with col1:
                    st.write(f"{transaction['date']}")
                    st.write(transaction['description'])

                with col2:
                    transaction_type = transaction['type']
                    color = "🟢" if transaction_type == "DEPOSIT" else "🔴"
                    st.write(f"{color} {transaction_type}")

                with col3:
                    amount_sign = "+" if transaction['type'] == "DEPOSIT" else "-"
                    st.write(f"{amount_sign}${transaction['amount']:.2f}")

                with col4:
                    st.write(f"${transaction['balance']:.2f}")
                    
                st.markdown("---")

            if len(account.transaction_history) > 10:
                st.info(f"Showing last 10 transactions. Total transactions: {len(account.transaction_history)}")
        else:
            st.info("No transactions yet. Make your first deposit or withdrawal!")


if _name_ == "_main_":

    main()       
