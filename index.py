from dash import html
from app import app

app.layout = html.Div(
    children=[
        html.H1(children="Roulette Dashboard"),
        # dcc.Interval(id='interval-component', interval=1*1000, n_intervals=0)  # 1*1000=1000 milliseconds=1 second
    ]
)


if __name__ == "__main__":
    app.run_server(debug=True)

