<<<<<<< HEAD
# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.
=======
# Askara AI – Smart Exam Practice Tool

Askara AI is a smart exam prediction system that helps students prepare for exams faster and more effectively.  
It analyzes patterns from past exam papers and uses AI to generate likely future questions.  
Students can instantly view answers and ask for clarifications just like having a personal tutor.

---

## What It Does

- Predicts likely exam questions using past papers and topic modeling  
- Lets users generate one question at a time to simulate real exam practice  
- Provides instant answers using an AI model (GPT)  
- Offers follow-up clarifications when needed  
- Now supports a clean, interactive web UI with question history  

---

## Tech Stack

| Layer       | Tool / Library        |
|-------------|------------------------|
| Frontend    | React (Vite), CSS      |
| Backend     | FastAPI (Python)       |
| AI Model    | OpenAI GPT-4 (via API) |
| Embedding   | Sentence Transformers  |
| Topic Model | BERTopic (UMAP + HDBSCAN) |

---

## What's New (Updated Version)

This is an updated version of the original Askara AI project, which was previously built using Gradio.

We’ve now implemented:  
- A fully custom React frontend (replacing Gradio)  
- A FastAPI backend to handle API requests securely  
- Improved UI/UX with scrolling, question flow, and clarification input  
- Cleaner project structure for production readiness  

The core prediction logic still follows the same method:  
Past papers → Topic modeling → Sampling → GPT-4 → Predicted questions  

---

## Preview Screenshot

<img src="screenshots/askara_homepage.png" width="100%" alt="Askara AI Screenshot" />


---

## Project Structure

### askara-ai/

#### backend/
- `main.py` – Backend routes and GPT logic
- `...` – Other FastAPI files

#### frontend/
- `App.jsx` – React UI logic
- `App.css` – Frontend styling
- `...` – Other React components

#### Root Files
- `README.md` – Project documentation
- `requirements.txt` – Python dependencies
- `...` – Additional config or data files


## How to Run It Locally

### Backend (FastAPI)

cd backend
pip install -r requirements.txt
uvicorn main:app --reload


### Frontend (React)

cd frontend
npm install
npm run dev


Make sure your frontend points to the FastAPI backend (e.g., http://localhost:8000).

---

## Upcoming Improvements

- "Next Question" flow (already added)  
- Session summary view  
- Question difficulty selection  
- Save session history (optional)  

---

## Author
Marvellous Chitenga  
Computer Engineering @ Vistula University  
AI, backend systems, and building real-world tools  

---

## Live Demo (Coming Soon)

Hosted version will be added here once deployed on Vercel or GCP Cloud Run.



>>>>>>> 
