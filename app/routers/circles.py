# MARK: - routers/circles.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.circle import Circle, CircleMember
from app.schemas.circle import CircleCreate, CircleResponse, InviteCodeResponse, CircleJoinRequest
from app.services.auth_service import get_current_user
import pyotp
import time

router = APIRouter(prefix="/circles", tags=["Circles"])

# Set the refresh interval to 45 seconds as requested
TOTP_INTERVAL = 45

@router.post("/", response_model=CircleResponse)
def create_circle(
    request: CircleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1. Generate secure, random Base32 secrets for BOTH roles
    member_secret = pyotp.random_base32()
    admin_secret = pyotp.random_base32() # ✅ NEW: Secret for generating admin codes
    
    # 2. Create the Circle
    new_circle = Circle(
        name=request.name,
        admin_id=current_user.id,
        totp_secret=member_secret,
        admin_totp_secret=admin_secret # ✅ Save admin secret
    )
    db.add(new_circle)
    db.commit()
    db.refresh(new_circle)
    
    # 3. Add the creator as the Admin in circle_members
    admin_member = CircleMember(
        circle_id=new_circle.id,
        user_id=current_user.id,
        role="admin"
    )
    db.add(admin_member)
    db.commit()
    
    return new_circle


@router.get("/{circle_id}/invite", response_model=InviteCodeResponse)
def get_invite_code(
    circle_id: str,
    role: str = Query("member", description="Role to invite: 'member' or 'admin'"), # ✅ NEW: Accept role parameter
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1. Ensure the circle exists
    circle = db.query(Circle).filter(Circle.id == circle_id).first()
    if not circle:
        raise HTTPException(status_code=404, detail="Circle not found")
        
    # 2. OPTION 1 APPLIED: Only the admin can generate invite codes
    if str(circle.admin_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Only Circle Admins can generate invite codes")
        
    # 3. Select the correct secret based on the requested role
    if role == "admin":
        # Backward compatibility for old circles created before this feature
        if not circle.admin_totp_secret:
            circle.admin_totp_secret = pyotp.random_base32()
            db.commit()
        secret_to_use = circle.admin_totp_secret
    else:
        secret_to_use = circle.totp_secret
        
    # 4. Generate the current 8-digit code based on the time and the chosen secret
    totp = pyotp.TOTP(secret_to_use, digits=8, interval=TOTP_INTERVAL)
    current_code = totp.now()
    
    # 5. Calculate exactly how many seconds are left before this code dies (for your iOS pie chart)
    current_unix_time = int(time.time())
    expires_in_seconds = TOTP_INTERVAL - (current_unix_time % TOTP_INTERVAL)
    
    return InviteCodeResponse(
        code=current_code,
        expires_in_seconds=expires_in_seconds
    )


@router.post("/join")
def join_circle(
    request: CircleJoinRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # We fetch all circles to check their TOTP against the entered code. 
    all_circles = db.query(Circle).all()
    
    matched_circle = None
    assigned_role = "member"
    
    # ✅ Check BOTH secrets to see which role the code belongs to!
    for circle in all_circles:
        # Check Member Code First
        totp_member = pyotp.TOTP(circle.totp_secret, digits=8, interval=TOTP_INTERVAL)
        if totp_member.verify(request.invite_code, valid_window=1):
            matched_circle = circle
            assigned_role = "member"
            break
            
        # Check Admin Code Second
        if circle.admin_totp_secret:
            totp_admin = pyotp.TOTP(circle.admin_totp_secret, digits=8, interval=TOTP_INTERVAL)
            if totp_admin.verify(request.invite_code, valid_window=1):
                matched_circle = circle
                assigned_role = "admin"
                break
            
    if not matched_circle:
        raise HTTPException(status_code=400, detail="Invalid or expired invite code")
        
    # Check if user is already in the circle
    existing_member = db.query(CircleMember).filter(
        CircleMember.circle_id == matched_circle.id,
        CircleMember.user_id == current_user.id
    ).first()
    
    if existing_member:
        raise HTTPException(status_code=400, detail="You are already a member of this circle")
        
    # Add them to the circle with the correct dynamic role
    new_member = CircleMember(
        circle_id=matched_circle.id,
        user_id=current_user.id,
        role=assigned_role # ✅ Assigns "admin" or "member" automatically!
    )
    db.add(new_member)
    db.commit()
    
    return {"message": f"Successfully joined {matched_circle.name} as an {assigned_role}!"}


@router.get("/", response_model=list[CircleResponse])
def get_my_circles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Find all circles where this user is a member
    my_circles = db.query(Circle).join(CircleMember).filter(
        CircleMember.user_id == current_user.id
    ).all()
    
    return my_circles