import pandas as pd
from matplotlib import style
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import time
import serial  # For Arduino communication
import numpy as np
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

# Initialize Arduino communication
arduino = serial.Serial(port='COM4', baudrate=115200, timeout=1)

# Define thresholds and timers
blink_count = 0
turn_direction = True  # True for right, False for left
single_blink_detected = False
last_blink_time = None
double_blink_time_threshold = 2.0  # 2 second for double blink
previous_rise = None

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

    # Compute differences to detect rate of change
    diff = np.diff(eegdf["ch2"].values)
    rise = np.max(diff)
    drop = np.min(diff)

    #print(f"Current rise: {rise}, Previous rise: {previous_rise}")

    # Blink detection based on comparison with previous rise value
    if previous_rise is not None and rise > (previous_rise + 6):  # Blink threshold logic
        current_time = time.time()
        print("Blink detected")

        # Blink timing logic
        if last_blink_time is None:  # First blink
            last_blink_time = current_time
            blink_count = 1
        else:
            time_diff = current_time - last_blink_time
            #print(f"Time since last blink: {time_diff:.2f} seconds")  # Debugging output


            if time_diff <= double_blink_time_threshold:  # Double blink timing check
                blink_count += 1
                #print(f"Double blink detected, count: {blink_count}")
            else:
                # Reset blink count if time difference exceeds threshold
                blink_count = 1  # Treat this as a new blink
            last_blink_time = current_time  # Update the last blink time

        # Check for single and double blink detection
        if blink_count == 1:
            single_blink_detected = True
        elif blink_count == 2:
            print("Double blink detected")
            blink_count = 0  # Reset blink count after double blink
            arduino.write(b's')  # Send 's' to shoot
            print("Shoot")

        if single_blink_detected:
            if turn_direction:
                arduino.write(b'd')  # Right
                arduino.write(b'd')  # Right
                arduino.write(b'd')  # Right
                arduino.write(b'd')  # Right
                print("turn1")
            else:
                arduino.write(b'd')  # Left
                arduino.write(b'd')  # Left
                arduino.write(b'd')  # Right
                arduino.write(b'd')  # Right
                print("turn2")
            turn_direction = not turn_direction
            single_blink_detected = False

    # Jaw clench detection based on rise and drop
    if rise > 100 and drop < -150:  # Jaw clench threshold
        print("Jaw clench detected")
        arduino.write(b'w')
        print("Move Forward")
    previous_rise = rise


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
