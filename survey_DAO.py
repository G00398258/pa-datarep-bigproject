import mysql.connector
import db_config as cfg

class Survey_DAO:
    connection = ''
    cursor = ''
    host = ''
    user = ''
    password = ''
    database = ''
    #port = 0
    
    def __init__(self):
        self.host = cfg.mysql['host']
        self.user = cfg.mysql['user']
        self.password = cfg.mysql['password']
        self.database = cfg.mysql['database']
        #self.port = cfg.mysql['port']

    def getcursor(self): 
        self.connection = mysql.connector.connect(
            host = self.host,
            user = self.user,
            password = self.password,
            database = self.database,
        )
        self.cursor = self.connection.cursor()
        return self.cursor


    def closeAll(self):
        self.connection.close()
        self.cursor.close()
         

    def create(self, values):
        cursor = self.getcursor()
        sql = "INSERT INTO SurveyResults (EmployeeID, IT_Overall_Score, Laptop_Score, Accessories_Score,\
            Applications_Score, Support_Score, Positive_Feedback, Negative_Feedback, Follow_Up) \
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        cursor.execute(sql, values)

        self.connection.commit()
        newid = cursor.lastrowid
        self.closeAll()
        return newid


    def getAll(self):
        cursor = self.getcursor()
        sql = "SELECT * FROM SurveyResults"
        cursor.execute(sql)
        results = cursor.fetchall()
        returnArray = []
        print(results)
        for result in results:
            print(result)
            returnArray.append(self.convertToDictionary(result))
        
        self.closeAll()
        return returnArray


    def findByResponseID(self, id):
        cursor = self.getcursor()
        sql = "SELECT * FROM SurveyResults WHERE ResponseID = %s"
        values = (id,)

        cursor.execute(sql, values)
        result = cursor.fetchone()
        returnvalue = self.convertToDictionary(result)
        self.closeAll()
        return returnvalue


    def update(self, values):
        cursor = self.getcursor()
        sql = "UPDATE SurveyResults SET EmployeeID = %s, IT_Overall_Score = %s, Laptop_Score = %s, Accessories_Score = %s,\
             Applications_Score = %s, Support_Score = %s, Positive_Feedback = %s, Negative_Feedback = %s, \
                Follow_Up = %s WHERE ResponseID = %s"
        cursor.execute(sql, values)
        self.connection.commit()
        self.closeAll()
        

    def delete(self, id):
        cursor = self.getcursor()
        sql = "DELETE FROM SurveyResults WHERE ResponseID = %s"
        values = (id,)

        cursor.execute(sql, values)

        self.connection.commit()
        self.closeAll()
        
        print("Record for ResponseID", values, "has been deleted")


    def convertToDictionary(self, result):
        colnames = ['ResponseID', 'EmployeeID', 'IT_Overall_Score', 'Laptop_Score', 'Accessories_Score',
            'Applications_Score', 'Support_Score', 'Positive_Feedback', 'Negative_Feedback', 'Follow_Up']
        item = {}
        
        if result:
            for i, colName in enumerate(colnames):
                value = result[i]
                item[colName] = value
        
        return item

    def get_survey_stats(self):
        # method gets some stats from three different tables in the DB
        # each query result is turned into a dict and stored in a list that's passed back to the server
        cursor = self.getcursor()

        # count responses
        sql = "SELECT COUNT(*) AS Responses FROM SurveyResults"
        cursor.execute(sql)
        resultsArray = []
        result = cursor.fetchall()
        print(result)

        item = {}

        for r in result:
            value = r[0]
            item['NumResponses'] = value
        resultsArray.append(item)


        # calculate average scores
        sql = "SELECT AVG(IT_Overall_Score) AS IT_Overall, AVG(Laptop_Score) AS Laptops, \
            AVG(Accessories_Score) AS Accessories, AVG(Applications_Score) AS Applications, \
                AVG(Support_Score) AS Support FROM SurveyResults"
        cursor.execute(sql)
        results = cursor.fetchall()
        print(results)

        item = {}
    
        for result in results:
            item['IT_Overall'] = result[0]
            item['Laptops'] = result[1]
            item['Accessories'] = result[2]
            item['Applications'] = result[3]
            item['Support'] = result[4]
            resultsArray.append(item)
        
        sql = "SELECT e.Department, COUNT(e.Department) AS Dept_Responses \
            FROM SurveyResults s LEFT JOIN Employees e ON s.EmployeeID = e.EmployeeID \
                GROUP BY e.Department"
        cursor.execute(sql)
        results = cursor.fetchall()
        print(results)

        items = {}
        items['results'] = []

        for result in results:
            item = {}
            item['Department'] = result[0]
            item['Dept_Responses'] = result[1]
            items['results'].append(item)
        resultsArray.append(items['results'])

        # laptop detractors (low scorers)
        sql = "SELECT d.DeviceModel, COUNT(d.DeviceModel) AS Negative_Scores \
            FROM SurveyResults s LEFT JOIN Laptops d ON s.EmployeeID = d.EmployeeID \
                WHERE s.Laptop_Score < 4 GROUP BY d.DeviceModel"
        cursor.execute(sql)
        results = cursor.fetchall()
        print(results)

        items = {}
        items['results'] = []

        for result in results:
            item = {}
            item['DeviceModel'] = result[0]
            item['Negative_Scores'] = result[1]
            items['results'].append(item)
        resultsArray.append(items['results'])

        # info for employees open to being contacted for follow up
        sql = "SELECT s.ResponseID, e.EmployeeID, CONCAT(e.FirstName,e.LastName,'@dell.com') AS Email, e.ManagerID, \
            e.Location, e.JobTitle, e.Department, d.DeviceModel, d.DeviceAgeMonths, s.Follow_Up, s.IT_Overall_Score, \
                s.Laptop_Score, s.Accessories_Score, s.Applications_Score, s.Support_Score \
                FROM Employees e LEFT JOIN SurveyResults s ON e.EmployeeID = s.EmployeeID \
                    LEFT JOIN Laptops d ON s.EmployeeID = d.EmployeeID WHERE Follow_Up = 'Yes'"

        cursor.execute(sql)
        results = cursor.fetchall()
        print(results)

        items = {}
        items['results'] = []

        for result in results:
            item = {}
            item['ResponseID'] = result[0]
            item['EmployeeID'] = result[1]
            item['Email'] = result[2]
            item['ManagerID'] = result[3]
            item['Location'] = result[4]
            item['JobTitle'] = result[5]
            item['Dept'] = result[6]
            item['LaptopModel'] = result[7]
            item['LaptopAgeMths'] = result[8]
            item['FollowUp'] = result[9]
            item['ITOverall'] = result[10]
            item['LaptopScore'] = result[11]
            item['AccessoriesScore'] = result[12]
            item['AppsScore'] = result[13]
            item['SupportScore'] = result[14]
            items['results'].append(item)
        resultsArray.append(items['results'])

        self.closeAll()

        return resultsArray
        
    # Methods below are used to create the DB and tables used in this project
    def create_database(self):
        self.connection = mysql.connector.connect(
            host = self.host,
            user = self.user,
            password = self.password   
        )
        self.cursor = self.connection.cursor()
        # I used the DB name datarepbigproject
        sql = "CREATE DATABASE "+ self.database
        self.cursor.execute(sql)

        self.connection.commit()
        self.closeAll()

    def create_tables(self):
        cursor = self.getcursor()
        # create employees table
        sql = "create table Employees (EmployeeID int NOT NULL, FirstName varchar(50),LastName varchar(50) NOT NULL,\
            JobTitle varchar(255), Department varchar(255) NOT NULL, Salary decimal(19,4), Location varchar(50), \
                ManagerID int NOT NULL, PRIMARY KEY (EmployeeID));"
        cursor.execute(sql)
        self.connection.commit()

        # insert into employees table
        sql = "INSERT INTO Employees \
        VALUES (1, 'Michael', 'Dell', 'Chief Financial Officer & Owner', 'Dept. of the CEO', 1000000, 'United States', 1),\
        (2, 'Gillian', 'Kane', 'President, Digital', 'Dell Digital', 750000, 'Ireland', 1),\
        (3, 'John', 'Doe', 'President, Services', 'Dell Services', 750000, 'Australia', 1),\
        (4, 'Mary', 'Joyce', 'President, Logistics ', 'Dell Logistics', 750000, 'Germany', 1),\
        (5, 'Robert', 'Friend', 'Director', 'Dell Digital', 500000, 'Scotland', 2),\
        (6, 'Ruby', 'McGuire', 'Director', 'Dell Services', 500000, 'United States', 3),\
        (7, 'Jason', 'Flash', 'Director', 'Dell Logistics', 500000, 'New Zealeand', 4),\
        (8, 'Aaron', 'Paul', 'Manager', 'Dell Digital', 250000, 'United States', 5),\
        (9, 'Ellie', 'Boo', 'Principal Software Engineer', 'Dell Digital', 100000, 'England', 5),\
        (10, 'David', 'Grey', 'Senior Software Engineer', 'Dell Digital', 75000, 'Canada', 5),\
        (11, 'Silvia', 'Italia', 'Software Engineer', 'Dell Digital', 47500, 'Italy', 5),\
        (12, 'Eduardo', 'Zorro', 'Software Engineer', 'Dell Digital', 47500, 'Brazil', 5),\
        (13, 'Alex', 'Drake', 'Manager', 'Dell Services', 175000, 'United States', 6),\
        (14, 'Amber', 'May', 'Advisor', 'Dell Services', 65000, 'Ireland', 6),\
        (15, 'Muskan', 'Ashok', 'Senior Analyst', 'Dell Services', 43750, 'India', 6),\
        (16, 'Francois', 'Robin', 'Analyst', 'Dell Services', 35000, 'France', 6),\
        (17, 'Emilia', 'Natalia', 'Manager', 'Dell Logistics', 157975, 'Slovakia', 7),\
        (18, 'James', 'Bane', 'Procurement Lead', 'Dell Logistics', 98250, 'United States', 7),\
        (19, 'Christina', 'Hayes', 'Warehouse Coordinator', 'Dell Logistics', 77000, 'Belgium', 7);"
        cursor.execute(sql)
        self.connection.commit()

        # create surveyresults table
        sql = "create table SurveyResults (ResponseID int AUTO_INCREMENT NOT NULL, EmployeeID int NOT NULL,\
	        IT_Overall_Score int NOT NULL,Laptop_Score int,Accessories_Score int,Applications_Score int,\
	        Support_Score int,Positive_Feedback varchar(255),Negative_Feedback varchar(255),Follow_Up varchar(3) NOT NULL,\
	            PRIMARY KEY (ResponseID),FOREIGN KEY (EmployeeID) REFERENCES Employees(EmployeeID));"
        cursor.execute(sql)
        self.connection.commit()

        # insert into surveyresults table
        sql = 'INSERT INTO SurveyResults (EmployeeID, IT_Overall_Score, Laptop_Score, Accessories_Score,\
        Applications_Score, Support_Score, Positive_Feedback, Negative_Feedback, Follow_Up)\
        VALUES (14, 7, 3, 7, 5, 6, "The people at the support desk are always very friendly", "My laptop crashes almost every day, no matter what I have open", "Yes"),\
        (9, 9, 8, 9, 9, 10, "I love my wireless headset. Also, chatbot has been a great addition to IT support", "Zoom can take a long time to open", "Yes"),\
        (16, 1, 1, 3, 2, 5, "The onsite support guys are great, even if everything else is going downhill", "We should have better laptops - we are a computer company after all. Nothing works the way it should e.g. sales apps. I want another monitor for when I work from home but there''s no option for me to request one", "No"),\
        (7, 8, 7, 7, 7, 8, "MS Teams has made collaborating much easier now that we''ve all gone remote", "I miss being able to dial out in Skype, Teams doesn''t seem to have the same functionality", "Yes");'
        cursor.execute(sql)
        self.connection.commit()

        # create laptops table
        sql = "create table Laptops (DeviceID int AUTO_INCREMENT NOT NULL,EmployeeID int NOT NULL,DeviceModel varchar(50),\
            DeviceAgeMonths int,PRIMARY KEY (DeviceID),FOREIGN KEY (EmployeeID) REFERENCES Employees(EmployeeID));"
        cursor.execute(sql)
        self.connection.commit()

        # insert into laptops table
        sql = "INSERT INTO Laptops (EmployeeID, DeviceModel, DeviceAgeMonths)\
        VALUES (1,'XPS 3000',3),\
        (2,'Precision Tower',8),\
        (3,'Precision Tower',5),\
        (4,'Precision Tower',7),\
        (5,'Latitude Premium',12),\
        (6,'Latitude Premium',14),\
        (7,'Latitude Premium',16),\
        (8,'Inspiron 221',11),\
        (9,'Precision 5560',17),\
        (10,'Latitute 2-in-1',13),\
        (11,'Latitude Basic',22),\
        (12,'Latitude Basic',22),\
        (13,'Inspiron 221',11),\
        (14,'Precision 5560',17),\
        (15,'Latitute 2-in-1',18),\
        (16,'Latitude Basic',30),\
        (17,'Inspiron 221',11),\
        (18,'Precision 5560',17),\
        (19,'Precision 5560',17);"
        cursor.execute(sql)
        self.connection.commit()
        
        self.closeAll()

survey_DAO = Survey_DAO()

if __name__ == '__main__' :
    #survey_DAO.create_database()
    #survey_DAO.create_tables()
    print("Hello from surveyDAO")