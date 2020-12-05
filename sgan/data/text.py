import os
import re
import random

from itertools import cycle

default_path = os.path.join(os.path.dirname(__file__), '../../data/text.txt')


class TextIterator:
    def __init__(self, path=None, min_size=180, max_size=220, seed=42, shuffle=True):
        path = path or default_path
        with open(path) as f:
            text = f.read()

        parsed_text = re.sub(r'\s+', ' ', text, flags=re.M)
        sentences = []
        for s in re.split(r'(?<=[.!?…]) ', parsed_text):
            if min_size < len(s) < max_size:
                sentences.append(s)

        if shuffle:
            random.seed(seed)
            random.shuffle(sentences)

        self.sentences = sentences

    def __len__(self):
        return len(self.sentences)

    def __call__(self):
        return self.create_generator()

    def create_generator(self):
        def gen():
            # this allows to get same results for each experiment
            for s in cycle(self.sentences):
                yield s

        return gen()