"""
Very simple genetic programming example using the virtual machine.

Tip: Run with pypy for speed.

TODO:
- Crossover should allow this:
        parent1:    .........
        parent2:    ---------
        result:     ..----...
        instead of: ....-----
- Refactor the main code, make it modular (should be completely controllable
  from the outside)
"""

import random
import vm

def randomize(vm,
        length=(10,10),
        ints=(0,999),
        strs=(1,10),
        instruction_ratio=0.5,
        number_string_ratio=0.8,
        exclude=[".", "exit", "read", "write", "stack"]):

    """Replaces existing code with completely random instructions. Does not
    optimize code after generating it.

    Args:
        length: Tuple of minimum and maximum code lengths. Code length will
        be a random number between these two, inclusive values.

        ints: Integers in the code will be selected at random from this
        inclusive range.

        strs: Inclusive range of the length of strings in the code.

        instruction_ratio: Ratio of instructions to numbers/strings,
        meaning that if this value is 0.5 then there will just as many
        instructions in the code as there are numbers and strings.

        number_string_ratio: Ratio of numbers to strings.

        exclude: Excluded instructions. For genetic programming, one wants
        to avoid the program to hang for user input.  The default value is
        to exclude console i/o and debug instructions.

    Returns:
        The VM.
    """
    vm.code = []
    instructions = dict([i for i in vm.instructions.items() if i[0] not
        in exclude])

    for _ in xrange(random.randint(*length)):
        r = random.random()
        if r <= instruction_ratio:
            # Generate a random instruction
            vm.code.append(random.choice(instructions.keys()))
        elif r <= number_string_ratio:
            # Generate a random number
            vm.code.append(random.randint(*ints))
        else:
            # Generate a random string
            vm.code.append('"%s"' % "".join(chr(random.randint(1,127))
                for n in xrange(0, random.randint(*strs))))
    return vm

def crossover(m, f):
    """Produces an offspring from two Machines, whose code is a
    combination of the two."""
    point = random.randint(0, min(len(m.code), len(f.code)))
    return vm.Machine(m.code[:point] + f.code[point:])


def run_result(vm, steps):
    """Run a VM for a given number of steps and return True if it ran without
    errors."""
    try:
        vm.run(steps)
        return True
    except StopIteration:
        return True
    except Exception:
        return False


def main(num_machines=1000, generations=100000, steps=20, max_codelen=10,
        keep_top=50, mutation_rate=0.075):

    """Attemptes to create a program that puts the number 123 on the top of the
    stack.
    """

    print("Using GP to create a program that puts 123 on the ToS.")

    def fitfunc(vm):
        slen = len(vm.stack)
        rlen = len(vm.return_stack)
        default = 9999.9, slen + rlen, len(vm.code)

        # Machines with no code should not live to next generation
        if len(vm.stack) > 0 and len(vm.code) > 0:
            tos = vm.top
            if isinstance(tos, int):
                distance = abs(123.0 - tos)/123.0
                return distance, slen + rlen, len(vm.code)
        return default

    machines = [randomize(vm.Machine([]), length=(1, max_codelen)) for n in
            xrange(0, num_machines)]

    try:
        for no in xrange(0, generations):
            # Run all machines and collect results (top of stack)
            results = [(run_result(m.reset(), steps), i) for (i,m) in
                    enumerate(machines)]

            # Calculate their fitness score, sort by fitness, code length
            orig = machines
            fitness = sorted(map(lambda (r,i): (fitfunc(orig[i]),i), results))

            # Select the best
            best = [machines[i] for (r,i) in fitness[:keep_top]]

            # Interbreed them (TODO: choose stochastically with result as
            # weight)
            machines = []
            while len(machines) < num_machines:
                try:
                    # TODO: Could make sure that m!=f here
                    machines.append(crossover(random.choice(best),
                        random.choice(best)))
                except IndexError:
                    break

            # Adds mutations from time to time
            mutations = 0
            for m in machines:
                if random.random() <= mutation_rate:
                    # Mutation consists of changing, inserting or deleting an
                    # instruction
                    kind = random.random()
                    if len(m.code) > 1:
                        i = random.randint(0, len(m.code)-1)
                    elif len(m.code) > 0:
                        i = 0
                    else:
                        continue
                    if kind <= 0.5:
                        # change
                        op = randomize(vm.Machine([])).code[0]
                        m.code[i] = op
                        mutations += 1
                    elif kind <= 0.75:
                        # deletion
                        del m.code[i]
                        mutations += 1
                    else:
                        # insertion
                        op = randomize(vm.Machine([])).code[0]
                        m.code.insert(i, op)
                        mutations += 1

            # Display results
            chosen = [(orig[i], result) for result, i in fitness[:keep_top]]
            avg = sum(res for (m,(res,slen,codelen)) in chosen)/float(len(chosen))
            avglen = sum(codelen for (m,(res,slen,codelen)) in chosen)/float(len(chosen))
            slen = sum(slen for (m,(res,slen,codelen)) in chosen)/float(len(chosen))
            print("Generation %d fitness %.7f stack length %.2f code length %.2f mutations %d" %
                    (no, avg, slen, avglen, mutations))

            if avg == 0.0 and avglen < 2:
                print("Stopping because avg==0 and avglen<2.")
                break
    except KeyboardInterrupt:
        pass

    print("Best 10:")
    for m, (result, slen, codelen) in chosen[0:10]:
        print("fitness=%f tos=%s slen=%d len=%d code: %s" % (result, m.top,
            slen, len(m.code), m.code_string))

if __name__ == "__main__":
    main()
