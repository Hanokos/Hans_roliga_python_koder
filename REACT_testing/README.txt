This is a react test. install the correct pip install and make sure that its structured like this:


my_project/
│── .venv/  ----------------------- OBS! not necessary, but I RECOMMEND a virtual environment.
│── backend/                               or it could screw up other codes you're doing.
│   ├── _pycache_/       
│   ├── main.py           # FastAPI backend
│   ├── requirements.txt  # Dependencies for Python
│── frontend/
│   ├── build/
│   ├── node_modules/
│   ├── public/
│   ├── src/
│   │   ├── App.jsx       # Main React component
│   │   ├── App.css       # Main React component
│   │   ├── App.test.js/
│   │   ├── index.css/
│   │   ├── index.js/
│   │   ├── reportWebVitals.js/
│   │   ├── setupTests.js/
│   ├── .gitignore       
│   ├── package.json          # Dependencies for React
│   ├── package-lock.json        
│   ├── README.md             # Instructions


you need to ahve two open terminals and run following commands in the right foldes to make it work:

bakend:
uvicorn main:app --reload

frontend:
npm start
