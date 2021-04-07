from scripticus import looker_api, bddr, t1_api as mmm, beautifulization as bfz, mailicus as ms, reporticus as t1
from scripticus.looker_api import looker_df
import imp
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
# import warnings
# warnings.filterwarnings('ignore')

# Global API credentials - dont change them!
client_id = 'XXXX'
client_secret = 'XXXX'

######## ----------Please carefully fill in --------- ###########
username = 'XXXX'
password = 'XXXX'

# ****Set up Criterias for reports****
organization_id='XXXX'
agency_id = 'XXXX'
pixel_id='XXXX'
start_date='2020-01-01'
end_date='2021-01-30'
campaign_id = 'AAA,BBB'


######## ----------Pathway function --------- ###########


def genSankey(df,cat_cols=[],value_cols='',title='Sankey Diagram'):
    # maximum of 6 value cols -> 6 colors
    colorPalette = ['#4B8BBE','#306998','#FFE873','#FFD43B','#646464']
    labelList = []
    colorNumList = []
    for catCol in cat_cols:
        labelListTemp =  list(set(df[catCol].values))
        colorNumList.append(len(labelListTemp))
        labelList = labelList + labelListTemp
        
    # remove duplicates from labelList
    labelList = list(dict.fromkeys(labelList))
    
    # define colors based on number of levels
    colorList = []
    for idx, colorNum in enumerate(colorNumList):
        colorList = colorList + [colorPalette[idx]]*colorNum
        
    # transform df into a source-target pair
    for i in range(len(cat_cols)-1):
        if i==0:
            sourceTargetDf = df[[cat_cols[i],cat_cols[i+1],value_cols]]
            sourceTargetDf.columns = ['source','target','count']
        else:
            tempDf = df[[cat_cols[i],cat_cols[i+1],value_cols]]
            tempDf.columns = ['source','target','count']
            sourceTargetDf = pd.concat([sourceTargetDf,tempDf])
        sourceTargetDf = sourceTargetDf.groupby(['source','target']).agg({'count':'sum'}).reset_index()
        
    # add index for source-target pair
    sourceTargetDf['sourceID'] = sourceTargetDf['source'].apply(lambda x: labelList.index(x))
    sourceTargetDf['targetID'] = sourceTargetDf['target'].apply(lambda x: labelList.index(x))
    
    # creating the sankey diagram
    data = dict(
        type='sankey',
        node = dict(
          pad = 15,
          thickness = 20,
          line = dict(
            color = "black",
            width = 0.5
          ),
          label = labelList,
          color = colorList
        ),
        link = dict(
          source = sourceTargetDf['sourceID'],
          target = sourceTargetDf['targetID'],
          value = sourceTargetDf['count']
        )
      )
    
    layout =  dict(
        title = title,
        font = dict(
          size = 10
        )
    )
       
    fig = dict(data=[data], layout=layout)
    return fig




######## ----------Pathway function --------- ###########

vertical = 'craetive_name' 
print ('Start_date: {} and end_date: {}'.format(start_date,end_date))

sql='sql_pathway.hql'

replacements  = {
    '_start_date_': start_date,
    '_end_date_': end_date,
    '_organization_id_': organization_id,
    '_campaign_id_': campaign_id,
    '_pixel_id_': pixel_id,
    '_vertical_': vertical 
}


filename = 'campaign_pv'

x = t1.qubole(api_token,sql,replacements, filename)

xy=x[(x['number_of_unique_touchpoints']>1) & (x['converters']>1)]


x_performance = x[['number_of_unique_touchpoints','percent_unique_converters', 'converters','total_spend_on_converters', 'total_unique_users_in_path',
       'total_impressions_served_on_path', 'total_spend_on_path']].groupby(['number_of_unique_touchpoints'],  as_index=False ).sum()

x_performance['% of total_spend_on_converters'] = x_performance['total_spend_on_converters'] / x_performance['total_spend_on_converters'].sum()
x_performance['% of total_spend_on_path'] = x_performance['total_spend_on_path'] / x_performance['total_spend_on_path'].sum()
x_performance['CR, % of unique users'] =  x_performance['converters'] /(x_performance['total_unique_users_in_path'])
x_performance['CPA'] = x_performance['total_spend_on_path'] / x_performance['converters']


x_performance.columns = ['number_of_touchpoints', '%_unique_converters',
       'converters', 'spend_on_converters', 'unique_users',
       'impressions', 'total_spend', '%_spend_on_converters',
       '%_total_spend', 'CR_unique_users', 'CPA']
x_performance['frequency'] =   x_performance['impressions'] / x_performance['unique_users']
x_performance['%_unique_users'] =  x_performance['unique_users'] /x_performance['unique_users'].sum()
path_performance = x_performance[['number_of_touchpoints','impressions', 'unique_users', 'frequency', 'total_spend', '%_total_spend','%_unique_users',
                                  'CPA', 'spend_on_converters']].head()

#Show the touchpoints statistics                             
                               
cm = sns.light_palette("blue", as_cmap=True)
format_dict = {'total_spend':'{0:,.2f}', 'spend_on_converters': '{:.2f}',  'frequency': '{:.2f}', 'viewability_rate_100_percent': '{:.2f}', 'total_revenue':'{0:,.1f}','NDC':'{0:,.2f}','%_total_spend':'{0:,.2%}', '%_unique_users':'{0:,.2%}','CPC':'{0:,.2f}','CPA_Signup':'{0:,.2f}','CR_unique_users': '{:.2%}', 'CPA_NDC':'{0:,.1f}','CPA_DC':'{0:,.1f}','ROI': '{:.2f}','CPM': '{0:,.1f}', 'vCPM': '{0:,.1f}','CPC': '{0:,.1f}','CPA': '{0:,.3f}'}
tp = path_performance.style.background_gradient(cmap=cm, subset=['CPA', '%_total_spend']).format(format_dict).hide_index()
tp


#Show the pathways

import pandas as pd
import plotly

import plotly.offline as py
from plotly.offline import iplot
py.offline.init_notebook_mode(connected=True)
import plotly.graph_objs as go


fig = genSankey(xy,cat_cols=['first_touchpoint','last_touchpoint'],value_cols='converters',title='First_last_campaign contact_before_conversion')
plotly.offline.plot(fig, filename='creative_pathway.html', validate=False)
py.iplot(fig, filename='creative_pathway')