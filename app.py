"""
AI DOCUMENTATION
----------------
AI Tools Used: Google Gemini

Key Prompts Provided:
1. "calculating the flow rate of an undersaturated volatile oil using Darcy's Law"
2. "radial flow"
3. "a full, fixed baseline curve (for example, plotting Pressure Differential from 0 up to a hardcoded maximum of 5,000 psi) and dynamically highlight the user's specific slider input"

Manual Verification/Fix:
The most important element I had to manually verify was the correct application of the standard oilfield unit conversion factor (7.08e-3) within the steady-state radial flow equation, as well as confirming the physical boundary logic in the error handling to ensure unphysical negative values wouldn't bypass the warning state.
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- 1. TITLE, SUBTITLE, AND INSTRUCTIONS ---
st.title("PE 262: Radial Flow Dashboard")
st.subheader("Undersaturated Volatile Oil IPR Calculator")
st.write(
    "**Instructions:** Adjust the formation and fluid properties in the sidebar. "
    "The application will calculate steady-state radial flow, generate a performance table, "
    "and plot your specific operating point on the baseline IPR curve."
)

# --- 2. SIDEBAR INPUTS ---
st.sidebar.header("Input Parameters")

# Sliders deliberately allow zero/negative values to demonstrate error handling
permeability = st.sidebar.slider("Permeability (mD)", min_value=-50.0, max_value=1000.0, value=150.0, step=10.0)
pressure_diff = st.sidebar.slider("Pressure Differential (psi)", min_value=-500.0, max_value=5000.0, value=1500.0, step=50.0)
viscosity = st.sidebar.slider("Viscosity (cp)", min_value=0.0, max_value=10.0, value=1.5, step=0.1)

# --- 3. ERROR HANDLING ---
# Catches unphysical values or division-by-zero attempts before they break the application
if permeability <= 0 or pressure_diff < 0 or viscosity <= 0:
    st.warning("Error. Check input parameters")
else:
    # --- 4. BACKEND CALCULATIONS ---
    # Static Constants
    h = 50.0     # Reservoir thickness (ft)
    re = 1000.0  # External drainage radius (ft)
    rw = 0.5     # Wellbore radius (ft)
    Bo = 1.5     # Formation Volume Factor (rb/STB)
    
    # Darcy's Law Function for Radial Flow (Oilfield Units)
    def calculate_flow(k, dp, mu):
        return (7.08e-3 * k * h * dp) / (mu * Bo * np.log(re / rw))
    
    # Calculate dynamic user operating point
    operating_q = calculate_flow(permeability, pressure_diff, viscosity)
    
    # Generate Baseline Curve Array (0 to 5000 psi)
    dp_array = np.linspace(0, 5000, 20)
    q_array = [calculate_flow(permeability, p, viscosity) for p in dp_array]
    
    # --- 5. PANDAS RESULTS TABLE ---
    st.subheader("Performance Table")
    df = pd.DataFrame({
        "Pressure Differential (psi)": dp_array,
        "Flow Rate (STB/d)": q_array
    })
    # Display the table with formatting to two decimal places
    st.dataframe(df.style.format("{:.2f}"))
    
    # --- 6. MATPLOTLIB CHART ---
    st.subheader("Inflow Performance Relationship (IPR)")
    fig, ax = plt.subplots(figsize=(8, 5))
    
    # Plotting baseline curve
    ax.plot(q_array, dp_array, color='#003366', linewidth=2, label="IPR Baseline")
    
    # Highlighting the dynamic user operating point
    ax.scatter(operating_q, pressure_diff, color='#FF3333', s=100, zorder=5, label="Operating Point")
    
    # Chart formatting
    ax.set_xlabel("Flow Rate, q (STB/d)")
    ax.set_ylabel("Pressure Differential, $\Delta$P (psi)")
    ax.set_title("IPR Curve for Undersaturated Volatile Oil")
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.legend()
    
    # Render plot in Streamlit
    st.pyplot(fig)
