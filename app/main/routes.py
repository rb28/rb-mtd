import requests
import json
import webbrowser
import datetime
import pandas as pd
from urllib.parse import urlparse, parse_qs
from flask import flash, render_template, redirect, url_for
from app.main import bp
from app.main.forms import OAuthForm, TokenForm, RedirectForm, TestForm
from app.auth.forms import LoginForm
from flask import session
from flask import request
from app.utils import OAuthSignIn
from datetime import date, timedelta
from collections import OrderedDict
from flask_login import login_required
from openpyxl import load_workbook
from app.models import Vat_return



def get_first_day(dt, d_years=0, d_months=0):
    # d_years, d_months are "deltas" to apply to dt
    y, m = dt.year + d_years, dt.month + d_months
    a, m = divmod(m-1, 12)
    return date(y+a, m+1, 1)

def get_last_day(dt):
    return get_first_day(dt, 0, 1) + timedelta(-1)

def get_first_tax_period():
    d = date.today()
    y = d.year
    return date(y, 4, 1)



@bp.route('/home')
@login_required
def home():

    org = session['org']
    title = 'Main Home'
    return render_template('main/home.html', title=title, org=org)



@bp.route('/authorize/<provider>')
@login_required
def oauth_authorize(provider):
    #if not current_user.is_anonymous():
    #    return redirect(url_for('home'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()



@bp.route('/callback/<provider>')
@login_required
def oauth_callback(provider):
    #if not current_user.is_anonymous():
    #    return redirect(url_for('home'))
    oauth = OAuthSignIn.get_provider(provider)
    access_token = oauth.callback()
    
    return render_template('main/oauth_callback.html', title='OAuth-callback', access_token=access_token)



@bp.route('/refresh/<provider>')
@login_required
def oauth_refresh(provider):
    #if not current_user.is_anonymous():
    #    return redirect(url_for('home'))
    oauth = OAuthSignIn.get_provider(provider)
    access_token = oauth.refresh_token()
    
    return render_template('main/oauth_callback.html', title='OAuth-callback', access_token=access_token)



@bp.route('/retrieve/vat_obligations', methods=['GET','POST'])
@login_required
def vat_obligations():
    
    dt_from = request.form.get('datepicker1', get_first_tax_period().__format__('%Y-%m-%d'))
    dt_to = request.form.get('datepicker2', get_last_day(date.today()).__format__('%Y-%m-%d'))

    params = {
               'from': dt_from,
               'to': dt_to
             }

    
    vrn = session['vrn']  #'789904852'
    endpoint = '/organisations/vat/{}/obligations'.format(vrn)
    oauth = OAuthSignIn.get_provider('hmrc')
    response = oauth.get_data(endpoint, params)

    r = response.json()
    
    
    colnames = {'1':'start','2':'end','3':'due','4':'status','5':'received'}
    orderedcols = OrderedDict()

    for i in sorted(colnames):
        orderedcols[i] = colnames[i]


    if response.status_code != 200:
              
            flash('{}: - {}'.format(response.status_code, r['message']))
            
            return render_template('main/vat_obligations.html', title="vat obligations")


    d = r['obligations']
    

    return render_template('main/vat_obligations.html', title="vat obligations", my_data=d, colnames=orderedcols)




@bp.route('/retrieve/vat_liabilities', methods=['GET','POST'])
@login_required
def vat_liabilities():
    
    dt_from = request.form.get('datepicker1', get_first_tax_period().__format__('%Y-%m-%d'))
    dt_to = request.form.get('datepicker2', get_last_day(date.today()).__format__('%Y-%m-%d'))

    params = {
               'from': dt_from,
               'to': dt_to
             }

    
    vrn = session['vrn'] #'789904852'
    endpoint = '/organisations/vat/{}/liabilities'.format(vrn)
    oauth = OAuthSignIn.get_provider('hmrc')
    response = oauth.get_data(endpoint, params)

    r = response.json()

    colnames = {'1':'taxPeriod-from', '2':'taxPeriod-to','3':'type','4':'originalAmount','5':'oustandingAmount','6':'due'}
    orderedcols = OrderedDict()

    for i in sorted(colnames):
        orderedcols[i] = colnames[i]

    if response.status_code != 200:
              
            flash('{}: - {}'.format(response.status_code, r['message']))
            
            return render_template('main/vat_liabilities.html', title="vat liabilities")
    

    d = r['liabilities']
    
    
    return render_template('main/vat_liabilities.html', title="vat liabilities", my_data=d, colnames=orderedcols)





@bp.route('/retrieve/vat_payments', methods=['GET','POST'])
@login_required
def vat_payments():
    
    dt_from = request.form.get('datepicker1', get_first_tax_period().__format__('%Y-%m-%d'))
    dt_to = request.form.get('datepicker2', get_last_day(date.today()).__format__('%Y-%m-%d'))

    params = {
               'from': dt_from,
               'to': dt_to
             }

    
    vrn = session['vrn'] #'789904852'
    endpoint = '/organisations/vat/{}/payments'.format(vrn)
    oauth = OAuthSignIn.get_provider('hmrc')
    response = oauth.get_data(endpoint, params)

    r = response.json()
        
    
    colnames = {'1':'amount', '2':'received'}
    orderedcols = OrderedDict()

    for i in sorted(colnames):
        orderedcols[i] = colnames[i]
    
    if response.status_code != 200:
              
            flash('{}: - {}'.format(response.status_code, r['message']))
            
            return render_template('main/vat_payments.html', title="vat payments")
    

    d = r['payments']


    return render_template('main/vat_payments.html', title="vat payments", my_data=d, colnames=orderedcols)



@bp.route('/upload/vat_return/<string:period>', methods=['GET','POST'])
@login_required
def upload_return(period):
    
    periodKey = period
    rtn = { "periodKey": periodKey }

    rows = { 1: {'id': 'periodKey', 'desc':'Box 1. Period Key'},
                 2: {'id': 'vatDueSales', 'desc':'Box 2. Vat Due on Sales'},
                 3: {'id': 'vatDueAcquisitions', 'desc':'Box 3. VAT Due on Acquisitions'},
                 4: {'id': 'totalVatDue', 'desc':'Box 4. Total VAT Due'},
                 5: {'id': 'vatReclaimedCurrPeriod', 'desc':'Box 5. VAT Reclaimed in Current Period'},
                 6: {'id': 'netVatDue', 'desc':'Box 6. Net VAT to be paid to HMRC or reclaimed'},
                 7: {'id': 'totalValueSalesExVAT', 'desc':'Box 7. Total Value of Sales (excl. VAT)'},
                 8: {'id': 'totalValuePurchasesExVAT', 'desc':'Box 8. Total value of Purchases (excl. VAT)'},
                 9: {'id': 'totalValueGoodsSuppliedExVAT', 'desc':'Box 9. Total Value of Goods Supplied (excl. VAT)'},
                 10:{'id': 'totalAcquisitionsExVAT', 'desc':'Box 10. Total Acquisitions (excl. VAT)'},
                 11:{'id':'finalised', 'desc':'Box 11. Finalised VAT Return'}
                 }

    orderedrows = OrderedDict()

    for i in sorted(rows):
        orderedrows[i] = rows[i]

    title = 'MTD File Upload'

    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        f = request.files['file']

        wb = load_workbook(filename= f, read_only=True)
        ws = wb['Sheet1']

        # Read the cell values into a list of lists
        data_rows = []
        
        for row in ws['B7':'C16']:
            data_cols = []
            
            for cell in row:
                data_cols.append(cell.value)
                data_rows.append(data_cols)

       # Transform into dataframe
       
        df = pd.DataFrame(data_rows, columns=['key','value'])

       # Convert dataframe into dictionary
        ds = df.set_index('key')['value'].to_dict()
        
        rtn.update(ds)

        return render_template('main/vat_upload.html', period=periodKey, title=title, rtn = rtn, rows = orderedrows)
    
            
 

    
    return render_template('main/vat_upload.html', period=period, title=title, rtn = rtn, rows = orderedrows)




@bp.route('/submit/vat_return', methods=['GET','POST'])
@login_required
def submit_vat_return():

#   get periodKey for outstanding vat return. 
    
    vrn = session['vrn'] #'789904852'
    endpoint = '/organisations/vat/{}/returns'.format(vrn)

    vat_return = Vat_return.query.filter_by(period_key=periodKey).first()

    ''' check if vat return available for open period or if already submitted  '''
    if vat_return is None:
        flash('VAT return for period is not vailable. Please upload VAT return and try again')
        return redirect(url_for())

    if vat_return.is_submitted():
        flash('The VAT return for the period has already been submitted.')
        return redirect(url_for())


    data = {'periodKey': vat_return.period_key,
            'vatDueSales': vat_return.vat_due_sales,
            'vatDueAcquisitions': vat_return.vat_due_acquisitions,
            'totalVatDue': vat_return.total_vat_due,
            'vatReclaimedCurrPeriod': vat_return.vat_reclaimed_curr_period,
            'netVatDue': vat_return.net_vat_due,
            'totalValueSalesExVAT': vat_return.total_value_sales_ex_vat,
            'totalValuePurchasesExVAT': vat_return.total_value_purchases_ex_vat,
            'totalValueGoodsSuppliedExVAT': vat_return.total_value_goods_supplied_ex_vat,
            'totalAcquisitionsExVAT': total_value_acquisitions_ex_vat,
            'finalised': vat_return.finalised
            }

    oauth = OAuthSignIn.get_provider('hmrc')
    response = oauth.post_data(endpoint, data)
    r = response.json()

    if response.status_code != 200:
              
        flash('{}: - {}'.format(response.status_code, r['message']))

        return render_template('main/vat_return.html', title="Submit vat return")
    
    
    vat_return.is_submitted = True
    vat_return.submitted_on = datetime.utcnow()
    db.session.commit()

    return render_template('home/dashboard.htm')
        
    
 


@bp.route('/view/vat_return/<periodKey>', methods=['GET','POST'])
@login_required
def view_vat_return(periodKey):


#    
    periodKey = periodKey
    vrn = session['vrn'] #'789904852'
    endpoint = '/organisations/vat/{}/returns/{}'.format(vrn, periodKey)
    oauth = OAuthSignIn.get_provider('hmrc')
    response = oauth.get_data(endpoint, params)

    r = response.json()
    
    return 







@bp.route('/test', methods=['GET','POST'])
def test():
    form = TestForm()
    new = 1
    url = 'http://docs.python.org/library/webbrowser.html'
    chrome_path = '"C:\Program Files (x86)\Google\Chrome\Application\Chrome.exe" %s'
    if form.validate_on_submit():
        webbrowser.get(chrome_path).open(url, new=new)

    return render_template('test.html', title='TEST', form=form)




'''
User ID
157344663649

Password
vynwYfqLeu6b

Corporation Tax UTR
2263514067

VAT Registration Number
789904852

Organisation Details
{"name":"Company UZRETT","address":{"line1":"24 Xavier Street","line2":"Romford","postcode":"TS21 1PA"}}


'''