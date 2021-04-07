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


mm = t1.T1_API(username,password,client_id,client_secret)
dimensions='campaign_name,strategy_name,exchange_name,day_part_name,weekday_name'
metrics='impressions,clicks,post_click_conversions,post_view_conversions,total_conversions,total_spend'

df = mm.t1_report(endpoint='day_part', dimensions=dimensions,
                         filter='campaign_id='+campaign_id,
                         metrics=metrics,
                         precision='4',time_rollup='all',order='date',start_date=start_date,end_date=end_date)


daypart=mm.pivot(df, dimensions=['day_part_name','weekday_name'],\
                               metrics=['impressions', 'clicks', 'total_spend','total_conversions'],  kpi = ['CPA','CPC'], sortby = 'total_spend', ascending = False)

# data vizualization
sns.set_style('whitegrid')
sns.set_context('notebook')

f, ax=plt.subplots(figsize = (15,10))

heatmap_conv = pd.pivot_table(daypart, values='total_conversions', 
                     index=['day_part_name'], 
                     columns='weekday_name')

heatmap_conv.index = pd.CategoricalIndex(heatmap_conv.index,categories=['Morning Commute (6am-9am)','Mid-Morning (9-11:30)','Lunch (11:30-1:30)','Mid-Afternoon (1:30-4:30)','Evening Commute (4:30-7pm)','Night (7pm-11pm)','Late Night (11pm-2am)','Overnight (2am-6am)'])
# heatmap_conv.sort_index(0,inplace=True)
heatmap_conv.columns = pd.CategoricalIndex(heatmap_conv.columns,categories=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'])
# heatmap_conv.sort_index(1,inplace=True)


sns.heatmap(heatmap_conv, cmap="YlGnBu", annot=True)