# Modeling Trader Account Balance: A Deterministic Approach
 A deterministic model for trader account balance analysis, featuring a Streamlit app for interactive exploration. Focuses on expectation, median, and mode.

This document details our modeling process used to simulate trader account balance, focusing on a deterministic approach as opposed to stochastic methods like Monte Carlo simulations. We will explain why a deterministic approach is more suitable for this problem, derive relevant mathematical formulas, and show how these are implemented in a user-friendly Streamlit application.

## Why Not Monte Carlo?

Monte Carlo simulations are popular for modeling systems under uncertainty. However, they have limitations when applied to trader account balances, primarily because they focus on the **mean** (average) outcome. Here's why this is problematic in our context:

*   **Asymmetry of Profits and Losses:** In trading, potential profits can be theoretically infinite, while losses are limited to the trader's account size. This asymmetry makes the mean an unreliable indicator of typical scenarios. (You can read more about non-ergodic systems)
*   **Emphasis on "Typical" Scenarios:** Monte Carlo simulations tend to converge on the average case, which doesn't represent the most common or likely outcome.
*   **Deterministic Nature:**  Our model assumes that the stop-loss at each time period is a fixed, predetermined fraction of the actual balance, making the system more amenable to deterministic analysis.
*   **Computational Expense**: Monte Carlo is computationally expensive because it involves a large number of simulations to approximate the true distribution and thus exact results are usually not available.

Given these factors, we focus on computing the **expectation, mode, and median** of the account balance, which provide a more comprehensive understanding of potential outcomes.

## Mathematical Model

Our model considers a trader who uses a fixed stop-loss percentage of their account balance. Here are the key parameters:

*   `B0`: Initial balance.
*   `r`: Risk-reward ratio.
*   `s`: Stop-loss percentage (expressed as a decimal).
*   `p`: Winning probability.
*   `n`: Number of trades.
*   `u`: Growth factor when a trade is won, computed as `1 + r*s`.
*   `d`: Discounting factor when a trade is lost, computed as `1 - s`.
*   `q`: Losing rate, computed as `1-p`.

### Expectation (Average)

The expected account balance after *n* trades is given by:

   *   **E(B(n)) = B0 \* (p\*u + (1-p)\*d)^n**
    *   This formula calculates the average outcome over 'n' trades.

The average growth rate is:

   *   **E(R(n)) = (p*u + q*d)^n** (Gross return)
   *   **E(r(n)) = (p*u + q*d)^n - 1** (Net return)

The formula to calculate the expected square balance and variance are respectively:

   *   **E(B(n)²) = B0² \* (p\*u² + q\*d²)^n**
   *   **Var(B(n)) = B0² \* (p\*u² + q\*d²)^n - B0² \* (p\*u + q\*d)^2n**  (Balance variance)
   *   **Var(r(n)) = Var(R(n)) = (p\*u² + q\*d²)^n - (p\*u + q\*d)^2n** (Return variance)

These formulas are implemented in the code as functions `average` and `std`.

### Mode (Most Likely Outcome)

The mode is the most frequent outcome. We compute the terms and corresponding coefficients using the binomial theorem.
*  Terms: `b0 * (u)**(n-k) * (d)**k`
* Coefficients: `binomial_coefficient(n, k) * p**(n-k) * (1-p)**k`

The mode is computed by finding the terms with the highest coefficients. We provide the two most likely outcomes (`modes`).

### Median

The median is the middle value. We generate all possible outcomes based on the binomial distribution and select the median value. This is implemented using `generate_data` and `median` functions.

### Growth rate

The functions `growth_average` and `growth_mode` calculate growth rate as follow:
   *   **average growth per trade**:  `p*(1 + r*s) + (1 - p)*(1 - s) - 1`
   *  **most likely outcome growth per trade**:  `(1 + r*s)**p * (1 - s)**(1 - p) - 1`

## Python Implementation

The core of our model is built using Python, with libraries like NumPy, Pandas, and Matplotlib used for calculations, and visualization.

### Key Functions

*   **`compute_ud(r, s)`**: Calculates the growth factor (`u`) and discount factor (`d`).
*   **`average(b0, p, r, s, n)`**: Computes the expected balance after *n* trades.
*   **`std(b0, p, r, s, n)`**: Computes the standard deviation of the balance.
*   **`binomial_coefficient(n, k)`**: Calculates the binomial coefficient (n choose k).
*   **`generate_terms(b0, u, d, p, n)`**: Generates all possible outcomes and their coefficients based on the binomial theorem.
*   **`max_indices(coefs, first=True)`**: Finds the indices of the maximum coefficients.
*   **`modes(b0, p, r, s, n)`**: Computes the two most likely outcomes.
*  **`generate_data(coefs, terms)`**: Generates data for median calculations based on binomial distribution.
*   **`median(b0, p, r, s, n)`**: Computes the median balance.

## Streamlit Application

A Streamlit application provides an interactive user interface to explore the model. Here's how to use it:

### Sidebar Parameters

The sidebar allows you to adjust the following parameters:

*   **Initial Balance 💰:** Starting amount.
*   **Winning probability ✔:** Probability of a winning trade (0-100%).
*   **Risk-reward ratio 🏆:** Ratio of potential profit to potential loss.
*   **Stop loss percent 🚩:** Percentage of the balance risked on each trade (0-100%).
*   **N° of trades 📊:** Number of trades to simulate.

### Central Tendencies

You can choose which central tendencies to display:

*   **Show Average**: Displays the average account balance over time.
*   **Show Median**: Displays the median account balance over time.
*   **Show Most Likely Outcome 1**: Displays the most likely outcome over time.
*   **Show Most Likely Outcome 2**: Displays the second most likely outcome over time.

### Main Panel

The main panel provides:

*   **Growth analysis**: The application calculates the average and most likely growth both overall and per trade.
*   **Interactive Plot**: An animated Plotly chart displays the selected central tendencies over the number of trades. The graph is updated dynamically according to the selected central tendencies with the checkboxes on the side bar.
    * The animation is controlled using the Play button.
    * Hovering over the graph displays the data value at that point of the x-axis.
*   **Download Data Button**: Download the plotted data as a CSV file for further analysis.

### Running the streamlit app
If needed install the required packages using/
```python
pip install pandas numpy plotly streamlit

```
When it's done, you can run the app using:
```python
streamlit run "Equity Simulator.py"
```

## Conclusion

Our deterministic approach offers a robust alternative to Monte Carlo simulations for modeling trader account balances. By focusing on the **expectation, median, and mode**, this modeling process and Streamlit application helps in providing a more realistic view of potential trading outcomes. The Streamlit application allows the user to manipulate parameters dynamically which allows to explore the effect of different trading choices.