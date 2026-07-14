from __future__ import annotations

from fast_path.models import OrderRequest, ParsedSignal


class OrderBuilder:
    def __init__(self, magic: int) -> None:
        self._magic = magic

    def build(self, signal: ParsedSignal) -> list[OrderRequest]:
        orders: list[OrderRequest] = []
        for index, leg in enumerate(signal.legs):
            comment = f"{signal.provider}_{signal.signal_id}_{index}"
            orders.append(
                OrderRequest(
                    symbol=leg.symbol,
                    direction=leg.direction,
                    lot=leg.lot,
                    sl=leg.sl,
                    tp=leg.tp,
                    magic=self._magic,
                    comment=comment[:31],
                    signal_id=signal.signal_id,
                    signal_uuid=signal.signal_uuid,
                    provider=signal.provider,
                    leg_index=index,
                )
            )
        return orders
