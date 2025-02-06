import pm4py
from pm4py.algo.conformance.tokenreplay import algorithm as token_based_replay_algorithm
from pm4py.algo.conformance.tokenreplay.diagnostics import duration_diagnostics
import streamlit as st
import pandas as pd
import math


def show(full_log, filtered_log):
    sample_pct = st.number_input(
        "% of full log to sample during token replay",
        min_value=1,
        max_value=100,
        value=50,
        step=1,
    )
    if st.button("🔍 Run performance diagnostics"):
        num_cases = math.floor(
            full_log["case:concept:name"].nunique() * (sample_pct / 100)
        )
        full_log = pm4py.convert_to_event_log(
            pm4py.sample_cases(full_log.copy(), num_cases=num_cases)
        )
        filtered_log = pm4py.convert_to_event_log(filtered_log.copy())

        print("Creating Petri net from filtered log")
        net, initial_marking, final_marking = pm4py.discover_petri_net_inductive(
            filtered_log
        )

        parameters_tbr = {
            token_based_replay_algorithm.Variants.TOKEN_REPLAY.value.Parameters.DISABLE_VARIANTS: True,
            token_based_replay_algorithm.Variants.TOKEN_REPLAY.value.Parameters.ENABLE_PLTR_FITNESS: True,
        }

        print("Replaying traces using full log and petri net")
        replayed_traces, place_fitness, trans_fitness, unwanted_activities = (
            token_based_replay_algorithm.apply(
                full_log, net, initial_marking, final_marking, parameters=parameters_tbr
            )
        )

        print("Running transition diagnostics")
        trans_diagnostics = duration_diagnostics.diagnose_from_trans_fitness(
            full_log, trans_fitness
        )

        trans_data = []
        print("For each problematic transition, diagnostics about case duration:")
        for trans in trans_diagnostics:
            print(str(trans))
            trans_data.append(
                {
                    "Transition": str(trans),
                    "Fit Median Time (hrs)": trans_diagnostics[trans]["fit_median_time"]
                    / 3600,
                    "Underfed Median Time (hrs)": trans_diagnostics[trans][
                        "underfed_median_time"
                    ]
                    / 3600,
                    "Relative Throughput": trans_diagnostics[trans][
                        "relative_throughput"
                    ],
                }
            )

        df_trans = pd.DataFrame(trans_data)
        st.title("Transition performance diagnostics")
        st.dataframe(df_trans)

        print("Running activity diagnostics")
        act_diagnostics = duration_diagnostics.diagnose_from_notexisting_activities(
            full_log,
            unwanted_activities,
        )

        act_data = []
        for act in act_diagnostics:
            act_data.append(
                {
                    "Activity": act,
                    "Number Containing": act_diagnostics[act]["n_containing"],
                    "Fit Median Time (hrs)": act_diagnostics[act]["fit_median_time"]
                    / 3600,
                    "Containing Median Time (hrs)": act_diagnostics[act][
                        "containing_median_time"
                    ]
                    / 3600,
                    "Relative Throughput": act_diagnostics[act]["relative_throughput"],
                }
            )
        df_act = pd.DataFrame(act_data)
        st.title("Activity performance diagnostics")
        st.dataframe(df_act)
