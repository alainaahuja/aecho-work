import dao
from dash import Dash
import dash_core_components as dcc
from dash.dependencies import Input, Output
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px

dashB_app = Dash()

Id_drop = dcc.Dropdown(value = 'AK10010044969',
        options = [
            {'label': 'AK10010074965', 'value': 'AK10010074965'},
            {'label': 'AK10010036519', 'value': 'AK10010036519'},
            {'label': 'AK10010044969', 'value': 'AK10010044969'}
        ], id = 'my-drop')

dashB_app.layout = html.Div([
        html.Div([
            html.H1(children='Aecho Hire Dashboard'),
            Id_drop,
            dcc.Graph(id='id-graph')
        ])
])

@dashB_app.callback(
    Output(component_id='id-graph', component_property='figure'),
    [Input(component_id='my-drop', component_property='value')]
)

def update_id(selected_id):
    interview_id=selected_id
    sql = """
      select Distinct               
      vmk.variable_label variable
      , a.mean 
      ,round(-1*a.std::numeric, 4) std
      ,a.ranks
      from interview_summary a
      inner join variable_master_key vmk on a.variable = vmk.variable and a.service_name = vmk.service_name 
      where a.interview_id = '{}' 
      and a.service_name like 'vs-%%' 
      and vmk.active_variable = 1
      order by a.ranks desc
      """.format(interview_id)
      
    df = dao.get_data(sql)
    freq = df.groupby(["mean", "std"]).size().to_frame("freq").values
     
    df = df.drop_duplicates().groupby(["mean", "std"])["variable"].apply(lambda v: '<br>'.join(v)).reset_index()
    df['freq'] = freq*3
    df['freqstr']=df['freq'].astype(str)
    print(df['variable'])

    ID_drop = selected_id
    fig = px.scatter(df,x="std", y="mean", log_x=False, log_y=False, text="variable",
    size='freq',
    color= 'freqstr',
    color_discrete_sequence=px.colors.qualitative.Pastel2,   #Antique,
    hover_data={'freqstr':False, 'freq':False, 'std':True, 'mean':True},
    size_max=120 #60
    )

    fig.update_traces(textposition='middle center', cliponaxis = False)

    fig.update_layout(
        height=800,
        width=1400,
        title_text='<br><span style="font-size: 22px">  Psychometric Variability</span>',
        title={
            "yref": "container",
            "y" : 1,
            "yanchor" : "bottom"  
        },
        xaxis_title="<<   --  Less      Consistency    More  ++   >> ",
        yaxis_title="<<   --  Lower     Intensity       Higher  ++   >> ",
        hoverlabel=dict(
        bgcolor="rgb(124,124,124)",
        font_size=12,
        font_family="Arial"
        ),
        xaxis=dict(zeroline=False, showgrid=False),
        yaxis=dict(zeroline=False, showgrid=False),
        showlegend=False,
        paper_bgcolor="LightSteelBlue"
        )

    fig.update_yaxes(automargin=True, title_font={"size": 16})
    fig.update_xaxes(automargin=True, title_font={"size": 16})
    fig.update_traces(textfont_size=10)
    fig.add_vline(x=-0.15, line_width=1, line_dash="dash", line_color="green")
    fig.add_hline(y=0.5, line_width=1, line_dash="dash", line_color="green")
        
    return fig

if __name__ == '__main__':
    dashB_app.run_server(debug=True)
