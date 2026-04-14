"""
IT대구 시간표 서버 (Flask)
실행: python app.py
접속: http://localhost:5000
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # GitHub Pages 등 모든 origin 허용

# ──────────────────────────────────────────
# 설정
# ──────────────────────────────────────────
CAMPUS_LIST = ['대구', '강남', '신촌', '부산', '인천', '대전']
EXCEL_FILE  = os.path.join(os.path.dirname(__file__), 'timetable.xlsx')

# ──────────────────────────────────────────
# 엑셀 로드
# ──────────────────────────────────────────
def load_timetable() -> pd.DataFrame:
    """
    timetable.xlsx 를 읽어 DataFrame 반환.
    필수 컬럼: 캠퍼스, 과정명, 개강일, 종강일, 요일, 시작시간, 종료시간
    선택 컬럼: 진행상태 (진행중 / 예정 / 오늘개강 / 종료)
    """
    if not os.path.exists(EXCEL_FILE):
        print(f"[경고] {EXCEL_FILE} 파일이 없습니다. 예시 데이터를 반환합니다.")
        return _sample_df()
    try:
        df = pd.read_excel(EXCEL_FILE, dtype=str)
        # 날짜 컬럼 정규화 → YYYY-MM-DD
        for col in ['개강일', '종강일']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%Y-%m-%d')
        return df
    except Exception as e:
        print(f"[오류] 엑셀 로드 실패: {e}")
        return pd.DataFrame()


def _sample_df() -> pd.DataFrame:
    """timetable.xlsx 가 없을 때 테스트용 샘플 데이터"""
    year = datetime.now().year
    data = [
        {'캠퍼스':'대구','과정명':'자바 웹 개발자 과정','개강일':f'{year}-04-07',
         '종강일':f'{year}-08-29','요일':'월화수목금','시작시간':'09:00','종료시간':'18:00','진행상태':'진행중'},
        {'캠퍼스':'대구','과정명':'파이썬 데이터 분석','개강일':f'{year}-05-02',
         '종강일':f'{year}-09-30','요일':'월화수목금','시작시간':'09:00','종료시간':'18:00','진행상태':'예정'},
        {'캠퍼스':'대구','과정명':'UI/UX 디자인','개강일':f'{year}-04-14',
         '종강일':f'{year}-07-31','요일':'토일','시작시간':'10:00','종료시간':'17:00','진행상태':'진행중'},
        {'캠퍼스':'강남','과정명':'자바 웹 개발자 과정','개강일':f'{year}-04-08',
         '종강일':f'{year}-08-30','요일':'월화수목금','시작시간':'09:00','종료시간':'18:00','진행상태':'진행중'},
    ]
    return pd.DataFrame(data)


# ──────────────────────────────────────────
# 유틸
# ──────────────────────────────────────────
WEEKEND_DAYS = {'토', '일'}

def is_weekend_course(yoil: str) -> bool:
    return any(d in str(yoil) for d in WEEKEND_DAYS)

def course_overlaps_month(row, year: int, month: int) -> bool:
    """강의 기간이 해당 연/월과 겹치는지 확인"""
    try:
        from calendar import monthrange
        month_start = f'{year}-{month:02d}-01'
        last_day    = monthrange(year, month)[1]
        month_end   = f'{year}-{month:02d}-{last_day:02d}'
        start = str(row.get('개강일', '') or '')
        end   = str(row.get('종강일', '') or '')
        if not start or not end:
            return True
        return start <= month_end and end >= month_start
    except Exception:
        return True


# ──────────────────────────────────────────
# API 엔드포인트
# ──────────────────────────────────────────
@app.route('/api/campuses')
def get_campuses():
    """캠퍼스 목록 반환"""
    return jsonify(CAMPUS_LIST)


@app.route('/api/courses')
def get_courses():
    """
    쿼리 파라미터:
      month   - 조회 월 (정수, 예: 4)
      type    - weekday | weekend
      campus  - 캠퍼스명 (예: 대구)
      q       - 과정명 검색 키워드
    """
    month  = request.args.get('month',  type=int, default=0)
    ctype  = request.args.get('type',   default='weekday')   # weekday | weekend
    campus = request.args.get('campus', default='').strip()
    q      = request.args.get('q',      default='').strip()
    year   = datetime.now().year

    df = load_timetable()
    if df.empty:
        return jsonify({'courses': []})

    # 1) 캠퍼스 필터
    if campus and '캠퍼스' in df.columns:
        df = df[df['캠퍼스'] == campus]

    # 2) 월 필터 (강의 기간이 해당 월과 겹침)
    if month:
        df = df[df.apply(lambda r: course_overlaps_month(r, year, month), axis=1)]

    # 3) 평일/주말 필터
    if '요일' in df.columns:
        if ctype == 'weekday':
            df = df[~df['요일'].apply(is_weekend_course)]
        elif ctype == 'weekend':
            df = df[df['요일'].apply(is_weekend_course)]

    # 4) 키워드 필터
    if q and '과정명' in df.columns:
        df = df[df['과정명'].str.contains(q, case=False, na=False)]

    # 5) NaN → 빈 문자열 변환 후 직렬화
    df = df.fillna('')
    courses = df.to_dict(orient='records')

    return jsonify({'courses': courses})


# ──────────────────────────────────────────
# 실행
# ──────────────────────────────────────────
if __name__ == '__main__':
    print("=" * 50)
    print("  IT대구 시간표 서버 시작")
    print(f"  주소: http://localhost:5000")
    print(f"  엑셀: {EXCEL_FILE}")
    print("  종료: Ctrl+C")
    print("=" * 50)
    app.run(debug=True, port=5000)
