import argparse

import stormpy as sp
import stormpy.pomdp


def build_pomdp(program):
    options = sp.BuilderOptions([])
    options.set_build_state_valuations()
    options.set_build_choice_labels()
    options.set_build_all_labels()

    return sp.build_sparse_model_with_options(program, options)

def main():
    parser = argparse.ArgumentParser(description='Converter')

    parser.add_argument('--input', '-i', help='Model file', required=True)
    parser.add_argument('--output', '-o', help='Model file', required=True)
    args = parser.parse_args()

    input_program = sp.parse_prism_program(args.input)
    model = build_pomdp(input_program)
    model = sp.pomdp.make_canonic(model)

    if len(model.initial_states) > 1:
        raise RuntimeError("We require a unique initial state")

    with open(args.output, 'w') as file:
        file.write("pomdp\n\n")
        file.write("observables\n")
        file.write("\to\n")
        file.write("endobservables\n\n")
        file.write("module model\n")
        nrstates = model.nr_states
        initstate = model.initial_states[0]
        nrobservations = model.nr_observations
        initob = model.get_observation(initstate)
        file.write(f"\ts : [0..{nrstates}] init {initstate};\n")
        file.write(f"\to : [0..{nrobservations}] init {initob};\n")
        for state in model.states:
            for action in state.actions:
                file.write(f"\t[act{action}] s={state} -> ")
                updates = []
                for transition in action.transitions:
                    next_state = transition.column
                    updates.append(f"{transition.value()} : (s'={next_state}) & (o'={model.get_observation(next_state)})")
                file.write(" + ".join(updates))
                file.write(";\n")
        file.write("endmodule\n")


if __name__ == "__main__":
    main()
