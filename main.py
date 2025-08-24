from flask import Flask,request,jsonify,abort
import logging
from extensions import db
import datetime
from masker import maskdigits
from models import Accounts,Customers,BVNNIN
from nubangenerator import savingaccountgen,currentaccountgen
from flask_basicauth import BasicAuth
from cryptography.fernet import Fernet
from encrypter import load_key_from_file
import sqlalchemy
from sqlalchemy.sql import text


#Loading the encryption key for encrypting the notes
key = load_key_from_file()
fernet = Fernet(key)

app = Flask(__name__)

app.config.from_pyfile('config.py')

app.config['SQLALCHEMY_DATABASE_URI'] = app.config['DB_CONNECTION_STRING']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

app.config.from_pyfile('config.py')

app.config['BASIC_AUTH_USERNAME'] = app.config['BASIC_AUTH_USERNAME']
app.config['BASIC_AUTH_PASSWORD'] = app.config['BASIC_AUTH_PASSWORD']
app.config['BASIC_AUTH_REALM'] = app.config['BASIC_AUTH_USER_PROMPT']

basic_auth = BasicAuth(app)

def create_app():
    #binding the db to the flask app
    db.init_app(app)

    # import models to register them
    from models import Accounts,Customers

    with app.app_context():
        db.create_all()  # Creates all tables

    return app

#setting up log file
logger = logging.getLogger("PennyApi")
handler = logging.FileHandler('PennyApi.log')
logging.basicConfig(level=logging.INFO)
logger.addHandler(handler)
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(message)s'))
#log set up complete

app = create_app()

@app.route('/account/create',methods=['POST'])
@basic_auth.required
def create_account():
    customerdata = request.get_json()
    if 'firstname' not in customerdata or 'lastname' not in customerdata  or 'gender' not in customerdata or  'email' not in customerdata or 'phone' not in customerdata or 'bvn' not in customerdata or 'nin' not in customerdata:
        abort(400, description="Account can not be created without customer details")
    else:
       try:
          if 'othername' in customerdata:
              othername = customerdata['othername'].strip().capitalize()
              fullname = customerdata['firstname'].strip().capitalize() +" "+othername+" "+ customerdata['lastname'].strip().capitalize()
          else:
             othername = ""
             fullname = customerdata['firstname'].strip().capitalize() +" "+ customerdata['lastname'].strip().capitalize()

          phone = customerdata['phone'].strip()
          if phone.isdigit == True or len(phone) == 11:
              phonenumber = '+234'+phone[1:]
          else:  
              abort(400, description="Invalid Phonenumber")    

          email = customerdata['email'].strip().lower()
          #email sanitizer
          if (email.endswith((app.config['EMAIL_PREFIX'])) and '@' in email):
              email = email
          else:  
              abort(400, description="Invalid Email")   
        

          originbvn =customerdata['bvn']
          originnin = customerdata['nin']
          
          #encrypting bvn and nin
          bvnencrypt = fernet.encrypt(originbvn.encode())
          ninencrypt = fernet.encrypt(originnin.encode())
    

          bvn = maskdigits(originbvn)
          nin = maskdigits(originnin)
          
          availabletypes = ['savings','current']
          accounttype = customerdata['accounttype']
          if accounttype in availabletypes :
              check=availabletypes.index(accounttype)
              if check == 0:
                 try:
                   nuban =savingaccountgen()
                 except sqlalchemy.exc.IntegrityError as exp:
                         logger.exception("Savings Account Number Regenerating",exc_info=exp)
                         nuban =savingaccountgen()
                 except Exception as exp:
                      logger.exception("Unexpected error while generating Savings account number", exc_info=exp)
                      abort(500, description="An error occurred while generating account number")
              else:
                  try:
                    nuban = currentaccountgen()
                  except sqlalchemy.exc.IntegrityError as exp:
                      logger.exception("Current Account Number Regenerating", exc_info=exp)
                      nuban = currentaccountgen()
                  except Exception as exp:
                      logger.exception("Unexpected error while generating current account number", exc_info=exp)
                      abort(500, description="An error occurred while generating account number")
          try:
             newcustomers = Customers(firstname=customerdata['firstname'],Othername=othername,lastname=customerdata['lastname'],fullname=fullname,email=email,phone=phonenumber,BVN=bvn,NIN=nin,gender=customerdata['gender'])
             db.session.add(newcustomers)
             db.session.commit()
             logger.info("New customer created successfully created")
          except sqlalchemy.exc.IntegrityError as exp:
                db.session.rollback()
                abort(400,description="Customer with same BVN and NIN already exists")
                logger.exception("Customer with same BVN and NIN already exists")
        #   except:
        #       logger.exception("An error occured while Creating customer")
        #       db.session.rollback()
        #       abort(500,description="An error Occured while creating customer")

          try:
             newaccounts = Accounts(cusid=newcustomers.id,account_number=nuban,account_type=accounttype,created_at = datetime.datetime.utcnow(),createdby='PennyAPI')
             db.session.add(newaccounts)
             db.session.commit()
             logger.info("Customer Account created successfully created->")
          except:
             logger.exception("An error occured while Creating account")
             db.session.rollback()
             abort(500,description="An error Occured while creating account")
                #write to BVNNIN DB
          try:
            newbvnninentry = BVNNIN(cusid=newcustomers.id,BVN=bvnencrypt,NIN=ninencrypt)
            db.session.add(newbvnninentry)
            db.session.commit()
            logger.info("New bvn/nin entry successfully created")
          except:
              logger.exception("An error occured while Creating new bvn/nin entry")
              db.session.rollback()
              abort(500,description="An error Occured while creating new bvn/nin entry")


          output =[]
          newcustomer = {}
          newcustomer['cusid'] = newcustomers.id
          newcustomer['firstname']=customerdata['firstname']
          newcustomer['Othername']=othername
          newcustomer['lastname']=customerdata['lastname']
          newcustomer['fullname']=fullname
          newcustomer['gender']=customerdata['gender']
          newcustomer['email']=email
          newcustomer['phone']=phonenumber
          newcustomer['BVN']=bvn
          newcustomer['NIN']=nin
          newcustomer['Nuban']=nuban
          newcustomer['accounttype']=accounttype
          output.append(newcustomer)
       except:
          logger.exception("An error occured please try again, invalid or incomplete customer data provided")
          db.session.rollback()
          abort(500,description="An error occured please try again, invalid or incomplete customer data provided")
    return jsonify({"Message":"Account Created Successfully","Customer":output}),200


@app.route('/account/createbycusid',methods=['POST'])
@basic_auth.required
def createbycusid():
  newrecord = request.get_json()
  if 'cusid' not in newrecord or'accounttype' not in newrecord:
     abort(400, description="Provide accurate records")
  else:
      
       checkcusid = Customers.query.filter_by(id=newrecord['cusid']).first()
       #print("->>>>>>>>>>>>>>>>>>",checkcusid.id)
  
       if checkcusid:
          availabletypes = ['savings','current']
          accounttype = newrecord['accounttype']
          if accounttype in availabletypes :
              check=availabletypes.index(accounttype)
              if check == 0:
                 nuban =savingaccountgen()
              else:
                  nuban = currentaccountgen()
          else:
              #return jsonify({"Message":"Account type is currently not available"}),404
              abort(404, description="Account type is currently not available")
          try:
               newaccounts = Accounts(cusid=checkcusid.id,account_number=nuban,account_type=accounttype,created_at = datetime.datetime.utcnow(),createdby='PennyAPI')
               db.session.add(newaccounts)
               db.session.commit()
               logger.info("Customer Account created successfully created")
          except:
               logger.exception("An error occured while Creating account")
               db.session.rollback()
               abort(500,description="An error Occured while creating account")
    #  except:
    #     abort(500,description="An error Occured please try again - Customer does not exist")
  return jsonify({"Message":"New Account Created Successfully"}),200


@app.route('/account/<cusid>',methods=['GET'])
@basic_auth.required
def getaccountbycusid(cusid):
   
     result = db.session.execute(text('SELECT c.id,c.fullname,c.email,c.gender,c.phone,a.account_number,a.account_type,a.balance,a.status,a.transaction_limit,bn.BVN,bn.NIN FROM customers AS c INNER JOIN accounts AS a ON c.id = a.cusid INNER JOIN bvnninrecords AS bn ON c.id = bn.cusid WHERE c.id = :value;'), {"value": cusid})
     result = result.fetchall()
     try: 
      details = {
      'CusID':result[0][0],
      'Fullname':result[0][1],
      'Email':result[0][2],
      'Gender':result[0][3],
      'Phone':result[0][4],
      'BVN':fernet.decrypt(result[0][10]).decode(),
      'NIN':fernet.decrypt(result[0][11]).decode(),
      'Accounts':{'NoOfAccounts': len(result),}}
  
      for i, row in enumerate(result, start=1):
        details["Accounts"][f"account_{i}"] = {
        "type": row[6],
        "account_no": row[5],
        "balance": float(row[7]),  
        "status": row[8],
        "limit": float(row[9])}
     except:
         abort(400,"This account does not exist")
     return jsonify(details),200


@app.route('/account/<nuban>',methods=['GET'])
@basic_auth.required
def getaccountbynuban(nuban):
   
     result = db.session.execute(text('select a.cusid,c.fullname,a.account_number,a.account_type,a.balance,a.status,a.transaction_limitfrom accounts as a,customers as c where a.account_number = :value and c.id = a.cusid;'), {"value": nuban})
     result = result.fetchall()
     try: 
      details = {
      'CusID':result[0][0],
      'Fullname':result[0][1],
      'Email':result[0][2],
      'Gender':result[0][3],
      'Phone':result[0][4],
      'BVN':fernet.decrypt(result[0][10]).decode(),
      'NIN':fernet.decrypt(result[0][11]).decode(),
      'Accounts':{'NoOfAccounts': len(result),}}
  
      for i, row in enumerate(result, start=1):
        details["Accounts"][f"account_{i}"] = {
        "type": row[6],
        "account_no": row[5],
        "balance": float(row[7]),  
        "status": row[8],
        "limit": float(row[9])}
     except:
         abort(400,"This account does not exist")
     return jsonify(details),200

@app.route('/account/<nuban>/status',methods=['PATCH'])
@basic_auth.required
def statusmanagement(nuban):
    account = Accounts.query.filter_by(account_number=nuban).first()
    newstatus = request.get_json()
    if account:
         if 'status' not in newstatus:
             abort(400, description="Provide status for account")
         else:
             status = ['active', 'frozen', 'closed']
             userstatus = newstatus['status'].strip().lower()
             if  userstatus in status:
                 try:
                   account.status = userstatus
                   db.session.commit()
                 except:
                     db.session.rollback()
                     abort(400,"Failed to change status of account")
             else:
                 abort(400, description="Account Status does not exist")
    else:
        abort(400, description="Account does not exist")
    return jsonify("Account status updated")


@app.route('/account/<nuban>/limit',methods=['PATCH'])
@basic_auth.required
def limitmanagement(nuban):
    #current accounts cant have a more than 10million and savings cant have a limit of more than 20million
    account = Accounts.query.filter_by(account_number=nuban).first()
    newlimit = request.get_json()
    if account:
         if 'limit' not in newlimit:
             abort(400, description="Provide limit for account")
         else:
             if isinstance(newlimit['limit'],str) == True:
                 abort(400, description="Transaction Limit must be an amount")
             newlimit = float(newlimit['limit'])
             print(account.account_type)
             if account.account_type == 'savings' and newlimit <= app.config['SAVINGS_LIMIT_MAX']:
                 account.transaction_limit = newlimit
                 db.session.commit()
             elif account.account_type == 'current' and newlimit <= app.config['CURRENT_LIMIT_MAX']:
                 account.transaction_limit = newlimit
                 db.session.commit()
             else:
                 abort(400, description="Transaction Limit for current accounts cannot be more than 10million and savings accounts cannot be more than 20million")
    else:
        abort(400, description="Account does not exist")
    
    return jsonify("Transaction Limit for "+nuban+" has been increased")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
    #app.run(debug=True)