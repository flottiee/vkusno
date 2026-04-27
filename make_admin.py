from instance.data_db import db_session
from app.models.users import User

db_session.global_init("instance/db/vkusno.db")
db_sess = db_session.create_session()

# Замени на свой email, под которым ты регистрировался
email = "hl@com.com" 
user = db_sess.query(User).filter(User.email == email).first()

if user:
    user.speciality = "admin"
    db_sess.commit()
    print(f"Пользователь {email} теперь админ!")
else:
    print("Пользователь не найден. Сначала зарегистрируйся через сайт.")