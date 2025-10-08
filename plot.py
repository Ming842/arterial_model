import pickle
import numpy as np

# Replace 'your_file.pkl' with the path to your pickle file
with open('Output\simulation_output_006.pkl', 'rb') as f:
    data = pickle.load(f)

print(data)

import matplotlib.pyplot as plt

# Plot the output (data.x) and input (data.y0) on separate subplots for clarity
fig, axs = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

indices = np.where((data.t >= 0) & (data.t < 10))[0]
print(f'Indices where 2 < t < 4: {indices}')
print(f'Corresponding t values: {data.t[indices]}')
# Output plot
# axs[0].plot(data.t[indices], data.x[indices, 2], label='Output: ' + data.xnames[2], color='tab:blue')
axs[0].plot(data.t, data.x[:, 20], label='Output: ' + data.xnames[20], color='tab:blue')
axs[0].set_ylabel('Output Value')
axs[0].legend()
axs[0].grid(True)

# Input plot
axs[1].plot(data.t, data.y0, label='Input', linestyle='--', color='tab:orange')
axs[1].set_xlabel('Time (s)')
axs[1].set_ylabel('Input Value')
axs[1].legend()
axs[1].grid(True)

plt.tight_layout()
plt.show()


print(len(data.t))
sum_x = sum(data.x[indices, 2])
print(f'Sum of output values from index 100 to 200: {sum_x}')