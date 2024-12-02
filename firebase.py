import firebase_admin
from firebase_admin import credentials, auth,firestore
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

# firebase sdk credentials
_firebase_credentials = {
    "type": os.getenv("FIREBASE_TYPE"),
    "project_id": os.getenv("FIREBASE_PROJECT_ID"),
    "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
    "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace('\\n', '\n'),  # Handle multiline keys
    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
    "client_id": os.getenv("FIREBASE_CLIENT_ID"),
    "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
    "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
    "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_X509_CERT_URL"),
    "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL"),
    "universe_domain":os.getenv('FIREBASE_UNIVERSE_DOMAIN')
}

# initialize firebase admin sdk
_cred = credentials.Certificate(_firebase_credentials)
firebase_admin.initialize_app(_cred)

# initialize db connection
db = firestore.client() 

# =============================================================================================================================
# ===========================================  FIREBASE USER MANAGEMENT  ======================================================
# =============================================================================================================================

# verify id token
def _verify_id_token(id_token):
    try:
        decoded_token = auth.verify_id_token(id_token)
        user_id = decoded_token['uid']
        email=decoded_token['email']
        handle_new_user(user_id,email)
        return user_id,email
    except Exception as e:
        print(f"Token verification failed: {e}")
        return None

# register user in case authGuard found new user entry
def handle_new_user(uid,email):
    print("handling new user")
    user_ref = db.collection('users').document(uid)
    user_doc = user_ref.get()

    if not user_doc.exists:
        user_ref.set({
            'uid': uid,
            'email': email,
            'credit': 0,  # Default credit value
            'created_at': firestore.SERVER_TIMESTAMP
        })
        print(f'New user {uid} added to Firestore with email {email}.')
    else:
        print(f'User {uid} already exists.')

# auth guard that trigger before each route
def firebase_auth_required(func):
    def wrapper(*args, **kwargs):
        id_token = request.headers.get('Authorization')  # Expecting "Bearer <token>"
        if not id_token or not id_token.startswith("Bearer "):
            return jsonify({'error': 'Authorization header missing or invalid'}), 401
        id_token = id_token.split("Bearer ")[1]

        print("id token",id_token)
        user_id,email = _verify_id_token(id_token)
        

        if not user_id:
            return jsonify({'error': 'Invalid or expired token'}), 401

        # Optionally, attach user_id to request context
        request.auth_user_id = user_id
        request.auth_email=email
        print("closing auth guard")
        return func(*args, **kwargs)
    return wrapper


# =============================================================================================================================
# ===========================================  FIREBASE CREDITS MANAGEMENT  ===================================================
# =============================================================================================================================
def get_credit_of_user(uid):
    user_ref = db.collection('users').document(uid)
    user_doc = user_ref.get()

    if user_doc.exists:
        return user_doc.to_dict().get('credit', 0)  # Default to 0 if no credit field exists
    else:
        print(f"No document found for user {uid}")
        return 0 

def increment_credit_by_amount(uid,amount):
    # fetch current amount from db
    current_credits = get_credit_of_user(uid)

    # increment amount and store back in db
    updated_credit = current_credits + amount
    user_ref = db.collection('users').document(uid)
    user_ref.update({
        'credit': updated_credit
    })

    print(f"User {uid}'s credit updated to {updated_credit}.")
    return updated_credit

def decrement_credit_by_amount(uid,amount):
    # fetch current amount from db
    current_credits = get_credit_of_user(uid)

    # deduct amount and store back in db
    # Check if the user has enough credit to deduct
    if current_credits >= amount:
        # Decrement the credit
        new_credit = current_credits - amount

        user_ref = db.collection('users').document(uid)
        user_ref.update({
            'credit': new_credit
        })
        print(f"User {uid}'s credit updated to {new_credit}.")
        return new_credit
    else:
        print(f"Insufficient credit for user {uid}. Current credit: {current_credits}.")
        return current_credits     

def is_enough_to_pay_modal(uid,amount):
    current_amount=get_credit_of_user(uid)
    if current_amount >= amount:
        return True
    else:
        return False