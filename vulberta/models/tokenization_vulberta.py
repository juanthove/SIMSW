from typing import List

from tokenizers import NormalizedString, PreTokenizedString
from tokenizers.pre_tokenizers import PreTokenizer
from transformers import PreTrainedTokenizerFast

try:
    from clang import cindex
except ModuleNotFoundError as e:
    raise ModuleNotFoundError(
        "VulBERTa Clang tokenizer requires `libclang`. Please install it via `pip install libclang`.",
    ) from e


class ClangPreTokenizer:
    cidx = cindex.Index.create()

    def clang_split(
        self,
        i: int,
        normalized_string: NormalizedString,
    ) -> List[NormalizedString]:
        tok = []
        tu = self.cidx.parse(
            "tmp.c",
            args=[""],
            unsaved_files=[("tmp.c", str(normalized_string.original))],
            options=0,
        )
        for t in tu.get_tokens(extent=tu.cursor.extent):
            spelling = t.spelling.strip()
            if spelling == "":
                continue
            tok.append(NormalizedString(spelling))
        return tok

    def pre_tokenize(self, pretok: PreTokenizedString):
        pretok.split(self.clang_split)


class VulBERTaTokenizer(PreTrainedTokenizerFast):
    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )
        self._tokenizer.pre_tokenizer = PreTokenizer.custom(ClangPreTokenizer())
