#%% importing packages
import streamlit as st
import plotly.graph_objects as go  # Import plotly.graph_objects
import pandas as pd
import numpy as np
import math


#%% utils function
def compute_ud(risk_reward_ratio, stop_loss_percent):
    return 1 + risk_reward_ratio*stop_loss_percent, 1 - stop_loss_percent

def average(initial_balance, win_probability, risk_reward_ratio, stop_loss_percent, n):
    return initial_balance * (win_probability*(1 + risk_reward_ratio*stop_loss_percent) + (1-win_probability)*(1 - stop_loss_percent))**n

def stdev(initial_balance, win_probability, risk_reward_ratio, stop_loss_percent, n):
    avg = average(initial_balance, win_probability, risk_reward_ratio, stop_loss_percent, n)
    avg_of_square = initial_balance**2 * (win_probability*(1 + risk_reward_ratio*stop_loss_percent)**2 + (1-win_probability)*(1 -stop_loss_percent)**2)**n
    return np.sqrt(avg_of_square - avg**2) 

def generate_terms(initial_balance, up, down, win_probability, n):
    terms = []
    terms_p = []
    coefficients = []
    for k in range(n+1):
        coefficient = math.comb(n, k)
        term = initial_balance * (up)**(n-k) * (down)**k
        term_p = (win_probability)**(n-k) *  (1-win_probability)**k
        coefficients = np.append(coefficients, coefficient * term_p)
        terms = np.append(terms, term)
    return coefficients, terms
    

def max_indices(coefs, first=True):
    position = 0 if first else -1
    max_indices = np.where(coefs == np.max(coefs))[0]
    return max_indices[position]

def modes(initial_balance, win_probability, risk_reward_ratio, stop_loss_percent, n):
    mod1, mod2 = [], []
    for i in n:
        coefs, terms = generate_terms(initial_balance, (1 + risk_reward_ratio*stop_loss_percent), (1 - stop_loss_percent), win_probability, i)
        idx1 = max_indices(coefs, first=True)
        idx2 = max_indices(coefs, first=False)
        mod1 = np.append(mod1, terms[idx1])
        mod2 = np.append(mod2, terms[idx2])
    return mod1, mod2

def generate_data(coefs, terms):
    return np.repeat(terms, np.round(coefs * len(terms)).astype(int))

def median(initial_balance, win_probability, risk_reward_ratio, stop_loss_percent, n):
    med = []
    for i in n:
        coefs, terms = generate_terms(initial_balance, (1 + risk_reward_ratio*stop_loss_percent), (1 - stop_loss_percent), win_probability, i)
        data = generate_data(coefs, terms)
        med = np.append(med, np.median(data))
    return med

def growth_average(win_probability, risk_reward_ratio, stop_loss_percent):
    return win_probability*(1 + risk_reward_ratio*stop_loss_percent) + (1 - win_probability)*(1 - stop_loss_percent) - 1

def growth_mode(win_probability, risk_reward_ratio, stop_loss_percent):
    return (1 + risk_reward_ratio*stop_loss_percent)**win_probability * (1 - stop_loss_percent)**(1 - win_probability) - 1

def write_growth(growth, growth_per_trade):
    if growth <= 0:
        color = 'red'
    else:
        color = 'green'
    st.write(f'<p style="font-weight: bold; color: {color}; font-size: 24px;"> <span style="font-size: 48px;"> {growth*100:.2f}% | </span> {growth_per_trade*100:.2f}% </p>', unsafe_allow_html=True)


#%% ui
# settings
st.set_page_config(layout="wide")

# creating sidebar and reading user input
st.sidebar.header('Trading parameters ⚙️')
initial_balance = st.sidebar.number_input("Initial Balance 💰:", min_value=0, value=100)
win_probability = st.sidebar.number_input("Winning probability ✔:", min_value=0.0, max_value=100.0, step=0.05, value=50.0)
risk_reward_ratio = st.sidebar.number_input("Risk reward ratio 🏆:", min_value=0.0, value=2.0, format='%f')
stop_loss_percent = st.sidebar.number_input("Stop loss percent 🚩:", min_value=0.0, max_value=100.0, step=0.05, value=2.0)
n = st.sidebar.number_input("N° of trades 📊:", min_value=1, max_value=250, step=1, value=10, format='%d')

# check box for usier input and
st.sidebar.header('Central Tendencies')
show_avg = st.sidebar.checkbox('Show Average', value=False)
show_med = st.sidebar.checkbox('Show Median', value=True)
show_mo1 = st.sidebar.checkbox('Show Most Likely Outcome 1', value=True)
show_mo2 = st.sidebar.checkbox('Show Most Likely Outcome 2', value=True)

# processing
## computing stats
win_probability /= 100
stop_loss_percent /= 100
n = np.arange(0, n+1)

avg = average(initial_balance, win_probability, risk_reward_ratio, stop_loss_percent, n)
med = median(initial_balance, win_probability, risk_reward_ratio, stop_loss_percent, n)
mo1 = modes(initial_balance, win_probability, risk_reward_ratio, stop_loss_percent, n)[0]
mo2 = modes(initial_balance, win_probability, risk_reward_ratio, stop_loss_percent, n)[1]
std = stdev(initial_balance, win_probability, risk_reward_ratio, stop_loss_percent, n)

## dataframe
# Create a dictionary with column names and lists
data={"Average": avg,
      "Median": med,
      "Most likely outcome 1": mo1,
      "Most likely outcome 2": mo2}
# Create a boolean list or Series
boolean_list = [show_avg, show_med, show_mo1, show_mo2]
# Select the columns based on the boolean list
selected_columns = [column for column, boolean in zip(data.keys(), boolean_list) if boolean]
# Create a new DataFrame with the selected columns
central = pd.DataFrame({column: data[column] for column in selected_columns})

avg_growth = growth_average(win_probability, risk_reward_ratio, stop_loss_percent)
mod_growth = growth_mode(win_probability, risk_reward_ratio, stop_loss_percent)

# graphing
st.write('Avg. growth | per trade:')
write_growth((1 + avg_growth)**(n[-1])-1, avg_growth)
st.write('Most likely growth | per trade:')
write_growth((1 + mod_growth)**(n[-1])-1, mod_growth)


# Create a Plotly figure
fig = go.Figure()

# Add initial traces (empty data)
for column in central.columns:
    fig.add_trace(go.Scatter(
        x=[],
        y=[],
        mode='lines',
        name=column
    ))

# Add frames for animation
frames = [
    go.Frame(
        data=[go.Scatter(x=central.index[:i+1], y=central[column][:i+1]) for column in central.columns],
        name=f'frame{i}'
    )
    for i in range(len(central))
]

# Add frames to the figure
fig.frames = frames

# Add animation controls
fig.update_layout(
    updatemenus=[{
        'type': 'buttons',
        'showactive': False,
        'buttons': [{
            'label': 'Play',
            'method': 'animate',
            'args': [None, {
                'frame': {'duration': 50, 'redraw': True},  # Duration in milliseconds
                'fromcurrent': True,
            }]
        }]
    }],
    hovermode='x unified',
    xaxis=dict(showgrid=True, range=[0, n[-1]+1]),
    yaxis=dict(showgrid=True),
    autosize=True
)

# Display the chart in Streamlit
st.plotly_chart(fig, use_container_width=True)

# progress_bar.empty()

# Add download functionality
csv = central.to_csv(index=True)
st.download_button(
    label="Download data as CSV",
    data=csv,
    file_name='trading_analysis.csv',
    mime='text/csv'
)

