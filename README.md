# AttendanceWithDeepLearning
cnn 기반의 coral model과 Alexa 인공지능 스피커를 활용한 스마트 출결관리 시스템

1.주제 및 목표
2.요구사항
-개인당 주 52시간 근무시간 제한
-웹 상에서 월별, 주별 근무시간 그래프로 표현
-출근, 퇴근, 외근, 조퇴 등의 구분
(--음성(alexa voice service)를 이용한 기능 실행)
3.설계
4. 기능 및 구현
-------(db)근무시간 테이블 + tag 테이블

------(Server)개인당 주 52시간 근무시간 제한(server)
(m)tag 시간 insertㅇ
(m)00:00시에 근무시간 테이블 update -> tag테이블의 개개인의 퇴근tag.tagtime-출근tag.tagtime를 근무시간 table에 insert
(m)총 30시간이 되면 alert! #######
(m)월별 근무시간 조회
(m)주별 근무시간 조회
(m)일별 근무시간 조회
(m)카메라에서 결과 받기
5. 평가

-----(Web)웹 상에서 월별, 주별 근무시간 그래프로 표현( chart.js를 이용한 그래프 그리기)
 (method3)일별 근무시간 그리기
 (method4)주별 근무시간 그리기
 (method5)월별 근무시간 그리기
 (m)alert 띄우기

-------(hardware)출근, 퇴근 등의 구분
 nodemcu 스위치로 구분
