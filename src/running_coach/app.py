from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/")
def test():
    res = {"test": "Hello World"}
    return JSONResponse(content=res, status_code=200)

