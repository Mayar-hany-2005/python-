import streamlit as st
import numpy as np
import pandas as pd
import plotly.figure_factory as ff
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots

# 1. إعدادات الصفحة (لازم تكون أول سطر)
st.set_page_config(page_title="Insurance Dashboard", layout="wide")

st.title("Charge & Customer Analysis Dashboard 📊")

# 2. تحميل البيانات (استخدام cache عشان الـ Dashboard تكون سريعة)
@st.cache_data
def load_data():
    df = pd.read_csv("insurance.csv")
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
    return df

df = load_data()
bmi_data = df["bmi"].values.tolist()

# ألوان مخصصة للرسومات
accent = "#fd7922"
light_accent = "#ffd699"
pie_colors = ["#fd7922", "#f7e9cc", "#fbf6ee", "#d65a31"]

# 3. بناء الرسومات البيانية
# --- توزيع الشحنات ---
trace0 = go.Histogram(x=df["charges"], name="Charges", marker=dict(color=accent))
trace1 = go.Histogram(x=np.log(df["charges"]), name="Log Charges", marker=dict(color=light_accent))
dist_fig = make_subplots(rows=1, cols=2, subplot_titles=["Charge Distribution", "Log Charge Distribution"])
dist_fig.add_trace(trace0, 1, 1)
dist_fig.add_trace(trace1, 1, 2)
dist_fig.update_layout(title="Charge Distribution Analysis", bargap=0.05, showlegend=True)

# --- توزيع العملاء حسب العمر ---
pie_fig = px.pie(df, names='Age Group', title='Customer Distribution by Age Group',
                 color_discrete_sequence=pie_colors, hole=0.3)
pie_fig.update_traces(textinfo='percent+value', marker_line_color='rgba(0,0,0,0.3)', marker_line_width=1.5)

# --- خريطة الارتباط ---
numeric_df = df.select_dtypes(include=['number'])
corr = numeric_df.corr()
heatmap_fig = px.imshow(corr, text_auto=True, color_continuous_scale='Oranges', title="Correlation Heatmap")

# --- توزيع مؤشر كتلة الجسم ---
bmi_fig = ff.create_distplot([bmi_data], ['Body Mass Index Distribution'], colors=[accent], show_rug=False)
bmi_fig.update_layout(title='Normal Distribution (BMI)')

# --- الشحنات مقابل الفئة العمرية ---
fig1 = px.strip(df, x="age_cat", y="charges", title="Charges vs Age Category", color_discrete_sequence=[accent])

# --- المدخن مقابل الشحنات ---
fig3 = px.strip(df, x="smoker", y="charges", color="weight_condition",
                title="Smoker Status vs Charges", color_discrete_sequence=pie_colors)

# --- Pair Plot لحالة الشحنات ---
df["charge_status"] = pd.qcut(df["charges"], q=3, labels=["Low", "Medium", "High"])
fig4 = px.scatter_matrix(df, dimensions=["age", "bmi", "charges"], color="charge_status",
                         title="Interactive Pair Plot by Charge Status")
fig4.update_traces(diagonal_visible=False, showupperhalf=False)

# 4. عرض الرسومات في الواجهة باستخدام الأعمدة (Columns)
st.plotly_chart(dist_fig, use_container_width=True)

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(pie_fig, use_container_width=True)
    st.plotly_chart(bmi_fig, use_container_width=True)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.plotly_chart(heatmap_fig, use_container_width=True)
    st.plotly_chart(fig4, use_container_width=True)
    st.plotly_chart(fig3, use_container_width=True)
