from blockchain import Blockchain, Transaction


def main() -> None:
    chain = Blockchain(validators={"validator-1", "validator-2"})
    chain.add_transaction(
        Transaction(
            "supplier",
            "warehouse",
            120,
            "Приёмка",
            metadata={"voucher": "VT-2024-0001", "color": "blue"},
        )
    )
    chain.add_transaction(
        Transaction(
            "warehouse",
            "production",
            80,
            "Передача в работу",
            metadata={"voucher": "VT-2024-0001", "color": "blue"},
        )
    )

    block = chain.mine_block("validator-1")

    print("Новый блок создан:")
    print(f"  index={block.index}")
    print(f"  hash={block.hash}")
    print(f"  previous_hash={block.previous_hash}")
    print(f"  transactions={len(block.transactions)}")
    print(f"  chain_valid={chain.is_valid()}")


if __name__ == "__main__":
    main()
