import argparse

import stormpy as sp
import stormpy.pomdp

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(message)s', level=logging.INFO)


def build_pomdp(program):
    options = sp.BuilderOptions([])
    options.set_build_state_valuations()
    options.set_build_choice_labels()
    options.set_build_all_labels()

    model =  sp.build_sparse_model_with_options(program, options)
    model = sp.pomdp.make_canonic(model)
    return model

def main():
    parser = argparse.ArgumentParser(description='Converter')

    parser.add_argument('--input', '-i', help='Model file', required=True)
    parser.add_argument('--output', '-o', help='Model file', required=True)
    args = parser.parse_args()

    logger.info("Parse input program...")
    input_program = sp.parse_prism_program(args.input)
    logger.info("Build pomdp...")
    model = build_pomdp(input_program)

    if len(model.initial_states) > 1:
        raise RuntimeError("We require a unique initial state")
    logger.info("Write pomdp to file...")
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

    logger.info("Check whether we can parse output...")
    # As a simple check, we control whether storm can parse the output.
    sp.parse_prism_program(args.output)
    logger.info("Done.")


if __name__ == "__main__":
    main()
