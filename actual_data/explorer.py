import os
import re
import pandas as pd
import matplotlib.pyplot as plt

def accumulate(path):
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

if __name__ == '__main__':
    df = accumulate("europe")
    df.plot(x="Date", y="Deaths")
    plt.show()
