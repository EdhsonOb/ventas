from flask import Flask, render_template, request
import xmlrpc.client
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
# Valores iniciales
valor_anio = 0
valor_mes = 0

def execute_rpc(url, db, username, password, model, method, domain=[], fields=[]):
    common_proxy = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common_proxy.authenticate(db, username, password, {})
    models_proxy = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    data = models_proxy.execute_kw(db, uid, password, model, method, [domain], {'fields': fields})
    return data

@app.route('/', methods=['GET', 'POST'])
def home():
    global valor_anio, valor_mes

    # Configuración de la conexión XML-RPC
    url = 'https://biancorelab.odoo.com'
    db = 'biancorelab'
    username = 'erodriguez@biancorelab.com'
    password = '2iUaFfRinJTf6w4'

    # Filtro adicional
    domain = [
        "&",
        ("state", "not in", ("draft", "cancel")),
        "&",
        "|",
        ("move_type", "=", "out_invoice"),
        ("move_type", "=", "out_refund"),
        "&",
        "|",
        ("move_type", "=", "out_invoice"),
        ("move_type", "=", "in_invoice"),
        "&",
        ("invoice_date", ">=", "2023-01-01"),
        ("invoice_date", "<=", "2023-12-31")
    ]

    # Consulta a la tabla account.invoice.report con el filtro adicional
    invoice_report_data = execute_rpc(url, db, username, password, 'account.invoice.report', 'search_read', domain, ['move_id', 'partner_id', 'invoice_date', 'price_total', 'price_subtotal', 'product_categ_id', 'product_id', 'product_uom_id', 'quantity'])

    # Calcular los subtotales
    subtotal_anio = sum(record['price_subtotal'] for record in invoice_report_data)
    subtotal_mes = sum(record['price_subtotal'] for record in invoice_report_data if datetime.strptime(record['invoice_date'], '%Y-%m-%d').month == datetime.now().month)

    if request.method == 'POST':
        valor_anio = float(request.form.get('meta_anio', 0))
        valor_mes = float(request.form.get('meta_mes', 0))

    return render_template('meta.html', subtotal_anio=subtotal_anio, subtotal_mes_actual=subtotal_mes, valor_anio=valor_anio, valor_mes=valor_mes)

if __name__ == '__main__':
    app.run(debug=True)
