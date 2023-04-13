import pandas as pd
import seaborn as sns
import base64
from io import BytesIO

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
# import plotly.graph_objs as go
import plotly.express as px


def correlation_heatmap(tables, col, k=5):
    # Concatenate all tables into a single dataframe
    #df = pd.concat(tables, axis=1)
    df = tables[0]

    # Compute pairwise correlations between all columns
    corr = df.corr(numeric_only=True)

    # Select the k columns that are most highly correlated with the specified column
    top_cols = corr[col].sort_values(ascending=False)[1:k+1].index

    # Extract the corresponding sub-correlation matrix
    corr_top = corr.loc[top_cols, top_cols]

    # Plot the heatmap using seaborn
    #sns.set(style='white')
    # fig = plt.figure(figsize=(8, 5))
    # ax = sns.heatmap(corr_top, cmap='YlGnBu', annot=True, fmt='.2f', linewidths=0.5)
    # ax.set_title(f'Top {k} highest correlated columns with {col} across {len(tables)} tables')

    # fig = go.Heatmap(corr_top)

    fig = px.imshow(corr_top, text_auto=True)
    
    return fig
