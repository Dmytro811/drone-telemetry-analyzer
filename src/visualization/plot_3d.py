import plotly.graph_objects as go
import pandas as pd

def plot_3d_trajectory(enu_df, color_by='spd'):
    """
    Побудова 3D траєкторії з примусовим кубічним виглядом сцени.
    """
    if enu_df is None or enu_df.empty:
        return None

    fig = go.Figure()

    # Основна лінія траєкторії
    fig.add_trace(go.Scatter3d(
        x=enu_df['east'],
        y=enu_df['north'],
        z=enu_df['up'],
        mode='lines',
        line=dict(
            color=enu_df[color_by] if color_by in enu_df else None,
            colorscale='Viridis',
            width=5,
            colorbar=dict(title="Швидкість (м/с)" if color_by == 'spd' else "Час")
        ),
        name='Траєкторія'
    ))

    # Точки старту та фінішу
    fig.add_trace(go.Scatter3d(
        x=[enu_df['east'].iloc[0]], y=[enu_df['north'].iloc[0]], z=[enu_df['up'].iloc[0]],
        mode='markers', marker=dict(size=6, color='green'), name='Старт'
    ))
    fig.add_trace(go.Scatter3d(
        x=[enu_df['east'].iloc[-1]], y=[enu_df['north'].iloc[-1]], z=[enu_df['up'].iloc[-1]],
        mode='markers', marker=dict(size=6, color='red'), name='Фініш'
    ))

    # --- НАЛАШТУВАННЯ САМЕ ТУТ ---
    fig.update_layout(
        title="3D Аналіз польоту",
        template="plotly_dark",
        scene=dict(
            xaxis_title='Схід (м)',
            yaxis_title='Північ (м)',
            zaxis_title='Висота (м)',
            # 'cube' змушує всі осі виглядати однаковими за довжиною візуально
            aspectmode='cube', 
            # Додаємо сітку, щоб було краще видно об'єм
            xaxis=dict(showgrid=True, zeroline=True),
            yaxis=dict(showgrid=True, zeroline=True),
            zaxis=dict(showgrid=True, zeroline=True),
        ),
        margin=dict(l=0, r=0, b=0, t=40),
        # Робимо саму область графіка більшою
        height=700 
    )

    return fig