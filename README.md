#  RFIDAuthX – Secure RFID Access Control System

A complete RFID-based access control backend built using **FastAPI**, **PostgreSQL**, and **NodeMCU + RC522**.  
This system allows **secure admin-only registration**, **login/logout tracking**, and **real-time user monitoring** — all authenticated via **JWT OAuth2 tokens**.



---

##  Features

- **RFID-based Login/Logout** using NodeMCU + RC522
-  **Admin-only Registration** with OAuth2 + JWT
-  **Smart User Presence Detection** (based on latest log)
-  View **Registered Users** and **Full Access Logs**
-  Cancel ongoing registration
-  Timeout logic (auto-cancel if card not scanned in 30s)
-  Track individual user's log history

---

##  Folder Structure

RFIDAuthX/<br/>
│
├── dev-app/ <br/>
│ ├── main.py<br/>
│     ├── models.py<br/>
│     ├── schemas.py<br/>
│     ├── access.py<br/>
│     ├── security.py<br/>
│     ├── database.py<br/>
│     └── requirements.txt<br/>


---

##  Tech Stack

| Layer        | Tools Used                         |
|--------------|------------------------------------|
| Backend      | FastAPI, Pydantic, SQLAlchemy      |
| Auth         | OAuth2, JWT (python-jose)          |
| Database     | PostgreSQL                         |
| Hardware     | NodeMCU (ESP8266), RFID RC522      |
| Misc         | Passlib (password hashing), Uvicorn|

---

##  Getting Started

### 🔧 Prerequisites
- Python 3.8+
- PostgreSQL
- NodeMCU with RFID-RC522 module

###  Setup

1. Clone the repo  
   ```bash
   git clone https://github.com/N-ADITHYA/RFIDAuthX.git
   cd RFIDAuthX/dev-app
   ```
2. Install dependencies
   ```bash
    pip install -r requirements.txt
    Configure .env or update DATABASE_URL in database.py
   ```
3. Configure .env or update DATABASE_URL in database.py

   
4. Run the FastAPI server
    ```
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
    ```

 ## Admin API Endpoints (Token Protected)
 | Endpoint                            | Description                     |
| ----------------------------------- | ------------------------------- |
| `POST /login`                       | Admin login (returns JWT token) |
| `POST /start_registration`          | Initiate new user registration  |
| `POST /cancel_registration`         | Abort registration process      |
| `GET  /users`                       | List all registered users       |
| `GET  /logs`                        | View full scan history          |
| `GET  /get_current_users_logged_in` | Show currently logged-in users  |
| `GET  /users/{id}/logs`             | Logs of a specific user         |


Use Swagger UI: ```http://localhost:8000/docs```

## How It Works
-> Admin logs in → receives JWT

-> Admin starts registration with user name + phone

-> System waits for card scan (within 30s)

-> On scan → UID is bound to the user and saved

-> Future scans log the user in/out automatically

If scan doesn’t happen in 30s → registration expires <br/>
If card/mobile is duplicate → error returned


## Blog Series
Part 1 – [Building the RFID Access System](https://rfid-tag.hashnode.dev/how-i-built-an-rfid-access-thing-using-nodemcu-and-fastapi?source=more_articles_bottom_blogs)

Part 2 – [Admin-Only Registration](https://rfid-tag.hashnode.dev/the-admin-powers-to-my-rfid-fastapi-system-is-here-part-2?source=more_articles_bottom_blogs)

Part 3 – [Power Mode ON (Logs, Live Tracking)](https://rfid-tag.hashnode.dev/part-3-of-my-rfid-system-has-got-some-cool-features)



 ## Want to Contribute or Connect?
Got feedback or wanna try it out?

 Contact me at: www.iadiee.live/#contact <br/>
 Star the repo if you liked it
 Issues and PRs are welcome!

---
  
 ## License

This project is licensed under the [MIT License](LICENSE).


