from flask import Flask, jsonify, request
import redis, ssl, random
from datetime import datetime
from flask_mail import Mail, Message

app = Flask(__name__)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'appathleta@gmail.com'
app.config['MAIL_PASSWORD'] = 'qiikvsidfnpxlvzv'
app.config['MAIL_DEFAULT_SENDER'] = 'appathleta@gmail.com'

redis_url = 'rediss://red-cs64793tq21c73dojdrg:M8jUtQQ66z8ZS9MWIfPcniDoTbC3mQzK@oregon-redis.render.com:6379'
r = redis.Redis.from_url(url= redis_url, ssl_cert_reqs=None)
mail = Mail(app)

# @app.route('/set', methods=['POST'])
# def set_value():
#     user = request.json.get('email')
#     if user:
#         date = datetime.now().strftime("%Y%m%d%H%M%S")
#         key = f"{user}_{date}"
#         value = random.randint(100000, 999999)
#         r.set(key, value, ex=300)
#         return jsonify({'chave': key, 'valor': value}), 200
#     else:
#         return jsonify({'error': 'Por favor, forneça o email do usuario'}), 400

@app.route('/set/<email>', methods=['POST'])
def set_value(email):
    user = email
    if user:
        date = datetime.now().strftime("%Y%m%d%H%M%S")
        key = f"{user}_{date}"
        value = random.randint(100000, 999999)
        r.set(key, value, ex=300)

        # Corpo HTML do email
        html_body = f"""
        <html>
        <body>
            <div style="font-family: Arial, sans-serif; text-align: center; padding: 20px;">
                <h2 style="color: #F4A900;">Seu Código de Verificação</h2>
                <p>Olá,</p>
                <p>Seu código de verificação é:</p>
                <div style="font-size: 24px; font-weight: bold; background-color: #F4F4F4; padding: 10px; border-radius: 5px; display: inline-block; margin-top: 10px;">
                    {value}
                </div>
                <p style="margin-top: 20px;">O código expira em 5 minutos.</p>
                <p>Atenciosamente,<br>Equipe Athleta</p>
            </div>
        </body>
        </html>
        """
        # Enviar o email
        try:
            msg = Message('Seu código de verificação', recipients=[user])
            msg.body = f"Olá, seu código de verificação é: {value}"
            msg.html = html_body
            mail.send(msg)
        except Exception as e:
            return jsonify({'message': str(e)}), 500
        return jsonify({"message":"Email enviado","key":key}), 200
    else:
        return jsonify({'message': 'Por favor, forneça o email do usuario'}), 400

# Rota para obter um valor do Redis
@app.route('/get/<key>/<value>', methods=['GET'])
def get_value(key,value):
    valor = r.get(key)
    if valor:
        valor = valor.decode('utf-8')
        if valor == value:
            return jsonify({'message':'Chave valida'}), 200
        else:
            return jsonify({'message': 'Codigo OTP incorreto'}), 400
    else:
        return jsonify({'message' 'Email incorreto'}), 404

# Rota para deletar um valor do Redis
@app.route('/delete/<key>', methods=['DELETE'])
def delete_value(key):
    result = r.delete(key)
    
    if result:
        return jsonify({'message': f'Chave {key} foi deletada com sucesso!'}), 200
    else:
        return jsonify({'message': 'Chave não encontrada'}), 404

if __name__ == '__main__':
    app.run(debug=True)