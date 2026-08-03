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
text_color = "#333333"

# ==========================================
# 3. بناء جميع الرسومات البيانية (12 رسمة)
# ==========================================

# 1. توزيع الشحنات
trace0 = go.Histogram(x=df["charges"], name="Charges", marker=dict(color=accent))
trace1 = go.Histogram(x=np.log(df["charges"]), name="Log Charges", marker=dict(color=light_accent))
dist_fig = make_subplots(rows=1, cols=2, subplot_titles=["Charge Distribution", "Log Charge Distribution"])
dist_fig.add_trace(trace0, 1, 1)
dist_fig.add_trace(trace1, 1, 2)
dist_fig.update_layout(title="Charge Distribution Analysis", bargap=0.05, showlegend=True)

# 2. توزيع العملاء حسب العمر
pie_fig = px.pie(df, names='Age Group', title='Customer Distribution by Age Group',
                 color_discrete_sequence=pie_colors, hole=0.3)
pie_fig.update_traces(textinfo='percent+value', marker_line_color='rgba(0,0,0,0.3)', marker_line_width=1.5)

# 3. خريطة الارتباط
numeric_df = df.select_dtypes(include=['number'])
corr = numeric_df.corr()
heatmap_fig = px.imshow(corr, text_auto=True, color_continuous_scale='Oranges', title="Correlation Heatmap")

# 4. توزيع مؤشر كتلة الجسم
bmi_fig = ff.create_distplot([bmi_data], ['Body Mass Index Distribution'], colors=[accent], show_rug=False)
bmi_fig.update_layout(title='Normal Distribution (BMI)')

# 5. توزيع مؤشر كتلة الجسم حسب الفئة العمرية
age_groups = {'Young Adult': pie_colors[0], 'Adult': pie_colors[1], 'Senior': pie_colors[2]}
data1 = []
for group, color in age_groups.items():
    data1.append(go.Box(y=df[df['age_cat'] == group]['bmi'], name=group, boxmean=True, marker=dict(color=color)))
bmi_age_layout = go.Layout(title="Body Mass Index Distribution by Age Category", boxmode='group')
bmi_age_fig = go.Figure(data=data1, layout=bmi_age_layout)

# 6. مؤشر كتلة الجسم حسب التدخين والعمر
groups = [
    ('Young Adult', 'yes', 'Young A. Smoker'), ('Young Adult', 'no', 'Young A. Non-Smoker'),
    ('Adult', 'yes', 'Senior A. Smoker'), ('Adult', 'no', 'Senior A. Non-Smoker'),
    ('Senior', 'yes', 'Elder Smoker'), ('Senior', 'no', 'Elder Non-Smoker')
]
colors = pie_colors + [accent, light_accent]
traces = []
for (age_group, smoker, name), color in zip(groups, colors):
    bmi_values = df.loc[(df['age_cat'] == age_group) & (df['smoker'] == smoker), 'bmi'].values
    traces.append(go.Box(y=bmi_values, name=name, fillcolor=color))
bmi_smoker_layout = go.Layout(title='Body Mass Index of Smokers Status by Age Category', showlegend=False)
bmi_smoker_fig = go.Figure(data=traces, layout=bmi_smoker_layout)

# 7. الشحنات مقابل الفئة العمرية
fig1 = px.strip(df, x="age_cat", y="charges", title="Charges vs Age Category", color_discrete_sequence=[accent])

# 8. حالة الوزن + الفئة العمرية مقابل الشحنات
fig2 = px.strip(df, x="age_cat", y="charges", color="weight_condition",
                title="Weight Condition vs Age and Charges", color_discrete_sequence=pie_colors)

# 9. المدخن + حالة الوزن مقابل الشحنات
fig3 = px.strip(df, x="smoker", y="charges", color="weight_condition",
                title="Smoker Status vs Charges", color_discrete_sequence=pie_colors)

# 10. توزيع الشحنات حسب حالة الوزن والتدخين (Violin)
point_pos_smoker, point_pos_non_smoker = [-0.9, -1.1, -0.6, -0.3], [0.45, 0.55, 1, 0.4]
show_legend_flags = [True, False, False, False]
violin_data = []
weight_conditions = pd.unique(df['weight_condition'])
for i, condition in enumerate(weight_conditions):
    for smoker_status, fill_color, point_pos, group_name in [('yes', accent, point_pos_smoker[i], 'Smoker'), ('no', light_accent, point_pos_non_smoker[i], 'Non-Smoker')]:
        trace = go.Violin(
            x=df['weight_condition'][(df['smoker'] == smoker_status) & (df['weight_condition'] == condition)],
            y=df['charges'][(df['smoker'] == smoker_status) & (df['weight_condition'] == condition)],
            name=group_name, side='negative' if smoker_status == 'yes' else 'positive',
            legendgroup=group_name, scalegroup=group_name, showlegend=show_legend_flags[i],
            points='all', pointpos=point_pos, fillcolor=fill_color, opacity=0.7
        )
        violin_data.append(trace)
violin_layout = go.Layout(title="Charges Distribution by Weight Condition (Grouped by Smoking)", violinmode="overlay")
violin_fig = go.Figure(data=violin_data, layout=violin_layout)

# 11. رسوم بيانية متعددة لحالة الشحنات (Pair Plot)
df["charge_status"] = pd.qcut(df["charges"], q=3, labels=["Low", "Medium", "High"])
custom_palette = {"Low": light_accent, "Medium": accent, "High": text_color}
fig4 = px.scatter_matrix(df, dimensions=["age", "bmi", "charges"], color="charge_status",
                         color_discrete_map=custom_palette, title="Advanced Charges Analysis")
fig4.update_traces(diagonal_visible=False, showupperhalf=False)

# 12. الرسم البياني الراداري (Radar Chart)
grouped = df.groupby(['region', 'weight_condition'])['charges'].mean().unstack()
weight_labels = ['Underweight', 'Normal Weight', 'Overweight', 'Obese']
regions = grouped.index.tolist()
grouped = grouped.reindex(columns=weight_labels).fillna(0)
radar_data = []
for i, region in enumerate(regions):
    values = grouped.loc[region].values.tolist()
    trace = go.Scatterpolar(
        r=values + values[:1], theta=weight_labels + weight_labels[:1], fill='toself',
        name=region, line=dict(color=pie_colors[i], width=2)
    )
    radar_data.append(trace)
radar_layout = go.Layout(title=dict(text="Average Medical Charges by Weight Condition (Regional)", x=0.5))
fig5 = go.Figure(data=radar_data, layout=radar_layout)


# ==========================================
# 4. عرض الرسومات في الواجهة بشكل منظم
# ==========================================

# رسومات واخدة عرض الشاشة بالكامل
st.plotly_chart(dist_fig, use_container_width=True)

# تقسيم باقي الرسومات على عمودين
col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(pie_fig, use_container_width=True)
    st.plotly_chart(bmi_fig, use_container_width=True)
    st.plotly_chart(bmi_smoker_fig, use_container_width=True)
    st.plotly_chart(fig2, use_container_width=True)

with col2:
    st.plotly_chart(heatmap_fig, use_container_width=True)
    st.plotly_chart(bmi_age_fig, use_container_width=True)
    st.plotly_chart(fig1, use_container_width=True)
    st.plotly_chart(fig3, use_container_width=True)

# رسومات متقدمة واخدة عرض الشاشة من تحت
st.divider()
st.plotly_chart(violin_fig, use_container_width=True)
st.plotly_chart(fig4, use_container_width=True)
st.plotly_chart(fig5, use_container_width=True)
