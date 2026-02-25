# How to Run the HABO Backend
# The backend is Python — it runs in VS Code (or any terminal), NOT in Xcode.
# Xcode is only for your iOS Swift app.

===========================================================================
WHAT YOU NEED INSTALLED ON YOUR MAC
===========================================================================

1. Python 3.11 or newer
   Check if you have it: open Terminal and type:
     python3 --version
   If you see "Python 3.11.x" or higher you are good.
   If not, download from: https://www.python.org/downloads/

2. VS Code (recommended editor for the backend)
   Download from: https://code.visualstudio.com
   Install the Python extension inside VS Code
   (click Extensions icon on left sidebar, search "Python", install the Microsoft one)

3. A Supabase account (free) for the database
   Sign up at: https://supabase.com

4. A Railway account (free) for hosting
   Sign up at: https://railway.app


===========================================================================
STEP 1 — SET UP THE FOLDER
===========================================================================

1. Create a new folder on your Mac called "habo_backend"
   Put it somewhere easy to find, like your Desktop or Documents

2. Copy all the backend files into it so the structure looks like:

   habo_backend/
     app/
       __init__.py
       config.py
       database.py
       main.py
       models/
         __init__.py
         user.py
         task.py
         chat.py
       schemas/
         __init__.py
         user.py
         task.py
         chat.py
         payment.py
       routers/
         __init__.py
         auth.py
         tasks.py
         users.py
         chat.py
         payments.py
       services/
         __init__.py
         auth_service.py
         task_service.py
         user_service.py
         chat_service.py
         payment_service.py
     alembic/
       env.py
       versions/
         001_initial.py
     alembic.ini
     requirements.txt
     railway.toml
     .env           ← you will create this in Step 3


===========================================================================
STEP 2 — OPEN THE FOLDER IN VS CODE
===========================================================================

1. Open VS Code
2. Click File → Open Folder
3. Select your habo_backend folder
4. Click Open

You will see all the files in the left sidebar.


===========================================================================
STEP 3 — CREATE YOUR .env FILE
===========================================================================

In VS Code, right-click in the file explorer sidebar and click "New File".
Name it exactly:   .env

Paste this into it and fill in your real values:

DATABASE_URL=postgresql://postgres:[YOUR_PASSWORD]@db.[YOUR_PROJECT_REF].supabase.co:5432/postgres
SECRET_KEY=any-long-random-string-at-least-32-characters-long
RAILWAY_TOKEN=fill-this-in-later
RAZORPAY_KEY_ID=rzp_test_xxxxxxxxxxxx
RAZORPAY_KEY_SECRET=your-razorpay-secret
ALLOWED_ORIGINS=http://localhost:8081

Where to get DATABASE_URL:
  - Go to supabase.com → your project → Settings → Database
  - Scroll to "Connection string" → copy the URI format
  - Replace [YOUR-PASSWORD] with your actual database password


===========================================================================
STEP 4 — OPEN THE TERMINAL IN VS CODE
===========================================================================

In VS Code press:   Ctrl + ` (backtick key, top-left of keyboard)
OR go to: Terminal → New Terminal

A terminal panel opens at the bottom of VS Code.
You should see your habo_backend folder path in the prompt.


===========================================================================
STEP 5 — CREATE A VIRTUAL ENVIRONMENT
===========================================================================

A virtual environment keeps your project's Python packages separate.
Type these commands one at a time, pressing Enter after each:

  python3 -m venv venv

Wait a few seconds. Then activate it:

  On Mac:
    source venv/bin/activate

You will see (venv) appear at the start of your terminal prompt.
This means it worked. Always make sure you see (venv) before running commands.


===========================================================================
STEP 6 — INSTALL DEPENDENCIES
===========================================================================

With (venv) active, type:

  pip install -r requirements.txt

This will download and install all the required Python packages.
It takes 1–3 minutes. You will see a lot of text scrolling — that is normal.
Wait for it to finish and return to your prompt.


===========================================================================
STEP 7 — RUN DATABASE MIGRATIONS
===========================================================================

This creates all the tables in your Supabase database.
Make sure your .env file has the correct DATABASE_URL first.

Type:
  alembic upgrade head

You will see output like:
  INFO  [alembic.runtime.migration] Running upgrade  -> 001_initial

If you see an error about "could not connect", your DATABASE_URL is wrong.
Double check it in Supabase settings.


===========================================================================
STEP 8 — START THE SERVER
===========================================================================

Type:
  uvicorn app.main:app --reload --port 8000

You will see:
  INFO:     Uvicorn running on http://127.0.0.1:8000

The server is now running on your Mac!
--reload means it automatically restarts when you change any Python file.


===========================================================================
STEP 9 — TEST IT IS WORKING
===========================================================================

Open your browser and go to:
  http://localhost:8000/health

You should see:
  {"status":"ok","service":"HABO MicroGigs API"}

Also open:
  http://localhost:8000/docs

This shows you the full API documentation with all endpoints.
You can test each endpoint directly from this page.


===========================================================================
STEP 10 — UPDATE YOUR IOS APP TO POINT TO THE SERVER
===========================================================================

While developing on the same Mac:

Open APIClient.swift in Xcode and change:
  let API_BASE_URL = "http://localhost:8000"

When testing on a physical iPhone on the same WiFi:
  Find your Mac's local IP address (System Settings → WiFi → Details)
  It will be something like 192.168.1.5
  Change it to:
  let API_BASE_URL = "http://192.168.1.5:8000"

For production (after deploying to Railway):
  let API_BASE_URL = "https://your-app-name.railway.app"


===========================================================================
STEP 11 — DEPLOY TO RAILWAY (so iPhone works anywhere)
===========================================================================

1. Install Railway CLI:
   Open Terminal and type:
     npm install -g @railway/cli

2. Login:
     railway login

3. Inside your habo_backend folder:
     railway init
     railway up

4. Set environment variables in Railway dashboard:
   - Go to railway.app → your project → Variables
   - Add each line from your .env file as a separate variable

5. Your backend gets a public URL like:
     https://habo-backend-production.railway.app

6. Update APIClient.swift with that URL and rebuild in Xcode.


===========================================================================
DAILY WORKFLOW
===========================================================================

Every time you want to work on the backend:

1. Open VS Code → open habo_backend folder
2. Open Terminal (Ctrl+`)
3. Type:  source venv/bin/activate
4. Type:  uvicorn app.main:app --reload --port 8000
5. Leave it running in the background while you work in Xcode

To stop the server: press Ctrl+C in the VS Code terminal


===========================================================================
TROUBLESHOOTING
===========================================================================

"command not found: uvicorn"
  → You forgot to activate venv. Run: source venv/bin/activate

"connection refused" from iPhone app
  → Server not running, OR using localhost instead of your Mac's IP address

"could not translate host name" on alembic upgrade
  → DATABASE_URL in .env is wrong. Copy it again from Supabase settings.

"ModuleNotFoundError"
  → Run pip install -r requirements.txt again with venv active

Port 8000 already in use
  → Change port: uvicorn app.main:app --reload --port 8001
    And update API_BASE_URL in APIClient.swift to match
