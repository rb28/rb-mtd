from flask import flash, render_template, redirect, request, url_for
from app.api import bp



@bp.route('/mtd_returns', methods=['GET', 'POST'])

def mtd_returns():

    return render_template('mtd_return.html')