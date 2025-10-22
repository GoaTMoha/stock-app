👇



📦 Stock Manager App — Frontend



A lightweight, modular, and responsive frontend for the Stock Manager App — a personal inventory and sales management system built with Flask (backend) and HTML/CSS/JS (frontend).

This frontend connects to the existing backend REST API.



🚀 Features



🔐 Authentication: Login, Logout (via Flask session)



🧾 Clients Management: Add, list, search clients



📦 Products Management: Add, list, search, and view categories



💰 Sales \& Purchases: Record and view transactions



🏪 Inventory Overview: Real-time stock status



📊 Dashboard Analytics: Display sales, revenue, and product insights



⚙️ Cache \& Performance: Works smoothly with Redis caching (if enabled)



💻 Responsive Design: Optimized for desktop and tablet use



🧱 Folder Structure



frontend/

│

├── index.html             # Landing page (redirects to login if not authenticated)

├── login.html             # Login form

├── dashboard.html         # Dashboard overview

├── clients.html           # Clients management page

├── products.html          # Products management page

├── sales.html             # Sales creation \& history

├── purchases.html         # Purchases creation \& history

├── inventory.html         # Inventory overview

│

├── assets/

│   ├── css/

│   │   ├── style.css      # Global styles

│   │   ├── dashboard.css  # Dashboard-specific styling

│   │   └── forms.css      # Form and input styling

│   ├── js/

│   │   ├── main.js        # Shared JS logic (auth, routing, etc.)

│   │   ├── api.js         # All API calls (fetch wrappers)

│   │   ├── dashboard.js   # Dashboard data visualization

│   │   ├── clients.js     # CRUD operations for clients

│   │   ├── products.js    # CRUD operations for products

│   │   ├── sales.js       # Handle sales and purchases

│   │   └── inventory.js   # Manage and display inventory data

│   └── img/

│       └── logo.png       # App logo or icons

│

└── README.md              # (This file)



⚙️ Setup Instructions

1️⃣ Prerequisites



Make sure your backend Flask server is running:



flask run





By default, it runs on:



http://127.0.0.1:5000



2️⃣ Run the Frontend



You can serve the frontend using any local server.

For example, using VS Code Live Server or Python HTTP server:



cd frontend

python -m http.server 8080





Then open:



http://localhost:8080/



🔗 API Configuration



By default, all API calls are made to:



const API\_BASE\_URL = "http://127.0.0.1:5000/api";





If you deploy your backend separately, update the API\_BASE\_URL in assets/js/api.js.



🧠 Key Design Principles



Modular JS: Each page has its own script (clients.js, products.js, etc.)



Reusable Components: Shared header, sidebar, and modals for a consistent UI



Vanilla JS Fetch API: For all CRUD operations



Responsive CSS Grid Layouts



Session-based Authentication: Uses Flask-Login cookies (no localStorage tokens)



🎨 UI Guidelines



Color Palette:



Primary: #1E88E5



Secondary: #1565C0



Accent: #42A5F5



Background: #F5F7FA



Typography:



Font: Inter or Roboto, sans-serif



Layout:



Sidebar navigation for modules



Main content area for dynamic tables and forms



📊 Future Improvements (Optional)



Add DataTables.js for sorting/filtering tables



Add Chart.js for dashboard analytics



Add Toast notifications for user feedback



Add service worker for offline caching



Convert to a SPA (Single Page Application) using React or Vue later



🧪 Testing



Manually test each page after backend is running:



Login and verify redirect to dashboard



Create clients/products/sales and verify persistence



Reload dashboard and confirm cached performance



Check logs for any failed API requests



🛠️ Tech Stack

Layer		Technology

Frontend	HTML, CSS, Vanilla JS

Backend		Flask (Python)

Database	SQLite (or PostgreSQL for production)

Caching		Redis (optional)

Auth		Flask-Login Sessions

🧾 License



MIT License — free for personal and educational use.

