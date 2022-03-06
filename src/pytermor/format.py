from typing import Optional, AnyStr

from pytermor.sequence import SGRSequence


class Format:
    def __init__(self, opening_seq: SGRSequence, closing_seq: Optional[SGRSequence] = None, reset: bool = False):
        self._opening_seq: SGRSequence = opening_seq
        self._closing_seq: SGRSequence = SGRSequence(0) if reset else closing_seq

    def __call__(self, text: Optional[AnyStr] = None) -> AnyStr:
        result = self._opening_seq.str
        if text is not None:
            result += text
        if self._closing_seq is not None:
            result += self._closing_seq.str
        return result

    @property
    def open(self) -> AnyStr:
        return self._opening_seq.str

    @property
    def close(self) -> AnyStr:
        return self._closing_seq.str if self._closing_seq else ''
