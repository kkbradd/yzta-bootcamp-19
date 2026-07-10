"""WebSocket giren ucu: /ws/canli — bağlantı kabulü (plan Bölüm 9).

Yayının kendisi çıkan adaptörde (ws_yayin.BaglantiYoneticisi); bu uç yalnızca
istemcileri yöneticiye kaydeder ve kopuşu bekler.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

ws_router = APIRouter()


@ws_router.websocket("/ws/canli")
async def canli_yayin(websocket: WebSocket) -> None:
    yonetici = websocket.app.state.ws_yonetici
    await yonetici.baglan(websocket)
    try:
        while True:
            # İstemciden veri beklenmez; receive yalnızca kopuşu algılamak için.
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        # Her çıkış yolunda temizlik: beklenmeyen istisnada da bağlantı sette kalmasın.
        yonetici.kopar(websocket)
