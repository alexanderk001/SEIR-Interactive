import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import CheckButtons, Slider, TextBox

# Explicit Euler method for numerical integration
def euler(f, t0, x0, t1, h):
    """
    Solves an ODE using the explicit Euler method.

    Parameters:
        f  : function - The derivative function of the system.
        t0 : float - Initial time.
        x0 : array-like - Initial state vector.
        t1 : float - Final time.
        h  : float - Step size.

    Returns:
        List of time steps and corresponding state values.
    """
    t = t0
    x = x0
    trajectory = [[t, x]]

    for k in range(0, 1 + int((t1 - t0) / h)):
        t = t0 + k * h
        x = x + h * f(t, x)
        trajectory.append([t, x])

    return trajectory

# SEIR model equations
def SEIR_model(beta, alpha, gamma):
    """
    Defines the SEIR model differential equations.

    Parameters:
        beta  : float - Transmission rate.
        alpha : float - Rate at which exposed individuals become infectious.
        gamma : float - Recovery rate.

    Returns:
        Function representing the SEIR model.
    """
    def f(t, x):
        S, E, I, R = x
        return np.array([
            -beta * S * I,              # dS/dt
            beta * S * I - alpha * E,   # dE/dt
            alpha * E - gamma * I,      # dI/dt
            gamma * I                   # dR/dt
        ])
    return f

# SEIR simulation function
def SEIR_simulation(beta, alpha, gamma, E0, I0, days, step=0.1):
    """
    Runs an SEIR model simulation.

    Parameters:
        beta  : float - Transmission rate.
        alpha : float - Rate at which exposed individuals become infectious.
        gamma : float - Recovery rate.
        E0    : float - Initial proportion of exposed individuals.
        I0    : float - Initial proportion of infectious individuals.
        days  : int - Number of days to simulate.
        step  : float - Time step for numerical integration.

    Returns:
        Time array and arrays of S, E, I, R values.
    """
    S0 = 1.0 - E0 - I0  # Initial proportion of susceptible individuals
    x0 = np.array([S0, E0, I0, 0.0])  # Initial state
    f = SEIR_model(beta, alpha, gamma)
    result = euler(f, 0, x0, days, step)
    t, x = zip(*result)
    return np.array(t), np.array(x).T

# Function to create an interactive SEIR diagram
def diagram():
    plt.style.use('seaborn-v0_8-poster')
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.subplots_adjust(left=0.1, bottom=0.4)

    # Initial parameters
    initial_N = 10_000_000
    initial_R0 = 1.0
    initial_alpha = 1 / 5.5
    initial_gamma = 1 / 3.0
    initial_beta = initial_R0 * initial_gamma
    initial_E0 = 10_000
    initial_I0 = 2_000
    initial_days = 140

    # Run initial SEIR simulation
    t, (S, E, I, R) = SEIR_simulation(
        beta=initial_beta,
        alpha=initial_alpha,
        gamma=initial_gamma,
        E0=initial_E0 / initial_N,
        I0=initial_I0 / initial_N,
        days=initial_days
    )

    # Plot SEIR curves
    line_S, = ax.plot(t, S, label='Susceptible (S)', color='blue')
    line_E, = ax.plot(t, E, label='Exposed (E)', color='#FFA500', linestyle='--')
    line_I, = ax.plot(t, I, label='Infectious (I)', color='red')
    line_R, = ax.plot(t, R, label='Recovered (R)', color='green', linestyle='--')

    ax.set_title("SEIR Model Simulation", fontsize=16)
    ax.set_xlabel("Days", fontsize=12)
    ax.set_ylabel("Proportion of Population", fontsize=12)
    ax.legend(fontsize=12, fancybox=True, shadow=True)
    ax.grid(linestyle=':', linewidth=2.0, color='#808080')

    # Interactive controls (sliders and text boxes)

    # Slider for R0
    ax_slider_R0 = plt.axes([0.2, 0.275, 0.65, 0.03])
    slider_R0 = Slider(ax_slider_R0, label='Basic Reproduction Number (R0)', valmin=0.1, valmax=15.0, valinit=initial_R0, valstep=0.1)

    # Text boxes for initial parameters
    textboxes = {
        "Population (N)  ": (0.2, 0.2, str(initial_N)),
        "Initial Exposed (E0)  ": (0.2, 0.125, str(initial_E0)),
        "Initial Infectious (I0)  ": (0.2, 0.05, str(initial_I0)),
        "Simulation Days  ": (0.45, 0.2, str(initial_days)),
        "α (Infection Rate)  ": (0.45, 0.125, f"{initial_alpha:.4f}"),
        "γ (Recovery Rate)  ": (0.45, 0.05, f"{initial_gamma:.4f}")
    }

    textboxes_widgets = {}
    for label, (x, y, initial) in textboxes.items():
        ax_box = plt.axes([x, y, 0.1, 0.05])
        textboxes_widgets[label] = TextBox(ax_box, label, initial=initial)

    # Checkbox for logarithmic scale
    def toggle_log_scale(event):
        ax.set_yscale('log' if ax.get_yscale() == 'linear' else 'linear')
        fig.canvas.draw_idle()

    ax_checkbox_log = plt.axes([0.7, 0.2, 0.1, 0.05])
    checkbox_log = CheckButtons(ax_checkbox_log, labels=['Log Scale'], actives=[False])
    checkbox_log.labels[0].set_fontsize(10)
    checkbox_log.on_clicked(toggle_log_scale)

    # Update function for interactive changes
    def update(val=None):
        try:
            N = int(textboxes_widgets["Population (N)  "].text)
            E0 = int(textboxes_widgets["Initial Exposed (E0)  "].text) / N
            I0 = int(textboxes_widgets["Initial Infectious (I0)  "].text) / N
            days = int(textboxes_widgets["Simulation Days  "].text)
            alpha = float(textboxes_widgets["α (Infection Rate)  "].text)
            gamma = float(textboxes_widgets["γ (Recovery Rate)  "].text)
        except ValueError:
            print("Invalid input! Please enter numeric values.")
            return

        R0 = slider_R0.val
        beta = R0 * gamma

        # Run updated SEIR simulation
        t, (S, E, I, R) = SEIR_simulation(beta=beta, alpha=alpha, gamma=gamma, E0=E0, I0=I0, days=days)

        # Update plot data
        line_S.set_xdata(t)
        line_S.set_ydata(S)
        line_E.set_xdata(t)
        line_E.set_ydata(E)
        line_I.set_xdata(t)
        line_I.set_ydata(I)
        line_R.set_xdata(t)
        line_R.set_ydata(R)

        ax.relim()
        ax.autoscale_view()
        fig.canvas.draw_idle()

    # Connect widgets to update function
    slider_R0.on_changed(update)
    for widget in textboxes_widgets.values():
        widget.on_submit(update)

    plt.show()

# Run the interactive SEIR model visualization
diagram()
