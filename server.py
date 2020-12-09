from flask import Flask, request as f_request, jsonify, render_template
from flaskext.mysql import MySQL
from datetime import datetime
from flask_ask import Ask,session,statement,question,request
import time
import os
import json
import logging

app = Flask(__name__)
ask=Ask(app,"/")
logging.getLogger('flask_ask').setLevel(logging.DEBUG)


app.config['MYSQL_DATABASE_HOST'] = 'team04.ckzbwnwwxarf.ap-northeast-2.rds.amazonaws.com'
app.config['MYSQL_DATABASE_USER'] = 'admin'
app.config['MYSQL_DATABASE_PASSWORD'] = 'asdqwe123#team04'
app.config['MYSQL_DATABASE_DB'] = 'IoT_Project'

mysql = MySQL()
mysql.init_app(app)

@app.route('/test')
def test():
    return render_template('test.html')

@app.route('/final')
def final():
    return render_template('web_final.html')


# tag시 tag table에 insert
@app.route('/tag', methods=['POST','GET'])
def post_tag_table():
    body = f_request.get_json()
    cursor = mysql.get_db().cursor()
    name = body['name']
    type = body['tag_type']
    cursor.execute("select emp_id from IoT_Project.Employee_Info where emp_name=%s",name)
    result=cursor.fetchone()
    id=result[0]
    time = datetime.now()


    cursor = mysql.get_db().cursor()

    cursor.execute("insert into IoT_Project.Tag (emp_id, tag_time, tag_type) values (%s, %s, %s)", (id, time, type))

    mysql.get_db().commit()
    print(name+' is '+type)
    return jsonify({"message": "success"})


# tag table -> tag
@app.route('/insert')
def insert_work_table():
    cursor = mysql.get_db().cursor()
    cursor.execute("select emp_id,tag_time,tag_type from IoT_Project.Tag where tag_time>date_sub(now(),interval 1 day) and tag_time<now() group by emp_id,tag_type")
    row_headers = [x[0] for x in cursor.description]
    result=cursor.fetchall()
    json_data=[]
    for result in result:
        json_data.append(dict(zip(row_headers,result)))
    leave_data=[]
    come_data=[]
    final_data=[]
    for data in json_data:
        if data['tag_type'] == 'Leave':
            temp1={}
            temp1['emp_id']=data['emp_id']
            temp1['tag']=data['tag_type']
            temp1['tag_time']=data['tag_time']
            leave_data.append(temp1)
        elif data['tag_type']=='Come':
            temp2={}
            temp2['emp_id'] = data['emp_id']
            temp2['tag'] = data['tag_type']
            temp2['tag_time'] = data['tag_time']
            come_data.append(temp2)
    for data in leave_data:
        for data2 in come_data:
            if data['emp_id']==data2['emp_id']:
                temp3={}
                temp3['emp_id']=data['emp_id']
                temp3['work_time']=data['tag_time']-data2['tag_time']
                final_data.append(temp3)
    for data in final_data:
        data['work_time']=str(data['work_time'])
    return jsonify(final_data);
# 일별 근무시간 조회
@app.route('/work/<emp_id>/<sdate>/<edate>')
def get_work_time(emp_id,sdate, edate):

    cursor = mysql.get_db().cursor()
    cursor.execute('select id, emp_id, working_date, time_to_sec(working_time) as"working_time"  from work_time WHERE date(working_date) >= date(%s) and date(working_date) <= date(%s) and emp_id=%s order by working_date',
                   (sdate, edate, emp_id))


    row_headers = [x[0] for x in cursor.description]

    print(row_headers)
    result = cursor.fetchall()
    print(result)
    json_data=[]

    for result in result:
        json_data.append(dict(zip(row_headers, result)))


    for data in json_data:
        sum_date = []
        D = str(data['working_date'])
        sum_date.append(D)
        data['working_date'] = sum_date

    print(json_data)
    return jsonify(json_data)


# 주별 근무시간 조회
@app.route('/work/week/<emp_id>/<sdate>/<edate>')
def get_work_week(emp_id,sdate, edate):
    cursor = mysql.get_db().cursor()
    cursor.execute("SELECT emp_id,"
                   " concat(month(working_date),'월',week(working_date)-week(date_sub(working_date,interval dayofmonth(working_date) -1 day))+1,'주차') AS month_date"
                   ",week(working_date) AS 'week_date',sum(time_to_sec(working_time)) as working_time "
                   "FROM IoT_Project.work_time "
                   "where emp_id=%s and working_date >=%s and working_date <=%s GROUP BY emp_id, week_date",(emp_id,sdate, edate))

    row_headers = [x[0] for x in cursor.description]

    result = cursor.fetchall()
    json_data=[]
    for result in result:
        json_data.append(dict(zip(row_headers, result)))

    for data in json_data:
        data['working_time'] = str(data['working_time'])
        data['month_date']=str(data['month_date'])
    print(json_data)
    return jsonify(json_data)


# 알렉사 이용한 결석확인
@ask.intent('AbsentIntent')
def tell_absent():
    cursor = mysql.get_db().cursor()
    cursor.execute('select emp_name from IoT_Project.Employee_Info as a left join (select * from IoT_Project.Tag where tag_time between now() and date_add(now(), interval +1 day)) as b on a.emp_id = b.emp_id where b.tag_type is null;')

    row_headers = [x[0] for x in cursor.description]
    result = cursor.fetchall()
    json_data = []
    for result in result:
        json_data.append(dict(zip(row_headers, result)))

    print(json_data)

    absent_list=''

    for data in json_data:
        absent_list = absent_list + data['emp_name']
        absent_list = absent_list + " "

    if len(absent_list) >=3 and len(absent_list) <=6 :
        absent_list = absent_list + 'is absent'
    elif len(absent_list) >6 :
        absent_list = absent_list + 'are absent'
    else:
        absent_list = 'all attended'

    # return absent_list
    return statement(absent_list).simple_card('skyler', absent_list)




if __name__ == '__main__':
    app.run(debug=True)