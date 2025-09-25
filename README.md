# Odoo 18 Quick Setup Guide

A quick guide to setting up a local Odoo 18 development environment with **Python 3.11**.

### ⚙️ Prerequisites

-   Git
-   Python 3.11 (including the `venv` module)
-   PostgreSQL
-   System build tools and development libraries (e.g., `build-essential`, `python3.11-dev`, `libpq-dev` on Debian/Ubuntu).

### 🚀 Setup Steps

**1. Clone Repositories**
```bash
mkdir ~/odoo-project && cd ~/odoo-project
git clone --depth 1 --branch 18.0 https://www.github.com/odoo/odoo
git clone git@github.com:kubickaoliver/aktin_case_study.git
```

**2. Create venv & Install Dependencies**
```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r ./odoo/requirements.txt
```

**3. Create PostgreSQL User**
```bash
# The system will prompt for a password for the new 'odoo_user'
sudo -u postgres createuser --createdb --pwprompt odoo_user
```

**4. Create `odoo.conf` File**

Create the file `~/odoo-project/odoo.conf` with the following content and fill in your details:
```ini
[options]
admin_passwd = <your_master_password>
addons_path = ./odoo/addons,./aktin_case_study/addons
db_host = 127.0.0.1
db_port = 5432
db_user = odoo_user
db_password = <password_from_step_3>
xmlrpc_port = 8017
```

### ▶️ Run Server

```bash
# Make sure your venv is activated (source venv/bin/activate)
python3 ./odoo/odoo-bin -c odoo.conf
```
The server will be running at `http://localhost:8072`.

### ✅ Code Quality (Ruff Linter)

To maintain code quality, we use the **Ruff** linter and formatter.

**1. Install Ruff**
```bash
# Make sure your venv is activated
pip install ruff
```

**2. Run Ruff**

Run these commands from the project root:
```bash
# Check all custom addons for errors
ruff check addons

# Automatically fix all fixable errors
ruff check addons --fix
```