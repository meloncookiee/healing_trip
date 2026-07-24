tourguide2 url - https://openapi.gg.go.kr/TouristResort
*경기도 관광정보

기본인자
기본인자 목록
변수명	타입	변수 설명	설명
KEY	STRING	인증키	기본값 : sample key
Type	STRING	호출 문서(xml, json)	기본값 : xml
pIndex	INTEGER	페이지 위치	기본값 : 1(sample key는 1 고정)
pSize	INTEGER	페이지 당 요청 숫자	기본값 : 100(sample key는 5 고정)


요청인자
요청인자 목록
변수명	타입	설명
SUM_YY	STRING(선택)	합계연도
SIGUN_NM	STRING(선택)	시군명
SIGUN_CD	STRING(선택)	시군코드

출력값 목록
No	출력명	출력설명
1	LIST_TOTAL_COUNT	행총건수
2	CODE	응답결과코드
3	MESSAGE	응답결과메세지
4	API_VERSION	API버전
5	SUM_YY	합계연도
6	SIGUN_NM	시군명
7	TOURESRT_DIV_NM	관광지구분명
8	TOURESRT_NM	관광지명
9	APPONT_DE	지정일자
10	MAKE_PLAN_FIRST_APRV_DE	조성계획최초승인일자
11	APPONT_AR	지정면적
12	MAKE_PLAN_AR	조성계획면적
13	OPERT_MAINBD_NM	운영주체명
14	REFINE_ZIP_CD	정제우편번호
15	REFINE_LOTNO_ADDR	정제지번주소
16	REFINE_ROADNM_ADDR	정제도로명주소
17	REFINE_WGS84_LAT	정제WGS84위도
18	REFINE_WGS84_LOGT	정제WGS84경도
19	SIGUN_CD	시군코드

에러코드
구분	코드	설명
ERROR	300	필수 값이 누락되어 있습니다. 요청인자를 참고 하십시오.
ERROR	290	인증키가 유효하지 않습니다. 인증키가 없는 경우, 홈페이지에서 인증키를 신청하십시오.
ERROR	310	해당하는 서비스를 찾을 수 없습니다. 요청인자 중 SERVICE를 확인하십시오.
ERROR	333	요청위치 값의 타입이 유효하지 않습니다.요청위치 값은 정수를 입력하세요.
ERROR	336	데이터요청은 한번에 최대 1,000건을 넘을 수 없습니다.
ERROR	337	일별 트래픽 제한을 넘은 호출입니다. 오늘은 더이상 호출할 수 없습니다.
ERROR	500	서버 오류입니다. 지속적으로 발생시 홈페이지로 문의(Q&A) 바랍니다.
ERROR	600	데이터베이스 연결 오류입니다. 지속적으로 발생시 홈페이지로 문의(Q&A) 바랍니다.
ERROR	601	SQL 문장 오류 입니다. 지속적으로 발생시 홈페이지로 문의(Q&A) 바랍니다.
INFO	000	정상 처리되었습니다.
INFO	300	관리자에 의해 인증키 사용이 제한되었습니다.
INFO	200	해당하는 데이터가 없습니다.
