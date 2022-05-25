import argparse

import stormpy as sp
import stormpy.pomdp

import logging
logger = logging.getLogger(__name__)


def build_pomdp(program):
    options = sp.BuilderOptions([])
    options.set_build_state_valuations()
    options.set_build_choice_labels()
    options.set_build_all_labels()
    options.set_build_all_reward_models()

    model =  sp.build_sparse_model_with_options(program, options)
    model = sp.pomdp.make_canonic(model)
    return model

def main():
    parser = argparse.ArgumentParser(description='Converter')

    parser.add_argument('--input', '-i', help='Model file', required=True)
    parser.add_argument('--output', '-o', help='Model file', required=True)
    parser.add_argument('--debug', help="Debug output", action='store_true')
    parser.add_argument('--quiet', help="Mute output", action='store_true')
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(format='%(message)s', level=logging.DEBUG)
    elif args.quiet:
        logging.basicConfig(format='%(message)s', level=logging.WARNING)
    else:
        logging.basicConfig(format='%(message)s', level=logging.INFO)


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
        logger.debug("Write transitions...")
        for state in model.states:
            for action in state.actions:
                file.write(f"\t[act{action}] s={state} -> ")
                updates = []
                for transition in action.transitions:
                    next_state = transition.column
                    updates.append(f"{transition.value()} : (s'={next_state}) & (o'={model.get_observation(next_state)})")
                file.write(" + ".join(updates))
                file.write(";\n")
        file.write("endmodule\n\n")

        logger.debug("Write labels...")
        for label in model.labeling.get_labels():
            if label in ["init", "deadlock"]:
                continue
            file.write(f"label \"{label}\" = ")
            options = []
            for s in model.labeling.get_states(label):
                options.append(f"s={s}")
            file.write(" | ".join(options))
            file.write(";\n")

        logger.debug("Write rewards...")
        for reward_model_name in model.reward_models:
            file.write(f"\nrewards \"{reward_model_name}\"\n")
            rewmodel = model.get_reward_model(reward_model_name)
            if rewmodel.has_transition_rewards:
                raise RuntimeError("Transition rewards are not supported")
            if rewmodel.has_state_action_rewards:
                logger.debug(f"Write state action rewards for {reward_model_name}")
                for state in model.states:
                    for act in state.actions:
                        file.write(f"\t[act{act}] s={state} : {rewmodel.get_state_action_reward(model.get_choice_index(int(state),act.id))};\n")
            if rewmodel.has_state_rewards:
                logger.debug(f"Write state rewards for {reward_model_name}")
                for state in model.states:
                    logger.debug(f"Write state rewards for {reward_model_name}")
                    file.write(f"\ts={state} : {rewmodel.get_state_reward(state)};\n")
            file.write("endrewards\n")


    logger.info("Check whether we can parse output...")
    # As a simple check, we control whether storm can parse the output.
    sp.parse_prism_program(args.output)
    logger.info("Done.")


if __name__ == "__main__":
    main()
