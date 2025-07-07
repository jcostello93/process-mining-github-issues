import streamlit as st
import pm4py


def show(sample_log, net, im, fm):
    fitness = pm4py.fitness_token_based_replay(sample_log, net, im, fm)
    simplicity = pm4py.analysis.simplicity_petri_net(net, im, fm)
    precision = pm4py.precision_token_based_replay(sample_log, net, im, fm)
    generalization = pm4py.algo.evaluation.generalization.algorithm.apply(
        sample_log, net, im, fm
    )

    st.title("Petri Net Evaluation Results")

    metrics = {
        "Percentage of Fitting Traces": fitness["percentage_of_fitting_traces"],
        "Average Trace Fitness": fitness["average_trace_fitness"],
        "Simplicity": simplicity,
        "Precision": precision,
        "Generalization": generalization,
    }

    st.table([{"Metric": k, "Value": v} for k, v in metrics.items()])
