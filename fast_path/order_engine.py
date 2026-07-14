from __future__ import annotations

import logging
from typing import Sequence

import MetaTrader5 as mt5

from fast_path.models import Direction, OrderRequest, SentOrder

logger = logging.getLogger(__name__)


class OrderEngine:
    def __init__(self, magic: int, terminal_path: str | None = None) -> None:
        self._magic = magic
        self._terminal_path = terminal_path
        self._connected = False

    def connect(self) -> None:
        if self._connected:
            return
        kwargs = {}
        if self._terminal_path:
            kwargs["path"] = self._terminal_path
        if not mt5.initialize(**kwargs):
            raise RuntimeError(f"MT5 initialize failed: {mt5.last_error()}")
        self._connected = True
        logger.info("MT5 connected")

    def disconnect(self) -> None:
        if self._connected:
            mt5.shutdown()
            self._connected = False

    def send_all(self, orders: Sequence[OrderRequest]) -> list[SentOrder]:
        if not self._connected:
            self.connect()

        results: list[SentOrder] = []
        for order in orders:
            results.append(self._send_market(order))
        return results

    def _send_market(self, order: OrderRequest) -> SentOrder:
        symbol_info = mt5.symbol_info(order.symbol)
        if symbol_info is None:
            return SentOrder(
                request=order,
                ticket=None,
                retcode=None,
                error=f"Symbol not found: {order.symbol}",
            )
        if not symbol_info.visible:
            if not mt5.symbol_select(order.symbol, True):
                return SentOrder(
                    request=order,
                    ticket=None,
                    retcode=None,
                    error=f"symbol_select failed: {order.symbol}",
                )

        tick = mt5.symbol_info_tick(order.symbol)
        if tick is None:
            return SentOrder(
                request=order,
                ticket=None,
                retcode=None,
                error=f"No tick for {order.symbol}",
            )

        price = tick.ask if order.direction == Direction.BUY else tick.bid
        order_type = (
            mt5.ORDER_TYPE_BUY if order.direction == Direction.BUY else mt5.ORDER_TYPE_SELL
        )

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": order.symbol,
            "volume": order.lot,
            "type": order_type,
            "price": price,
            "sl": order.sl or 0.0,
            "tp": order.tp or 0.0,
            "deviation": 30,
            "magic": order.magic,
            "comment": order.comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        result = mt5.order_send(request)
        if result is None:
            return SentOrder(
                request=order,
                ticket=None,
                retcode=None,
                error=f"order_send returned None: {mt5.last_error()}",
            )

        ok = result.retcode == mt5.TRADE_RETCODE_DONE
        return SentOrder(
            request=order,
            ticket=result.order if ok else None,
            retcode=result.retcode,
            error=None if ok else result.comment,
        )
