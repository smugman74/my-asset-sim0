import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="부부 노후 자산 시뮬레이터", layout="wide")

st.title("💰 부부 맞춤형 자산 시뮬레이터 (v2.1)")
st.markdown("---")

# --- 사이드바 설정 ---
st.sidebar.header("📊 기본 및 고정 투자 설정")
init_asset = st.sidebar.number_input("초기 자본 (억 원)", value=4.0) * 100000000
return_rate = st.sidebar.slider("연평균 수익률 (%)", 5.0, 15.0, 11.0) / 100
start_age = st.sidebar.number_input("내 현재 나이 (만)", value=51) 
withdraw_age = st.sidebar.number_input("인출 시작 나이 (만)", value=62)
withdraw_rate = st.sidebar.slider("월 인출률 (자산 대비 %)", 0.1, 1.0, 0.5) / 100

st.sidebar.header("⚙️ 기간 및 금액 조정 가능 항목")
isa_years = st.sidebar.number_input("ISA 납입 기간 (년)", value=3)
isa_amount = st.sidebar.number_input("ISA 연간 납입액 (만 원)", value=1000) * 10000

direct_years = st.sidebar.number_input("미국 직투 납입 기간 (년)", value=3)
direct_amount = st.sidebar.number_input("미국 직투 연간 납입액 (만 원)", value=1000) * 10000

# --- 시뮬레이션 로직 ---
data = []
current_total = init_asset

for year in range(0, 50):
    age = start_age + year
    yearly_saving = 0
    
    if year < 10: yearly_saving += 18000000 # 본인 연금/IRP
    if year < isa_years: yearly_saving += isa_amount # ISA
    if year < direct_years: yearly_saving += direct_amount # 미국직투
    if year < 10: yearly_saving += 9000000 # 아내 연금/IRP

    current_total = (current_total + yearly_saving) * (1 + return_rate)
    
    monthly_withdraw = 0
    if age >= withdraw_age:
        monthly_withdraw = current_total * withdraw_rate
        current_total -= (monthly_withdraw * 12)

    data.append({
        "나이": age,
        "자산총액": round(current_total / 100000000, 2),
        "월인출액": round(monthly_withdraw / 10000, 0)
    })

df = pd.DataFrame(data)

# --- 화면 출력 ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 자산 성장 추이 (단위: 억)")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["나이"], y=df["자산총액"], name="자산 총액", 
                             line=dict(color='#1f77b4', width=3)))
    fig.update_layout(xaxis_title="내 나이", yaxis_title="억 원")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("💵 노후 월 예상 인출액 (단위: 만)")
    # 이 부분에서 "나 age" 오타를 "나이"로 수정했습니다.
    withdraw_df = df[df["나이"] >= withdraw_age] 
    if not withdraw_df.empty:
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=withdraw_df["나이"], y=withdraw_df["월인출액"], 
                              name="월 수령액", marker_color='#2ca02c'))
        fig2.update_layout(xaxis_title="내 나이", yaxis_title="만 원")
        st.plotly_chart(fig2, use_container_width=True)

st.subheader("📋 상세 데이터")
st.dataframe(df, use_container_width=True)