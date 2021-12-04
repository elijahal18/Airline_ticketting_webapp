from flask import Flask, render_template, request, session, url_for, redirect  # importing the render_template function
import pymysql
import datetime
 
app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
#Configure MySQL
conn = pymysql.connect(host='localhost', user='root', password='', db='finalairline',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)
    # database name is 'finalairline'

# home route
@app.route("/")
def hello():
    return render_template('startpage.html')
    
@app.route('/login')
def login():
    return render_template('login.html')
  
@app.route('/logAuth', methods=['GET', 'POST'])
def loginAuth():
    #grabs information from the forms
    email = request.form['email']
    password = request.form['password']
    usertype = request.form['usertype']
    try:
        cursor = conn.cursor()
        if usertype == 'staff':
            query = 'SELECT * FROM airline_staff WHERE username = %s and password = md5(%s)'
        elif usertype == 'customer':
            query = 'SELECT * FROM customer WHERE email = %s and password = md5(%s)'
        
        cursor.execute(query, (email, password))
        #stores the results in a variable
        # data = result of query
        data = cursor.fetchone()
        cursor.close()
        error = None
        #print(data)
        
        if(data):
            if usertype == 'staff':
                session['username'] = email
                return redirect(url_for('staffHome')) #redirect to staff home page
            elif usertype == 'customer':
                session['username'] = email
                return redirect(url_for('customerHome')) #redirect to customer home page
        else:
          error = 'Invalid login or username'
          return render_template('login.html', error = error)
    except conn.Error as e:
        print("Error reading data from airline_staff or customer table while login", e)
    finally:
        cursor.close()
    error = 'Invalid login attempt. Please try again'
    return render_template('login.html', error = error)
      
@app.route('/customerHome')
def customerHome():
    email = session['username']
    try:
        cursor = conn.cursor();
        query = 'SELECT purchase.t_id, Ticket.airline_operator, ticket.flight_num FROM purchase, Ticket, Flight WHERE purchase.t_id = Ticket.t_id AND Ticket.airline_operator = Flight.airline_operator AND Ticket.flight_num = Flight.flight_num AND Flight.dept_datetime > curdate() AND purchase.email = %s'
        cursor.execute(query, (email))
        data = cursor.fetchall()
        cursor.close()
    except conn.Error as e:
        print("Error reading data from purchase, Ticket, Flight table", e)
    finally:
        cursor.close()
    return render_template('customerhome.html', email=email, ticketinfo=data)
      
      



@app.route('/registerCustomer')
def registerCustomer():
    return render_template('registerCust.html')

@app.route('/AuthCustomer', methods=['GET', 'POST'])
def AuthCustomer():
    email = request.form['email']
    name = request.form['name']
    password = request.form['password']
    building_number = request.form['building_number']
    street = request.form['street']
    city = request.form['city']
    state = request.form['state']
    phone_number = request.form['phone_number']
    passport_number = request.form['passport_number']
    passport_expiration = request.form['passport_expiration']
    passport_country = request.form['passport_country']
    DOB = request.form['date_of_birth']
    error = None
    try:
        #cursor used to send queries
        cursor = conn.cursor()
        query = 'SELECT * FROM customer WHERE email = %s'
        cursor.execute(query, (email))
        #stores the results in a variable
        # data = result of query
        data = cursor.fetchone()
        # use fetchall() if you are expecting more than 1 data row
        error = None
    except conn.Error as e:
        print("Error reading data from customer", e)
        error = "Error reading data from customer. Please try again"
        cursor.close()
        return render_template('registerCust.html', error = error)
    if(data): #if data exists
        error = "This user already exists"
        cursor.close()
        return render_template('registerCust.html', error = error)
    else:
        try:
            ins = 'INSERT INTO customer VALUES(%s, %s, md5(%s), %s, %s, %s, %s, %s, %s, %s, %s, %s)'
            #insert query
            cursor.execute(ins, (email, name, password, building_number, street, city, state, phone_number, passport_number, passport_expiration, passport_country,DOB))
            conn.commit()
            cursor.close()
            return render_template('startpage.html')
        except conn.Error as e:
            print("Error writing data into customer", e)
            cursor.close()
            error = "Error writing data into customer. Please try again"
    return render_template('registerCust.html', error = error)
        

@app.route('/registerStaff')
def registerStaff():
    return render_template('registerStaff.html')
    
@app.route('/AuthStaff', methods=['GET', 'POST'])
def AuthStaff():
    username = request.form['username']
    password = request.form['password']
    f_name = request.form['first_name']
    l_name = request.form['last_name']
    DOB = request.form['date_of_birth']
    airline_name = request.form['airline_name']
    error = None
    try:
        cursor = conn.cursor()
        query = 'SELECT * FROM airline_staff WHERE username = %s'
        cursor.execute(query, (username))
        data = cursor.fetchone()
    except conn.Error as e:
        print("Error reading data from airline_staff", e)
        error = "Error reading data from airline_staff. Please try again"
        cursor.close()
        return render_template('registerStaff.html', error = error)
    if data:
        error = "This user already exists"
        return render_template('registerStaff.html')
    else:
        try:
            ins = 'INSERT INTO Airline_staff VALUES(%s, %s, md5(%s), %s, %s, %s)'
            cursor.execute(ins, (username, airline_name, password, f_name, l_name, DOB))
            conn.commit()
            cursor.close()
            return render_template('startpage.html')
        except conn.Error as e:
            print("Error writing data into airline_staff", e)
            cursor.close()
            error = "Error writing data into airline_staff. Please try again"
    return render_template('registerStaff.html', error = error)

@app.route('/staffHome')
def staffHome():
    username = session['username']
    return render_template('staffhome.html', username=username)


@app.route('/addAirport')
def addAirportPage():
    return render_template('addAirport.html')

@app.route('/addAirportAuth', methods=['POST'])
def addAirport():
    id = request.form['airport_id']
    name = request.form['airport_name']
    city = request.form['city']
    try:
        cursor = conn.cursor()
        query = 'insert into airport values (%s, %s, %s)'
        cursor.execute(query, (id, name, city))
        conn.commit()
        cursor.close()
    except conn.Error as e:
        print("Error writing data into airport table", e)
    finally:
        cursor.close()
    return redirect(url_for('staffHome'))

@app.route('/addAirplane')
def addAirplane():
    return render_template('addAirplane.html')

@app.route('/addAirplaneAuth', methods=['POST'])
def addAirplaneAuth():
    id = request.form['id']
    owner_name = request.form['owner']
    seats = request.form['seats']
    try:
        cursor = conn.cursor()
        query = 'insert into airplane values (%s, %s, %s)'
        cursor.execute(query, (id, owner_name, seats))
        conn.commit()
        cursor.close()
    except conn.Error as e:
        print("Error inserting data into airplane table", e)
    finally:
        cursor.close()
    return redirect(url_for('staffHome'))

def getStaffAirline():
    username = session['username']
    try:
        cursor = conn.cursor()
        query = 'select airline_name from Airline_staff where username = %s'
        cursor.execute(query, (username))
        airline = cursor.fetchone()['airline_name']
        cursor.close()
        return airline
    except conn.Error as e:
        print("Error reading data into airline_staff table", e)
    finally:
        cursor.close()
    return None
    
@app.route('/createFlight')
def createFlight():
    error = None
    username = session['username']#watch for key errors! ex. if you just type the url/createFlight without logging in
    airline = getStaffAirline()
    if airline is None:
        error = 'Staff has no airline? Please log in again'
        session.pop('username')
        return render_template('error.html', error=error)
    
    cursor = conn.cursor()
    query = 'select name from airport'
    cursor.execute(query)
    airports = cursor.fetchall()
    
    query = 'select airplane_id from airplane where airline_name = %s' #Specified that the airline that the staff works for is the only airline we want?
    cursor.execute(query, (airline))
    availableairplane = cursor.fetchall()

    query = 'select flight_num, dept_datetime, status from flight where airline_operator = %s'
    cursor.execute(query, (airline))
    futureFlights = cursor.fetchall()
    
    cursor.close()
    return render_template('createFlight.html', airports=airports, availableairplane=availableairplane, futureFlights=futureFlights)

@app.route('/createFlightAuth', methods=['POST'])
def createFlightAuth():
    flightnum = request.form['flightnum']
    arrivetime = request.form['arrivetime']
    departtime = request.form['departtime']
    airline_operator = request.form['airline_operator']
    owner_name = request.form['owner_airline']
    departnum = request.form['departnum']
    arrivenum = request.form['arrivenum']
    airplane_num = request.form['airplanenum']
    base_price = request.form['base_price']
    status = request.form['status']
    try:
        cursor = conn.cursor()
        query = 'insert into flight values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(query, (flightnum, departtime, airline_operator, owner_name, arrivetime, departnum, arrivenum, airplane_num, base_price, status))
        conn.commit()
        '''
        query = 'select max(t_id) from Ticket'
        cursor.execute(query)
        data=cursor.fetchall()
        lasttid=data[0]['max(t_id)']
        query = 'select * from airplane where airplane_id=%s'
        cursor.execute(query, airplane_num)
        data = cursor.fetchall()
        numseats=data[0]['num_seats']
        for i in range(numseats):
            query = 'insert into Ticket values (%s, %s, %s, %s, %s)'
            cursor.execute(query, (lasttid+i,flightnum,departtime,airline_operator,null))
            conn.commit()
        '''
        
    except conn.Error as e:
        print("Error inserting data into flight table", e)
    finally:
        cursor.close()
    return redirect(url_for('staffHome'))
    
@app.route('/changeStatus', methods=['POST'])
def changeStatus():
    username = session['username']
    cursor = conn.cursor()
    airline = getStaffAirline()
    flightnum = request.form['flight_num']
    status = request.form['status']
    if not status:
        error = 'no new status selected'
        return redirect(url_for('createFlight', error=error))
    
    query = 'update flight set status=%s where flight_num=%s and airline_operator = %s'
    cursor.execute(query, (status, flightnum, airline))
    conn.commit()
    cursor.close()
    return redirect(url_for('createFlight'))

@app.route('/createFlight/viewRatings', methods=['POST'])
def viewRatings():
    username = session['username']
    cursor = conn.cursor()
    flightnum = request.form['fli']
    query = 'select * from review where flight_num=%s'
    cursor.execute(query, (flightnum))
    ratedata=cursor.fetchall()
    total=0
    count=0
    for i in ratedata:
        count+=1
        total+=i['rating']
    print(ratedata)
    avgrate=total/count
    print(total)
    return render_template('viewflightRatings.html', ratedata=ratedata, avgrate=avgrate)


    
    
@app.route('/viewCustomers')
def viewCustomers():
    airline = getStaffAirline()
        
    cursor = conn.cursor()
    query = 'select email, count(t_id) as tickets from purchase natural join Ticket where airline_operator= %s and purchasedate_time >= date_sub(curdate(), interval 1 year) group by email having tickets >= all (select count(t_id) from purchase natural join ticket  where airline_operator = %s and purchasedate_time >= date_sub(curdate(), interval 1 year) GROUP by email)'
    cursor.execute(query, (airline, airline))
    data = cursor.fetchall()
    cursor.close()
    n=len(data)
    for i in range(n):
        for j in range(0, n-i-1):
            if data[j]['tickets'] < data[j+1]['tickets']:
                data[j],data[j+1]= data[j+1],data[j]

    return render_template('viewCustomers.html', results=data[0:1])
    
@app.route('/viewReports')
def viewReports():

    airline = getStaffAirline()
    currentmonth = datetime.datetime.now().month
    monthtickets = []
        
    cursor = conn.cursor()
    for i in range(0, 12):
        query = 'select count(t_id) as num_tic from purchase natural join ticket where year(purchasedate_time) = year(curdate() - interval ' + str(i) + ' month) and month(purchasedate_time) = month(curdate() - interval ' + str(i) + ' month) and airline_operator=%s'
        cursor.execute(query, (airline))
        data = cursor.fetchall()
        salemonth = ((currentmonth - (i+1)) % 12) + 1
        print (data[0]['num_tic'])
        monthtickets.append([data[0]['num_tic'], salemonth])
        print(monthtickets)
    cursor.close()
    return render_template('viewReports.html', results=monthtickets)


@app.route('/viewReports/dates', methods=['POST'])
def viewReportsDates():
    airline = getStaffAirline()
    start = request.form['start']
    end = request.form['end']
    
    cursor = conn.cursor()
    query = 'select count(t_id) as num_tic from purchase natural join ticket where airline_operator=%s and purchasedate_time between %s and %s'
    cursor.execute(query, (airline, start, end))
    data = cursor.fetchall()
    cursor.close()
    print(data)
    
    return render_template('viewReportswDate.html', tot_sales=data[0]['num_tic'], start=start, end=end)

@app.route('/Revenue')
def Revenue():
    airline = getStaffAirline()
    cursor = conn.cursor()
    query = 'select sum(sold_price) as yearrev from purchase natural join ticket where airline_operator=%s and purchasedate_time between DATE_SUB(curdate(), interval 1 year) and curdate()'
    cursor.execute(query, (airline))
    yearrev = cursor.fetchall()
    query = 'select sum(sold_price) as monthrev from purchase natural join ticket where airline_operator=%s and purchasedate_time between DATE_SUB(curdate(), interval 1 month) and curdate()'
    cursor.execute(query, (airline))
    monthrev = cursor.fetchall()
    cursor.close()
    return render_template('viewRevenue.html', yearrev=yearrev, monthrev=monthrev)

@app.route('/topDestinations')
def topDestinations():
    airline = getStaffAirline()
    cursor = conn.cursor()
    query = 'select arrive_airport_id, count(t_id) from ticket NATURAL JOIN flight NATURAL JOIN purchase where airline_operator=%s and purchasedate_time between DATE_SUB(curdate(), interval 3 month) and curdate() group by arrive_airport_id'
    cursor.execute(query, (airline))
    monthdata=cursor.fetchall()
    #sort and get top 3
    query = 'select arrive_airport_id, count(t_id) from ticket NATURAL JOIN flight NATURAL JOIN purchase where airline_operator=%s and purchasedate_time between DATE_SUB(curdate(), interval 1 year) and curdate() group by arrive_airport_id'
    cursor.execute(query, (airline))
    yeardata=cursor.fetchall()
    query= 'select * from Airport'
    cursor.execute(query)
    Airport_data=cursor.fetchall()
    cursor.close()

    n=len(monthdata)
    for i in range(n):
        for j in range(0, n-i-1):
            if monthdata[j]['count(t_id)'] < monthdata[j+1]['count(t_id)']:
                monthdata[j],monthdata[j+1]= monthdata[j+1],monthdata[j]
    r=len(yeardata)
    for i in range(n):
        for j in range(0, r-i-1):
            if yeardata[j]['count(t_id)'] < yeardata[j+1]['count(t_id)']:
                yeardata[j],yeardata[j+1]= yeardata[j+1],yeardata[j]
    for i in monthdata:
        for j in Airport_data:
            if j['airport_id']==i['arrive_airport_id']:
                i['city']=j['city']
    for i in yeardata:
        for j in Airport_data:
            if j['airport_id']==i['arrive_airport_id']:
                i['city']=j['city']
    #return redirect(url_for('createFlight'))
    return render_template('topDestinations.html', monthdata=monthdata[0:3], yeardata=yeardata[0:3])
 
@app.route('/publicSearch')
def publicSearch():
    return render_template('search.html')

@app.route('/searchResult', methods=['GET', 'POST'])
def searchResult():
    srcName = request.form['srcName']
    srcCity = request.form['srcCity']
    dstName = request.form['dstName']
    dstCity = request.form['dstCity']
    departtime = request.form['departtime']
    arrivetime = request.form['arrivetime']
    
    try:
        #cursor used to send queries
        cursor = conn.cursor()
        query = 'select flight_num, airline_operator, dept_datetime, arrive_datetime, base_price, status from flight,airport as S, airport as D where date(dept_datetime) <= %s and date(arrive_datetime) <= %s and %s = S.name and %s = D.name and %s = S.city and %s = D.city and dept_airport_id = S.airport_id and arrive_airport_id = D.airport_id'
        cursor.execute(query, (departtime, arrivetime, srcName, dstName, srcCity, dstCity))
        #stores the results in a variable
        data = cursor.fetchall()
        cursor.close()
        error = None
        if not data:
            error = 'No results met your filters: Please try again'
        return render_template('search.html', error=error, results=data)
    except conn.Error as e:
        print("Error reading data from flight,airport as S, airport as D table", e)
        cursor.close()
        error = 'Invalid search filters: Please try again'
        return render_template('search.html', error=error)

@app.route('/customerhome/viewMyFlights', methods=['GET', 'POST'])
def viewMyFlights():
    username = session['username']
    error = None
    try:
        #cursor used to send queries
        cursor = conn.cursor()
        query = 'select ticket.t_id, flight_num, dept_datetime, airline_operator, sold_price from ticket, purchase where date(dept_datetime) >= now() and email = %s and ticket.t_id = purchase.t_id'
        cursor.execute(query, (username))
        #stores the results in a variable
        data = cursor.fetchall()
        cursor.close()
        if not data:
            error = 'You have not made any reservations. Please purchase tickets to see your history.'
        return render_template('viewFlights.html', error=error, results=data)
    except conn.Error as e:
        print("Error reading data from flight,airport as S, airport as D table", e)
        cursor.close()
        error = 'Invalid query: Please try again'
        return render_template('viewFlights.html', error=error)

@app.route('/customerhome/ratings')
def reviewTemplate():
    return render_template('review.html')

@app.route('/reviewAuth', methods=['POST'])
def reviewAuth():
    username = session['username']
    flight_num = request.form['flight_num']
    dept_datetime = request.form['dept_datetime']
    airline_operator = request.form['airline_operator']
    rating = request.form['rating']
    comment = request.form['comment']
    if int(rating) > 5:
        error = 'rating is > 5'
        return render_template('review.html', error=error)
    if int(rating) < 0:
        error = 'rating is < 0'
        return render_template('review.html', error=error)
    # Verify that the flight is one they have PREVIOUSLY flown
    try:
        cursor = conn.cursor()
        query = 'select * from ticket as S, purchase as T where S.t_id = T.t_id and email = %s and flight_num = %s and dept_datetime = %s and airline_operator = %s and dept_datetime < now()'
        cursor.execute(query, (username, flight_num, dept_datetime, airline_operator))
        conn.commit()
    except conn.Error as e:
        print("Error reading data from ticket,purchase table", e)
        cursor.close()
        error = 'Ticket/Purchase Review attempt was unsuccessful, invalid Flight'
        return render_template('review.html', error=error)
    finally:
        cursor.close()
    data = cursor.fetchall()
    print(data)
    if not data:
        error = 'You have not been on that flight previously'
        return render_template('review.html', error=error)
    try:
        cursor = conn.cursor()
        query = 'insert into review values (%s, %s, %s, %s, %s, %s)'
        cursor.execute(query, (username, flight_num, dept_datetime, airline_operator, rating, comment))
        conn.commit()
        cursor.close()
    except conn.Error as e:
        print("Error inserting data into review table", e)
        cursor.close()
        error = 'Review attempt was unsuccessful'
        return render_template('review.html', error=error)
    return redirect(url_for('customerHome'))

@app.route('/customerhome/purchaseTicket')
def purchaseTicket():
    return render_template('purchaseTicket.html')

@app.route('/purchaseTicketAuth', methods=['POST'])
def purchaseTicketAuth():
    username = session['username']
    t_id = request.form['t_id']
    card_type = request.form['card_type']
    number = request.form['number']
    expiration = request.form['expiration']
    Cardname = request.form['Cardname']
    try:
        cursor = conn.cursor()
        query = 'insert into purchase values (%s, %s, %s, %s, %s, now())'
        cursor.execute(query, (username, t_id, card_type, number, expiration, Cardname))
        query = 'select base_price, num_seats, S.flight_num, S.dept_datetime, S.airline_operator from ticket as S, flight as T, airplane as U where t_id = %s and S.flight_num = T.flight_num and S.dept_datetime = T.dept_datetime and S.airline_operator = T.airline_operator and T.airplane_id = U.airplane_id'
        cursor.execute(query, (t_id))
        data = cursor.fetchone()
        base = data[base_price]
        capacity = data[num_seats]
        flight_num = data[flight_num]
        dept_datetime = data[dept_datetime]
        airline_operator = data[airline_operator]
        query = 'select count(*) from ticket as S, flight as T where S.flight_num = T.flight_num and S.dept_datetime = T.dept_datetime and S.airline_operator = T.airline_operator and S.flight_num = %s and S.dept_datetime = %s and S.airline_operator = %s'
        cursor.execute(query, (flight_num, dept_datetime, airline_operator))
        data = cursor.fetchone()
        if data < (0.75 * capacity):
            query = 'update ticket set sold_price = %s where t_id = %s'
            cursor.execute(query, (base, t_id))
        else:
            query = 'update ticket set sold_price = %s * 1.25 where t_id = %s'
            cursor.execute(query, (base, t_id))
        cursor.execute(query, (t_id))
        conn.commit()
    except conn.Error as e:
        print("Error inserting data into ticket and/or purchase table", e)
        cursor.close()
    finally:
        cursor.close()
    return redirect(url_for('customerHome'))

@app.route('/logout')
def logout():
    session.pop('username')
    return redirect('/login')
  
app.run(debug = True)

