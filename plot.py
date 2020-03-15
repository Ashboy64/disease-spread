import matplotlib.pyplot as plt
import pandas as pd
import argparse
import os

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plot simulation data on disease spread.')
    parser.add_argument("--dir", type=str, help='path for simulation results')

    args = parser.parse_args()
    df = pd.read_csv(os.path.join(args.dir, "log.csv"))

    unique = df.apply(lambda x: x["susceptible"] + x["latent"] + x["infected"] + x["recovered"] + x["dead"], axis=1).unique()
    print(unique)

    assert len(unique) == 1
    df.plot()
    plt.show()
