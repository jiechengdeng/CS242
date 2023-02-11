import matplotlib.pyplot as plt

data = {100000:3.16, 200000:5.79,300000:8.41, 400000:11.04, 500000:13.67,
        600000:16.36, 700000:19.01, 800000:21.72, 900000:24.44, 1000000:27.23,
        1100000:30.05}

y = list(data.values())
x = list(data.keys())
fig, ax = plt.subplots(figsize=(15,5))
ax.set_xscale('linear')
ax.get_xaxis().get_major_formatter().set_scientific(False)

ax.set_yscale('linear')
ax.get_yaxis().get_major_formatter().set_scientific(False)
plt.plot(x, y)
plt.xlabel("Number of Documents",fontsize=15)
plt.ylabel("Time (in minutes)",fontsize=15)
plt.title("Time vs Number of Documents",fontsize=15)
plt.show()