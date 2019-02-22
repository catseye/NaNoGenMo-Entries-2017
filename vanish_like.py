import random
import sys

class Sentence(object):
    def __init__(self, s):
        s = s.strip()
        assert s.endswith(('.', '?'))
        self.ender = s[-1]
        self.words = s[0:-1].split(' ')

    def __str__(self):
        words = list(self.words)
        words[0] = words[0][0].upper() + words[0][1:]
        while words[-1].endswith(('.', ',', '?')):
            words[-1] = words[-1][0:-1]
        return ' '.join(words) + self.ender

    def reduce(self):
        del self.words[random.randint(0, len(self.words) - 1)]

if __name__ == '__main__':
    sentences = [Sentence(line) for line in sys.stdin]
    initial_word_count = sum([len(sentence.words) for sentence in sentences])
    assert initial_word_count >= 316, initial_word_count

    while sentences:
        print '  '.join([str(s) for s in sentences]) + '\n'
        random.choice(sentences).reduce()
        sentences = [s for s in sentences if s.words]
