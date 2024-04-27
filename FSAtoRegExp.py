from collections import defaultdict
from dataclasses import dataclass


class FSAtoRegExpTranslator:
    """
    type: str t // t ∈ {deterministic, non-deterministic}

    states: list[str] [s1,s2,...] // s1 , s2, ... ∈ latin letters, words and numbers

    alphabet: list[str] [a1,a2,...] // a1 , a2, ... ∈ latin letters, words, numbers and character '_' (underscore)

    initial: str [s] // s ∈ states

    accepting: list[str] [s1,s2,...] // s1, s2 ∈ states

    transitions: dict[str, dict[str, set[str]]] [s1>a>s2,...] // s1,s2,...∈ states; a ∈ alphabet
    ----------------[from---[trans, {to-states}]]----
    """
    @dataclass
    class Transition:
        def __init__(self, from_state: str, through: str):
            self.from_state = from_state
            self.through = through
            self.to = list()
        def append(self, to: str):
            if to not in self.to: self.to.append(to)
        def __repr__(self):
            return f'{self.from_state}->{self.through}->{self.to}'
    @dataclass
    class State:
        def __init__(self, name: str):
            self.name = name
            self.transitions: dict[str, FSAtoRegExpTranslator.Transition] = dict()
        def __repr__(self):
            return ', '.join([x.__repr__() for x in self.transitions.values()]) + '\n'
    class MyException(Exception):
        pass

    def __init__(self):
        self.states: dict[str, FSAtoRegExpTranslator.State] = dict()
        self.alphabet: list[str] = list()
        self.initial: str = ''
        self.accepting: list[str] = list()

    def valid_string(self, line: str, name: str):
        if line.find(f"{name}=[") != 0 or line[-2] != ']': raise FSAtoRegExpTranslator.MyException("E1: Input file is malformed")

    def input_data(self, file: str):
        # file handling
        with open('input.txt', 'r') as f:# open file

            # TYPE
            line = f.readline()
            self.valid_string(line, "type")
            type = line[6:-2]
            if type not in ['deterministic', 'non-deterministic']: raise FSAtoRegExpTranslator.MyException("E1: Input file is malformed")
            self.type = type


            # STATES
            line = f.readline()
            self.valid_string(line, "states")
            states_set = line[8:-2].split(',')
            if '' in states_set: raise FSAtoRegExpTranslator.MyException("E1: Input file is malformed")
            for state in states_set:
                self.states[state] = FSAtoRegExpTranslator.State(state)


            # ALPHABET
            line = f.readline()
            self.valid_string(line, "alphabet")
            alphabet = line[10:-2].split(',')
            if '' in alphabet: raise FSAtoRegExpTranslator.MyException("E1: Input file is malformed")
            self.alphabet = alphabet


            # INITIAL
            line = f.readline()
            self.valid_string(line, "initial")
            initial = line[9:-2]
            if ',' in initial: raise FSAtoRegExpTranslator.MyException("E1: Input file is malformed")
            if initial == '': raise FSAtoRegExpTranslator.MyException("E2: Initial state is not defined")
            if initial not in self.states: raise FSAtoRegExpTranslator.MyException(f"E4: A state '{initial}' is not in the set of states")
            self.initial = initial


            # ACCEPTING
            line = f.readline()
            self.valid_string(line, "accepting")
            accepting = sorted(set(line[11:-2].split(',')))
            if '' in accepting and len(accepting) != 1:
                raise FSAtoRegExpTranslator.MyException("E1: Input file is malformed")
            if '' in accepting and len(accepting) == 1:
                raise FSAtoRegExpTranslator.MyException("E3: Set of accepting states is empty")
            for state in accepting:
                if state not in self.states.keys():
                    raise FSAtoRegExpTranslator.MyException(f"E4: A state '{state}' is not in the set of states")
            self.accepting = accepting


            # TRANSITIONS
            line = f.readline()
            self.valid_string(line, "transitions")
            transitions_set = line[13:-2].split(',')
            if '' in transitions_set:
                raise FSAtoRegExpTranslator.MyException("E1: Input file is malformed")
            if len(set(transitions_set)) != len(transitions_set):
                raise FSAtoRegExpTranslator.MyException("E1: Input file is malformed")

            for transition in transitions_set:
                _from, through, to = transition.split('>')
                if _from == '':
                    raise FSAtoRegExpTranslator.MyException("E1: Input file is malformed")
                if through == '':
                    raise FSAtoRegExpTranslator.MyException("E1: Input file is malformed")
                if to == '':
                    raise FSAtoRegExpTranslator.MyException("E1: Input file is malformed")
                if _from not in self.states.keys():
                    raise FSAtoRegExpTranslator.MyException(f"E4: A state '{_from}' is not in the set of states")
                if to not in self.states.keys():
                    raise FSAtoRegExpTranslator.MyException(f"E4: A state '{to}' is not in the set of states")
                if through not in alphabet:
                    raise FSAtoRegExpTranslator.MyException(f"E5: A transition '{through}' is not represented in the alphabet ")
                if through not in self.states[_from].transitions:
                    self.states[_from].transitions[through] = FSAtoRegExpTranslator.Transition(_from, through)
                self.states[_from].transitions[through].append(to)

            self.__check_valid()

    def __check_valid(self) -> None:
        done: set[str] = set()

        def dfs(state_from: str, done):
            done.add(state_from)
            state_transitions = self.states[state_from].transitions
            for transition in state_transitions.values():
                if len(transition.to) != 1 and self.type == "deterministic":
                    raise FSAtoRegExpTranslator.MyException(f"E7: FSA is non-deterministic")
                for state_to in transition.to:
                    if state_to not in done:
                        dfs(state_to, done)
        dfs(self.initial, done)
        for state in self.states.keys():
            if state not in done:
                raise FSAtoRegExpTranslator.MyException("E6: Some states are disjoint")

    def get_regex_string(self) -> str:
        R: list[dict[tuple, list[str] | str]] = [defaultdict(list).copy() for _ in range(len(self.states) + 1)]  # [('from', 'to') : a1|a2|a3...]
        for state_from in self.states.values():
            for transition in state_from.transitions.values():
                for state_to in transition.to:
                    R[0][(state_from.name, state_to)].append(transition.through)

        for state in self.states:
            R[0][(state, state)].append('eps')

        for x in R[0].keys():
            R[0][x] = '|'.join(R[0][x])

        for i_k, k in enumerate(self.states):
            for i in self.states:
                for j in self.states:
                    R[i_k + 1][(i, j)] = ''
                    ik = R[i_k].get((i, k), '{}')
                    kk = R[i_k].get((k, k), '{}')
                    kj = R[i_k].get((k, j), '{}')
                    ij = R[i_k].get((i, j), '{}')
                    R[i_k + 1][(i, j)] += f"({ik})" if ik != "" else ''
                    R[i_k + 1][(i, j)] += f"({kk})*" if kk != "" else ''
                    R[i_k + 1][(i, j)] += f"({kj})" if kj != "" else ''
                    R[i_k + 1][(i, j)] += f"|({ij})" if ij != "" else ''

        result = f"({')|('.join([R[-1][(self.initial, accept)] for accept in self.accepting])})"
        return result

if __name__ == "__main__":
    """ input example
    type=[non-deterministic]
    states=[q0,q1]
    alphabet=[0,1]
    initial=[q0]
    accepting=[q1]
    transitions=[q0>0>q0,q0>1>q0,q1>0>q1,q1>1>q1,q1>0>q0,q1>1>q0]
    """
    fsa = FSAtoRegExpTranslator()
    try:
        fsa.input_data('input.txt')
        answer = fsa.get_regex_string()
        print(answer)
    except FSAtoRegExpTranslator.MyException as e:
        print(e)
    except Exception as e:
        print("E1: Input file is malformed")

