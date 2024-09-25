from flask import Blueprint,render_template,url_for,redirect,flash,request,jsonify
from flask_login import current_user,login_required
from . import db
from .models import Message, ChatSession
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import json
from sqlalchemy import desc


views = Blueprint('views',__name__)


def chatbot(request,current_session):
   # print('ID',current_user.id)
   
   # print('Current_user.history1',type(current_user.history), current_user.history)
   # print('zzzzzzzzzzzzzzzzz',type(current_session))
   
   if len(current_session.history) == 0:
      new_history = []
   else:
      new_history = json.loads(current_session.history)
   
   
   # print('new_history1', type(new_history), new_history)
   
   
   genai.configure(api_key="API_KEY") # Hidden API_KEY 
   model = genai.GenerativeModel('gemini-1.5-flash')
   
   chat_session = model.start_chat(history=new_history)
   response = chat_session.send_message(request,
               safety_settings={
                  HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                  HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                  HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                  HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                  # HarmCategory.HARM_CATEGORY_UNSPECIFIED: HarmBlockThreshold.BLOCK_ONLY_HIGH
               })
   
   new_history.append({
      "role": "user",
      "parts": [
        request
      ]})

   new_history.append(
      {"role": "model",
      "parts": [
        response.text
      ]})
   
   # print('new_history2',type(new_history), new_history)
   current_session.history = json.dumps(new_history)
   # print('Current_user.history2',type(current_user.history),current_user.history)
   db.session.add(current_session)
   # db.session.flush()
   db.session.commit()
   # print('Current_user.history3', type(current_user.history),current_user.history)
   # print('ID',current_user.id)
   print(type(response), type(response.text), response, response.text, repr(response.text))
   return response.text

 

@views.route('/home', methods=['GET','POST'])
@login_required
def homepage():
   # global id_current_session
   # Lấy giá trị session_id hiện tại đc truyền qua tham số
   current_session_id = request.args.get('session_id')
   #Check tồn tại, không thì return None
   
   if current_session_id:
      # Lấy đối tượng session hiện tại
      current_session = ChatSession.query.filter_by(id=current_session_id,user_id = current_user.id).first()
   else:
      current_session = ChatSession.query.filter_by(user_id=current_user.id).order_by(desc(ChatSession.id)).first()
      
   if request.method =='POST':
      message_request = request.form.get('request')
      if message_request.strip() != '':
         message_response = chatbot(message_request, current_session)
         
         new_message = Message(request=message_request, response =message_response,chatSession_id=current_session_id)
         print(repr(new_message.response))
         db.session.add(new_message)
         db.session.commit()
         
         flash('Add new message successfully!', 'success')
      else:
         flash('No content in request','warning')
         
         
   return render_template('homepage.html',user=current_user, sessionChat=current_session)


# @views.route('/save-history', methods=['POST','GET'])
# @login_required
# def save_history():
   
#    global history
#     # Nhận dữ liệu từ frontend (JS)
#    data = request.json
#    savedhistory = data.get('history')
#    history = savedhistory
#    # Xử lý dữ liệu hoặc lưu trữ nó
#    print(f"Received history from localStorage: {savedhistory}")
   
#    flash('Set/Get History successfully!','success')
   
#    return jsonify({"status": "success", "received_history": savedhistory})

@views.route('/deletel-all-message',methods=['POST'])
@login_required
def delete_message():
   
   # user_id = current_user.id
   current_session_id = request.args.get('session_id')
   
   
   num_deleted = Message.query.filter_by(chatSession_id=current_session_id).delete()
   db.session.commit()
   
   flash(f'{num_deleted} messages deleted successfully!', 'success')
   return redirect(url_for('views.homepage'))



@views.route('/add-new-sessionChat',methods=['POST','GET'])
@login_required
def add_sessionChat():
   # global id_current_session
   if request.method =='POST':
      # Lấy dữ liệu ng dùng nhập ở ô name_sessionChat
      name_sessionChat = request.form.get('name_sessionChat')
      # Check dữ liệu không rỗng
      if name_sessionChat.strip() != '':
         # Tạo 1 bản ghi mới
         new_sessionChat = ChatSession(name=name_sessionChat, history=[], user_id = current_user.id)
         # Add bản ghi vào csdl
         db.session.add(new_sessionChat)
         # Chốt
         db.session.commit()
         # Lấy id của session vừa tạo
         session_id = new_sessionChat.id
         # Message thông báo
         flash('Created new chat session successfully','success')
         # Chuyển tới trang homepage kèm s_id
         return redirect(url_for('views.homepage',session_id=session_id))
      else:
         # flash('Name of session is null','warning')
         return redirect(url_for('views.homepage',session_id=None))
         
   # else:
      
   # Link tới trang homepage      
   

@views.route('/delete-session',methods=['POST'])
@login_required
def delete_session():
   # Chuyển dữ liệu  từ json -> python và get, trả về 1 dict
   session = json.loads(request.data)
   # Lấy value: id từ key
   session_id = session['chatSession_id']
   # Lấy các bản ghi message chứa khóa ngoài là session_id
   messages = Message.query.filter(Message.chatSession_id == session_id).all()
   # Tham chiếu tới bản ghi từ id
   session_delete = ChatSession.query.get(session_id)
   # Check trạng thái bản ghi cần xóa
   if session_delete:
      #Xóa message tương ứng
      for message in messages:
         db.session.delete(message)
      # Xóa bản ghi
      db.session.delete(session_delete)
      # Chốt
      db.session.commit()
      # Gửi thông báo
      flash('Deleted chat session successfully','success')
   # Trả về phía JS (FE)
   return jsonify()

@views.route('/rename-session',methods=['POST'])
@login_required
def rename_session():
   session_id = request.args.get('session_id')
   session = ChatSession.query.filter(ChatSession.id == session_id).first()
   newName = request.form.get('newName_session')
   if newName.strip() != '':
      session.name = newName
      db.session.commit()
      
   return redirect(url_for('views.homepage',session_id = session_id))
   
         
         
         
         
