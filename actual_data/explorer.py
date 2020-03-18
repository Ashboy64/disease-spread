import os
import re
import pandas as pd
import matplotlib.pyplot as plt

def accumulate_actual_italy(path):
    main_df = pd.DataFrame({"Date":[], "Cases":[], "Deaths":[]})
    for fname in os.listdir(path):

        date = re.search('2.*_0', fname)
        date = date.group(0)[:-2]

        df = pd.read_csv(os.path.join(path, fname))
        for col in list(df):
            if col != "Cases" and col != "Deaths":
                country_col = col
                break
        df = df.loc[df[country_col] == "Italy"]
        df = df.drop([country_col], axis=1)
        df["Date"] = date
        main_df = main_df.append(df)

    return main_df

def accumulate_simulated(path):
    df = pd.read_csv(os.path.join(path, "log.csv"))
    df = df.drop([col for col in list(df) if col != "dead"], axis=1)
    df = df.loc[df["dead"] > 0].head(18)
    df["dead"] = df["dead"].apply(lambda x: 206*x)
    df["Deaths"] = df["dead"]
    df = df.drop(["dead"], axis=1)
    return df

if __name__ == '__main__':
    df = accumulate_actual_italy("europe")
    simulated = accumulate_simulated("../logs/log_18_03_2020_11_44_25")

    df.index = simulated.index
    df["Simulated Deaths"] = simulated["Deaths"]
    df["Actual Deaths"] = df["Deaths"]
    df = df.drop(["Deaths", "Cases"], axis=1)

    df.plot()
    plt.show()
