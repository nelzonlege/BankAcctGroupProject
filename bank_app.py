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

    
