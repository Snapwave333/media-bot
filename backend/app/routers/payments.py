from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import stripe
from app.database import get_db
from app.models import User, VideoJob, Payment, SubscriptionStatus
from app.schemas import PaymentIntentCreate, PaymentIntentResponse
from app.auth import get_current_user
from app.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/payments", tags=["Payments"])

stripe.api_key = settings.stripe_secret_key


@router.post("/create-payment-intent", response_model=PaymentIntentResponse)
async def create_payment_intent(
    payment_data: PaymentIntentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a Stripe PaymentIntent for a single video purchase.
    """
    if not settings.stripe_secret_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payment service not configured"
        )

    # Determine amount based on payment type
    if payment_data.payment_type == "single_video":
        amount = 5000  # $50.00 in cents
    else:
        raise HTTPException(status_code=400, detail="Invalid payment type")

    # Verify job exists and belongs to user (if specified)
    if payment_data.video_job_id:
        result = await db.execute(
            select(VideoJob).where(
                VideoJob.id == payment_data.video_job_id,
                VideoJob.user_id == current_user.id
            )
        )
        job = result.scalar_one_or_none()
        if not job:
            raise HTTPException(status_code=404, detail="Video job not found")

    try:
        # Create PaymentIntent
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency="usd",
            customer=current_user.stripe_customer_id,
            metadata={
                "user_id": current_user.id,
                "video_job_id": payment_data.video_job_id,
                "payment_type": payment_data.payment_type
            }
        )

        # Record payment intent in database
        payment = Payment(
            user_id=current_user.id,
            video_job_id=payment_data.video_job_id,
            stripe_payment_intent_id=intent.id,
            amount=amount,
            currency="usd",
            status="pending",
            payment_type=payment_data.payment_type
        )
        db.add(payment)
        await db.commit()

        return PaymentIntentResponse(
            client_secret=intent.client_secret,
            amount=amount,
            currency="usd"
        )

    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/create-subscription")
async def create_subscription(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a subscription for unlimited video generation.
    """
    if not settings.stripe_secret_key or not settings.stripe_price_subscription:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Subscription service not configured"
        )

    try:
        # Create subscription
        subscription = stripe.Subscription.create(
            customer=current_user.stripe_customer_id,
            items=[{"price": settings.stripe_price_subscription}],
            payment_behavior="default_incomplete",
            expand=["latest_invoice.payment_intent"]
        )

        return {
            "subscription_id": subscription.id,
            "client_secret": subscription.latest_invoice.payment_intent.client_secret
        }

    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Handle Stripe webhook events.
    """
    if not settings.stripe_webhook_secret:
        raise HTTPException(status_code=400, detail="Webhook not configured")

    payload = await request.body()

    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, settings.stripe_webhook_secret
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle specific events
    if event["type"] == "payment_intent.succeeded":
        await handle_payment_success(event["data"]["object"], db)
    elif event["type"] == "payment_intent.payment_failed":
        await handle_payment_failure(event["data"]["object"], db)
    elif event["type"] == "customer.subscription.updated":
        await handle_subscription_update(event["data"]["object"], db)
    elif event["type"] == "customer.subscription.deleted":
        await handle_subscription_deleted(event["data"]["object"], db)

    return {"status": "success"}


async def handle_payment_success(payment_intent, db: AsyncSession):
    """Handle successful payment."""
    # Update payment record
    result = await db.execute(
        select(Payment).where(Payment.stripe_payment_intent_id == payment_intent["id"])
    )
    payment = result.scalar_one_or_none()

    if payment:
        payment.status = "succeeded"
        await db.commit()


async def handle_payment_failure(payment_intent, db: AsyncSession):
    """Handle failed payment."""
    result = await db.execute(
        select(Payment).where(Payment.stripe_payment_intent_id == payment_intent["id"])
    )
    payment = result.scalar_one_or_none()

    if payment:
        payment.status = "failed"
        await db.commit()


async def handle_subscription_update(subscription, db: AsyncSession):
    """Handle subscription status update."""
    customer_id = subscription["customer"]

    result = await db.execute(
        select(User).where(User.stripe_customer_id == customer_id)
    )
    user = result.scalar_one_or_none()

    if user:
        status_map = {
            "active": SubscriptionStatus.ACTIVE,
            "past_due": SubscriptionStatus.PAST_DUE,
            "canceled": SubscriptionStatus.CANCELED,
            "trialing": SubscriptionStatus.TRIALING
        }
        user.subscription_status = status_map.get(subscription["status"])
        user.subscription_id = subscription["id"]
        await db.commit()


async def handle_subscription_deleted(subscription, db: AsyncSession):
    """Handle subscription cancellation."""
    customer_id = subscription["customer"]

    result = await db.execute(
        select(User).where(User.stripe_customer_id == customer_id)
    )
    user = result.scalar_one_or_none()

    if user:
        user.subscription_status = SubscriptionStatus.CANCELED
        user.subscription_id = None
        await db.commit()


@router.get("/subscription/status")
async def get_subscription_status(
    current_user: User = Depends(get_current_user)
):
    """Get current user's subscription status."""
    return {
        "subscription_status": current_user.subscription_status,
        "subscription_id": current_user.subscription_id,
        "has_active_subscription": current_user.subscription_status == SubscriptionStatus.ACTIVE
    }
