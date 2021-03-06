
# Simulation configurations
ARRAY_MESH_CALCULATION = True
EN_WIND = False

# Genetic Algorithm configurations
GA_POP_NUM = 10         # Population per generation
GA_GEN_NUM = 100        # Number of generations
GA_MULTITHREAD = False  # Enable multithreading

# Route parameters
SL_CONTROL_STOP = 16.67  # Control stop speed limit (ms-1)
SL_HIGHWAY = 36.1  # Highway speed limit (ms-1)

# Control stop parameters
CS_EXIT_TIME = 1     # Amount of time for driver to enter control stop and exit vehicle to hit timer (minutes)
CS_ENTER_TIME = 1    # Amount of time for driver to hit timer and exit control stop (minutes)
CS_WAIT_TIME = 30    # Amount of time to hold during the control stop (minutes)

# Start/end of day parameters
SE_START_SETUP_TIME = 2 # Amount of time to set up driver before start of day
SE_END_SETUP_TIME = 2   # Amount of time to set up charging after end of day stop
