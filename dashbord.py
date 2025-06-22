
import numpy as np
import pandas as pd
import plotly.figure_factory as ff
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots
from dash import Dash, html, dcc, Input, Output
df = pd.read_csv(r"D:\مشاريعي\BA\insurance.csv")
df['Age Group'] = pd.cut(df['age'],
                         bins=[0, 35, 55, 100],
                         labels=['Young (18-35)', 'Middle (36-55)', 'Senior (55+)'],
                         right=False)

df['weight_condition'] = pd.cut(df['bmi'],
                                bins=[0, 18.5, 25, 30, 100],
                                labels=['Underweight', 'Normal Weight', 'Overweight', 'Obese'])

df['age_cat'] = pd.cut(df['age'],
                       bins=[0, 35, 55, 100],
                       labels=['Young Adult', 'Adult', 'Senior'],
                       right=False)

bmi_data = df["bmi"].values.tolist()

app = Dash(__name__)
server = app.server


themes = {
    "dark": {
        "bg": "#1a1a1a",  
        "text": "#fbf6ee",  
        "secondary_text": "#d9d9d9", 
        "accent": "#fd7922",  
        "light_accent": "#f7e9cc",  
        "pie_colors": ["#fd7922", "#f7e9cc", "#fbf6ee", "#d65a31"],
        "heatmap_scale": [[0.0, '#f7e9cc'], [0.5, '#fd7922'], [1.0, '#262626']],
        "border": "1px solid #333333"  
    },
    "light": {
        "bg": "#f5f5f5",  
        "text": "#333333",
        "secondary_text": "#666666",
        "accent": "#fd7922",
        "light_accent": "#ffd699",
        "pie_colors": ["#fd7922", "#ffcc99", "#ffd699", "#e69500"],
        "heatmap_scale": [[0.0, '#ffd699'], [0.5, '#fd7922'], [1.0, '#4a4a4a']],
        "border": "1px solid #e6e6e6"
    }
}


app.layout = html.Div([
    html.H1("Charge & Customer Analysis Dashboard", id='main-title', style={'textAlign': 'center', 'marginBottom': '20px'}),

    html.Button("Toggle Dark/Light Mode", 
        id="toggle-theme", 
        n_clicks=0,
        style={
            'padding': '10px 20px',
            'borderRadius': '8px',
            'backgroundColor': '#fd7922',
            'color': 'white',
            'border': 'none',
            'fontWeight': 'bold',
            'cursor': 'pointer',
            'margin': '0 auto 30px',
            'display': 'block',
            'boxShadow': '0 2px 5px rgba(0,0,0,0.2)'
    }),

 
 dcc.Graph(id='charge-distribution'),
    dcc.Graph(id='age-distribution'),
    dcc.Graph(id='correlation-heatmap'),
    dcc.Graph(id='bmi-distribution'),
    dcc.Graph(id='bmi-distribution-age'),
    dcc.Graph(id='bmi-distribution-smoker'),
    dcc.Graph(id='charges-vs-age-category'),
    dcc.Graph(id='weight-condition-vs-age-charges'),
    dcc.Graph(id='smoker-weight-condition-vs-charges'),
    dcc.Graph(id='charges-distribution-weight-condition-smoker'),
    dcc.Graph(id='charges-status-pair-plot', style={'marginBottom': '20px'}),
   dcc.Graph(id='charges-weight-condition-radar'),
    ],id='main-container', style={
    'padding': '20px',
    'maxWidth': '1400px',
    'margin': '0 auto',
    'fontFamily': 'Arial, sans-serif'
})

@app.callback(
    [Output('main-container', 'style'),
     Output('main-title', 'style'),
     Output('charge-distribution', 'figure'),
     Output('age-distribution', 'figure'),
     Output('correlation-heatmap', 'figure'),
     Output('bmi-distribution', 'figure'),
     Output('bmi-distribution-age', 'figure'),
     Output('bmi-distribution-smoker', 'figure'),
     Output('charges-vs-age-category', 'figure'),
     Output('weight-condition-vs-age-charges', 'figure'),
     Output('smoker-weight-condition-vs-charges', 'figure'),
     Output('charges-distribution-weight-condition-smoker', 'figure'), 
     Output('charges-status-pair-plot', 'figure'),
     Output('charges-weight-condition-radar', 'figure')], 
    Input('toggle-theme', 'n_clicks')
)
def update_dashboard(n_clicks):
    mode = "dark" if n_clicks % 2 == 0 else "light"
    theme = themes[mode]

    # 1. توزيع الشحنات
    trace0 = go.Histogram(x=df["charges"], name="Charges", marker=dict(color=theme["accent"]))
    trace1 = go.Histogram(x=np.log(df["charges"]), name="Log Charges", marker=dict(color=theme["light_accent"]))

    dist_fig = make_subplots(rows=1, cols=2, subplot_titles=["Charge Distribution", "Log Charge Distribution"])
    dist_fig.add_trace(trace0, 1, 1)
    dist_fig.add_trace(trace1, 1, 2)
    dist_fig.update_layout(
        title="Charge Distribution Analysis",
        bargap=0.05,
        showlegend=True,
        plot_bgcolor=theme["bg"],
        paper_bgcolor=theme["bg"],
        font=dict(color=theme["text"]),
        title_font=dict(size=18, color=theme["accent"]),
        margin=dict(l=50, r=50, t=80, b=50),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        )
    )
    dist_fig.update_annotations(font=dict(color=theme["text"], size=12))

    # 2. توزيع العملاء حسب العمر
    pie_fig = px.pie(df, names='Age Group', title='Customer Distribution by Age Group',
                     color_discrete_sequence=theme["pie_colors"], hole=0.3)
    pie_fig.update_traces(
        textinfo='percent+value', 
        marker_line_color='rgba(0,0,0,0.3)', 
        marker_line_width=1.5,
        textfont=dict(color=theme["bg"], size=12)
    )
    pie_fig.update_layout(
        plot_bgcolor=theme["bg"], 
        paper_bgcolor=theme["bg"],
        font=dict(color=theme["text"]), 
        title_font=dict(size=18, color=theme["accent"]),
        margin=dict(l=50, r=50, t=80, b=50),
        legend=dict(
            font=dict(size=12),
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )

    # 3. خريطة الارتباط
    numeric_df = df.select_dtypes(include=['number'])
    corr = numeric_df.corr()
    heatmap = go.Heatmap(
        z=corr.values,
        x=corr.columns,
        y=corr.columns,
        colorscale=theme["heatmap_scale"],
        colorbar=dict(title='Correlation', tickfont=dict(color=theme["text"]))
    )
    heatmap_fig = go.Figure(data=[heatmap])
    heatmap_fig.update_layout(
        title="Heatmap of Correlation Matrix",
        xaxis_title="Features",
        yaxis_title="Features",
        plot_bgcolor=theme["bg"],
        paper_bgcolor=theme["bg"],
        font=dict(color=theme["text"]),
        title_font=dict(size=18, color=theme["accent"]),
        margin=dict(l=80, r=50, t=80, b=80),
        xaxis=dict(tickfont=dict(size=10)),
        yaxis=dict(tickfont=dict(size=10))
    )

    # 4. توزيع مؤشر كتلة الجسم
    bmi_fig = ff.create_distplot([bmi_data], ['Body Mass Index Distribution'],
                                 colors=[theme["accent"]], show_rug=False)
    bmi_fig.update_layout(
        title='Normal Distribution<br>Central Limit Theorem Condition',
        plot_bgcolor=theme["bg"],
        paper_bgcolor=theme["bg"],
        font=dict(color=theme["text"], size=12),
        title_font=dict(size=18, color=theme["accent"]),
        legend=dict(bgcolor=theme["bg"]),
        margin=dict(l=50, r=50, t=80, b=50),
        xaxis=dict(title="BMI Value"),
        yaxis=dict(title="Density")
    )

    # 5. توزيع مؤشر كتلة الجسم حسب الفئة العمرية
    age_groups = {
        'Young Adult': theme["pie_colors"][0],
        'Adult': theme["pie_colors"][1],
        'Senior': theme["pie_colors"][2]
    }

    data1 = []
    for group, color in age_groups.items():
        data1.append(go.Box(
            y=df[df['age_cat'] == group]['bmi'],
            name=group,
            boxmean=True,
            marker=dict(color=color),
            boxpoints='outliers',
            line=dict(color=theme["text"])
        ))

    bmi_age_layout = go.Layout(
        title="<b>Body Mass Index Distribution by Age Category</b>",
        titlefont=dict(size=18, color=theme["accent"]),
        xaxis=dict(
            title="<b>Age Category</b>", 
            titlefont=dict(size=14, color=theme["text"]),
            tickfont=dict(color=theme["text"])
        ),
        yaxis=dict(
            title="<b>Body Mass Index (BMI)</b>", 
            titlefont=dict(size=14, color=theme["text"]),
            tickfont=dict(color=theme["text"])
        ),
        plot_bgcolor=theme["bg"],
        paper_bgcolor=theme["bg"],
        font=dict(color=theme["text"]),
        margin=dict(l=50, r=50, t=80, b=50),
        boxmode='group'
    )

    bmi_age_fig = go.Figure(data=data1, layout=bmi_age_layout)

    # 6. مؤشر كتلة الجسم حسب التدخين والعمر
    groups = [
        ('Young Adult', 'yes', 'Young A. Smoker'),
        ('Young Adult', 'no', 'Young A. Non-Smoker'),
        ('Adult', 'yes', 'Senior A. Smoker'),
        ('Adult', 'no', 'Senior A. Non-Smoker'),
        ('Senior', 'yes', 'Elder Smoker'),
        ('Senior', 'no', 'Elder Non-Smoker')
    ]

    colors = theme["pie_colors"] + [theme["accent"], theme["light_accent"]]

    traces = []
    for (age_group, smoker, name), color in zip(groups, colors):
        bmi_values = df.loc[(df['age_cat'] == age_group) & (df['smoker'] == smoker), 'bmi'].values
        traces.append(go.Box(
            y=bmi_values,
            name=name,
            boxpoints='outliers',
            jitter=0.5,
            whiskerwidth=0.2,
            fillcolor=color,
            marker=dict(size=4, color=theme["text"]),
            line=dict(width=1, color=theme["text"])
        ))

    bmi_smoker_layout = go.Layout(
        title='<b>Body Mass Index of Smokers Status by Age Category</b>',
        titlefont=dict(size=18, color=theme["accent"]),
        xaxis=dict(
            title='<b>Status</b>', 
            titlefont=dict(size=14, color=theme["text"]),
            tickfont=dict(color=theme["text"])
        ),
        yaxis=dict(
            title='<b>Body Mass Index</b>', 
            titlefont=dict(size=14, color=theme["text"]),
            tickfont=dict(color=theme["text"]), 
            dtick=5
        ),
        plot_bgcolor=theme["bg"],
        paper_bgcolor=theme["bg"],
        showlegend=False,
        font=dict(color=theme["text"]),
        margin=dict(l=50, r=50, t=80, b=50)
    )

    bmi_smoker_fig = go.Figure(data=traces, layout=bmi_smoker_layout)

    # 7. الشحنات مقابل الفئة العمرية
    fig1 = px.strip(df, x="age_cat", y="charges",
                    title="Charges vs Age Category",
                    color_discrete_sequence=[theme["accent"]])
    fig1.update_layout(
        plot_bgcolor=theme["bg"], 
        paper_bgcolor=theme["bg"],
        font=dict(color=theme["text"]),
        title_font=dict(size=18, color=theme["accent"]),
        yaxis=dict(
            color=theme["text"], 
            gridcolor=theme["secondary_text"],
            tickfont=dict(color=theme["text"]), 
            zerolinecolor=theme["secondary_text"]
        ),
        xaxis=dict(
            color=theme["text"],
            tickfont=dict(color=theme["text"])
        ),
        margin=dict(l=50, r=50, t=80, b=50)
    )

    # 8. حالة الوزن + الفئة العمرية مقابل الشحنات
    fig2 = px.strip(df, x="age_cat", y="charges", color="weight_condition",
                    title="Weight Condition vs Age and Charges",
                    color_discrete_sequence=theme["pie_colors"])
    fig2.update_layout(
        plot_bgcolor=theme["bg"], 
        paper_bgcolor=theme["bg"],
        font=dict(color=theme["text"]),
        title_font=dict(size=18, color=theme["accent"]),
        yaxis=dict(
            color=theme["text"], 
            gridcolor=theme["secondary_text"],
            tickfont=dict(color=theme["text"]), 
            zerolinecolor=theme["secondary_text"]
        ),
        xaxis=dict(
            color=theme["text"],
            tickfont=dict(color=theme["text"])
        ),
        margin=dict(l=50, r=50, t=80, b=50),
        legend=dict(
            title="Weight Condition",
            font=dict(size=12),
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    # 9. المدخن + حالة الوزن مقابل الشحنات
    fig3 = px.strip(df, x="smoker", y="charges", color="weight_condition",
                    title="Smoker Status vs Charges",
                    color_discrete_sequence=theme["pie_colors"])
    fig3.update_layout(
        plot_bgcolor=theme["bg"], 
        paper_bgcolor=theme["bg"],
        font=dict(color=theme["text"]),
        title_font=dict(size=18, color=theme["accent"]),
        yaxis=dict(
            color=theme["text"], 
            gridcolor=theme["secondary_text"],
            tickfont=dict(color=theme["text"]), 
            zerolinecolor=theme["secondary_text"]
        ),
        xaxis=dict(
            color=theme["text"],
            tickfont=dict(color=theme["text"])
        ),
        margin=dict(l=50, r=50, t=80, b=50),
        legend=dict(
            title="Weight Condition",
            font=dict(size=12),
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    # 10. توزيع الشحنات حسب حالة الوزن والتدخين
    point_pos_smoker = [-0.9, -1.1, -0.6, -0.3]
    point_pos_non_smoker = [0.45, 0.55, 1, 0.4]
    show_legend_flags = [True, False, False, False]
    
    smoker_colors = {
        'fill': theme["accent"],
        'line': '#d65a31',
        'marker': theme["light_accent"]
    }

    non_smoker_colors = {
        'fill': theme["light_accent"],
        'line': '#b3b3b3',
        'marker': theme["text"]
    }

    data = []
    weight_conditions = pd.unique(df['weight_condition'])

    for i, condition in enumerate(weight_conditions):
        for smoker_status, colors, point_pos, group_name in [
            ('yes', smoker_colors, point_pos_smoker[i], 'Smoker'),
            ('no', non_smoker_colors, point_pos_non_smoker[i], 'Non-Smoker')
        ]:
            trace = go.Violin(
                x=df['weight_condition'][(df['smoker'] == smoker_status) & (df['weight_condition'] == condition)],
                y=df['charges'][(df['smoker'] == smoker_status) & (df['weight_condition'] == condition)],
                name=group_name,
                side='negative' if smoker_status == 'yes' else 'positive',
                legendgroup=group_name,
                scalegroup=group_name,
                showlegend=show_legend_flags[i],
                box=dict(visible=True, width=0.3),
                meanline=dict(visible=True),
                points='all',
                pointpos=point_pos,
                jitter=0.05,
                scalemode='count',
                line=dict(color=colors['line'], width=2),
                marker=dict(size=4, line=dict(width=1, color=colors['marker'])),
                fillcolor=colors['fill'],
                opacity=0.7
            )
            data.append(trace)

    layout = go.Layout(
        title="Charges Distribution by Weight Condition<br><sub>Grouped by Smoking Status",
        titlefont=dict(size=18, color=theme["accent"]),
        yaxis=dict(
            title="Charges",
            titlefont=dict(size=14, color=theme["text"]),
            gridcolor=theme["secondary_text"],
            zeroline=False,
            tickfont=dict(color=theme["text"])
        ),
        xaxis=dict(
            title="Weight Condition",
            titlefont=dict(size=14, color=theme["text"]),
            tickfont=dict(color=theme["text"])
        ),
        violinmode="overlay",
        violingap=0,
        violingroupgap=0,
        plot_bgcolor=theme["bg"],
        paper_bgcolor=theme["bg"],
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color=theme["text"], size=12)
        ),
        margin=dict(l=50, r=50, t=80, b=50)
    )

    fig = go.Figure(data=data, layout=layout)

    # 11. رسوم بيانية متعددة لحالة الشحنات
    df["charge_status"] = pd.qcut(df["charges"], q=3, labels=["Low", "Medium", "High"])

    custom_palette = {
        "Low": theme["light_accent"],
        "Medium": theme["accent"],
        "High": theme["text"]
    }

    fig4 = px.scatter_matrix(df,
                            dimensions=["age", "bmi", "charges"],
                            color="charge_status",
                            color_discrete_map=custom_palette,
                            title="Advanced Charges Analysis<br>Interactive Pair Plot by Charge Status",
                            labels={"age": "Age", "bmi": "BMI", "charges": "Charges"},
                            hover_data=["smoker", "weight_condition"])

    fig4.update_layout(
        plot_bgcolor=theme["bg"],
        paper_bgcolor=theme["bg"],
        font=dict(color=theme["text"], size=12),
        title_font=dict(size=18, color=theme["accent"]),
        legend_title_text='Charge Status',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=12)
        ),
        margin=dict(l=50, r=50, t=80, b=50)
    )

    fig4.update_traces(
        diagonal_visible=False, 
        showupperhalf=False, 
        marker=dict(
            size=4, 
            line=dict(width=1, color=theme["text"])
        ),
        selector=dict(type='splom')
    )

    # 12. الرسم البياني الراداري
    grouped = df.groupby(['region', 'weight_condition'])['charges'].mean().unstack()
    weight_labels = ['Underweight', 'Normal Weight', 'Overweight', 'Obese']
    regions = grouped.index.tolist()
    grouped = grouped.reindex(columns=weight_labels).fillna(0)

    data = []
    region_colors = theme["pie_colors"]

    for i, region in enumerate(regions):
        values = grouped.loc[region].values.tolist()
        trace = go.Scatterpolar(
            r=values + values[:1],
            theta=weight_labels + weight_labels[:1],
            fill='toself',
            name=region,
            line=dict(color=region_colors[i], width=2),
            fillcolor=f'rgba({int(region_colors[i][1:3], 16)}, {int(region_colors[i][3:5], 16)}, {int(region_colors[i][5:7], 16)}, 0.5)',
            marker=dict(size=4, color=region_colors[i]),
            hovertemplate='<b>%{theta}</b><br>Charges: $%{r:,.2f}<extra></extra>'
        )
        data.append(trace)

    layout = go.Layout(
        title=dict(
            text="<b>Average Medical Charges by Weight Condition</b><br><sub>Regional Comparison</sub>",
            font=dict(size=18, color=theme["accent"]),
            x=0.5,
            xanchor='center'
        ),
        polar=dict(
            radialaxis=dict(
                visible=True,
                color=theme["text"],
                gridcolor=theme["secondary_text"],
                tickfont=dict(color=theme["text"]),
                title=dict(text='Average Charges ($)', font=dict(color=theme["text"]))
            ),
            angularaxis=dict(
                color=theme["text"],
                gridcolor=theme["secondary_text"],
                tickfont=dict(color=theme["text"])
            ),
            bgcolor=theme["bg"],
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5,
            font=dict(color=theme["text"], size=12)
        ),
        paper_bgcolor=theme["bg"],
        plot_bgcolor=theme["bg"],
        hovermode='closest',
        margin=dict(l=50, r=50, t=80, b=50)
    )

    fig5 = go.Figure(data=data, layout=layout)

    fig5.add_annotation(
        text="Data Source: Insurance Dataset",
        xref="paper", yref="paper",
        x=0.5, y=-0.15,
        showarrow=False,
        font=dict(size=10, color=theme["text"])
    )

    return (
        {
            'backgroundColor': theme["bg"], 
            'padding': '20px',
            'borderRadius': '10px',
            'maxWidth': '1400px',
            'margin': '0 auto'
        },
        {
            'textAlign': 'center', 
            'color': theme["accent"],
            'marginBottom': '20px',
            'fontSize': '28px'
        },
        dist_fig,
        pie_fig,
        heatmap_fig,
        bmi_fig,
        bmi_age_fig,
        bmi_smoker_fig,
        fig1,
        fig2,
        fig3,
        fig,
        fig4,
        fig5    
    )

if __name__ == '__main__':
     app.run(debug=True, port=8050)