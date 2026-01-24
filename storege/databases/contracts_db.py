from pathlib import Path
from typing import Dict, List
import json
from dataclasses import dataclass, asdict

@dataclass
class Contract:
    id: str
    contractor_name: str
    partner_name: str
    conditions: str

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'Contract':
        return cls(**data)

class ContractsDatabase:
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.contracts: Dict[str, Contract] = {}
        self.load()

    def load(self):
        if self.db_path.exists():
            try:
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.contracts = {cid: Contract.from_dict(cdata) for cid, cdata in data.items()}
            except:
                self.contracts = {}

    def save(self):
        data = {cid: contract.to_dict() for cid, contract in self.contracts.items()}
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add_contract(self, contract: Contract) -> bool:
        if contract.id in self.contracts:
            return False
        self.contracts[contract.id] = contract
        self.save()
        return True