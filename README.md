# CodeAlpha_DataRedundancySystem
Cloud Computing Internship, Task 1: a system that classifies incoming data as **unique**, **duplicate** or **invalid (false positive)** and appends only unique, verified entries to the database.

## How it works
1. **Validation:** name and email required, valid email format, numeric phone.
2. **Duplicate email:** rejected with "Duplicate email: this email is already registered."
3. **Duplicate user:** same phone and a similar name (RapidFuzz >= 90%) is rejected.
4. Only valid, unique users are saved in the database.

## Run locally
```bash
python -m venv venv
venv\Scripts\activate      # Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
python app.py              # open http://127.0.0.1:5000
```
Open the page, register a user, then register the same email again to see the duplicate message.

## API
| Method | Route | Purpose |
|---|---|---|
| POST | /register | JSON `{name,email,phone}` |
| GET | /users | list stored users |

## Deploy to the cloud
**Option A, AWS EC2:** launch Ubuntu t2/t3.micro, open ports 22 and 80, then:
```bash
git clone <your-repo> && cd CodeAlpha_DataRedundancySystem
sudo apt update && sudo apt install -y python3-venv
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
sudo venv/bin/gunicorn -b 0.0.0.0:80 app:app
```
**Option B, Google Cloud Run (easiest):**
```bash
gcloud run deploy data-redundancy --source . --allow-unauthenticated --region asia-south1
```
**Option C, Render / Azure App Service:** connect the GitHub repo, start command `gunicorn app:app`.

> SQLite resets on serverless platforms. For persistent storage, point the code at AWS RDS / Cloud SQL (PostgreSQL) using SQLAlchemy or psycopg2 and an environment variable for credentials.
