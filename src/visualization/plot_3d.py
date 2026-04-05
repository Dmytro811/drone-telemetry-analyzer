import plotly.graph_objects as go

def plot_3d_trajectory(df, color_by='spd'):
    """
    Будує 3D траєкторію з динамічним фарбуванням.
    """
    if df.empty or 'east' not in df or 'north' not in df or 'up' not in df:
        return None

    # Беремо значення для фарбування (швидкість або час)
    values = df[color_by]

    # Будуємо графік використовуючи рідні можливості Plotly
    fig = go.Figure(data=[go.Scatter3d(
        x=df['east'],
        y=df['north'],
        z=df['up'],
        mode='lines+markers',
        # Фарбуємо ЛІНІЮ та МАРКЕРИ
        line=dict(
            color=values, 
            colorscale='Turbo', # Turbo - дуже красивий кольоровий перехід від синього до червоного
            width=5
        ),
        marker=dict(
            size=2, 
            color=values, 
            colorscale='Turbo', 
            showscale=True, # Показує шкалу швидкості збоку
            colorbar=dict(title="Швидкість (м/с)" if color_by == 'spd' else "Час")
        ),
        name='Траєкторія'
    )])

    # Налаштовуємо вигляд
    fig.update_layout(
        title=f'3D Траєкторія польоту',
        scene=dict(
            xaxis_title='Схід (метри)',
            yaxis_title='Північ (метри)',
            zaxis_title='Висота (метри)'
        ),
        template="plotly_dark", # Темна тема виглядає крутіше і сучасніше
        margin=dict(l=0, r=0, b=0, t=40)
    )

    return fig