import plotly.graph_objects as go
from .color_mapping import get_color_map

def plot_3d_trajectory(df, color_by='spd'):
    """
    Create a 3D plot of the trajectory with color mapping.

    Args:
        df (pd.DataFrame): DataFrame with 'east', 'north', 'up', and color_by column
        color_by (str): Column to color by ('spd' for speed, 'timestamp' for time)

    Returns:
        plotly Figure
    """
    if df.empty or 'east' not in df or 'north' not in df or 'up' not in df:
        return None

    values = df[color_by]
    colors = get_color_map(values)

    fig = go.Figure(data=[go.Scatter3d(
        x=df['east'],
        y=df['north'],
        z=df['up'],
        mode='lines+markers',
        line=dict(color='blue', width=2),
        marker=dict(size=4, color=colors, colorscale='Viridis', showscale=True),
        name='Trajectory'
    )])

    fig.update_layout(
        title=f'3D Trajectory colored by {color_by}',
        scene=dict(
            xaxis_title='East (m)',
            yaxis_title='North (m)',
            zaxis_title='Up (m)'
        )
    )

    return fig