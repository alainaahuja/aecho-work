import dao
import json
import pandas as pd
import plotly.express as px

def psychometric_scatter(selected_id):
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
    
    #this is sample Json, json passed in this format will give desired result
    Data = pd.DataFrame(df).to_json()
    #print(df['variable'])

    ID_drop = selected_id
    fig = px.scatter(json.loads(Data),x="std", y="mean", log_x=False, log_y=False, text="variable",
    size='freq',
    color= 'freqstr',
    color_discrete_sequence=px.colors.qualitative.Pastel2,   #Antique,
    hover_data={'freqstr':False, 'freq':False, 'std':True, 'mean':True},
    size_max=60
    )

    fig.update_traces(textposition='middle center', cliponaxis = False)

    fig.update_layout(
        height=400,
        width=700,
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
