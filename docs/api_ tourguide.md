tourguide url - https://infuser.odcloud.kr/oas/docs?namespace=15123631/v1

Name	Description
page
integer($int64)
(query)
page index

Default value : 1

1
perPage
integer($int64)
(query)
page size

Default value : 10

10
returnType
string
(query)
응답의 데이터 타입을 선택할 수 있습니다. (기본값: JSON)
XML형태의 응답결과를 얻기 위해서는 XML 값으로 설정

returnType


Code	Description
200	
성공적으로 수행 됨

Example Value
Model
{
  "page": 0,
  "perPage": 0,
  "totalCount": 0,
  "currentCount": 0,
  "matchCount": 0,
  "data": [
    {
      "제목": "string",
      "제작처": "string",
      "지역(시_도)": "string",
      "지역(시_군_구)": "string",
      "가이드북 링크": "string"
    }
  ]
}
401	
인증 정보가 정확 하지 않음

500	
API 서버에 문제가 발생하였음

Models
uddi:33264f0a-158f-4a5d-95cd-99c740c8a097_model{
제목	[...]
제작처	[...]
지역(시_도)	[...]
지역(시_군_구)	[...]
가이드북 링크	[...]
}
uddi:33264f0a-158f-4a5d-95cd-99c740c8a097_api{
page	[...]
perPage	[...]
totalCount	[...]
currentCount	[...]
matchCount	[...]
data	[...]
}