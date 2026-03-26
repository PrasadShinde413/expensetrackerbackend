from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Sum
from .models import User, TempUser, Category, Transaction, Budget
from .serializers import CategorySerializer, TransactionSerializer, BudgetSerializer
from .utils import generate_otp, send_otp_email  
# ✅ CORRECT
from django.shortcuts import get_object_or_404

# --- AUTHENTICATION ---

class RegisterView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({"error": "Email and password required"}, status=400)

        # 1. Check if User exists
        if User.objects.filter(email=email).exists():
            return Response({"error": "User already exists with this email"}, status=400)

        # 2. Prepare Data
        otp = generate_otp()
        hashed_pw = make_password(password)

        # 3. Store in TempUser table
        TempUser.objects.create(email=email, password=hashed_pw, otp=otp)

        # 4. SEND REAL EMAIL
        email_sent = send_otp_email(email, otp)

        if email_sent:
            return Response({"message": f"OTP successfully sent to {email}"})
        else:
            return Response({"error": "Account pending, but failed to send email. Check SMTP settings."}, status=500)

class VerifyOTPView(APIView):
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        
        temp_user = TempUser.objects.filter(email=email, otp=otp).last()
        if not temp_user:
            return Response({"error": "Invalid OTP"}, status=400)
            
        user = User.objects.create(email=email, password=temp_user.password)
        temp_user.delete()
        
        return Response({"message": "Account created", "user_id": user.id})

class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        user = User.objects.filter(email=email).first()
        if user and check_password(password, user.password):
            return Response({"message": "Login successful", "user_id": user.id})
        
        return Response({"error": "Invalid credentials"}, status=401)

# --- RESOURCE MANAGEMENT (Isolation by user_id) ---

class CategoryView(APIView):
    def get(self, request, user_id):
        items = Category.objects.filter(user_id=user_id)
        return Response(CategorySerializer(items, many=True).data)

    def post(self, request, user_id):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user_id=user_id)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

# class CategoryDetailView(APIView):
#     def put(self, request, user_id, pk):
#         item = CategorySerializer(Category, user_id=user_id, pk=pk)
#         serializer = CategorySerializer(item, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=400)

#     def delete(self, request, user_id, pk):
#         item = CategorySerializer(Category, user_id=user_id, pk=pk)
#         item.delete()
#         return Response({"message": "Category deleted successfully"}, status=204)
    

class CategoryDetailView(APIView):
    def put(self, request, user_id, pk):
        # Changed to _404
        item = get_object_or_404(Category, user_id=user_id, pk=pk)
        
        serializer = CategorySerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, user_id, pk):
        # Changed to _404
        item = get_object_or_404(Category, user_id=user_id, pk=pk)
        item.delete()
        return Response({"message": "Category deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    

class TransactionView(APIView):
    def get(self, request, user_id):
        items = Transaction.objects.filter(user_id=user_id).order_by('-date')
        return Response(TransactionSerializer(items, many=True).data)

    def post(self, request, user_id):
        serializer = TransactionSerializer(data=request.data)
        if serializer.is_valid():
            # Validate that the category belongs to the same user
            if serializer.validated_data['category'].user_id != int(user_id):
                return Response({"error": "Category mismatch"}, status=403)
            serializer.save(user_id=user_id)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class TransactionDetailView(APIView):
    def put(self, request, user_id, pk):
        item = get_object_or_404(Transaction, user_id=user_id, pk=pk)
        serializer = TransactionSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, user_id, pk):
        item = get_object_or_404(Transaction, user_id=user_id, pk=pk)
        item.delete()
        return Response({"message": "Transaction deleted"}, status=204)
    

class DashboardView(APIView):
    def get(self, request, user_id):
        txs = Transaction.objects.filter(user_id=user_id)
        income = txs.filter(type='income').aggregate(Sum('amount'))['amount__sum'] or 0
        expense = txs.filter(type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
        
        recent = txs.order_by('-id')[:5]
        
        return Response({
            "total_income": income,
            "total_expense": expense,
            "balance": income - expense,
            "recent_transactions": TransactionSerializer(recent, many=True).data
        })

class ReportView(APIView):
    def get(self, request, user_id):
        # Filtering logic
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        qs = Transaction.objects.filter(user_id=user_id)
        if start_date: qs = qs.filter(date__gte=start_date)
        if end_date: qs = qs.filter(date__lte=end_date)
        
        # Pie chart data
        category_summary = qs.values('category__name').annotate(total=Sum('amount'))
        
        # Monthly trend logic would go here...
        
        return Response({
            "category_summary": list(category_summary),
            "total_records": qs.count()
        })