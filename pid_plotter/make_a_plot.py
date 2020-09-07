import pandas as pd
import matplotlib.pyplot as plt
from pid_plotter import pid_plot

df = pd.read_csv('pid_plotter/imin_df.csv', index_col=0)

my_rule = df[df['rule'] == 110]

plt.figure()

pid_plot(my_rule, 3)

plt.savefig('test.png')
