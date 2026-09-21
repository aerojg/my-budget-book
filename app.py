import csv
from datetime import date
from pathlib import Path

import streamlit as st

st.title("나의 가계부")

# 선택지 목록 (인수인계서 3-1에서 확정한 값)
CATEGORIES = ["식비", "교통비", "주거/관리비", "의료/건강", "통신비", "문화/여가", "경조사/선물", "기타"]
PAYMENTS = ["신용카드", "체크카드", "현금", "계좌이체"]

# 저장 파일: app.py와 같은 폴더 안의 data/expenses.csv
# data/ 폴더는 .gitignore에 들어 있어 GitHub에 올라가지 않는다
DATA_FILE = Path(__file__).parent / "data" / "expenses.csv"
COLUMNS = ["날짜", "금액", "카테고리", "항목명", "결제수단", "메모", "입력방식"]


def save_expense(d):
    """지출 한 건을 CSV 파일 맨 아래 한 줄로 적는다."""
    DATA_FILE.parent.mkdir(exist_ok=True)
    is_new = not DATA_FILE.exists() or DATA_FILE.stat().st_size == 0
    # utf-8-sig: 엑셀에서 열어도 한글이 깨지지 않게 하는 저장 방식
    with open(DATA_FILE, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        if is_new:
            writer.writerow(COLUMNS)  # 새 파일이면 맨 윗줄에 칸 제목을 먼저 적는다
        writer.writerow([
            d["date"].strftime("%Y-%m-%d"),
            d["amount"],
            d["category"],
            d["item_name"],
            d["payment"],
            d["memo"],
            "직접입력",  # 입력방식은 화면에 보이지 않고 저장할 때 자동으로 적는다
        ])


# 메모지: 지금 어느 화면인지(step), 입력한 내용(draft)을 적어 둔다
if "step" not in st.session_state:
    st.session_state.step = "input"
if "draft" not in st.session_state:
    st.session_state.draft = {}

draft = st.session_state.draft

if st.session_state.step == "input":
    # ---------- 1. 입력 화면 ----------
    st.subheader("오늘의 지출 입력")

    date_value = st.date_input("날짜", value=draft.get("date", date.today()), format="YYYY-MM-DD")
    amount = st.number_input("금액 (원)", min_value=0, step=1000, value=draft.get("amount", 0), format="%d")
    category = st.radio("카테고리", CATEGORIES, index=CATEGORIES.index(draft.get("category", CATEGORIES[0])), horizontal=True)
    item_name = st.text_input("항목명", value=draft.get("item_name", ""), placeholder="예: 마트 장보기")
    payment = st.radio("결제수단", PAYMENTS, index=PAYMENTS.index(draft.get("payment", PAYMENTS[0])), horizontal=True)
    memo = st.text_input("메모 (선택)", value=draft.get("memo", ""), placeholder="필요할 때만 적어 주세요")

    if st.button("저장하기"):
        if amount <= 0:
            st.warning("금액을 입력해 주세요.")
        elif not item_name.strip():
            st.warning("항목명을 입력해 주세요.")
        else:
            st.session_state.draft = {
                "date": date_value,
                "amount": amount,
                "category": category,
                "item_name": item_name.strip(),
                "payment": payment,
                "memo": memo.strip(),
            }
            st.session_state.step = "confirm"
            st.rerun()

elif st.session_state.step == "confirm":
    # ---------- 2. 확인 화면 ----------
    st.subheader("입력한 내용 확인")

    rows = [
        ("날짜", draft["date"].strftime("%Y-%m-%d")),
        ("금액", f"{draft['amount']:,}원"),
        ("카테고리", draft["category"]),
        ("항목명", draft["item_name"]),
        ("결제수단", draft["payment"]),
        ("메모", draft["memo"] if draft["memo"] else "(없음)"),
    ]
    for label, value in rows:
        col1, col2 = st.columns([1, 2])
        col1.write(label)
        col2.write(value)

    if st.button("저장하기", type="primary"):
        try:
            save_expense(draft)
        except OSError:
            st.error("저장하지 못했습니다. expenses.csv 파일을 엑셀 등에서 열어 두었다면 닫은 뒤 다시 눌러 주세요.")
        else:
            st.session_state.step = "done"
            st.rerun()

    if st.button("다시 입력"):
        st.session_state.step = "input"
        st.rerun()

else:
    # ---------- 3. 완료 화면 ----------
    st.success("✓ 저장되었습니다")

    if st.button("하나 더 입력"):
        st.session_state.draft = {}
        st.session_state.step = "input"
        st.rerun()

    if st.button("목록 보기"):
        st.info("목록 화면은 다음 단계에서 만듭니다.")