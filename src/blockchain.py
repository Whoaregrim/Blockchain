from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from hashlib import sha256
import json
from typing import Iterable, Mapping


@dataclass(frozen=True)
class Transaction:
    sender: str
    recipient: str
    amount: float
    memo: str | None = None
    metadata: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Block:
    index: int
    timestamp: str
    transactions: tuple[Transaction, ...]
    previous_hash: str
    validator: str
    nonce: int
    hash: str


@dataclass
class Blockchain:
    validators: set[str]
    chain: list[Block] = field(default_factory=list)
    pending: list[Transaction] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.validators:
            raise ValueError("Нужен хотя бы один валидатор")
        if not self.chain:
            self.chain.append(self._create_genesis_block())

    def add_transaction(self, transaction: Transaction) -> None:
        self.pending.append(transaction)

    def mine_block(self, validator: str) -> Block:
        if validator not in self.validators:
            raise ValueError("Валидатор не авторизован")
        if not self.pending:
            raise ValueError("Нет транзакций для включения")

        previous_block = self.chain[-1]
        index = previous_block.index + 1
        timestamp = datetime.utcnow().isoformat()
        transactions = tuple(self.pending)
        nonce = 0
        block_hash = self._calculate_hash(
            index,
            timestamp,
            transactions,
            previous_block.hash,
            validator,
            nonce,
        )

        block = Block(
            index=index,
            timestamp=timestamp,
            transactions=transactions,
            previous_hash=previous_block.hash,
            validator=validator,
            nonce=nonce,
            hash=block_hash,
        )
        self.chain.append(block)
        self.pending.clear()
        return block

    def is_valid(self) -> bool:
        for current, previous in zip(self.chain[1:], self.chain[:-1]):
            if current.previous_hash != previous.hash:
                return False
            recalculated = self._calculate_hash(
                current.index,
                current.timestamp,
                current.transactions,
                current.previous_hash,
                current.validator,
                current.nonce,
            )
            if recalculated != current.hash:
                return False
            if current.validator not in self.validators:
                return False
        return True

    def _create_genesis_block(self) -> Block:
        timestamp = datetime.utcnow().isoformat()
        transactions: tuple[Transaction, ...] = tuple()
        validator = next(iter(self.validators))
        nonce = 0
        block_hash = self._calculate_hash(
            0,
            timestamp,
            transactions,
            "0",
            validator,
            nonce,
        )
        return Block(
            index=0,
            timestamp=timestamp,
            transactions=transactions,
            previous_hash="0",
            validator=validator,
            nonce=nonce,
            hash=block_hash,
        )

    @staticmethod
    def _calculate_hash(
        index: int,
        timestamp: str,
        transactions: Iterable[Transaction],
        previous_hash: str,
        validator: str,
        nonce: int,
    ) -> str:
        payload = "|".join(
            [
                str(index),
                timestamp,
                previous_hash,
                validator,
                str(nonce),
                ",".join(
                    "|".join(
                        [
                            f"{tx.sender}>{tx.recipient}:{tx.amount}:{tx.memo or ''}",
                            json.dumps(tx.metadata, sort_keys=True, ensure_ascii=False),
                        ]
                    )
                    for tx in transactions
                ),
            ]
        )
        return sha256(payload.encode("utf-8")).hexdigest()
