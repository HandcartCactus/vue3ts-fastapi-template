# Template For App

## Dev
### Backend
Cd to the backend project folder:
```bash
cd backend
```
If a venv does not exist, create one.
```bash
python3 -m venv venv
```
Activate the venv.
```bash
source venv/bin/activate
```
Install/update dependencies once in the venv.
```bash
pip install -r requirements.txt
```
Launch the API server.
```bash
uvicorn app.main:app --reload
```
Run tests (within venv and backend dir)
```bash
pytest
```


