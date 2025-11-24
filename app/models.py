# from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
# from sqlalchemy.orm import relationship
# from app.database import Base
# from datetime import datetime
# from sqlalchemy.sql import func


# class User(Base):
#     __tablename__ = "users"

#     id = Column(Integer, primary_key=True, index=True)
#     username = Column(String, unique=True, index=True, nullable=False)
#     password_hash = Column(String, nullable=False)
#     role = Column(String, nullable=False, default="reception")  # "admin" or "reception"
    
#     visitors = relationship("Visitor", back_populates="creator")


# # class Visitor(Base):
# #     __tablename__ = "visitors"

# #     id = Column(Integer, primary_key=True, index=True)
# #     name = Column(String, nullable=False)
# #     company = Column(String, nullable=True)
# #     email = Column(String, nullable=True)
# #     phone = Column(String, nullable=True)
# #     host = Column(String, nullable=True)
# #     purpose = Column(String, nullable=True)
# #     status = Column(String, default="checked-in")
# #     check_in_time = Column(DateTime, default=datetime.utcnow)
# #     check_out_time = Column(DateTime, nullable=True)

# #     created_by = Column(Integer, ForeignKey("users.id"))
# #     creator = relationship("User", back_populates="visitors")








# class Visitor(Base):
#     __tablename__ = "visitors"

#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, nullable=False)
#     company = Column(String)
#     email = Column(String)
#     phone = Column(String)
#     host = Column(String)
#     purpose = Column(String)
#     status = Column(String, default="pending")
#     check_in_time = Column(DateTime(timezone=True), server_default=func.now())
#     check_out_time = Column(DateTime(timezone=True), nullable=True)
#     created_at = Column(DateTime(timezone=True), server_default=func.now())
#     created_by = Column(String, nullable=True)


#     # 👇 Extra helpers for template
#     @property
#     def initials(self):
#         """Get initials from name (e.g., John Doe → JD)."""
#         if not self.name:
#             return ""
#         return "".join([part[0].upper() for part in self.name.split() if part])

#     @property
#     def duration(self):
#         """Get duration of visit (check-out - check-in)."""
#         end_time = self.check_out_time or datetime.utcnow()
#         if not self.check_in_time:
#             return "-"
#         delta = end_time - self.check_in_time
#         minutes = delta.total_seconds() // 60
#         if minutes < 60:
#             return f"{int(minutes)} mins"
#         hours, mins = divmod(int(minutes), 60)
#         return f"{hours}h {mins}m"







from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
from sqlalchemy.sql import func


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False, default="reception")

    visitors = relationship(
        "Visitor",
        back_populates="creator",
        cascade="all, delete"
    )





# class Visitor(Base):
#     __tablename__ = "visitors"

#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String,nullable=True)
#     # company = Column(String, nullable=True)
#     # email = Column(String, nullable=True)
#     phone = Column(String)
#     host = Column(String, nullable=True)
#     purpose = Column(String, nullable=True)
#     # check_in_time = Column(DateTime(timezone=True), server_default=func.now())
#     state = Column(String)
#     city = Column(String)
#     check_in_time = Column(DateTime, server_default=func.now())   # Jab visitor enter karega
#     check_out_time = Column(DateTime, nullable=True)              # Jab visitor niklega (default null)
#     status = Column(String(20), default="checked_in")  
#     # address = Column(String, nullable=True)
#     created_at = Column(DateTime(timezone=True), server_default=func.now())

#     created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
#     creator = relationship("User", back_populates="visitors")



class Visitor(Base):
    __tablename__ = "visitors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    phone = Column(String, nullable=False)
    host = Column(String, nullable=True)
    purpose = Column(String, nullable=True)
    state = Column(String, nullable=True)
    city = Column(String, nullable=True)

    # Appointment / Check-in times
    check_in_time = Column(DateTime, server_default=func.now())   # scheduled ya actual check-in
    check_out_time = Column(DateTime, nullable=True)

    # Status: scheduled, checked_in, checked_out, cancelled
    status = Column(String(20), default="scheduled")

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    creator = relationship("User", back_populates="visitors")



class OTP(Base):
    __tablename__ = "otps"

    id = Column(Integer, primary_key=True, index=True)
    otp_code = Column(String, nullable=False)   # OTP value
    visitor_id = Column(Integer, ForeignKey("visitors.id"), nullable=True)
    is_verified = Column(Boolean, default=False)  # ✅ Add this

    visitor = relationship("Visitor", backref="otps")


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    dob = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    aadhaar_number = Column(String, nullable=True)
    pan_number = Column(String, nullable=True)
    address = Column(String, nullable=True)
    emergency_name = Column(String, nullable=True)
    emergency_relation = Column(String, nullable=True)
    emergency_phone = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    creator = relationship("User")


