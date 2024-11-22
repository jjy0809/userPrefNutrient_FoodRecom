import sqlite3  # SQLite 데이터베이스 관련 모듈
import pandas as pd  # 데이터 분석 및 엑셀 파일 처리 라이브러리
from collections import Counter  # 리스트의 각 요소별 빈도 계산 모듈

# 음식DB 파일 경로
db_path = r"C:\Users\happy\Desktop\학교\고등학교\2학년\사용자 취향 및 영양 성분 기반 음식 추천\data\음식 영양성분 DB.db"
table = "nutrition_data" # DB 테이블명

# SQLite DB 연결 및 커서 생성
db = sqlite3.connect(db_path)
db.row_factory = sqlite3.Row 
cur = db.cursor() 

# 식단표 및 영양 성분 섭취 기준표 경로
diet_path = r"C:\Users\happy\Desktop\학교\고등학교\2학년\사용자 취향 및 영양 성분 기반 음식 추천\data\식단표.xlsx"
nut_path = r"C:\Users\happy\Desktop\학교\고등학교\2학년\사용자 취향 및 영양 성분 기반 음식 추천\data\영양소 섭취 기준.xlsx"

# 주요 영양 성분 리스트
nutrients = ["에너지", "단백질", "탄수화물", "칼슘", "나트륨", "비타민 A"]


# 식단표 읽고 저장 (p: 식단표 파일 경로)
def read_diet(p):
    diets = pd.read_excel(p)  # 식단표 엑셀 파일 읽고 저장
    res = []  # 식단 저장 리스트
    dates = diets.iloc[:, 0].astype(str).tolist()  # 날짜 저장
    for i, r in diets.iterrows():  # 날짜별로 반복하며 식단을 r에 대입
        daily = []  # 하루 식단 저장 리스트
        for meal in r[1:]:  # 날짜 열 제외
            if pd.notna(meal):  # 값이 비어있는지 검사
                daily.extend(meal.split(", "))  # 식단을  쉼표를 기준으로 분리하여 리스트에 추가
        res.append(daily)  # 하루 식단 추가
    return res, dates  # 날짜별 식단 리스트, 날짜 리스트 반환

# 영양소 섭취 기준 데이터를 읽기(p: 영양 성분 섭취 기준 파일 경로)
def read_nut(p):
    nutrient = pd.read_excel(p)  # 엑셀 파일 읽기
    res = {}  # 결과 저장용 딕셔너리
    for i, r in nutrient.iterrows():  # 각 행을 반복
        nut_name = r.iloc[0]  # 영양소 이름
        val = r.iloc[1:].tolist()  # 기준값 리스트
        res[nut_name] = val  # 딕셔너리에 추가
    return res  # 영양 성분별 나이대별 권장 섭취량 반환. {'영양성분': [권장 섭취량(인덱스 번호로 나이 구분)]}

# DB 테이블의 컬럼명 리스트 가져오기
def get_column():
    cur.execute(f"PRAGMA table_info({table})")  # 테이블 정보 가져오기
    columns = cur.fetchall()  # 결과 가져오기
    c_lst = [column[1] for column in columns]  # 컬럼 이름 추출
    return c_lst  # 컬럼명 리스트 반환

# 특정 조건에 따라 DB에서 행 검색(c: 검색할 컬럼명 리스트, q: 검색어)
def get_row(c, q):
    res = []  # 결과 저장 리스트
    if not str(q).isdigit():  # 검색어가 숫자가 아닌 경우
        for n in c:  # 각 컬럼을 기준으로 검색
            cur.execute(f"SELECT * FROM {table} WHERE {n} = ?", [q])  # 특정 컬럼에서 검색
            res.extend(dict(r) for r in cur.fetchall())  # 결과를 딕셔너리로 저장
    else:  # 검색어가 숫자인 경우
        cur.execute(f"SELECT * FROM {table} WHERE rowid = ?", [q])  # 인덱스로 검색
        res.extend(dict(cur.fetchall()))  # 결과를 딕셔너리로 저장
    return res  # 검색 결과들 리스트 반환

# 음식 검색(q: 검색어)
def search_food(query):
    res = []  # 결과 저장 리스트
    q_lst = [query]  # 검색어 리스트 초기화
    q_lst.extend(query.split())  # 검색어를 공백 기준으로 분리 및 추가
    for q in q_lst:  # 검색어 반복
        search_res = get_row(list([columns[0]] + columns[2:4]), q)  # 검색어로 검색
        for r in search_res:  # 검색 결과 반복
            if not r in res:  # 중복되지 않았다면
                res.append(r)  # 결과 리스트에 추가
    return res  # 검색 결과 리스트 반환

# 음식 리스트 출력(l: 음식 리스트)
def food_lst(l):
    for i, n in enumerate(l):  # 리스트 반복
        if i > 25: break # 음식 리스트가 과도하게 길면 뒷부분 자르기(터미널 잘림 방지) 
        print(f"{i+1}: {n['식품명']}")  # 인덱스 및 음식명 출력

# 음식 선택
def select_food(lst):
    food_lst(lst)  # 음식 리스트 출력
    div_line(1)
    ans = int(input("번호 입력 -> "))  # 사용자 입력
    #ans = 1 
    try:
        return lst[ans - 1]  # 선택 음식 반환
    except: # 예외 처리
        print("존재하지 않는 번호")
        div_line(2) 
        select_food(lst)  # 재귀 호출

# 음식 추가(foor: 검색 할 음식, idx: 결과가 저장될 날짜)
def append_foods(food, idx):
    print("search food: ", food)  # 검색할 음식 출력
    res = search_food(food)  # 음식 검색
    foods[idx].append(select_food(res))  # 음식 선택 후 리스트에 추가
    div_line(1)
    print(f"'{foods[idx][-1]['식품명']}' 추가 완료")  # 추가된 음식 출력

# 리스트 내 요소의 빈도 카운트 및 반환
def count(lst):
    count_lst = Counter(lst)  # 빈도 계산
    sorted_lst = count_lst.most_common()  # 빈도순 내림차순 정렬
    return sorted_lst  # 결과 반환

# 사용자 취향 추출(lst: 날짜별 음식 리스트)
def prefer(lst):
    rep_foods = []  # 대표식품명(취향) 리스트
    for l in lst:  # 날짜별 식단 반복
        for f in l:  # 음식 반복
            rep_foods.append(f['대표식품명'])  # 각 음식의 대표식품명 추가
    return count(rep_foods)  # 대표식품명 빈도 반환

# 날짜별 영양 성분 섭취량 
def daily_nuts(lst):
    res = []  # 결과 저장 리스트
    for i, l in enumerate(lst):  # 날짜 반복
        res.append({_: 0 for _ in nutrients})  # 영양소 초기화
        for f in l:  # 음식 반복
            for n in nutrients:  # 영양 성분 반복
                if f[n] != None:  # 영양 성분 데이터 존재하면
                    res[i][n] += int(f[n])  # 해당 영양 성분 값 누적 합
    return res  # 결과 반환

# 영양소 섭취량과 권장량 차이 계산 (미사용)
"""def differ_nuts(lst, age, nut_rec):
    res = []  # 결과 저장 리스트
    for i, l in enumerate(lst):  # 날짜 반복
        res.append({_: 0 for _ in nutrients})  # 초기화
        for n in nutrients:  # 영양 성분 반복
            res[i][n] = l[n] - nut_rec[n][age-1]  # 섭취량 및 권장량 차이 계산
    return res  # 결과 반환"""

# 평균 영양 성분 섭취량 계산(dn: 날짜별 영양 성분 섭취량)
def average_nuts(dn):
    sums = {n: 0 for n in nutrients}  # 누적 합 초기화
    for i in range(len(dn)):  # 날짜 반복
        for n in nutrients:  # 영양 성분 반복
            sums[n] += dn[i][n]  # 누적 합 계산
    aves = {n: round(sums[n] / len(dn), 3) for n in nutrients}  # 평균 계산
    return aves  # 평균 섭취량 반환

# 영양 성분 분석 출력 및 부족 영양 성분 반환(i: 날짜 인덱스, dn: 날짜별 영양 성분 섭취량, rn: 나이별 영양 성분 권장량, age:사용자 나이)
def print_nut(i, dn, rn, age):
    lack_nuts = []  # 부족 영양성분 리스트
    for n in nutrients:  # 영양 성분 반복
        div_line(1)
        try:
            dif_rate = round(dn[i][n] / rn[n][age-1] * 100, 3)  # 권장량 대비 섭취량 비율 계산
        except: # 예외 처리
            dif_rate = 0  # "0으로 나누는 문제" 발생시 0으로 설정
        stat = "과다" if abs(dif_rate) > 110 else ("적정" if dif_rate >= 90 else "부족")  # 상태 판별
        print(f"{n}: {dn[i][n]} / {dif_rate}% /", stat)  # 결과 출력
        if stat == "부족":  # 부족한 경우
            lack_nuts.append(n)  # 부족 영양 성분 리스트에 추가
    return lack_nuts  # 부족 영양성분 반환

# 영양 성분 분석 및 출력, 부족 영양성분 반환
def nut_res(dn, date, age, rn):
    for i in range(len(dn)):  # 날짜 반복
        div_line(3)
        print(f"{date[i]} 식단 영양 정보(영양 성분: 섭취량 / 권장량 대비 비율 / 과다 or 부족 or 적정)")  # 날짜 출력
        print_nut(i, dn, rn, age)  # 영양 성분 분석 정보 출력
    div_line(3)
    ave_nuts = [average_nuts(dn)]  # 평균 영양성분 섭취량 계산
    print("평균 영양 성분 정보(영양 성분: 평균 섭취량 / 권장량 대비 비율 / 과다 or 부족 or 적정)") 
    lack_nuts = print_nut(0, ave_nuts, rn, age)  # 평균 분석 정보 출력 및 부족 영양성분 계산
    return lack_nuts  # 부족 영양 성분 반환

# 음식 추천 및 출력(pref: 사용자 취향 상위 리스트, ln: 부족 영양성분 리스트)
def food_rec_print(pref, ln):
    rec_food_lst = []  # 추천 음식 저장 리스트
    div_line(3)
    for n in ln:  # 부족 영양성분 반복
        div_line(2) 
        print(f"사용자 취향 기반 '{n}' 다량 함유 음식 추천")  # 영양 성분 출력
        div_line(1)
        for p in pref:  # 선호 음식 반복
            food = search_food(p)  # 음식 검색
            if len(food) == 0: continue  # 검색 결과가 없으면 패스
            food = [f for f in food if f.get(n) != None]  # 해당 영양성분 포함 음식 필터링
            sorted_food = sorted(food, key=lambda x: x[n], reverse=True)  # 해당 영양성분 함량 기준 내림차순 정렬
            for i in range(3):  # 상위 3개 음식 출력
                try: 
                    print(sorted_food[i]['식품명'])
                    rec_food_lst.append(sorted_food[i]['식품명'])  # 추천 리스트 추가
                except: break  # 예외 발생(추천 결과가 3개 미만)시 반복 종료
    best_rec_food = count(rec_food_lst)  # 추천 음식 빈도 계산
    best_rec_food = [i[0] for i in best_rec_food[:min(len(best_rec_food), 5)]]  # 상위 5개 음식 선택
    div_line(3)
    print("최종 추천 음식")
    div_line(1)
    for f in best_rec_food:  # 추천 음식 출력
        if f[-2:] == '만두': f = f[:-2]  # '만두' 예외 처리
        print(f)  # 최종 추천 음식 출력

# 구분선 출력
def div_line(n):
    if n == 1:
        print("")
    elif n == 2:
        print("_________________________________________")
    else:
        print("\n_________________________________________\n")


# 메인 함수
def main():
    for i, diet in enumerate(diets):  # 날짜별 식단 반복
        foods.append([])  # 빈 리스트 추가
        for f in diet:  # 각 음식 반복
            div_line(3)
            append_foods(f, i)  # 음식 추가
            
    pref = prefer(foods)  # 취향 추출
    best_pref = [i[0] for i in pref[:len(pref)//10 + 1]]  # 상위 10% 취향 저장
    div_line(3)
    print("사용자 선호 음식: ")
    for bp in best_pref: print(bp)
    
    div_line(3)
    age = int(input("나이 입력 -> "))  # 사용자 나이 입력
    if age > 75: age = 75  # 75세 이상은 75세로 통일
    
    day_nuts = daily_nuts(foods)  # 날짜별 영양 성분 섭취량 계산
    nut_rec = read_nut(nut_path)  # 영양 성분 권장량 데이터 읽기
    #differ_daily_nuts = differ_nuts(day_nuts, age, nut_rec)  # 섭취량 및 권장량 사이 차이 계산(미사용)
    
    lack_nuts = nut_res(day_nuts, dates, age, nut_rec)  # 부족 영양성분 계산 및 영양 성분 분석 결과 출력
    div_line(1)
    print("부족 영양 성분: ", end='')  # 부족 영양 성분 출력
    for n in lack_nuts: print(n, end=' ')
    food_rec_print(best_pref, lack_nuts)  # 음식 추천 및 출력


# 프로그램 실행시
if __name__ == "__main__":
    columns = get_column()  # DB 컬럼 가져오기
    foods = []  # 날짜별 음식 리스트 초기화
    diets, dates = read_diet(diet_path)  # 식단 데이터 읽기
    main()  # 메인 함수 실행
