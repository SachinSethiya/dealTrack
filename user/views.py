from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import User
from .forms import UserForm

# List View
class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'user/user_list.html'
    context_object_name = 'users'
    paginate_by = 10
    
    def get_queryset(self):
        return User.objects.filter(showroom=self.request.user).order_by('-created_at')

# Detail View
class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'user/user_detail.html'
    context_object_name = 'user_obj'
    pk_url_kwarg = 'user_id'
    
    def get_object(self):
        return get_object_or_404(User, user_id=self.kwargs['user_id'], showroom=self.request.user)

# Create View
@login_required
def create_user(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.showroom = request.user
            user.save()
            messages.success(request, f'User {user.name} created successfully!')
            return redirect('user_list')
        else:
            messages.error(request, 'Error creating user. Please check the form.')
    else:
        form = UserForm()
    
    return render(request, 'user/user_form.html', {
        'form': form,
        'title': 'Add New User',
        'action': 'Create'
    })

# Update View
@login_required
def update_user(request, user_id):
    user = get_object_or_404(User, user_id=user_id, showroom=request.user)
    
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f'User {user.name} updated successfully!')
            return redirect('user_detail', user_id=user_id)
        else:
            messages.error(request, 'Error updating user. Please check the form.')
    else:
        form = UserForm(instance=user)
    
    return render(request, 'user/user_form.html', {
        'form': form,
        'user_obj': user,
        'title': 'Edit User',
        'action': 'Update'
    })

# Delete View
@login_required
def delete_user(request, user_id):
    user = get_object_or_404(User, user_id=user_id, showroom=request.user)
    
    if request.method == 'POST':
        user_name = user.name
        user.delete()
        messages.success(request, f'User {user_name} deleted successfully!')
        return redirect('user_list')
    
    return render(request, 'user/user_confirm_delete.html', {
        'user_obj': user
    })

# Legacy function for backward compatibility
def user(request):
    return UserListView.as_view()(request)