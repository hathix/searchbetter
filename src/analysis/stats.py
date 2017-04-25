import pandas as pd

def summary_of_frame(df):
    """
    Returns a dataframe containing the mean and standard deviation of the dataframe.
    """
    means = df.mean()
    stds = df.std()
    summary = pd.concat([means, stds], axis=1)
    summary.columns = ['mean', 'std']
    return summary
