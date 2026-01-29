"""Position on the chess board."""
from dataclasses import dataclass
from typing import Literal


File = Literal["a", "b", "c", "d", "e", "f", "g", "h"]
Rank = Literal[1, 2, 3, 4, 5, 6, 7, 8]

FILES: list[File] = ["a", "b", "c", "d", "e", "f", "g", "h"]
RANKS: list[Rank] = [1, 2, 3, 4, 5, 6, 7, 8]


@dataclass
class Position:
    """Represents a position on the chess board."""
    file: File
    rank: Rank

    def to_dict(self) -> dict:
        """Convert position to dictionary."""
        return {"file": self.file, "rank": self.rank}

    @classmethod
    def from_dict(cls, data: dict) -> "Position":
        """Create a Position from a dictionary."""
        return cls(file=data["file"], rank=data["rank"])

    def to_indices(self) -> tuple[int, int]:
        """Convert to array indices (file_idx, rank_idx)."""
        file_idx = FILES.index(self.file)
        rank_idx = self.rank - 1
        return file_idx, rank_idx

    @classmethod
    def from_indices(cls, file_idx: int, rank_idx: int) -> "Position | None":
        """Create Position from array indices."""
        if not (0 <= file_idx < 8 and 0 <= rank_idx < 8):
            return None
        return cls(file=FILES[file_idx], rank=RANKS[rank_idx])

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Position):
            return False
        return self.file == other.file and self.rank == other.rank

    def __hash__(self) -> int:
        return hash((self.file, self.rank))
