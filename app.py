import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
st.set_page_config(page_title="PropPulse | Sales Intelligence",page_icon="🏙️",layout="wide")
st.title("PropPulse")
st.caption("Real Estate Sales & Customer Intelligence | Synthetic CRM demonstration")
df=pd.read_csv(Path(__file__).parent/"data"/"leads.csv",parse_dates=["created_date"])
st.sidebar.header("Sales filters")
cities=["All"]+sorted(df.city.unique().tolist())
city=st.sidebar.selectbox("City",cities)
channels=st.sidebar.multiselect("Lead channel",sorted(df.channel.unique()),default=sorted(df.channel.unique()))
data=df.copy()
if city!="All": data=data[data.city==city]
data=data[data.channel.isin(channels)]
if data.empty:
    st.warning("No leads match these filters."); st.stop()
total=len(data); converted=(data.status=="Converted").sum()
conversion=converted/total*100
revenue=data.loc[data.status=="Converted","booking_value_inr"].sum()
avg_ticket=data.loc[data.status=="Converted","booking_value_inr"].mean()
a,b,c,d=st.columns(4)
a.metric("Qualified + unqualified leads",f"{total:,}")
b.metric("Conversion rate",f"{conversion:.1f}%")
c.metric("Booked value",f"₹{revenue/1e7:.2f} Cr")
d.metric("Average booking value",f"₹{avg_ticket/1e5:.1f} L" if pd.notna(avg_ticket) else "—")
left,right=st.columns(2)
with left:
    st.subheader("Lead funnel")
    funnel=data.status.value_counts().rename_axis("stage").reset_index(name="leads")
    st.plotly_chart(px.funnel(funnel,x="leads",y="stage",title="Current lead status mix"),use_container_width=True)
with right:
    st.subheader("Channel performance")
    channel=data.groupby("channel").agg(leads=("lead_id","count"),converted=("status",lambda x:(x=="Converted").sum())).reset_index()
    channel["conversion_pct"]=channel.converted/channel.leads*100
    st.plotly_chart(px.bar(channel,x="channel",y="conversion_pct",color="channel",title="Conversion by acquisition channel",labels={"conversion_pct":"Conversion (%)"}),use_container_width=True)
st.subheader("Demand and booking value")
monthly=data.assign(month=data.created_date.dt.to_period("M").astype(str)).groupby("month",as_index=False).agg(leads=("lead_id","count"),booked_value=("booking_value_inr","sum"))
x,y=st.columns(2)
x.plotly_chart(px.line(monthly,x="month",y="leads",markers=True,title="Lead volume trend"),use_container_width=True)
y.plotly_chart(px.bar(monthly,x="month",y="booked_value",title="Booked value trend (₹)"),use_container_width=True)
st.subheader("Lead register")
st.dataframe(data,use_container_width=True,hide_index=True)
st.download_button("Download filtered CRM data",data.to_csv(index=False).encode(),"sales_leads.csv","text/csv")
st.info("All customer and sales records are simulated. Do not use this prototype with real personal data without appropriate consent, access controls, retention policies and security review.")
