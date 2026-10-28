
# Causal Machine Learning and MLOps for Product Optimization

## Project Overview

An end-to-end research prototype demonstrating how causal
machine learning can be integrated with a basic automated
MLOps workflow to support customer discount decisions.

## Research Objective

Estimate heterogeneous treatment effects of promotional
discounts and use those estimates to support product
optimization decisions.

## Technologies

- Python 3.12
- Pandas and NumPy
- Scikit-learn
- Random Forest T-Learner
- Joblib
- JSON and CSV

## Pipeline

1. Generate synthetic customer data
2. Validate the dataset
3. Train a causal ML T-Learner
4. Evaluate treatment-effect estimates
5. Save trained models and experiment results
6. Generate discount recommendations

## Initial Results

- Dataset: 1,000 simulated customers
- Training set: 800 customers
- Test set: 200 customers
- Estimated average treatment effect: RM24.07
- Known average treatment effect: RM22.75
- Treatment-effect MAE: RM7.94
- Discounts recommended: 163 of 200 test customers

These results are from one synthetic experiment and
are not evidence of real-world business profitability.

## How to Run

Create a Python 3.12 virtual environment and activate it.

Install dependencies:

    python -m pip install -r requirements.txt

Run the pipeline:

    python run_pipeline.py

## Current Limitations

- Synthetic data only
- Initial T-Learner baseline
- No uncertainty intervals or repeated experiments
- Simplified campaign-cost decision rule
- Basic local experiment logging
- No production deployment or monitoring

## Future Improvements

- Compare multiple causal ML estimators
- Add explainability visualizations
- Evaluate robustness across repeated experiments
- Add automated tests and model monitoring
- Extend MLOps experiment tracking

## Research Context

This project supports exploratory development for an MSc
Data Science research direction:

"An Integrated MLOps Pipeline for Explainable Product
Optimization Using Causal Machine Learning."

This is an initial prototype, not a validated research
contribution or production system.
