


# from fastapi import FastAPI, Request, Depends, HTTPException, status, Form, Cookie
# from fastapi.responses import HTMLResponse, RedirectResponse
# from fastapi.templating import Jinja2Templates
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.future import select
# from sqlalchemy import func
# import sqlalchemy as sa
# from datetime import timedelta,datetime
# from typing import Optional
# from zoneinfo import ZoneInfo

# from jose import JWTError, jwt
# from app.models import User, Visitor
# from app.database import get_db
# from app.security import authenticate_user, create_access_token,SECRET_KEY, ALGORITHM,verify_access_token

# from app import crud, schemas
# from app.schemas import UserUpdate
# from app.auth import get_current_user
# from app.utils import mask_name, mask_email,mask_phone,get_initials,mask_address,_send_to_gateway,generate_otp,verify_otp


# from app.schemas import SMSRequest  # Add this import if SMSRequest is defined in schemas.py
# from app.settings import Settings, get_settings
# from app import models
# from fastapi.responses import JSONResponse







# IST = ZoneInfo("Asia/Kolkata")

# app = FastAPI(title="Receptionist Panel")

# # Templates
# login_templates = Jinja2Templates(directory="frontend")
# reception_templates = Jinja2Templates(directory="frontend/reception/templates")
# admin_templates = Jinja2Templates(directory="frontend/admin/templates")

# # ========================================== USER MANAGEMENT ENDPOINTS ===================================================


# # ---------------- LOGIN PAGE ---------------- #

# # @app.get("/", response_class=HTMLResponse)
# # async def login_page(request: Request,  access_token: Optional[str] = Cookie(None)):

# #     if access_token:

# #         redirect_url = "/admin/dashboard"

# #         response = RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)

# #         return response

    

   
# #     return login_templates.TemplateResponse("login.html", {"request": request})




# @app.get("/", response_class=HTMLResponse)
# async def login_page(
#     request: Request,
#     access_token: Optional[str] = Cookie(None)
# ):
#     if access_token:
#         # Decode the access token
#         token_data = verify_access_token(access_token)
#         if token_data:
#             role = token_data.get("role")

#             if role == "admin":
#                 redirect_url = "/admin/dashboard"
#                 response = RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)
#                 return response

#             elif role == "receptionist":
#                 redirect_url = "/receptionist/dashboard"
#                 response = RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)
#                 return response

#     # If no valid access token, show login page (with no caching)
#     response = login_templates.TemplateResponse("login.html", {"request": request})
#     response.headers["Cache-Control"] = "no-store"
#     response.headers["Pragma"] = "no-cache"
#     return response







# @app.post("/login", response_class=HTMLResponse)
# async def login(
#     request: Request,
#     username: str = Form(...),
#     password: str = Form(...),
#     db: AsyncSession = Depends(get_db)
# ):
    
#     # print(request)
#     # Authenticate user
#     user = await authenticate_user(db, username, password)
#     if not user:
#         return login_templates.TemplateResponse(
#             "login.html",
#             {"request": request, "error": "Invalid credentials"}
#         )

#     # Create access token
#     access_token_expires = timedelta(minutes=30)
#     access_token = create_access_token(
#         data={"sub": user.username, "role": user.role},
#         expires_delta=access_token_expires
#     )

#     # ✅ Choose dashboard by role
#     if user.role == "admin":
#         redirect_url = "/admin/dashboard"
#     elif user.role == "receptionist":
#         redirect_url = "/receptionist/dashboard"
#     else:
#         raise HTTPException(status_code=403, detail="Unauthorized role")

#     # ✅ Redirect to correct dashboard
#     response = RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)
#     response.set_cookie(
#         key="access_token",
#         value=access_token,
#         httponly=True,
#         max_age=1800
#     )
#     return response








# # ========================================== USER MANAGEMENT ENDPOINTS ===================================================





# @app.get("/admin/users", response_class=HTMLResponse)
# async def admin_users(
#     request: Request,
#     page: int = 1,
#     db: AsyncSession = Depends(get_db),
#     access_token: Optional[str] = Cookie(None)
# ):
#     current_user, redirect = await require_admin(request, db, access_token)
#     if redirect:
#         return redirect
    
#     per_page = 10
#     users, total_pages = await crud.get_users_paginated(db, page, per_page)
    
#     return admin_templates.TemplateResponse(
#         "user_management.html",
#         {
#             "request": request,
#             "current_user": current_user,
#             "users": users,
#             "page": page,
#             "total_pages": total_pages
#         }
#     )




# @app.post("/admin/users", response_class=HTMLResponse)
# async def admin_create_user(
#     request: Request,
#     username: str = Form(...),
#     password: str = Form(...),
#     role: str = Form(...),
#     db: AsyncSession = Depends(get_db),
#     access_token: Optional[str] = Cookie(None)
# ):
#     current_user, redirect = await require_admin(request, db, access_token)
#     if redirect:
#         return redirect

#     # Check if username already exists
#     result = await db.execute(select(User).where(User.username == username))
#     existing_user = result.scalars().first()
#     if existing_user:
#         users = await crud.get_users(db)
#         return admin_templates.TemplateResponse(
#             "user_management.html",
#             {
#                 "request": request,
#                 "current_user": current_user,
#                 "users": users,
#                 "error": "Username already exists"
#             }
#         )

#     # Create new user
#     hashed_password = crud.hash_password(password)
#     new_user = User(
#         username=username,
#         password_hash=hashed_password,
#         role=role
#     )

#     db.add(new_user)
#     await db.commit()
#     await db.refresh(new_user)

#     return RedirectResponse(url="/admin/users", status_code=status.HTTP_303_SEE_OTHER)







# @app.put("/admin/users/manage/{user_id}", response_class=HTMLResponse)
# async def admin_update_user(
#     request: Request,
#     user_id: int,
#     username: str = Form(None),
#     password: str = Form(None),
#     role: str = Form(None),
#     db: AsyncSession = Depends(get_db),
#     access_token: Optional[str] = Cookie(None)
# ):
#     current_user, redirect = await require_admin(request, db, access_token)
#     if redirect:
#         return redirect

#     # Get pagination parameters
#     page = int(request.query_params.get("page", 1))
#     per_page = 10
    
#     # Get the user to update
#     result = await db.execute(select(User).where(User.id == user_id))
#     user = result.scalars().first()
    
#     if not user:
#         users, total_pages = await crud.get_users_paginated(db, page, per_page)
#         return admin_templates.TemplateResponse(
#             "user_management.html",
#             {
#                 "request": request,
#                 "current_user": current_user,
#                 "users": users,
#                 "page": page,
#                 "total_pages": total_pages,
#                 "error": "User not found"
#             }
#         )

#     # Update fields if provided
#     if username:
#         # Check if new username is already taken by another user
#         result = await db.execute(select(User).where(User.username == username, User.id != user_id))
#         existing_user = result.scalars().first()
#         if existing_user:
#             users, total_pages = await crud.get_users_paginated(db, page, per_page)
#             return admin_templates.TemplateResponse(
#                 "user_management.html",
#                 {
#                     "request": request,
#                     "current_user": current_user,
#                     "users": users,
#                     "page": page,
#                     "total_pages": total_pages,
#                     "error": "Username already taken"
#                 }
#             )
#         user.username = username
    
#     if password:
#         user.password_hash = crud.hash_password(password)
    
#     if role:
#         user.role = role

#     await db.commit()
#     await db.refresh(user)

#     users, total_pages = await crud.get_users_paginated(db, page, per_page)
#     return admin_templates.TemplateResponse(
#         "user_management.html",
#         {
#             "request": request,
#             "current_user": current_user,
#             "users": users,
#             "page": page,
#             "total_pages": total_pages,
#             "success": "User updated successfully!"
#         }
#     )






# @app.delete("/admin/users/{user_id}", response_class=HTMLResponse)
# async def admin_delete_user(
#     request: Request,
#     user_id: int,
#     db: AsyncSession = Depends(get_db),
#     access_token: Optional[str] = Cookie(None)
# ):
#     current_user, redirect = await require_admin(request, db, access_token)
#     if redirect:
#         return redirect

#     # Get the user to delete
#     result = await db.execute(select(User).where(User.id == user_id))
#     user = result.scalars().first()
    
#     if not user:
#         users = await crud.get_users(db)
#         return admin_templates.TemplateResponse(
#             "user_management.html",
#             {
#                 "request": request,
#                 "current_user": current_user,
#                 "users": users,
#                 "error": "User not found"
#             }
#         )

#     # Prevent self-deletion
#     if user.id == current_user["id"]:
#         users = await crud.get_users(db)
#         return admin_templates.TemplateResponse(
#             "user_management.html",
#             {
#                 "request": request,
#                 "current_user": current_user,
#                 "users": users,
#                 "error": "Cannot delete your own account"
#             }
#         )

#     await db.delete(user)
#     await db.commit()

#     return RedirectResponse(url="/admin/users", status_code=status.HTTP_303_SEE_OTHER)

# # Add this to your sidebar menu in base.html
# # <li>
# #     <a href="/admin/users"
# #         class="flex items-center p-3 rounded-lg 
# #        {% if request.url.path == '/admin/users' %}bg-secondary text-white{% else %}text-dark hover:bg-secondary hover:text-white{% endif %}">
# #         <i class="fas fa-user-cog w-5 text-center mr-2"></i> User Management
# #     </a>
# # </li>



# # ------------------------------------------------ CURRENT USER HELPER --------------------------------------------- #



# async def require_receptionist(request, db, access_token):
#     current_user = await get_current_user(request=request, db=db, access_token=access_token)
#     if not current_user:
#         return None, RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

#     if current_user["role"] != "receptionist":
#         raise HTTPException(status_code=403, detail="Access forbidden")

#     return current_user, None








# # async def require_admin(request: Request, db: AsyncSession, access_token: Optional[str] = Cookie(None)):
# #     current_user = await get_current_user(request=request, db=db, access_token=access_token)
# #     if not current_user:
# #         return None, RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

# #     if current_user["role"] != "admin":
# #         raise HTTPException(status_code=403, detail="Access forbidden")

# #     return current_user, None







# async def require_admin(request: Request, db: AsyncSession, access_token: Optional[str]):
#     if not access_token:
#         return None, RedirectResponse(url="/login", status_code=302)

#     try:
#         payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get("sub")
#         role: str = payload.get("role")

#         if username is None or role != "admin":
#             return None, RedirectResponse(url="/login", status_code=302)

#     except JWTError:
#         return None, RedirectResponse(url="/login", status_code=302)

#     result = await db.execute(select(User).where(User.username == username))
#     user = result.scalars().first()
#     if not user:
#         return None, RedirectResponse(url="/login", status_code=302)

#     return user, None




# #================================================================ ADMIN DASHBOARD ===============================================================





# # @app.get("/admin/dashboard", response_class=HTMLResponse)
# # async def admin_dashboard(
# #     request: Request,
# #     db: AsyncSession = Depends(get_db),
# #     access_token: Optional[str] = Cookie(None)
# # ):
    
# #     print("acces token is",access_token)
# #     current_user, redirect = await require_admin(request, db, access_token)

# #     print("current user is",current_user)
# #     if redirect:
# #         return redirect

# #     today_visitors = await crud.count_today_visitors(db)
# #     # waiting_visitors = await crud.count_waiting_visitors(db)
# #     # checked_in_visitors = await crud.count_checked_in_visitors(db)
# #     recent_visitors = await crud.get_recent_visitors(db, limit=10)

# #     return admin_templates.TemplateResponse(
# #         "index.html",
# #         {
# #             "request": request,
# #             "current_user": current_user,
# #             "today_visitors": today_visitors,

# #             "recent_visitors": recent_visitors,
# #         }
# #     )




# @app.get("/admin/dashboard", response_class=HTMLResponse)
# async def admin_dashboard(
#     request: Request,
#     db: AsyncSession = Depends(get_db),
#     access_token: Optional[str] = Cookie(None)
# ):
#     current_user, redirect = await require_admin(request, db, access_token)

#     if redirect:
#         return redirect  # ❌ Agar token missing/invalid hai to login bhej do

#     today_visitors = await crud.count_today_visitors(db)
#     recent_visitors = await crud.get_recent_visitors(db, limit=10)

#     return admin_templates.TemplateResponse(
#         "index.html",
#         {
#             "request": request,
#             "current_user": current_user,
#             "today_visitors": today_visitors,
#             "recent_visitors": recent_visitors,
#         }
#     )





# @app.get("/admin/visitors/all", response_class=HTMLResponse)
# async def admin_all_visitors(
#     request: Request,
#     page: int = 1,
#     per_page: int = 10,
#     db: AsyncSession = Depends(get_db),
#     access_token: Optional[str] = Cookie(None),
# ):
#     current_user, redirect = await require_admin(request, db, access_token)
#     if redirect:
#         return redirect

#     # Count total visitors
#     result = await db.execute(sa.select(func.count(Visitor.id)))
#     total_visitors = result.scalar()

#     # Pagination
#     offset = (page - 1) * per_page
#     query = await db.execute(
#         sa.select(Visitor).order_by(Visitor.check_in_time.desc()).offset(offset).limit(per_page)
#     )
#     visitors = query.scalars().all()

#     total_pages = (total_visitors + per_page - 1) // per_page

#     return admin_templates.TemplateResponse(
#         "visitor.html",
#         {
#             "request": request,
#             "current_user": current_user,
#             "all_visitors": visitors,
#             "page": page,
#             "total_pages": total_pages,
#             "per_page": per_page,
#             "current_date": datetime.utcnow().strftime("%A, %B %d, %Y"),
#             "current_time": datetime.utcnow().strftime("%H:%M:%S"),
#         },
#     )





# # @app.get("/admin/visitors/{visitor_id}/edit")
# # async def admin_edit_visitor_page(
# #     request: Request,
# #     visitor_id: int,
# #     db: AsyncSession = Depends(get_db),
# #     access_token: Optional[str] = Cookie(None),
# # ):
# #     current_user = await get_current_user(request, db, access_token)
# #     if not current_user or current_user["role"] != "admin":
# #         return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

# #     result = await db.execute(select(Visitor).where(Visitor.id == visitor_id))
# #     visitor = result.scalars().first()

# #     if not visitor:
# #         raise HTTPException(status_code=404, detail="Visitor not found")

# #     return admin_templates.TemplateResponse(
# #         "visitor_edit.html",
# #         {
# #             "request": request,
# #             "visitor": visitor
# #         }
# #     )







# #===============================================RECEPTIONIST DASHBOARD ==============================================================


# @app.get("/receptionist/dashboard", response_class=HTMLResponse)
# async def receptionist_dashboard(
#     request: Request,
#     db: AsyncSession = Depends(get_db),
#     access_token: Optional[str] = Cookie(None)
# ):
#     current_user, redirect = await require_receptionist(request, db, access_token)
#     if redirect:
#         return redirect

#     today_visitors = await crud.count_today_visitors(db)
#     # waiting_visitors = await crud.count_waiting_visitors(db)
#     # checked_in_visitors = await crud.count_checked_in_visitors(db)
#     recent_visitors = await crud.get_recent_visitors(db, limit=10)

    
#     masked_visitors = []
#     for v in recent_visitors:
#         masked_visitors.append({
#            "id": v.id,
#             "name": mask_name(v.name),
#             "email": mask_email(v.email),
#             "phone": mask_phone(v.phone),
#             "company": v.company,
#             "host": v.host,
#             "address": mask_address(v.address),
#             "check_in_time": v.check_in_time,
#         })


#     # render template
            
#     return reception_templates.TemplateResponse(
#         "index.html",
#         {
#             "request": request,
#             "current_user": current_user,
#             "today_visitors": today_visitors,

#             "recent_visitors": masked_visitors,
#         }
#     )



# # ========================================== RECEPTIONIST VISITOR ENDPOINTS ===============================================





# # @app.get("/receptionist/visitors/all", response_class=HTMLResponse)
# # async def receptionist_all_visitors(
# #     request: Request,
# #     page: int = 1,
# #     per_page: int = 10,
# #     db: AsyncSession = Depends(get_db),
# #     access_token: Optional[str] = Cookie(None),
# # ):
# #     current_user, redirect = await require_receptionist(request, db, access_token)
# #     if redirect:
# #         return redirect

# #     # Count total visitors
# #     result = await db.execute(sa.select(func.count(Visitor.id)))
# #     total_visitors = result.scalar()

# #     # Pagination
# #     offset = (page - 1) * per_page
# #     query = await db.execute(
# #         sa.select(Visitor).order_by(Visitor.check_in_time.desc()).offset(offset).limit(per_page)
# #     )
# #     visitors = query.scalars().all()

# #     total_pages = (total_visitors + per_page - 1) // per_page

# #     return reception_templates.TemplateResponse(
# #         "visitor.html",
# #         {
# #             "request": request,
# #             "current_user": current_user,
# #             "all_visitors": visitors,
# #             "page": page,
# #             "total_pages": total_pages,
# #             "per_page": per_page,
# #             "current_date": datetime.utcnow().strftime("%A, %B %d, %Y"),
# #             "current_time": datetime.utcnow().strftime("%H:%M:%S"),
# #         },
# #     )





# # # Receptionist visitors endpoint
# # @app.get("/receptionist/visitors/all", response_class=HTMLResponse)
# # async def receptionist_all_visitors(
# #     request: Request,
# #     page: int = 1,
# #     per_page: int = 10,
# #     db: AsyncSession = Depends(get_db),
# #     access_token: Optional[str] = Cookie(None),
# # ):
# #     # Receptionist auth check
# #     current_user, redirect = await require_receptionist(request, db, access_token)
# #     if redirect:
# #         return redirect

# #     # Count total visitors
# #     result = await db.execute(sa.select(func.count(Visitor.id)))
# #     total_visitors = result.scalar()

# #     # Pagination
# #     offset = (page - 1) * per_page
# #     query = await db.execute(
# #         sa.select(Visitor).order_by(Visitor.check_in_time.desc()).offset(offset).limit(per_page)
# #     )
# #     visitors = query.scalars().all()

# #     # Masked data
# #     visitors_data = []
# #     for visitor in visitors:
# #         visitors_data.append({
# #             "id": visitor.id,
# #             "masked_name": mask_name(visitor.name),
# #             "initials": get_initials(visitor.name),
# #             "company": visitor.company,
# #             "masked_email": mask_email(visitor.email),
# #             "masked_phone": mask_phone(visitor.phone),
# #             "host": visitor.host,
# #             "masked_address": mask_address(visitor.address),
# #             "check_in_time": visitor.check_in_time,
# #         })

# #     total_pages = (total_visitors + per_page - 1) // per_page

# #     return reception_templates.TemplateResponse(
# #         "visitor.html",
# #         {
# #             "request": request,
# #             "current_user": current_user,
# #             "all_visitors": visitors_data,
# #             "page": page,
# #             "total_pages": total_pages,
# #             "per_page": per_page,
# #             "current_date": datetime.utcnow().strftime("%A, %B %d, %Y"),
# #             "current_time": datetime.utcnow().strftime("%H:%M:%S"),
# #         },
# #     )


# # Receptionist visitors endpoint - Sorted by check_in_time descending
# @app.get("/receptionist/visitors/all", response_class=HTMLResponse)
# async def receptionist_all_visitors(
#     request: Request,
#     page: int = 1,
#     per_page: int = 10,
#     db: AsyncSession = Depends(get_db),
#     access_token: Optional[str] = Cookie(None),
# ):
#     # Receptionist auth check
#     current_user, redirect = await require_receptionist(request, db, access_token)
#     if redirect:
#         return redirect

#     # Count total visitors
#     result = await db.execute(sa.select(func.count(Visitor.id)))
#     total_visitors = result.scalar()

#     # Ensure page is within valid range
#     if page < 1:
#         page = 1
#     total_pages = max(1, (total_visitors + per_page - 1) // per_page)
#     if page > total_pages:
#         page = total_pages

#     # Pagination - Order by check_in_time descending (newest first)
#     offset = (page - 1) * per_page
#     query = await db.execute(
#         sa.select(Visitor)
#         .order_by(Visitor.check_in_time.desc())  # Newest visitors first
#         .offset(offset)
#         .limit(per_page)
#     )
#     visitors = query.scalars().all()

#     # Debug: Print visitor times to verify order
#     print(f"Page {page} visitors:")
#     for i, visitor in enumerate(visitors):
#         print(f"  {i+1}. {visitor.check_in_time} - {visitor.name}")

#     # Masked data
#     visitors_data = []
#     for visitor in visitors:
#         # Format check_in_time to readable format
#         check_in_time_formatted = visitor.check_in_time.strftime("%d %b %Y, %I:%M %p")
        
#         visitors_data.append({
#             "id": visitor.id,
#             "masked_name": mask_name(visitor.name),
#             "initials": get_initials(visitor.name),
#             "company": visitor.company,
#             "masked_email": mask_email(visitor.email),
#             "masked_phone": mask_phone(visitor.phone),
#             "host": visitor.host,
#             "masked_address": mask_address(visitor.address),
#             "check_in_time": check_in_time_formatted,
#             "check_in_time_raw": visitor.check_in_time.isoformat(),
#         })

#     # Get current date and time
#     current_time = datetime.now()
#     current_date_display = current_time.strftime("%A, %B %d, %Y")
#     current_time_display = current_time.strftime("%H:%M:%S")

#     return reception_templates.TemplateResponse(
#         "visitor.html",
#         {
#             "request": request,
#             "current_user": current_user,
#             "all_visitors": visitors_data,
#             "page": page,
#             "total_pages": total_pages,
#             "per_page": per_page,
#             "total_visitors": total_visitors,
#             "current_date": current_date_display,
#             "current_time": current_time_display,
#         },
#     )

# # @app.post("/receptionist/visitors/check-in", response_class=HTMLResponse)
# # async def receptionist_check_in_submit(
# #     request: Request,
# #     name: str = Form(...),
# #     company: str = Form(None),
# #     email: str = Form(None),
# #     phone: str = Form(...),
# #     date: str = Form(""),
# #     time: str = Form(""),
# #     host: str = Form(...),
# #     purpose: str = Form(...),
# #     address: str =Form(...),
# #     db: AsyncSession = Depends(get_db),
# #     access_token: Optional[str] = Cookie(None),
# # ):
# #     current_user, redirect = await require_receptionist(request, db, access_token)
# #     if redirect:
# #         return redirect

# #     if date.strip() and time.strip():
# #         try:
# #             check_in_time = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
# #         except ValueError:
# #             check_in_time = datetime.now(IST)
# #     else:
# #         check_in_time = datetime.now(IST)

# #     check_in_time = check_in_time.replace(tzinfo=None)

# #     new_visitor = Visitor(
# #         name=name,
# #         company=company,
# #         email=email,
# #         phone=phone,
# #         host=host,
# #         purpose=purpose,
# #         check_in_time=check_in_time,
# #         address=address,
# #         created_by=current_user["id"],
# #     )

# #     db.add(new_visitor)
# #     await db.commit()
# #     await db.refresh(new_visitor)

# #     #     # ✅ OTP once used → delete
# #     # del OtpStore[phone]

# #     return RedirectResponse(url="/receptionist/visitors/all", status_code=status.HTTP_303_SEE_OTHER)


# @app.post("/receptionist/visitors/check-in", response_class=HTMLResponse)
# async def receptionist_check_in_submit(
#     request: Request,
#     name: str = Form(...),
#     company: str = Form(None),
#     email: str = Form(None),
#     phone: str = Form(...),
#     otp: str = Form(...),
#     date: str = Form(...),
#     time: str = Form(...),
#     host: str = Form(...),
#     purpose: str = Form(...),
#     address: str = Form(None),
#     db: AsyncSession = Depends(get_db),
#     access_token: Optional[str] = Cookie(None),
# ):
#     current_user, redirect = await require_receptionist(request, db, access_token)
#     if redirect:
#         return redirect



#     # Parse date and time
#     if date.strip() and time.strip():
#         try:
#             check_in_time = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
#             print(f"Parsed date/time: {check_in_time}")  # Debug
#         except ValueError:
#             print("Date parsing failed, using current time")  # Debug
#             check_in_time = datetime.now(IST)
#     else:
#         print("Using current time")  # Debug
#         check_in_time = datetime.now(IST)

#     check_in_time = check_in_time.replace(tzinfo=None)

#     # Create new visitor
#     new_visitor = Visitor(
#         name=name,
#         company=company,
#         email=email,
#         phone=phone,
#         host=host,
#         purpose=purpose,
#         address=address,
#         check_in_time=check_in_time,
#         created_by=current_user["id"],
#     )

#     db.add(new_visitor)
#     await db.commit()
#     await db.refresh(new_visitor)

#     print(f"Visitor {name} checked in successfully")  # Debug

#     return RedirectResponse(url="/receptionist/visitors/all", status_code=status.HTTP_303_SEE_OTHER)

# # ----------------------------------  SMS OTP ----------------------------------------

# @app.post("/sms/send")
# async def send_sms(payload: SMSRequest, settings: Settings = Depends(get_settings)):
#     return await _send_to_gateway(payload, settings)




# @app.post("/receptionist/visitors/verify-otp")
# async def verify_otp_endpoint(phone: str = Form(...), otp: str = Form(...)):


#     res=verify_otp(phone, otp)

#     print("is otp verified",otp,res)
#     if res:
#         return {"ok": True, "message": "OTP verified successfully"}
#     return JSONResponse(content={"ok": False, "message": "OTP verification failed"})


# @app.get("/logout")
# async def logout():
#     response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
#     response.delete_cookie("access_token")
#     return response













from fastapi import FastAPI, Request, Depends, HTTPException, status, Form, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
import sqlalchemy as sa
from sqlalchemy.orm import Session
from datetime import timedelta,datetime
from typing import Optional
from zoneinfo import ZoneInfo

from jose import JWTError, jwt
from app.models import User, Visitor,OTP
from app.database import get_db
from app.security import authenticate_user, create_access_token,SECRET_KEY, ALGORITHM,verify_access_token

from app import crud, schemas
from app.schemas import UserUpdate
from app.auth import get_current_user
from app.utils import mask_name,mask_phone,get_initials,_send_to_gateway,get_flashed_messages,verify_otp


from app.schemas import SMSRequest  # Add this import if SMSRequest is defined in schemas.py
from app.settings import Settings, get_settings
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware
import os
from app.utils import flash
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect







IST = ZoneInfo("Asia/Kolkata")

app = FastAPI(title="Receptionist Panel")

# Templates
login_templates = Jinja2Templates(directory="frontend")
reception_templates = Jinja2Templates(directory="frontend/reception/templates")
admin_templates = Jinja2Templates(directory="frontend/admin/templates")


#====================== flash msg key ======================

SECRET_KEY = os.environ.get("SECRET_KEY", "logan")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)








# ========================================== USER MANAGEMENT ENDPOINTS ===================================================


# ---------------- LOGIN PAGE ---------------- #

# @app.get("/", response_class=HTMLResponse)
# async def login_page(request: Request,  access_token: Optional[str] = Cookie(None)):

#     if access_token:

#         redirect_url = "/admin/dashboard"

#         response = RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)

#         return response

    

   
#     return login_templates.TemplateResponse("login.html", {"request": request})




@app.get("/", response_class=HTMLResponse)
async def login_page(
    request: Request,
    access_token: Optional[str] = Cookie(None)
):
    if access_token:
        # Decode the access token
        token_data = verify_access_token(access_token)
        if token_data:
            role = token_data.get("role")

            if role == "admin":
                redirect_url = "/admin/dashboard"
                response = RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)
                return response

            elif role == "receptionist":
                redirect_url = "/receptionist/dashboard"
                response = RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)
                return response

    # If no valid access token, show login page (with no caching)
    response = login_templates.TemplateResponse("login.html", {"request": request})
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    return response







@app.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    
    # print(request)
    # Authenticate user
    user = await authenticate_user(db, username, password)
    if not user:
        return login_templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid credentials"}
        )

    # Create access token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=access_token_expires
    )

    # ✅ Choose dashboard by role
    if user.role == "admin":
        redirect_url = "/admin/dashboard"
    elif user.role == "receptionist":
        redirect_url = "/receptionist/dashboard"
    else:
        raise HTTPException(status_code=403, detail="Unauthorized role")

    # ✅ Redirect to correct dashboard
    response = RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=1800
    )
    return response








# ========================================== USER MANAGEMENT ENDPOINTS ===================================================





@app.get("/admin/users", response_class=HTMLResponse)
async def admin_users(
    request: Request,
    page: int = 1,
    db: AsyncSession = Depends(get_db),
    access_token: Optional[str] = Cookie(None)
):
    current_user, redirect = await require_admin(request, db, access_token)
    if redirect:
        return redirect
    
    per_page = 10
    users, total_pages = await crud.get_users_paginated(db, page, per_page)
    
    return admin_templates.TemplateResponse(
        "user_management.html",
        {
            "request": request,
            "current_user": current_user,
            "users": users,
            "page": page,
            "total_pages": total_pages
        }
    )




@app.post("/admin/users", response_class=HTMLResponse)
async def admin_create_user(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
    db: AsyncSession = Depends(get_db),
    access_token: Optional[str] = Cookie(None)
):
    current_user, redirect = await require_admin(request, db, access_token)
    if redirect:
        return redirect

    # Check if username already exists
    result = await db.execute(select(User).where(User.username == username))
    existing_user = result.scalars().first()
    if existing_user:
        users = await crud.get_users(db)
        return admin_templates.TemplateResponse(
            "user_management.html",
            {
                "request": request,
                "current_user": current_user,
                "users": users,
                "error": "Username already exists"
            }
        )

    # Create new user
    hashed_password = crud.hash_password(password)
    new_user = User(
        username=username,
        password_hash=hashed_password,
        role=role
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return RedirectResponse(url="/admin/users", status_code=status.HTTP_303_SEE_OTHER)







@app.put("/admin/users/manage/{user_id}", response_class=HTMLResponse)
async def admin_update_user(
    request: Request,
    user_id: int,
    username: str = Form(None),
    password: str = Form(None),
    role: str = Form(None),
    db: AsyncSession = Depends(get_db),
    access_token: Optional[str] = Cookie(None)
):
    current_user, redirect = await require_admin(request, db, access_token)
    if redirect:
        return redirect

    # Get pagination parameters
    page = int(request.query_params.get("page", 1))
    per_page = 10
    
    # Get the user to update
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    
    if not user:
        users, total_pages = await crud.get_users_paginated(db, page, per_page)
        return admin_templates.TemplateResponse(
            "user_management.html",
            {
                "request": request,
                "current_user": current_user,
                "users": users,
                "page": page,
                "total_pages": total_pages,
                "error": "User not found"
            }
        )

    # Update fields if provided
    if username:
        # Check if new username is already taken by another user
        result = await db.execute(select(User).where(User.username == username, User.id != user_id))
        existing_user = result.scalars().first()
        if existing_user:
            users, total_pages = await crud.get_users_paginated(db, page, per_page)
            return admin_templates.TemplateResponse(
                "user_management.html",
                {
                    "request": request,
                    "current_user": current_user,
                    "users": users,
                    "page": page,
                    "total_pages": total_pages,
                    "error": "Username already taken"
                }
            )
        user.username = username
    
    if password:
        user.password_hash = crud.hash_password(password)
    
    if role:
        user.role = role

    await db.commit()
    await db.refresh(user)

    users, total_pages = await crud.get_users_paginated(db, page, per_page)
    return admin_templates.TemplateResponse(
        "user_management.html",
        {
            "request": request,
            "current_user": current_user,
            "users": users,
            "page": page,
            "total_pages": total_pages,
            "success": "User updated successfully!"
        }
    )






@app.delete("/admin/users/{user_id}", response_class=HTMLResponse)
async def admin_delete_user(
    request: Request,
    user_id: int,
    db: AsyncSession = Depends(get_db),
    access_token: Optional[str] = Cookie(None)
):
    current_user, redirect = await require_admin(request, db, access_token)
    if redirect:
        return redirect

    # Get the user to delete
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    
    if not user:
        users = await crud.get_users(db)
        return admin_templates.TemplateResponse(
            "user_management.html",
            {
                "request": request,
                "current_user": current_user,
                "users": users,
                "error": "User not found"
            }
        )

    # Prevent self-deletion
    # Prevent self-deletion
    if user.id == current_user.id:
        users = await crud.get_users(db)
        return admin_templates.TemplateResponse(
            "user_management.html",
            {
                "request": request,
                "current_user": current_user,
                "users": users,
                "error": "Cannot delete your own account"
            }
        )


    await db.delete(user)
    await db.commit()

    return RedirectResponse(url="/admin/users", status_code=status.HTTP_303_SEE_OTHER)



# ------------------------------------------------ CURRENT USER HELPER --------------------------------------------- #



async def require_receptionist(request, db, access_token):
    current_user = await get_current_user(request=request, db=db, access_token=access_token)
    if not current_user:
        return None, RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    if current_user["role"] != "receptionist":
        raise HTTPException(status_code=403, detail="Access forbidden")

    return current_user, None










async def require_admin(request: Request, db: AsyncSession, access_token: Optional[str]):
    if not access_token:
        return None, RedirectResponse(url="/login", status_code=302)

    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")

        if username is None or role != "admin":
            return None, RedirectResponse(url="/login", status_code=302)

    except JWTError:
        return None, RedirectResponse(url="/login", status_code=302)

    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    if not user:
        return None, RedirectResponse(url="/login", status_code=302)

    return user, None




#================================================================ ADMIN DASHBOARD ===============================================================








@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    db: AsyncSession = Depends(get_db),
    access_token: Optional[str] = Cookie(None)
):
    current_user, redirect = await require_admin(request, db, access_token)

    if redirect:
        return redirect  # ❌ Agar token missing/invalid hai to login bhej do

    today_visitors = await crud.count_today_visitors(db)
    recent_visitors = await crud.get_recent_visitors(db, limit=10)



    # Count total visitors
    result = await db.execute(sa.select(func.count(Visitor.id)))
    total_visitors = result.scalar()

    # ---------------- Future visitors --------------------------
    current_day = datetime.now().date()  # today’s date only



    query_future = await db.execute(
        sa.select(Visitor)
        .where(func.date(Visitor.check_in_time) > current_day)   # ✅ only future visitors
        .order_by(Visitor.check_in_time.asc())                   # nearest upcoming first
    )
    future_visitors = query_future.scalars().all()

    # ✅ get count
    apointment_visitors = len(future_visitors)


    return admin_templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "current_user": current_user,
            "today_visitors": today_visitors,
            "total_visitors":total_visitors,
            "apointment_visitors":apointment_visitors,
            "recent_visitors": recent_visitors,
        }
    )





@app.get("/admin/visitors/all", response_class=HTMLResponse)
async def admin_all_visitors(
    request: Request,
    db: AsyncSession = Depends(get_db),
    access_token: Optional[str] = Cookie(None),
):
    current_user, redirect = await require_admin(request, db, access_token)
    if redirect:
        return redirect

    # Count total visitors
    result = await db.execute(sa.select(func.count(Visitor.id)))
    total_visitors = result.scalar()
    

    # Pagination
    # offset = (page - 1) * per_page
    query = await db.execute(
          sa.select(Visitor).order_by(Visitor.check_in_time.desc())

    )
    visitors = query.scalars().all()


    return admin_templates.TemplateResponse(
        "visitor.html",
        {
            "request": request,
            "current_user": current_user,
            "all_visitors": visitors,
            # "page": page,
            # "total_pages": total_pages,
            # "per_page": per_page,
            "current_date": datetime.utcnow().strftime("%A, %B %d, %Y"),
            "current_time": datetime.utcnow().strftime("%H:%M:%S"),
        },
    )



# from sqlalchemy import select, func
# from sqlalchemy.ext.asyncio import AsyncSession
# from fastapi import Request, Depends, Cookie
# from fastapi.responses import HTMLResponse
# from datetime import datetime
# import sqlalchemy as sa

# @app.get("/admin/visitors/future-visitor", response_class=HTMLResponse)
# async def future_visitors(
#     request: Request,
#     db: AsyncSession = Depends(get_db),
#     access_token: Optional[str] = Cookie(None),
# ):
#     # ✅ Admin auth check
#     current_user, redirect = await require_admin(request, db, access_token)
#     if redirect:
#         return redirect

#     # ✅ Current datetime (IST)
#     current_time = datetime.now(IST).replace(tzinfo=None)

#     # ---------------- Future visitors (strictly after now) ----------------
#     query_future = await db.execute(
#         sa.select(Visitor)
#         .where(Visitor.check_in_time > current_time)
#         .order_by(Visitor.check_in_time.asc())
#     )
#     future_visitors = query_future.scalars().all()

#     # ---------------- Format future visitors data ----------------
#     future_visitors_data = []
#     for visitor in future_visitors:
#         future_visitors_data.append({
#             "id": visitor.id,
#             "name": visitor.name,
#             "initials": get_initials(visitor.name),
#             "phone": visitor.phone,
#             "host": visitor.host,
#             "purpose": visitor.purpose,
#             "city": visitor.city,
#             "state": visitor.state,
#             "check_in_time": visitor.check_in_time.strftime("%d %b %Y, %I:%M %p"),
#             "check_in_time_raw": visitor.check_in_time.isoformat(),
#             "status": visitor.status,
#         })

#     # ---------------- Count total visitors ----------------
#     total_visitors_result = await db.execute(sa.select(func.count(Visitor.id)))
#     total_visitors = total_visitors_result.scalar()

#     # ---------------- Current date/time for frontend ----------------
#     now_display = datetime.now(IST)
#     current_date_display = now_display.strftime("%A, %B %d, %Y")
#     current_time_display = now_display.strftime("%H:%M:%S")

#     flashed_messages = get_flashed_messages(request, with_categories=True)
#     appointment_visitors = len(future_visitors_data)

#     return admin_templates.TemplateResponse(
#         "future.html",
#         {
#             "request": request,
#             "current_user": current_user,
#             "total_visitors": total_visitors,
#             "future_visitors": future_visitors_data,
#             "apointment_visitors": appointment_visitors,
#             "current_date": current_date_display,
#             "current_time": current_time_display,
#             "flashed_messages": flashed_messages,
#         },
#     )

# --------------------------------- WebSocket for real-time updates --------------------------------


# # WebSocket manager for broadcasting messages
# class WebSocketManager:
#     def __init__(self):
#         self.active_connections: list[WebSocket] = []

#     async def connect(self, websocket: WebSocket):
#         await websocket.accept()
#         self.active_connections.append(websocket)

#     def disconnect(self, websocket: WebSocket):
#         if websocket in self.active_connections:
#             self.active_connections.remove(websocket)

#     async def broadcast(self, message: str):
#         for connection in self.active_connections:
#             try:
#                 await connection.send_text(message)
#             except Exception:
#                 self.disconnect(connection)

# manager = WebSocketManager()



# @app.websocket("/ws/receptionist")
# async def receptionist_ws(websocket: WebSocket):
#     await manager.connect(websocket)
#     try:
#         while True:
#             data = await websocket.receive_text()  # receptionist can also send messages if needed
#     except WebSocketDisconnect:
#         manager.disconnect(websocket)



# @app.post("/admin/notify-early-meeting/{visitor_id}")
# async def notify_receptionist_ws(
#     visitor_id: int,
#     db: AsyncSession = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     visitor = await db.get(Visitor, visitor_id)
#     if not visitor:
#         raise HTTPException(status_code=404, detail="Visitor not found")

#     message = f"Admin {current_user.username} requested early meeting for {visitor.name} ({visitor.phone})"

#     # Broadcast message to receptionist WebSocket(s)
#     await manager.broadcast(message)

#     return {"detail": "Notification sent"}

# ------------------- WebSocket Manager -------------------
class WebSocketManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                self.disconnect(connection)

manager = WebSocketManager()


# ------------------- Receptionist WebSocket -------------------
@app.websocket("/ws/receptionist")
async def receptionist_ws(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()  # receptionist can also send messages if needed
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# ------------------- Early Meeting Notification -------------------
@app.post("/admin/notify-early-meeting/{visitor_id}")
async def notify_receptionist_ws(
    visitor_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)  # returns dict
):
    visitor = await db.get(Visitor, visitor_id)
    if not visitor:
        raise HTTPException(status_code=404, detail="Visitor not found")

    # Fix here: use dictionary access
    # message = f"Admin {current_user['username']} requested early meeting for {visitor.name} ({visitor.phone})"

    message = f"Admin  requested early meeting for {visitor.name} ({visitor.phone})"


    # Broadcast message to receptionist WebSocket(s)
    await manager.broadcast(message)

    return {"detail": "Notification sent"}





# @app.get("/admin/visitors/future-visitor", response_class=HTMLResponse)
# async def receptionist_all_visitors(
#     request: Request,
#     db: AsyncSession = Depends(get_db),
#     access_token: Optional[str] = Cookie(None),
# ):
#     # ✅ Admin auth check
#     current_user, redirect = await require_admin(request, db, access_token)
#     if redirect:
#         return redirect

#     # ✅ Current IST time
#     current_time = datetime.now(IST).replace(tzinfo=None)
#     print("Current Time (IST):", current_time)

#     # ---------------- Future visitors (after now) ----------------
#     query_future = await db.execute(
#         sa.select(Visitor)
#         .where(Visitor.check_in_time > current_time)   # strictly future
#         .order_by(Visitor.check_in_time.asc())
#     )
#     future_visitors = query_future.scalars().all()

#     # Print raw future visitors from DB
#     print("Future Visitors from DB:")
#     for visitor in future_visitors:
#         print({
#             "id": visitor.id,
#             "name": visitor.name,
#             "phone": visitor.phone,
#             "host": visitor.host,
#             "purpose": visitor.purpose,
#             "city": visitor.city,
#             "state": visitor.state,
#             "check_in_time": visitor.check_in_time
#         })

#     # ---------------- Masked future visitors for template ----------------
#     future_visitors_data = []
#     for visitor in future_visitors:
#         only_date = visitor.check_in_time.strftime("%d %b %Y, %I:%M %p")
#         future_visitors_data.append({
#             "id": visitor.id,
#             "name": visitor.name,
#             "initials": get_initials(visitor.name),
#             "phone": visitor.phone,
#             "host": visitor.host,
#             "purpose": visitor.purpose,
#             "city": visitor.city,
#             "state": visitor.state,
#             "check_in_time": only_date,
#             "check_in_time_raw": visitor.check_in_time.isoformat(),
#         })

#     # ---------------- Other info ----------------
#     result = await db.execute(sa.select(func.count(Visitor.id)))
#     total_visitors = result.scalar()
#     flashed_messages = get_flashed_messages(request, with_categories=True)
#     current_display_time = datetime.now(IST)
#     current_date_display = current_display_time.strftime("%A, %B %d, %Y")
#     current_time_display = current_display_time.strftime("%H:%M:%S")
#     appointment_visitors = len(future_visitors)

#     print("Total visitors in DB:", total_visitors)
#     print("Number of future appointments:", appointment_visitors)

#     return admin_templates.TemplateResponse(
#         "future.html",
#         {
#             "request": request,
#             "current_user": current_user,
#             "total_visitors": total_visitors,
#             "future_visitors": future_visitors_data,
#             "apointment_visitors": appointment_visitors,
#             "current_date": current_date_display,
#             "current_time": current_time_display,
#             "flashed_messages": flashed_messages,
#         },
#     )




# ------------------- Scheduled Visitors -------------------
@app.get("/admin/visitors/future-visitor", response_class=HTMLResponse)
async def future_visitors_page(
    request: Request,
    db: AsyncSession = Depends(get_db),
    access_token: Optional[str] = Cookie(None)
):
    current_user, redirect = await require_admin(request, db, access_token)
    if redirect:
        return redirect

    now = datetime.now(IST).replace(tzinfo=None)
    query = await db.execute(select(Visitor).where(Visitor.check_in_time > now).order_by(Visitor.check_in_time.asc()))
    future_visitors = query.scalars().all()

    future_visitors_data = [
        {
            "id": v.id,
            "name": v.name,
            "initials": "".join([x[0] for x in v.name.split()]) if v.name else "",
            "phone": v.phone,
            "host": v.host,
            "purpose": v.purpose,
            "city": v.city,
            "state": v.state,
            "check_in_time": v.check_in_time.strftime("%d %b %Y, %I:%M %p"),
            "check_in_time_raw": v.check_in_time.isoformat()
        }
        for v in future_visitors
    ]

    flashed_messages = []  # implement your flash logic
    current_display_time = datetime.now(IST)
    current_date_display = current_display_time.strftime("%A, %B %d, %Y")
    current_time_display = current_display_time.strftime("%H:%M:%S")

    return admin_templates.TemplateResponse(
        "future.html",
        {
            "request": request,
            "current_user": current_user,
            "future_visitors": future_visitors_data,
            "current_date": current_date_display,
            "current_time": current_time_display,
            "flashed_messages": flashed_messages,
        },
    )




#===============================================RECEPTIONIST DASHBOARD ==============================================================


@app.get("/receptionist/dashboard", response_class=HTMLResponse)
async def receptionist_dashboard(
    request: Request,
    db: AsyncSession = Depends(get_db),
    access_token: Optional[str] = Cookie(None)
):
    # Receptionist auth
    current_user, redirect = await require_receptionist(request, db, access_token)
    if redirect:
        return redirect

    # Today's visitors (custom CRUD)
    today_visitors = await crud.count_today_visitors(db)

    # Recent visitors (latest 10)
    recent_visitors = await crud.get_recent_visitors(db, limit=10)


    # Count total visitors
    result = await db.execute(sa.select(func.count(Visitor.id)))
    total_visitors = result.scalar()

    # ---------------- Future visitors --------------------------
    current_day = datetime.now().date()  # today’s date only

    query_future = await db.execute(
        sa.select(Visitor)
        .where(func.date(Visitor.check_in_time) > current_day)   # ✅ only future visitors
        .order_by(Visitor.check_in_time.asc())                   # nearest upcoming first
    )
    future_visitors = query_future.scalars().all()

    # ✅ get count
    apointment_visitors = len(future_visitors)

    print("Future visitors count:", apointment_visitors)


# ---------------- Masked recent visitors --------------------------
    masked_visitors = []
    for v in recent_visitors:
        masked_visitors.append({
        "id": v.id,
            "masked_name": mask_name(v.name),
            "masked_phone": mask_phone(v.phone),
            "host": v.host,
            "purpose": v.purpose,
            "city": v.city,
            "state": v.state,
            "check_in_time": v.check_in_time.strftime("%d-%m-%Y %H:%M") if v.check_in_time else "",
            "check_out_time": v.check_out_time.strftime("%d-%m-%Y %H:%M") if v.check_out_time else ""
        })



    print(masked_visitors)
    # ---------------- Render template --------------------------
    return reception_templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "current_user": current_user,
            "today_visitors": today_visitors,        # visitors checked-in today
            "total_visitors": total_visitors,        # total visitor count (int)
            "apointment_visitors": apointment_visitors,  # future visitors count (int)
            "recent_visitors": masked_visitors,      # recent masked visitors
        }
    )




# ========================================== RECEPTIONIST VISITOR ENDPOINTS ===============================================








@app.post("/checkout/{visitor_id}")
async def checkout_visitor(visitor_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Visitor).where(Visitor.id == visitor_id))
    visitor = result.scalars().first()

    if not visitor:
        raise HTTPException(status_code=404, detail="Visitor not found")

    if visitor.check_out_time:  # already checked out
        raise HTTPException(status_code=400, detail="Visitor already checked out")

    visitor.check_out_time = datetime.now()
    visitor.status = "checked_out"

    await db.commit()
    await db.refresh(visitor)

    return {
        "message": "Visitor checked out successfully",
        "check_out_time": visitor.check_out_time.strftime("%d-%b-%Y %I:%M %p")
    }



# @app.post("/checkout/{visitor_id}")
# async def checkout_visitor(visitor_id: int, db: AsyncSession = Depends(get_db)):
#     result = await db.execute(select(Visitor).where(Visitor.id == visitor_id))
#     visitor = result.scalars().first()

#     if not visitor:
#         raise HTTPException(status_code=404, detail="Visitor not found")

#     # 🚨 Prevent checkout if future visitor
#     if visitor.check_in_time and visitor.check_in_time > datetime.utcnow():
#         raise HTTPException(
#             status_code=400,
#             detail="Future visitor cannot be checked out"
#         )

#     if visitor.check_out_time:  # already checked out
#         raise HTTPException(status_code=400, detail="Visitor already checked out")

#     visitor.check_out_time = datetime.utcnow()
#     # optional: add status field if you maintain
#     # visitor.status = "checked_out"

#     await db.commit()
#     await db.refresh(visitor)

#     return {
#         "message": "Visitor checked out successfully",
#         "check_out_time": visitor.check_out_time.strftime("%d-%b-%Y %I:%M %p")
#     }







# @app.get("/receptionist/visitors/all", response_class=HTMLResponse)
# async def receptionist_all_visitors(
#     request: Request,
#     db: AsyncSession = Depends(get_db),
#     access_token: Optional[str] = Cookie(None),
# ):
#     # Receptionist auth check
#     current_user, redirect = await require_receptionist(request, db, access_token)
#     if redirect:
#         return redirect

#     # Count total visitors
#     result = await db.execute(sa.select(func.count(Visitor.id)))
#     total_visitors = result.scalar()

#     # # Fetch all past + current visitors (newest first)
#     # query = await db.execute(
#     #     sa.select(Visitor).order_by(Visitor.check_in_time.desc())
#     # )
#     # visitors = query.scalars().all()


#     # ---------------- Visitors till today (past + current) ----------------
#     current_day = datetime.now().date()

#     query_visitors = await db.execute(
#         sa.select(Visitor)
#         .where(func.date(Visitor.check_in_time) <= current_day)   # ✅ today + past
#         .order_by(Visitor.check_in_time.desc())
#     )
#     visitors = query_visitors.scalars().all()

#     # ---------------- Future visitors --------------------------
#     # current_day = datetime.now().date()

#     query_future = await db.execute(
#         sa.select(Visitor)
#         .where(func.date(Visitor.check_in_time) > current_day)   # ✅ only future
#         .order_by(Visitor.check_in_time.asc())
#     )
#     future_visitors = query_future.scalars().all()

#     print("9999999999999999999999999999999--------------------------==> ",  future_visitors)



#     # ---------------- Masked past/current visitors ----------------
#     visitors_data = []
#     if visitors:
#         for visitor in visitors:
#             if visitor.check_in_time:
#                 check_in_time_formatted = visitor.check_in_time.strftime("%d %b %Y, %I:%M %p")
#                 check_out_time_formatted = (
#                     visitor.check_out_time.strftime("%d %b %Y, %I:%M %p") 
#                     if visitor.check_out_time else ""
#                 )

#                 visitors_data.append({
#                     "id": visitor.id,
#                     "masked_name": mask_name(visitor.name),
#                     "initials": get_initials(visitor.name),
#                     "masked_phone": mask_phone(visitor.phone),
#                     "host": visitor.host,
#                     "city": visitor.city,
#                     "state": visitor.state,
#                     "purpose": visitor.purpose,  # ✅ added
#                     "check_in_time": check_in_time_formatted,
#                     "check_out_time": check_out_time_formatted,
#                     "status": visitor.status,
#                     "check_in_time_raw": visitor.check_in_time.isoformat(),
#                     "check_out_time_raw": visitor.check_out_time.isoformat() if visitor.check_out_time else None,
#                 })

#     future_visitors_data = []
#     if future_visitors is not None:
#         for visitor in future_visitors:
#             only_date = visitor.check_in_time.strftime("%d %b %Y")
#             future_visitors_data.append({
#                 "id": visitor.id,
#                 "masked_name": mask_name(visitor.name),
#                 "initials": get_initials(visitor.name),
#                 "masked_phone": mask_phone(visitor.phone),
#                 "host": visitor.host,
#                 "purpose": visitor.purpose,  # ✅ added
#                 "city": visitor.city,
#                 "state": visitor.state,
#                 "check_in_time": only_date,
#                 "check_in_time_raw": visitor.check_in_time.isoformat(),
#             })

#         print(future_visitors_data)
    

#     # ---------------- Date/time + messages ----------------
#     current_time = datetime.now()
#     current_date_display = current_time.strftime("%A, %B %d, %Y")
#     current_time_display = current_time.strftime("%H:%M:%S")
#     flashed_messages = get_flashed_messages(request, with_categories=True)

#     appointment_visitors = len(future_visitors)

#     return reception_templates.TemplateResponse(
#         "visitor.html",
#         {
#             "request": request,
#             "current_user": current_user,
#             "all_visitors": visitors_data,
#             "total_visitors": total_visitors,
#             "future_visitors": future_visitors_data,
#             "apointment_visitors": appointment_visitors,
#             "current_date": current_date_display,
#             "current_time": current_time_display,
#             "flashed_messages": flashed_messages,
#         },
#     )



@app.get("/receptionist/visitors/all", response_class=HTMLResponse)
async def receptionist_all_visitors(
    request: Request,
    db: AsyncSession = Depends(get_db),
    access_token: Optional[str] = Cookie(None),
):
    # ✅ Receptionist auth check
    current_user, redirect = await require_receptionist(request, db, access_token)
    if redirect:
        return redirect

    # ✅ Auto-update scheduled → checked_in if check_in_time <= now
    current_time = datetime.now(IST).replace(tzinfo=None)
    await db.execute(
        sa.update(Visitor)
        .where(
            Visitor.status == "scheduled",
            Visitor.check_in_time <= current_time
        )
        .values(status="checked_in")
    )
    await db.commit()

    # ✅ Count total visitors
    result = await db.execute(sa.select(func.count(Visitor.id)))
    total_visitors = result.scalar()

    # ---------------- Visitors till now (past + current) ----------------
    query_visitors = await db.execute(
        sa.select(Visitor)
        .where(Visitor.check_in_time <= current_time)   # ✅ pure datetime compare
        .order_by(Visitor.check_in_time.desc())
    )
    visitors = query_visitors.scalars().all()

    # ---------------- Future visitors (strictly after now) ----------------
    query_future = await db.execute(
        sa.select(Visitor)
        .where(Visitor.check_in_time > current_time)   # ✅ strictly future
        .order_by(Visitor.check_in_time.asc())
    )
    future_visitors = query_future.scalars().all()

    # ---------------- Masked past/current visitors ----------------
    visitors_data = []
    if visitors:
        for visitor in visitors:
            if visitor.check_in_time:
                check_in_time_formatted = visitor.check_in_time.strftime("%d %b %Y, %I:%M %p")
                check_out_time_formatted = (
                    visitor.check_out_time.strftime("%d %b %Y, %I:%M %p") 
                    if visitor.check_out_time else ""
                )

                visitors_data.append({
                    "id": visitor.id,
                    "masked_name": mask_name(visitor.name),
                    "initials": get_initials(visitor.name),
                    "masked_phone": mask_phone(visitor.phone),
                    "host": visitor.host,
                    "city": visitor.city,
                    "state": visitor.state,
                    "purpose": visitor.purpose,
                    "check_in_time": check_in_time_formatted,
                    "check_out_time": check_out_time_formatted,
                    "status": visitor.status,
                    "check_in_time_raw": visitor.check_in_time.isoformat(),
                    "check_out_time_raw": visitor.check_out_time.isoformat() if visitor.check_out_time else None,
                })

    # ---------------- Masked future visitors ----------------
    future_visitors_data = []
    if future_visitors:
        for visitor in future_visitors:
            only_date = visitor.check_in_time.strftime("%d %b %Y, %I:%M %p")
            future_visitors_data.append({
                "id": visitor.id,
                "masked_name": mask_name(visitor.name),
                "initials": get_initials(visitor.name),
                "masked_phone": mask_phone(visitor.phone),
                "host": visitor.host,
                "purpose": visitor.purpose,
                "city": visitor.city,
                "state": visitor.state,
                "check_in_time": only_date,
                "check_in_time_raw": visitor.check_in_time.isoformat(),
            })

    # ---------------- Date/time + messages ----------------
    current_display_time = datetime.now(IST)  # ✅ use IST for consistency
    current_date_display = current_display_time.strftime("%A, %B %d, %Y")
    current_time_display = current_display_time.strftime("%H:%M:%S")
    flashed_messages = get_flashed_messages(request, with_categories=True)

    appointment_visitors = len(future_visitors)

    return reception_templates.TemplateResponse(
        "visitor.html",
        {
            "request": request,
            "current_user": current_user,
            "all_visitors": visitors_data,
            "total_visitors": total_visitors,
            "future_visitors": future_visitors_data,
            "apointment_visitors": appointment_visitors,
            "current_date": current_date_display,
            "current_time": current_time_display,
            "flashed_messages": flashed_messages,
        },
    )







# @app.post("/receptionist/visitors/check-in", response_class=HTMLResponse)
# async def receptionist_check_in_submit(
#     request: Request,
#     name: str = Form(...),
#     phone: str = Form(...),
#     otp: str = Form(...),
#     date: str = Form(...),
#     time: str = Form(...),
#     host: str = Form(...),
#     purpose: str = Form(...),
#     city: str = Form(None),
#     state:str = Form(None),
#     db: AsyncSession = Depends(get_db),
#     access_token: Optional[str] = Cookie(None),
# ):
#     # ✅ Receptionist auth check
#     current_user, redirect = await require_receptionist(request, db, access_token)
#     if redirect:
#         return redirect

#     # ✅ OTP Required Check
#     if not otp or otp.strip() == "":
#         flash(request, "OTP is required before check-in!", "danger")
#         return RedirectResponse(url="/receptionist/visitors/all", status_code=303)
#     try:
#         otp_int = int(otp)
#     except ValueError:
#         flash(request, "OTP must be a number!", "danger")
#         return RedirectResponse(url="/receptionist/visitors/all", status_code=303)

#     otp_record = await db.execute(
#         select(OTP)
#         .join(Visitor)
#         .where(Visitor.phone == (phone), OTP.otp_code == str(otp_int))   # ✅ int compare
#     )

#     otp_row = otp_record.scalar_one_or_none()

#     if not otp_row:
#         flash(request, "Invalid OTP! Please try again.", "danger")
#         return RedirectResponse(url="/receptionist/visitors/all", status_code=303)

#     # ✅ Parse date and time
#     if date.strip() and time.strip():
#         try:
#             check_in_time = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
#         except ValueError:
#             check_in_time = datetime.now(IST)
#     else:
#         check_in_time = datetime.now(IST)

#     check_in_time = check_in_time.replace(tzinfo=None)

#     print("came to store")

#     # ✅ Create new visitor only if OTP is valid
#     new_visitor = Visitor(
#         name=name,
#         phone=phone,
#         host=host,
#         purpose=purpose,
#         city =city,
#         state =state,
#         check_in_time=check_in_time,
#         # status="checked_in",   # ✅ Default
#         status="scheduled" if check_in_time.date() > datetime.now().date() else "checked_in",
#         created_by=current_user["id"],
#     )

#     db.add(new_visitor)
#     await db.commit()
#     await db.refresh(new_visitor)

#     print("visitor stored")
#     # ✅ Success
#     flash(request, f"Visitor {name} checked in successfully!", "success")
#     return RedirectResponse(url="/receptionist/visitors/all", status_code=303)


@app.post("/receptionist/visitors/check-in", response_class=HTMLResponse)
async def receptionist_check_in_submit(
    request: Request,
    name: str = Form(...),
    phone: str = Form(...),
    otp: str = Form(...),
    date: str = Form(...),
    time: str = Form(...),
    host: str = Form(...),
    purpose: str = Form(...),
    city: str = Form(None),
    state: str = Form(None),
    db: AsyncSession = Depends(get_db),
    access_token: Optional[str] = Cookie(None),
):
    # ✅ Receptionist auth check
    current_user, redirect = await require_receptionist(request, db, access_token)
    if redirect:
        return redirect

    # ✅ OTP Required Check
    if not otp or otp.strip() == "":
        flash(request, "OTP is required before check-in!", "danger")
        return RedirectResponse(url="/receptionist/visitors/all", status_code=303)
    try:
        otp_int = int(otp)
    except ValueError:
        flash(request, "OTP must be a number!", "danger")
        return RedirectResponse(url="/receptionist/visitors/all", status_code=303)

    # ✅ Find OTP (handle visitor_id=None case)
    otp_record = await db.execute(
        select(OTP)
        .outerjoin(Visitor)
        .where(
            OTP.otp_code == str(otp_int),
            ((Visitor.phone == phone) | (OTP.visitor_id.is_(None))),
            OTP.is_verified == True  # ✅ Only allow verified OTP
            
        )
    )
    otp_row = otp_record.scalar_one_or_none()

    if not otp_row:
        flash(request, "Invalid OTP! Please try again.", "danger")
        return RedirectResponse(url="/receptionist/visitors/all", status_code=303)

    # ✅ Consume OTP (delete after use)
    await db.delete(otp_row)
    await db.commit()

    # ✅ Parse date and time
    if date.strip() and time.strip():
        try:
            check_in_time = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        except ValueError:
            check_in_time = datetime.now(IST)
    else:
        check_in_time = datetime.now(IST)
    check_in_time = check_in_time.replace(tzinfo=None)

    print("came to store")

    # ✅ Create new visitor
    new_visitor = Visitor(
        name=name,
        phone=phone,
        host=host,
        purpose=purpose,
        city=city,
        state=state,
        check_in_time=check_in_time,
        status="scheduled" if check_in_time.date() > datetime.now().date() else "checked_in",
        created_by=current_user["id"],
    )

    db.add(new_visitor)
    await db.commit()
    await db.refresh(new_visitor)

    print("visitor stored")
    # ✅ Success message
    flash(request, f"Visitor {name} checked in successfully!", "success")
    return RedirectResponse(url="/receptionist/visitors/all", status_code=303)




# ------------------- Apoint ment time changement ------------------








@app.get("/receptionist/visitors/edit/{visitor_id}", response_class=HTMLResponse)
async def edit_future_visitor_form(
    request: Request,
    visitor_id: int,
    db: AsyncSession = Depends(get_db),
    access_token: Optional[str] = None
):
    # Receptionist auth
    current_user, redirect = await require_receptionist(request, db, access_token)
    if redirect:
        return redirect

    # Visitor fetch
    result = await db.execute(select(Visitor).where(Visitor.id == visitor_id))
    visitor = result.scalar_one_or_none()
    if not visitor:
        return RedirectResponse("/receptionist/visitors/all", status_code=303)

    # Pre-fill date and time
    date_str = visitor.check_in_time.strftime("%Y-%m-%d") if visitor.check_in_time else ""
    time_str = visitor.check_in_time.strftime("%H:%M") if visitor.check_in_time else ""

    return reception_templates.TemplateResponse(
        "edit_future_visitor.html",
        {
            "request": request,
            "visitor": visitor,
            "date_str": date_str,
            "time_str": time_str,
            "current_user": current_user
        }
    )


# @app.post("/receptionist/visitors/edit/{visitor_id}", response_class=HTMLResponse)
# async def edit_future_visitor_submit(
#     request: Request,
#     visitor_id: int,
#     date: str = Form(...),
#     time: str = Form(...),
#     db: AsyncSession = Depends(get_db),
#     access_token: Optional[str] = Cookie(None),
# ):
#     current_user, redirect = await require_receptionist(request, db, access_token)
#     if redirect:
#         return redirect

#     # Fetch visitor
#     result = await db.execute(select(Visitor).where(Visitor.id == visitor_id))
#     visitor = result.scalar_one_or_none()
#     if not visitor:
#         return RedirectResponse("/receptionist/visitors/all", status_code=303)

#     # Update time
#     try:
#         new_time = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
#     except ValueError:
#         new_time = datetime.now()

#     visitor.check_in_time = new_time

#     db.add(visitor)
#     await db.commit()
#     await db.refresh(visitor)

#     # Flash message (optional)
#     from starlette.middleware.sessions import flash
#     flash(request, f"Appointment updated successfully for {visitor.name}", "success")

#     return RedirectResponse("/receptionist/visitors/all", status_code=303)




from fastapi.responses import JSONResponse

@app.post("/receptionist/visitors/update/{visitor_id}")
async def update_visitor_ajax(
    visitor_id: int,
    date: str = Form(...),
    time: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Visitor).where(Visitor.id == visitor_id))
    visitor = result.scalar_one_or_none()
    if not visitor:
        return JSONResponse({"error": "Visitor not found"}, status_code=404)

    from datetime import datetime
    visitor.check_in_time = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")

    await db.commit()
    await db.refresh(visitor)

    # Return updated fields to render in table
    return JSONResponse({
        "id": visitor.id,
        "date": visitor.check_in_time.strftime("%Y-%m-%d"),
        "time": visitor.check_in_time.strftime("%H:%M")
    })

# ----------------------------------  SMS OTP ----------------------------------------

# @app.post("/sms/send")
# async def send_sms(payload: SMSRequest, settings: Settings = Depends(get_settings)):
#     return await _send_to_gateway(payload, settings)



# @app.post("/sms/send")
# async def send_sms(
#     payload: SMSRequest,
#     db: AsyncSession = Depends(get_db),
#     settings:Settings = Depends(get_settings)
# ):
    

#     print("payload is",payload)
#     # ✅ Find visitor either by visitor_id OR fallback to phone
#     if payload.visitor_id:
#         result = await db.execute(
#             sa.select(Visitor).where(Visitor.id == payload.visitor_id)
#         )
#         visitor_obj = result.scalar_one_or_none()
#     else:

#         # create a new visitor

#         visitor_obj = Visitor(
#            phone=payload.mobile
#         )
#         db.add(visitor_obj)
#         await db.commit()
#         await db.refresh(visitor_obj)

#         # result = await db.execute(
#         #     sa.select(Visitor)
#         #     .where(Visitor.phone == payload.mobile)
#         #     .order_by(Visitor.check_in_time.desc())  # latest record
#         #     .limit(1)
#         # )
#         # visitor_obj = result.scalar_one_or_none()
#     # print("visitor object is",visitor_obj)

#     if not visitor_obj:
#         raise HTTPException(status_code=404, detail="Visitor not found")

#     # ✅ Generate and save OTP
#     otp = await generate_and_store_otp(db, visitor_obj)

#     # ✅ Construct SMS text (append OTP if required)
#     sms_text = f"{payload.msg}. Your OTP is {otp}"

#     print(payload,type(payload))

#     # ✅ Send SMS via gateway (your utility)
#     # gateway_payload = {
#     #     "mobile": payload.mobile,
#     #     "msg": sms_text,
#     #     "senderid": payload.senderid if payload.senderid else "ODHGRP",
#     #     "msgType": payload.msgType,
#     #     "sendMethod": payload.sendMethod,
#     # }

#     await _send_to_gateway(payload, settings, db, visitor_obj)

#     return {"ok": True, "message": "OTP sent successfully"}





# @app.post("/sms/send")
# async def send_sms(
#     payload: SMSRequest,
#     db: AsyncSession = Depends(get_db),
#     settings: Settings = Depends(get_settings)
# ):
#     # ✅ Find latest visitor by phone
#     result = await db.execute(
#         sa.select(Visitor)
#         .where(Visitor.phone == payload.mobile)
#         .order_by(Visitor.check_in_time.desc())
#         .limit(1)
#     )
#     visitor_obj = result.scalar_one_or_none()

#     # ✅ If no visitor exists, we can still send OTP using mobile
#     if not visitor_obj:
#         # Create a temporary object just for _send_to_gateway
#         class TempVisitor:
#             name = None
#             phone = payload.mobile


#     # ✅ Send SMS via gateway
#     await _send_to_gateway(payload, settings, db, visitor_obj)

#     return {"ok": True, "message": "OTP sent successfully"}




@app.post("/sms/send")
async def send_sms(
    payload: SMSRequest,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings)
):
    # ✅ Find latest visitor by phone
    result = await db.execute(
        sa.select(Visitor)
        .where(Visitor.phone == payload.mobile)
        .order_by(Visitor.check_in_time.desc())
        .limit(1)
    )
    visitor_obj = result.scalar_one_or_none()

    # ✅ If no visitor exists, create a temporary object
    if not visitor_obj:
        class TempVisitor:
            name = None
            phone = payload.mobile
        visitor_obj = TempVisitor()  # <-- Assign instance here

    # ✅ Send SMS via gateway
    await _send_to_gateway(payload, settings, db, visitor_obj)

    return {"ok": True, "message": "OTP sent successfully"}



# @app.post("/receptionist/visitors/verify-otp")
# async def verify_visitor_otp(
#     phone: int = Form(...),
#     otp: str = Form(...),
#     db: AsyncSession = Depends(get_db),
# ):
  

#     res=verify_and_delete_otp(db,phone, otp)

#     print("is otp verified",otp,res)
#     if res:
#         return {"ok": True, "message": "OTP verified successfully"}
#     return JSONResponse(content={"ok": False, "message": "OTP verification failed"})


@app.post("/receptionist/visitors/verify-otp")
async def verify_visitor_otp(
    phone: str = Form(...),
    otp: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    res = await verify_otp(db, phone, otp)
    print("is otp verified",otp,res)

    if res:
        return {"ok": True, "message": "OTP verified successfully"}
    return JSONResponse(content={"ok": False, "message": "OTP verification failed"})




# @app.post("/receptionist/visitors/verify-otp")
# async def verify_otp(data: VerifyOtpRequest, db: AsyncSession = Depends(get_db)):
#     # Latest OTP for this phone
#     # result = await db.execute(
#     #     sa.select(OTP)
#     #     .join(OTP.visitor)
#     #     .where(OTP.visitor.has(phone=data.phone))
#     #     .order_by(OTP.created_at.desc())
#     #     .limit(1)
#     # )
#     # otp_record = result.scalar_one_or_none()

#     if not otp_record:
#         return {"ok": False, "message": "No OTP found for this phone."}

#     # Check OTP and expiry (5 min)
#     if otp_record.otp_code != data.otp:
#         return {"ok": False, "message": "Incorrect OTP."}

#     if datetime.datetime.utcnow() - otp_record.created_at > datetime.timedelta(minutes=5):
#         return {"ok": False, "message": "OTP expired."}

#     return {"ok": True, "message": "OTP verified successfully."}


# ========================================== EMPLOYEE ENDPOINTS ===============================================

@app.get("/admin/employees", response_class=HTMLResponse)
async def admin_employees(
    request: Request,
    db: AsyncSession = Depends(get_db),
    access_token: Optional[str] = Cookie(None)
):
    current_user, redirect = await require_admin(request, db, access_token)
    if redirect:
        return redirect

    return admin_templates.TemplateResponse(
        "employee.html",
        {
            "request": request,
            "current_user": current_user,
        }
    )


@app.get("/admin/employees/edit", response_class=HTMLResponse)
async def admin_employees_edit(
    request: Request,
    db: AsyncSession = Depends(get_db),
    access_token: Optional[str] = Cookie(None)
):
    current_user, redirect = await require_admin(request, db, access_token)
    if redirect:
        return redirect

    return admin_templates.TemplateResponse(
        "employee_edit.html",
        {
            "request": request,
            "current_user": current_user,
            "item": {}  # Add employee data here when needed
        }
    )


@app.get("/receptionist/employees", response_class=HTMLResponse)
async def receptionist_employees(
    request: Request,
    db: AsyncSession = Depends(get_db),
    access_token: Optional[str] = Cookie(None)
):
    current_user, redirect = await require_receptionist(request, db, access_token)
    if redirect:
        return redirect

    return reception_templates.TemplateResponse(
        "employee.html",
        {
            "request": request,
            "current_user": current_user,
        }
    )


@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("access_token")
    return response
