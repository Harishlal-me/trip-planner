🌍 Trip Planner – AI-Powered Travel Recommendation System

An intelligent AI-powered trip planning platform that helps users plan trips by recommending destinations, estimating budgets, optimizing routes, and integrating real-world travel data such as weather, geolocation, and country information.

This project is designed with scalability, modularity, and ML best practices, making it suitable for hackathons, academic projects, and real-world deployment.

✨ Features

🧠 Machine Learning–based destination ranking

💰 Budget prediction & cost indexing

🗺️ Route optimization using OSRM

🌦️ Live weather integration

🌍 Geocoding & country metadata

⚡ FastAPI backend with modular architecture

🧪 Model training & evaluation pipelines

🏗️ Project Structure
trip-planner-ml/
├── api/                    # FastAPI routes
│   └── routes/
├── data/
│   ├── kaggle_loader.py    # Dataset download logic
│   ├── data_preprocessor.py
│   └── feature_engineering.py
├── models/
│   ├── recommender/        # Destination ranking ML
│   ├── budget_prediction/ # Budget estimation ML
│   └── training/           # Trainer & evaluator
├── routing/                # Route optimization
├── services/               # External API integrations
├── frontend/               # Basic frontend (HTML)
├── main.py                 # FastAPI app entry point
├── requirements.txt
├── .gitignore
└── README.md

📊 Datasets

⚠️ Large datasets are NOT included in this repository due to GitHub size limits.

Why?

GitHub blocks files > 100 MB

Best practice: keep repos lightweight and reproducible

How to get data

Use the provided data loader scripts:

python data/kaggle_loader.py


Dataset sources may include Kaggle, OpenStreetMap, public travel datasets, and open APIs.

🚀 Getting Started
1️⃣ Clone the repository
git clone https://github.com/Harishlal-me/trip-planner.git
cd trip-planner

2️⃣ Create virtual environment
python -m venv venv
venv\Scripts\activate   # Windows

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Run the FastAPI server
uvicorn main:app --reload


Server will start at:

http://127.0.0.1:8000


API docs:

http://127.0.0.1:8000/docs

🧠 Machine Learning Components

Destination Ranking Model

Uses engineered features to score and rank travel locations

Budget Prediction Model

Predicts estimated trip cost based on destination, duration, and preferences

Evaluation Pipeline

Accuracy and performance metrics for model validation

🔐 Environment Variables

Create a .env file (not committed):

OPENWEATHER_API_KEY=your_key_here

🛠️ Tech Stack

Backend: FastAPI, Python

ML: scikit-learn, NumPy, Pandas

Routing: OSRM

APIs: OpenWeather, Nominatim, REST Countries

Data: Kaggle datasets, OpenStreetMap

📌 Best Practices Followed

✅ No large datasets in GitHub

✅ Modular architecture

✅ Clear separation of ML, services, and API layers

✅ Reproducible environment with requirements.txt

🚧 Future Enhancements

Frontend UI (React / Next.js)

User personalization & profiles

Real-time price tracking

Recommendation explainability

Cloud deployment (Render / AWS / Railway)

📜 License

This project is for educational and research purposes.

👨‍💻 Author

Harishlal
B.Tech CSE | Machine Learning & Backend Development
GitHub: https://github.com/Harishlal-me

⭐ If you like this project, give it a star!
