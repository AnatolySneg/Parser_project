import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello_world"}


if __name__ == "__main__":
    # uvicorn.run(app="main:app", reload=True)
    uvicorn.run(app="main:app", port=8888, reload=True)

    """
    From command line$ uvicorn main:app --host 192.168.0.165 --port 8000 --reload
    or
    $ uvicorn main:app  --reload
    """
