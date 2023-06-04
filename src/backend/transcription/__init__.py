from pydantic import BaseModel


class WhisperModelArgs(BaseModel):
    device: str = ""
    compute_type: str = (
        "float32"  # change to "int8" if low on GPU mem (may reduce accuracy)
    )
    batch_size: int = 8
