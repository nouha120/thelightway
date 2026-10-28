from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "API FastAPI pour The Light Way"}

@app.get("/predict-relapse/")
def predict_relapse():
    # Ici, on pourra ajouter le modèle IA
    return {"prediction": "Faible risque de rechute"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
