import pandas as pd
from matplotlib import style
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import time
import serial  # For Arduino communication
import numpy as np
import threading
from brainflow.board_shim import BoardShim, BrainFlowInputParams
from brainflow.data_filter import DataFilter, FilterTypes

# Initialize BrainFlow board and start streaming
BoardShim.enable_dev_board_logger()
params = BrainFlowInputParams()
params.board_id = 1
board_id = 1
params.serial_port = 'COM7'
board = BoardShim(board_id, params)
eeg_channels = BoardShim.get_eeg_channels(board_id)
sampling_rate = BoardShim.get_sampling_rate(board_id)
timestamp = BoardShim.get_timestamp_channel(board_id)

# Get the accelerometer channels for the specific board
accel_channels = BoardShim.get_accel_channels(board.board_id)

# Initialize Arduino communication
arduino = serial.Serial(port='COM4', baudrate=115200, timeout=1)

# Define thresholds and timers
blink_count = 0
turn_direction = True  # True for right, False for left
single_blink_detected = False
last_blink_time = None
double_blink_time_threshold = 2.0  # 2 seconds for double blink
previous_rise = None

# Start BrainFlow session
board.prepare_session()
board.start_stream()

# Set up the figure for 4 subplots
fig, axs = plt.subplots(4, 1, figsize=(10, 8))
fig.suptitle("Live EEG stream from Brainflow", fontsize=15)
style.use('fivethirtyeight')

# Initialize lists for plotting
eeg1, eeg2, eeg3, eeg4, timex = [], [], [], [], []


# Blink and Jaw Clench Detection Function
def detect_blinks_and_jaw_clench(eegdf):
    global blink_count, turn_direction, single_blink_detected, last_blink_time, previous_rise
    diff = np.diff(eegdf["ch2"].values)
    rise = np.max(diff)
    drop = np.min(diff)

    if previous_rise is not None and rise > (previous_rise + 6):
        current_time = time.time()
        print("Blink detected, JUMP")

    if rise > 100 and drop < -150:
        print("Jaw clench detected, ATTACK")
    previous_rise = rise


def get_accelerometer_data(num_samples=50):
    # Fetch data from the board; retrieve the latest 'num_samples' samples
    data = board.get_current_board_data(num_samples)

    if data is None:
        print("No data retrieved from the board.")
        return

    # Check if the accelerometer data is being retrieved correctly
    if len(data) == 0 or len(data[accel_channels]) == 0:
        print("No accelerometer data found.")
        return

    # Extract accelerometer data for each axis (X, Y, Z)
    accel_x = data[accel_channels[0]]
    accel_y = data[accel_channels[1]]
    accel_z = data[accel_channels[2]]

    # Print the latest accelerometer values for each axis
    print("Accelerometer Data (Last sample):")
    print(f"X-axis: {accel_x[-1]}")
    print(f"Y-axis: {accel_y[-1]}")
    print(f"Z-axis: {accel_z[-1]}")

    # Optionally, print all 'num_samples' values for a more detailed view
    print("\nAll Recent Accelerometer Data:")
    for i in range(num_samples):
        print(f"Sample {i + 1}: X={accel_x[i]}, Y={accel_y[i]}, Z={accel_z[i]}")


# Arduino controller function
def unoController():
    while True:
        if arduino.in_waiting > 0:
            line = arduino.readline().decode('utf-8').strip()
            if line:
                print(f"Controller Input: {line}")
        time.sleep(0.1)  # Add a small delay to prevent CPU overuse


# Start unoController in a separate thread
controller_thread = threading.Thread(target=unoController, daemon=True)
controller_thread.start()


# Define the function for updating the plot
def update_plot(i):
    global eeg1, eeg2, eeg3, eeg4, timex

    if board.get_board_data_count() >= 250:
        data = board.get_current_board_data(250)

        eegdf = pd.DataFrame(np.transpose(data[eeg_channels]))
        eegdf_col_names = ["ch1", "ch2", "ch3", "ch4"]
        eegdf.columns = eegdf_col_names

        timedf = pd.DataFrame(np.transpose(data[timestamp]))

        for count, channel in enumerate(eeg_channels):
            DataFilter.perform_bandstop(data[channel], sampling_rate, 58.0, 62.0, 4,
                                        FilterTypes.BUTTERWORTH.value, 0)
            DataFilter.perform_bandpass(data[channel], sampling_rate, 11.0, 31.0, 4,
                                        FilterTypes.BESSEL.value, 0)

        eeg1.extend(eegdf.iloc[:, 0].values)
        eeg2.extend(eegdf.iloc[:, 1].values)
        eeg3.extend(eegdf.iloc[:, 2].values)
        eeg4.extend(eegdf.iloc[:, 3].values)
        timex.extend(timedf.iloc[:, 0].values)

        # Call the detection function for blink and jaw clench
        detect_blinks_and_jaw_clench(eegdf)

        # Call the accelerometer data function
        # get_accelerometer_data()

        # Update each subplot with its corresponding EEG channel data
        axs[0].cla()
        axs[1].cla()
        axs[2].cla()
        axs[3].cla()

        axs[0].plot(timex, eeg1, label="Channel 1", color="red")
        axs[1].plot(timex, eeg2, label="Channel 2", color="blue")
        axs[2].plot(timex, eeg3, label="Channel 3", color="orange")
        axs[3].plot(timex, eeg4, label="Channel 4", color="purple")

        # Label each subplot
        axs[0].set_title("Channel 1")
        axs[1].set_title("Channel 2")
        axs[2].set_title("Channel 3")
        axs[3].set_title("Channel 4")

        for ax in axs:
            ax.set_xlabel("Time")
            ax.set_ylabel("Millivolts")

        plt.tight_layout()


# Run the animation continuously
ani = FuncAnimation(fig, update_plot, interval=5)

plt.tight_layout()
plt.show()

# Stop streaming and release the session when done
board.stop_stream()
board.release_session()
arduino.close()
