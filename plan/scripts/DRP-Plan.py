#!/usr/bin/env python
# coding: utf-8

# In[1]:


import plotly.figure_factory as ff
import pandas as pd
import random
import plotly.graph_objects as go


# In[2]:


catColors = dict(Project='rgb(255, 51, 0)', 
                 Hardware='rgb(230, 230, 0)', 
                 SkyModelling='rgb(51, 153, 255)', 
                 PSF='rgb(102, 0, 255)', 
                 WavelengthCalibration='rgb(153, 102, 255)', 
                 GeneralCalibration='rgb(204, 51, 255)',
                 Infrastructure='rgb(153, 0, 153)')


# In[3]:


def plt_line(df, fig, mls_yr, mls_text, color="gray"):
    
    fig.add_trace(
        go.Scatter(
            x = [mls_yr, mls_yr],
            y = [-1, len(df.index) + 1],
            mode = "lines+text",
            name = mls_text,
            textposition = "bottom center",
            line = go.scatter.Line(color = color, width = 1),
            showlegend = False
        )
    )


# In[4]:


def process_resources(row):
    name_effort = {name: row[name] for name in ['Price', 'Caplar', 'Belland', 'Developer-1', 'Yabe', 'Yamashita', 'Mineo', 'Developer-2', 'Siddiqui']}
    resource = [name for name, v in sorted(name_effort.items(), key=lambda item: item[1], reverse=True) if v > 0]
    out = ""
    for r in resource:
        out += f'{r}, '
    if out:
        return f'({out[:-2]})'
    return out      


# In[5]:


def addAnnotation(df, fig):
    c = 0
    for index, row in df.iterrows():
        resources = process_resources(row)
        fig['layout']['annotations'] += tuple([dict(x=row.get("Finish"), y=c, text=f"{row.get('Task')} {resources}", xanchor='right', ax='-10', ay='-10', showarrow=True, arrowhead=5, font=dict(color='black'))])
        c = c + 1


# In[6]:


def plot_plan(plan_file):
    # Load in CSV
    df0 = pd.read_csv(plan_file, skipinitialspace=True,  quotechar='"').applymap(lambda x: x.strip() if type(x)==str else x).iloc[::-1]

    # Filter out columns not needed for gantt plot
    df = df0[['Task', 'Start', 'Finish', 'Complete', 'Category']].copy()

    for cat in set(df['Category']):
        if cat not in catColors:
            print(f'category {cat} is not in color mapping') 

    arms_full = df[df['Task'] == 'SM3(B+R+N)@LAM']['Start'].values[0]
    engobs_start = df[df['Task'] == 'Engineering observations']['Start'].values[0]
    engobs_end = df[df['Task'] ==  'Engineering observations']['Finish'].values[0]
    ssp_end = df[df['Task'] == 'Call for SSP']['Start'].values[0]

    fig = ff.create_gantt(df, colors=catColors, index_col='Category',
                          show_colorbar=False, 
                          bar_width=0.1, 
                          showgrid_x=True, 
                          showgrid_y=False, 
                          title=plan_file,
                          height=1500,
                          width=2000)
    
    addAnnotation(df0, fig)
    
    fig.update_layout(plot_bgcolor='#FFFFFF')

    plt_line(df, fig, '2021-08-31', 'MSIP End', color='red')
    plt_line(df, fig, arms_full, 'R+B+N', color='gray')
    plt_line(df, fig, engobs_start, 'Eng Obs Start', color='green')
    plt_line(df, fig, ssp_end, 'Call for SSP', color='black')
    plt_line(df, fig, engobs_end , 'Eng Obs End', color='green')

    fig.show(renderer='browser')


# In[ ]:


plot_plan('../data/drp-plan.csv')


# ### [Now take a screenshot of resulting image]

# In[ ]:




