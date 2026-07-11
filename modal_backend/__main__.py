import uvicorn

from modal_backend.routes.base import app

if __name__ == '__main__':
    uvicorn.run(app)
