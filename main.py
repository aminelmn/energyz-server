from fastapi import FastAPI, Request
from typing import Any, Dict
from eneryz import projets as handle_pay_request, projets as handle_notif_request

app = FastAPI()

@app.post("/to_pay_energyz")
async def to_pay_energyz(request: Request):
    body = await request.json()
    return await handle_pay_request(body)

@app.post("/energyz_notif")
async def energyz_notif(request: Request):
    body = await request.json()
    return await handle_notif_request(body)
