import numpy as np

from iwef.utils import Vocab, round_number


class UnigramTable:
    def __init__(self, max_size: int = 100_000_000):
        self.max_size = max_size
        self.size = 0
        self.z = 0
        self.table = np.zeros(self.max_size)

    def sample(self) -> int:
        assert 0 < self.size
        unigram_idx = self.table[np.random.randint(0, self.size)]
        return unigram_idx

    def samples(self, n: int) -> np.ndarray:
        unigram_idxs = list(self.table[np.random.randint(0, self.size, size=n)])
        return unigram_idxs

    def build(self, vocab: Vocab, alpha: float) -> None:

        reserved_idxs = set(vocab.counter.keys())
        free_idxs = vocab.free_idxs
        counts = vocab.counter.to_numpy(reserved_idxs | free_idxs)
        vocab_size = len(counts)
        counts_pow = np.power(counts, alpha)
        z = np.sum(counts_pow)
        nums = self.max_size * counts_pow / z
        nums = np.vectorize(round_number)(nums)
        sum_nums = np.sum(nums)

        while self.max_size < sum_nums:
            w = int(np.random.randint(0, vocab_size))
            if 0 < nums[w]:
                nums[w] -= 1
                sum_nums -= 1

        self.z = z
        self.size = 0

        for w in range(vocab_size):
            self.table[self.size : self.size + nums[w]] = w
            self.size += nums[w]

    def update(self, word_idx: int, F: float) -> None:

        assert 0 <= word_idx
        assert 0.0 <= F

        self.z += F
        if self.size < self.max_size:
            if F.is_integer():
                copies = min(int(F), self.max_size)
                self.table[self.size : self.size + copies] = word_idx
            else:
                copies = min(round_number(F), self.max_size)
                self.table[self.size : self.size + copies] = word_idx
            self.size += copies

        else:
            n = round_number((F / self.z) * self.max_size)
            for _ in range(n):
                table_idx = np.random.randint(0, self.max_size)
                self.table[table_idx] = word_idx