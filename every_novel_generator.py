class Collector(object):
    def __init__(self, title, stream, limit=None):
        self.stream = stream
        self.count = 0
        self.limit = limit
        self.closed = False
        self.write('<html><head><title>{}</title></head><body><h1>{}</h1>'.format(title, title))

    def write(self, s):
        if self.closed:
            return
        self.stream.write(s)
        self.stream.flush()

    def recv(self, word, sender=None):
        if sender:
            self.write('<span title="{}">{}</span>\n'.format(sender.replace('<', '&lt;').replace('>', '&gt;'), word))
        else:
            self.write('{} '.format(word))
        self.count += 1
        if self.limit is not None and self.count >= self.limit:
            self.close()

    def close(self):
        self.write('</body></html>')
        self.closed = True

class Buffer(object):
    def __init__(self, title, collector, printable):
        self.title = title
        self.collector = collector
        self.printable = printable
        self.word = ''

    def flush(self):
        if self.word:
            self.output()
            self.word = ''

    def accum(self, chars):
        for char in chars:
            if char in self.printable:
                self.word += char
            else:
                self.flush()

    def output(self):
        self.collector.recv(self.word, sender=self.title)

class Alphabet(object):
    def __init__(self, chars):
        self.chars = list(chars)
        self.succ_map = dict([(c, chars[i + 1] if i < len(chars) - 1 else chars[0]) for i, c in enumerate(chars)])
        self.pred_map = dict([(c, chars[i - 1] if i > 0 else chars[-1]) for i, c in enumerate(chars)])

    def __contains__(self, c):
        return c in self.chars

    def first(self):
        return self.chars[0]

    def last(self):
        return self.chars[-1]

    def succ(self, c):
        return self.succ_map[c]

    def pred(self, c):
        return self.pred_map[c]

class IncrementableString(object):
    def __init__(self, alphabet, value):
        self.alphabet = alphabet
        self.value = list(value)

    def __str__(self):
        return ''.join(self.value)

    def zero(self):
        return self.alphabet.first()

    def succ_value(self, value):
        if not value:
            return [self.zero()]
        if value[0] == self.alphabet.last():
            return [self.zero()] + self.succ_value(value[1:])
        else:
            return [self.alphabet.succ(value[0])] + value[1:]

    def incr(self):
        self.value = self.succ_value(self.value)

class Interpreter(object):
    def __init__(self, program, buffer_, alphabet):
        self.program = program
        self.buffer = buffer_
        self.alphabet = alphabet
        self.pc = 0
        self.tape = {}
        self.head = 0L
        self.halted = False

    def read_tape(self):
        return self.tape.get(self.head, self.alphabet.first())

    def write_tape(self, symbol):
        self.tape[self.head] = symbol

    def step(self):
        instruction = self.program[self.pc]

        if instruction == '<':
            self.head -= 1L
        elif instruction == '>':
            self.head += 1L
        elif instruction == '+':
            self.write_tape(self.alphabet.succ(self.read_tape()))
        elif instruction == '-':
            self.write_tape(self.alphabet.pred(self.read_tape()))
        elif instruction == '.':
            self.buffer.accum(self.read_tape())
        elif instruction == '[':
            if self.read_tape() == self.alphabet.first():
                depth = 0
                while True:
                    if self.program[self.pc] == '[':
                        depth += 1
                    if self.program[self.pc] == ']':
                        depth -= 1
                        if depth == 0:
                            break
                    self.pc += 1
        elif instruction == ']':
            depth = 0
            while True:
                if self.program[self.pc] == '[':
                    depth -= 1
                if self.program[self.pc] == ']':
                    depth += 1
                self.pc -= 1
                if depth == 0:
                    break

        self.pc += 1
        if self.pc >= len(self.program):
            self.buffer.flush()
            self.halted = True

class ProgramGenerator(object):
    def __init__(self, start):
        self.source = IncrementableString(Alphabet('+-<>[].'), start)

    def next(self):
        program = str(self.source)
        self.source.incr()
        while not self.is_balanced(program):
            program = str(self.source)
            self.source.incr()

        return program

    def is_balanced(self, s):
        level = 0
        for c in s:
            if c == '[':
                level += 1
            elif c == ']':
                level -= 1
                if level < 0:
                    return False
        return level == 0

class Orchestrator(object):
    def __init__(self, collector, printable, starting_at):
        self.collector = collector
        self.printable = Alphabet(printable)
        self.alphabet = Alphabet(" " + printable)
        self.generator = ProgramGenerator(starting_at)
        self.interpreters = {}
        self.halted = False

    def step(self):
        reap = set()
        for program, interpreter in self.interpreters.iteritems():
            interpreter.step()
            if interpreter.halted:
                reap.add(program)
        for program in reap:
            del self.interpreters[program]

        program = self.generator.next()
        buffer_ = Buffer(program, self.collector, self.printable)
        self.interpreters[program] = Interpreter(program, buffer_, self.alphabet)

    def run(self):
        while not self.collector.closed:
            self.step()

if __name__ == '__main__':
    import string
    import sys
    title = "The Collected Works of Every Novel Generator Ever (Abridged Version)"
    collector = Collector(title, sys.stdout, limit=50000)
    Orchestrator(collector, string.lowercase + """.,!:;'"-""" + string.uppercase, starting_at='+').run()
